# This script takes the resumes and job description and matches the resumes to the job description.
# importing necessary libraries
from pathlib import Path
import re
import requests
import numpy as np
import json
import glob

# importing components
import Config
from utils import utils

JUDGE_SYSTEM = (
    "You are a strict hiring screener. "
    "Return concise, consistent JSON only—no extra text."
)

JUDGE_PROMPT_TEMPLATE = """JOB DESCRIPTION:
{jd}

RESUME EXCERPTS (most relevant first):
{excerpts}

Task: Score how well this candidate fits this job (0–100).

Rubric (strict):
- 60% responsibilities/requirements fit (must be evidenced in excerpts)
- 25% skills/tools match (explicit mentions preferred)
- 10% experience alignment (years/seniority)
- 5% other positives (education, domain, location)
If critical must-haves are missing, cap the score ≤ 60.

Output JSON ONLY:
{{
  "score": <0-100 integer>,
  "matched_skills": ["..."],
  "missing_must_haves": ["..."],
  "evidence_sentences": ["..."],
  "notes": "..."
}}"""


def chunk_text(text: str, target=Config.CHUNK_CHAR_TARGET, overlap=Config.CHUNK_CHAR_OVERLAP):
    """
    Character-based chunking with overlap, preferring to break on sentence boundaries.
    """
    # Normalize newlines to help sentence splitting
    text = re.sub(r"\r\n?", "\n", text)
    sentences = re.split(r"(?<=[\.\!\?])\s+(?=[A-Z0-9])", text)

    chunks = []
    buf = ""
    for s in sentences:
        if len(buf) + len(s) + 1 <= target:
            buf += ((" " if buf else "") + s)
        else:
            if buf:
                chunks.append(buf.strip())
                # start new buffer with overlap from end of previous buffer
                if overlap > 0 and len(buf) > overlap:
                    buf = buf[-overlap:] + " " + s
                else:
                    buf = s
            else:
                # very long single sentence; hard cut
                chunks.append(s[:target])
                buf = s[target-overlap:target] if overlap > 0 else ""
    if buf.strip():
        chunks.append(buf.strip())

    # Final cleanup
    return [c.strip() for c in chunks if c.strip()]

def ollama_embed(texts, model=Config.EMBED_MODEL):
    """Calls Ollama embeddings endpoint. Returns (n, d) numpy array."""
    # Ollama accepts one text per call; we’ll batch to avoid huge payloads.
    embs = []
    for t in texts:
        resp = requests.post(
            f"{Config.OLLAMA_HOST}/api/embeddings",
            json={"model": model, "prompt": t},
            timeout=Config.REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
        vec = np.array(data["embedding"], dtype=np.float32)
        embs.append(vec)
    return np.vstack(embs)

def cosine_sim_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Row-wise cosine similarity between A (n,d) and B (m,d)"""
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-9)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-9)
    return a_norm @ b_norm.T


def retrieve_top_chunks(jd_text, resume_text, k=Config.TOP_K):
    jd_chunks = [jd_text]
    resume_chunks = chunk_text(resume_text, Config.CHUNK_CHAR_TARGET, Config.CHUNK_CHAR_OVERLAP)

    if not resume_chunks:
        return [], []

    jd_emb = ollama_embed(jd_chunks)            # (1, d)
    res_emb = ollama_embed(resume_chunks)       # (n, d)

    sims = cosine_sim_matrix(res_emb, jd_emb).ravel()  # similarity of each chunk to JD
    top_idx = np.argsort(sims)[-k:][::-1]
    top_chunks = [resume_chunks[i] for i in top_idx]
    top_scores = [float(sims[i]) for i in top_idx]
    return top_chunks, top_scores

def build_excerpts_block(chunks):
    lines = []
    for i, c in enumerate(chunks, 1):
        # clip very long chunks to keep prompt size manageable
        trimmed = c if len(c) <= 1200 else c[:1200] + " …"
        lines.append(f"[{i}] {trimmed}")
    return "\n\n".join(lines)

def call_ollama_chat(prompt, system=JUDGE_SYSTEM, model=Config.LLM_MODEL) -> str:
    """Calls /api/chat with streaming disabled, returns the raw model text."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "options": {"temperature": 0},
        "stream": False
    }
    resp = requests.post(f"{Config.OLLAMA_HOST}/api/chat", json=payload, timeout=Config.REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return data.get("message", {}).get("content", "").strip()

def parse_strict_json(text):
    """Extract and validate a JSON object from model output."""
    # Try direct parse first
    try:
        return json.loads(text)
    except Exception:
        pass
    # Fallback: find first {...} block
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError("No JSON object found in model output.")
    return json.loads(m.group(0))

def judge_resume_against_jd(jd_text, top_chunks):
    excerpts = build_excerpts_block(top_chunks)
    prompt = JUDGE_PROMPT_TEMPLATE.format(jd=jd_text, excerpts=excerpts)
    out = call_ollama_chat(prompt)
    try:
        data = parse_strict_json(out)
    except Exception as e:
        # one retry with explicit correction
        correction = "\n\nYour previous output was not valid JSON. Respond with valid JSON only."
        out2 = call_ollama_chat(prompt + correction)
        data = parse_strict_json(out2)

    # light sanity checks
    data["score"] = int(max(0, min(100, int(data.get("score", 0)))))
    data.setdefault("matched_skills", [])
    data.setdefault("missing_must_haves", [])
    data.setdefault("evidence_sentences", [])
    data.setdefault("notes", "")
    return data

def score_one_resume(jd_path, resume_path):
    jd_text = Path(jd_path).read_text(encoding="utf-8").strip()
    resume_text = utils.extract_text_from_pdf(resume_path)

    top_chunks, top_scores = retrieve_top_chunks(jd_text, resume_text, k=Config.TOP_K)
    if not top_chunks:
        return {
            "candidate": Path(resume_path).name,
            "error": "No text extracted / no chunks found."
        }

    judge = judge_resume_against_jd(jd_text, top_chunks)
    return {
        "candidate": Path(resume_path).name,
        "score": judge["score"],
        "matched_skills": judge["matched_skills"],
        "missing_must_haves": judge["missing_must_haves"],
        "evidence_sentences": judge["evidence_sentences"],
        "notes": judge["notes"],
        "retrieval": {
            "top_k": Config.TOP_K,
            "chunk_similarities": top_scores
        }
    }

def score_directory(jd_path, resumes_dir):
    results = []
    for pdf in sorted(glob.glob(str(Path(resumes_dir) / "*.pdf"))):
        try:
            res = score_one_resume(jd_path, pdf)
        except Exception as e:
            res = {"candidate": Path(pdf).name, "error": str(e)}
        results.append(res)

    # sort by score desc if available
    results.sort(key=lambda r: r.get("score", -1), reverse=True)
    return results