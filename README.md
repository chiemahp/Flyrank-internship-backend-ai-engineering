# RAG Document QA

This repository contains a backend-focused learning project for building a Retrieval-Augmented Generation (RAG) document Q&A system, along with a sequence of assignment-based backend exercises that lead up to the full capstone project.

## Overview

The workspace is organized as a set of small, runnable Python projects covering:

- REST API development with FastAPI
- SQLite database integration
- JWT authentication
- Dockerized full-stack deployment
- AI-powered API integration
- Respectful web scraping
- RAG document Q&A capstone

## Repository structure

```text
RAG_Document_QA/
├── README.md
├── ASSIGNMENTS_README.md
├── assignment_01_crud_api/
├── assignment_02_database_api/
├── assignment_03_auth_api/
├── assignment_04_docker_fullstack/
├── assignment_05_ai_api/
├── assignment_06_respectful_scraper/
├── RAG_Document_QA/
│   └── RAG_Document_QA_Capstone/
└── describe/
```

## Assignments

Each assignment is a standalone project with its own README and dependency list:

1. `assignment_01_crud_api` — in-memory CRUD REST API
2. `assignment_02_database_api` — CRUD API backed by SQLite and SQLAlchemy
3. `assignment_03_auth_api` — JWT-protected API
4. `assignment_04_docker_fullstack` — server-rendered web app with Docker Compose
5. `assignment_05_ai_api` — API service using an LLM chat endpoint
6. `assignment_06_respectful_scraper` — robots-aware, rate-limited scraper

## Capstone project

The main capstone project lives in:

- `RAG_Document_QA/RAG_Document_QA_Capstone`

This project builds a document-based Q&A assistant that can:

- ingest PDF content
- split documents into chunks
- generate embeddings
- store embeddings in a vector database
- answer questions using a retrieval-augmented generation flow
- provide a simple Streamlit interface

## Quick start for the capstone

From the project root:

```bash
cd "RAG_Document_QA/RAG_Document_QA_Capstone"
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# or .venv\Scripts\Activate.ps1 on Windows PowerShell
pip install -r requirements.txt
cp .env.example .env
```

Then configure your environment variables in `.env` and run the pipeline:

```bash
python 01_ingest_chunk.py
python 02_embed_store.py
python 03_qa_chain.py
```

To run the Streamlit app:

```bash
streamlit run streamlit_app.py
```

To run with Docker:

```bash
docker compose up --build
```

## Notes

- Each assignment is independent and designed to be run from its own folder.
- The capstone project is the final application and demonstrates practical RAG workflows for document understanding.
- The project is intended for learning, experimentation, and assignment-based backend development.
