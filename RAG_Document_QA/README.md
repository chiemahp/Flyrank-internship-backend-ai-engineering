# Enterprise AI Knowledge Assistant — PDF RAG capstone

A local Retrieval-Augmented Generation (RAG) application that indexes PDF
documents in a persistent Chroma vector store, retrieves relevant passages,
and answers questions with source-file and page citations. PDFs can be added
from the Streamlit sidebar; each upload is added to the existing collection.

## Features

- Recursive PDF ingestion and configurable-size text chunking
- Persistent local Chroma storage with stable chunk IDs
- Groq chat completion with a configurable model
- Local embeddings through Chroma's default `all-MiniLM-L6-v2` model
- MMR retrieval and answers grounded in retrieved context
- Source filename and page citations shown with each answer
- Additive PDF uploads with filename sanitization, PDF validation, and a 20 MB
  per-file limit
- Local Python and Docker Compose run options
- Unit tests for chunking, upload validation, storage paths, and configuration

## Requirements

- Python 3.10 or later (the Docker image uses Python 3.12)
- A Groq API key for answering questions
- PDFs that you are authorized to process

Question text and retrieved passages are sent to Groq for answers. Embeddings
are generated locally by ChromaDB; its embedding model may be downloaded the
first time it is used. Do not upload confidential or regulated documents
unless your organization's policy permits this.

## Local setup (PowerShell)

Run from this project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:GROQ_API_KEY = "your-key"
# Optional: $env:GROQ_MODEL = "openai/gpt-oss-120b"
```

Copy `.env.example` to `.env` and add your Groq key there. The app loads `.env`
at startup, and `.env` is ignored by Git. Never commit API keys. Alternatively,
set `GROQ_API_KEY` in the current PowerShell session as shown above.

## Run

### Web application

```powershell
streamlit run streamlit_app.py
```

Open the displayed local URL, use the sidebar to select one or more PDFs, and
click **Add PDFs to knowledge base**. Uploaded files are checked, saved under
`docs/uploads/`, split into chunks, and indexed into the current Chroma
collection. Uploading an already-indexed file does not create duplicate chunks.
Ask a question in the chat box; each assistant response lists the retrieved
source files and one-based page numbers.

The Streamlit server enforces the configured 20 MB per-file upload size. The
same limit is checked in application code. The uploader accepts PDF files;
image-only/scanned PDFs require OCR and are not indexed as text.

### Command-line pipeline

The first three scripts are optional inspection and terminal workflows; they
are not required before using the upload-enabled app.

```powershell
python 01_ingest_chunk.py
python 02_embed_store.py
python 03_qa_chain.py "What are the main topics?"
```

`01_ingest_chunk.py` inspects the PDF chunks. `02_embed_store.py` embeds and
upserts all PDFs under `docs/`. `03_qa_chain.py` asks a single terminal
question. Run these commands from this directory so the default `docs/` and
`chroma_db/` paths resolve consistently.

## Docker Compose

Set the key in the current PowerShell session, then build and run:

```powershell
$env:GROQ_API_KEY = "your-key"
docker compose up --build
```

Optionally set `GROQ_MODEL` to choose another Groq model.

Open `http://localhost:8501`. Compose mounts named volumes for both uploaded
PDFs and the vector database, so they persist across container restarts. Stop
with `docker compose down`; to explicitly remove persisted data too, use
`docker compose down --volumes`.

## Tests

Run the offline unit tests from the project directory:

```powershell
python -m unittest discover -s tests -v
```

To verify the full application, set a valid API
key, upload a PDF containing text, and compare returned answers and citations
with the document itself.

## Pipeline settings

- Chunk size: 800 characters
- Chunk overlap: 100 characters
- Chroma collection: `my_docs_groq`
- Embedding model: Chroma's local default, `all-MiniLM-L6-v2`
- Chat model: `GROQ_MODEL` (default
  `openai/gpt-oss-120b`), temperature 0
- Retrieval: Maximal Marginal Relevance, `k=5`, `fetch_k=20`

The model is instructed to answer only from retrieved context and say "I don't
know" if the context does not provide an answer. Retrieval can still miss
relevant passages; validate answers and citations against the source PDF.



## Project files

- `rag_core.py` — loading, chunking, validation, vector-store, and QA logic
- `01_ingest_chunk.py`, `02_embed_store.py`, `03_qa_chain.py` — command-line
  pipeline steps
- `streamlit_app.py` — chat UI and PDF upload interface
- `tests/` — offline unit tests
- `Dockerfile`, `compose.yaml` — container deployment
- `SUBMISSION_CHECKLIST.md` — packaging and final verification checklist
- `package_submission.ps1` — creates a ZIP in the parent folder while excluding
  local PDFs, vector data, environments, databases, and secrets

To create the archive from PowerShell:

```powershell
.\package_submission.ps1
```

## Limitations and responsible use

This is a local academic proof of concept, not a production enterprise service.
It has no user login, tenant isolation, document-level authorization,
encryption-at-rest configuration, OCR, automated evaluation suite, or
background job queue. Anyone who can access the local app can use its
knowledge base. Do not expose it to an untrusted network or use it for private
content without adding appropriate controls.

## Project Demo-Video: 
