# AI-Based-Resume-Matching
This application will use AI to match resumes with a job description, summarise resumes and have the ability to chat with the assistant about the job or the resume

# Task
Build a small GenAI application that matches one or more resumes to a job description (JD) and shortlists resumes with more than 80% match.

The application must have the following:

* A front-end interface to upload Job Description and one or more resumes
* Application will do the AI analysis and arrive at a % match
* Application must also provide a summary of each resume

# Usage

1. Install ollama and pull the required models
```
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text
ollama pull llama3.1:8b        
```

2. Clone the repo
```
git clone https://github.com/anandhakrishnanh/AI-Based-Resume-Matching.git
cd AI-Based-Resume-Matching
```

3. Install the required packages
```
pip install -r requirements.txt
```

4. Run the application
```
chmod +x run.sh
./run.sh
```

# How it works
1. Upload a job description and one or more resumes using the front-end interface
2. We use a "llama3.1:8b" model to generate resume summaries for each resume
3. We use the "nomic-embed-text" model to generate embeddings for the job description and each resume
4. We extract the the most similar chunks from reach resume to the job description using cosine similarity
5. We use the "llama3.1:8b" model to generate a match percentage based on the similar chunks extracted in the previous step
6. We shortlist resumes with more than 80% match

# Improvements to be done later
1. CRUD operations to store JDs and resumes
2. User authentication
3. Use a database to store JDs and resumes
4. Instead of relying on an LLM, use a vector database to store embeddings of JDs and resumes and do similarity search
