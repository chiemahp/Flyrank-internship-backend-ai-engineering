FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rag_core.py streamlit_app.py ./
COPY 01_ingest_chunk.py 02_embed_store.py 03_qa_chain.py ./
COPY .streamlit ./.streamlit

RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/docs /app/chroma_db \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
