# This script contains the different functions and scripts used to generate summaries of resumes and job descriptions.
# importing the necessary libraries
import requests

# importing the necessary components
import Config

SYSTEM_PROMPT = (
    "You are an expert résumé analyst. Write a concise, neutral, factual summary from the text provided. "
    "Do not invent details. Use bullet points where helpful. Output plain text only."
)

# Final summary target style (plain text)
FINAL_INSTRUCTIONS = """Summarize this résumé for a recruiter. Focus on substance over prose.
Length: ~200–300 words.

Include these labeled sections in plain text:
- Profile: 2–3 lines (role, seniority, domains)
- Key Skills: comma-separated list (tools, frameworks, clouds, languages)
- Experience Highlights: 4–6 bullets (quantified impact if present, recent-first)
- Education & Certs: brief
- Notable Projects: 2–3 bullets (what/impact)
- Keywords: 12–18 terms for search (no duplicates)

Do not include personal data like phone, email, full address. Do not guess missing info."""

# Shorter summary for each chunk (used when merging)
CHUNK_INSTRUCTIONS = """Summarize this résumé segment focusing on role, seniority, tech stack, domains, and tangible achievements.
Use 4–6 bullets. No fluff. Plain text only."""

def call_ollama(prompt, system=SYSTEM_PROMPT, model=Config.LLM_MODEL, temperature=0.0) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "options": {"temperature": temperature},
        "stream": False
    }
    resp = requests.post(f"{Config.OLLAMA_HOST}/api/chat", json=payload, timeout=Config.REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return data.get("message", {}).get("content", "").strip()

def chunk_text(s: str, size=Config.CHUNK_SIZE, overlap=Config.CHUNK_OVERLAP):
    if len(s) <= size:
        return [s]
    chunks = []
    start = 0
    while start < len(s):
        end = min(len(s), start + size)
        chunks.append(s[start:end])
        if end == len(s):
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

def summarize_text(resume_text):
    if len(resume_text) <= Config.MAX_CHARS_SINGLE:
        prompt = FINAL_INSTRUCTIONS + "\n\nRESUME TEXT:\n" + resume_text
        return call_ollama(prompt)

    # Chunk → summarize each → merge
    chunks = chunk_text(resume_text)
    chunk_summaries = []
    for i, ch in enumerate(chunks, 1):
        prompt = f"{CHUNK_INSTRUCTIONS}\n\nRESUME SEGMENT [{i}/{len(chunks)}]:\n{ch}"
        chunk_summaries.append(call_ollama(prompt))

    # Merge pass
    merge_source = "\n\n---\n".join(chunk_summaries)
    merge_prompt = FINAL_INSTRUCTIONS + "\n\nCONSOLIDATE THESE SEGMENT SUMMARIES INTO ONE COHERENT RESUME SUMMARY:\n" + merge_source
    return call_ollama(merge_prompt)
