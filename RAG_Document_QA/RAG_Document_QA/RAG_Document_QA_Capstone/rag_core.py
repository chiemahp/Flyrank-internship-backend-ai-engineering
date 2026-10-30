"""Shared ingestion, vector-store, and retrieval-chain setup for the capstone."""

import hashlib
from io import BytesIO
import os
import re
from pathlib import Path
from typing import Any

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from pypdf.errors import PdfReadError

DEFAULT_DOCS_DIR = Path("docs")
DEFAULT_DB_DIR = Path("chroma_db")
COLLECTION_NAME = "my_docs"
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
MAX_PDF_UPLOAD_BYTES = 20 * 1024 * 1024


def split_documents(
    documents: list[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Document]:
    """Split loaded pages into chunks and normalize source metadata."""
    if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("Require chunk_size > chunk_overlap >= 0")
    if not documents:
        raise ValueError("No pages could be loaded from the supplied PDFs.")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    for chunk in chunks:
        source = Path(str(chunk.metadata.get("source", "")))
        try:
            chunk.metadata["source"] = str(source.resolve().relative_to(Path.cwd()))
        except ValueError:
            chunk.metadata["source"] = str(source.resolve())
    return chunks


def load_and_split_documents(
    docs_dir: Path = DEFAULT_DOCS_DIR,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Document]:
    """Load PDFs recursively and split pages into overlapping chunks."""
    if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("Require chunk_size > chunk_overlap >= 0")
    if not docs_dir.is_dir():
        raise FileNotFoundError(f"PDF directory does not exist: {docs_dir}")
    pdf_paths = sorted(docs_dir.rglob("*.pdf"))
    if not pdf_paths:
        raise FileNotFoundError(f"No PDF files found under: {docs_dir}")

    documents: list[Document] = []
    for pdf_path in pdf_paths:
        documents.extend(PyPDFLoader(str(pdf_path)).load())
    return split_documents(documents, chunk_size, chunk_overlap)


def index_uploaded_pdf(
    filename: str,
    content: bytes,
    docs_dir: Path = DEFAULT_DOCS_DIR,
    persist_directory: Path = DEFAULT_DB_DIR,
) -> tuple[str, int]:
    """Validate, persist, and index one uploaded PDF without replacing others."""
    if not content:
        raise ValueError("The uploaded PDF is empty.")
    if len(content) > MAX_PDF_UPLOAD_BYTES:
        raise ValueError("PDF exceeds the 20 MB upload limit.")
    if b"%PDF-" not in content[:1024]:
        raise ValueError("The uploaded file does not have a valid PDF header.")

    original_name = Path(filename.replace("\\", "/")).name
    if not original_name.lower().endswith(".pdf"):
        raise ValueError("Only files with a .pdf extension are accepted.")
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", original_name)
    if not safe_name or safe_name.lower() == ".pdf":
        raise ValueError("The uploaded PDF must have a valid filename.")

    try:
        reader = PdfReader(BytesIO(content), strict=False)
    except PdfReadError as exc:
        raise ValueError("The uploaded file is not a readable PDF.") from exc
    if not reader.pages:
        raise ValueError("The uploaded PDF contains no pages.")

    digest = hashlib.sha256(content).hexdigest()
    upload_dir = docs_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / f"{digest}-{safe_name}"
    created_file = False
    if destination.exists():
        if destination.read_bytes() != content:
            raise FileExistsError(f"An upload already exists at {destination}.")
    else:
        destination.write_bytes(content)
        created_file = True

    indexed = False
    try:
        pages = PyPDFLoader(str(destination)).load()
        chunks = split_documents(pages)
        if not chunks:
            raise ValueError(
                "No extractable text was found in the PDF. "
                "Scanned PDFs need OCR before they can be indexed."
            )
        store_chunks(chunks, persist_directory)
        indexed = True
    finally:
        if created_file and not indexed:
            destination.unlink(missing_ok=True)

    try:
        source = destination.resolve().relative_to(Path.cwd())
    except ValueError:
        source = destination.resolve()
    return source.as_posix(), len(chunks)


def get_vectorstore(
    persist_directory: Path = DEFAULT_DB_DIR,
) -> Chroma:
    """Open the persistent Chroma collection with the configured embeddings."""
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set. Export it before indexing or querying PDFs.")
    return Chroma(
        persist_directory=str(persist_directory),
        embedding_function=OpenAIEmbeddings(model=EMBEDDING_MODEL),
        collection_name=COLLECTION_NAME,
    )


def store_chunks(
    chunks: list[Document],
    persist_directory: Path = DEFAULT_DB_DIR,
) -> Chroma:
    """Upsert chunks by a stable content-derived id to make reruns idempotent."""
    if not chunks:
        raise ValueError("No document chunks to store")
    vectorstore = get_vectorstore(persist_directory)
    ids = []
    for chunk in chunks:
        identity = "\0".join(
            (
                str(chunk.metadata.get("source", "")),
                str(chunk.metadata.get("page", "")),
                chunk.page_content,
            )
        )
        ids.append(hashlib.sha256(identity.encode("utf-8")).hexdigest())
    vectorstore.add_documents(chunks, ids=ids)
    return vectorstore


def build_qa_chain(
    persist_directory: Path = DEFAULT_DB_DIR,
) -> Any:
    """Build a question-answer chain that returns source documents with answers."""
    vectorstore = get_vectorstore(persist_directory)
    collection = vectorstore.get(limit=1)
    if not collection.get("ids"):
        raise ValueError(
            f"No indexed documents found in {persist_directory}. "
            "Add PDFs to docs and run 02_embed_store.py first."
        )

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 5, "fetch_k": 20},
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer the question using only the supplied context. "
                'If the answer is not in the context, say "I don\'t know." '
                "Do not invent citations.",
            ),
            ("human", "Context:\n{context}\n\nQuestion: {question}"),
        ]
    )
    llm = ChatOpenAI(model=CHAT_MODEL, temperature=0)

    def format_documents(documents: list[Document]) -> str:
        return "\n\n".join(
            f"[Source: {document.metadata.get('source', 'unknown')}, "
            f"page: {int(document.metadata.get('page', 0)) + 1}]\n"
            f"{document.page_content}"
            for document in documents
        )

    def qa_step(question: str) -> dict[str, Any]:
        docs = retriever.invoke(question)
        context = format_documents(docs)
        answer = llm.invoke(prompt.format(context=context, question=question)).content
        return {"result": answer, "source_documents": docs}

    return RunnableLambda(qa_step)
