# DIRECTORY PATHS
DATA_DIRECTORY = "/media/anandha/Linux Files2/Projects/AI-Based-Resume-Matching/data"
RESUME_DIRECTORY = "/media/anandha/Linux Files2/Projects/AI-Based-Resume-Matching/data/resumes"
JOB_DESCRIPTION_DIRECTORY = "/media/anandha/Linux Files2/Projects/AI-Based-Resume-Matching/data/job_descriptions"
RESUME_SUMMARY = "/media/anandha/Linux Files2/Projects/AI-Based-Resume-Matching/data/resume_summaries"

# MATCHING PARAMETERS
MATCHING_METHOD = "LLM" # Options: "Keyword", "LLM"

# LLM PARAMETERS
OLLAMA_HOST = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL   = "llama3.1:8b"
REQUEST_TIMEOUT = 120  # seconds

# Resume summary model parameters
MAX_CHARS_SINGLE  = 14000
CHUNK_SIZE        = 12000
CHUNK_OVERLAP     = 500

# Ranking parameters
CHUNK_CHAR_TARGET = 1200     # ~750–900 tokens equivalent for prose; adjust as needed
CHUNK_CHAR_OVERLAP = 200     # overlap to preserve context
TOP_K = 6                    # how many chunks to pass to the judge
SHOW_TOP_N_RESUMES = 5       # how many top resumes to show in the frontend
SCORE_THRESHOLD = 80