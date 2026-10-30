# Final-year project submission checklist

## Before packaging

- [ ] Replace the author, institution, supervisor, course, and submission-date
  placeholders in any cover page or report required by your department.
- [ ] Keep only documents and API keys you are authorized to use. Do not include
  a real `.env`, `.streamlit/secrets.toml`, private PDF, or local vector database.
- [ ] Create a fresh Python environment and install `requirements.txt`.
- [ ] Run the automated tests with
  `python -m unittest discover -s tests -v`.
- [ ] Run the app, upload a permitted PDF, ask questions with a known answer, and
  verify each answer's source file and page against that PDF.
- [ ] Test an unsupported/non-PDF upload and a question not answered in the
  documents; record the observed behavior honestly in your report.
- [ ] If Docker is part of the submission, build and run with Compose and verify
  uploaded documents remain available after restarting the container.
- [ ] Include screenshots, measured results, and evaluation data only when you
  have actually collected them. Do not claim results this project has not
  measured.
- [ ] Follow your department's rules for AI assistance, citations, code
  attribution, report format, and archive naming.

## Recommended archive contents

Include source files, `requirements.txt`, `README.md`, this checklist, tests,
Docker files, and an `.env.example` with no secrets. Exclude `.venv/`, generated
`__pycache__/`, `docs/` containing user PDFs, `.env`, and `chroma_db/`.
