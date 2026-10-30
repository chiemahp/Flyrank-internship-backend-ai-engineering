"""Streamlit chat interface for the persistent PDF RAG collection."""

from pathlib import Path

import streamlit as st
from openai import OpenAIError

from rag_core import DEFAULT_DB_DIR, DEFAULT_DOCS_DIR, build_qa_chain, index_uploaded_pdf

st.set_page_config(page_title="Document Q&A", page_icon="📄")
st.title("Document Q&A with RAG")
st.caption("Answers are grounded in the indexed PDFs and include source pages.")


@st.cache_resource
def get_qa_chain(db_directory: str):
    return build_qa_chain(Path(db_directory))


with st.sidebar:
    st.header("Knowledge base")
    st.write("Upload PDFs to add them to the existing index.")
    with st.form("pdf_upload_form", clear_on_submit=True):
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            help="Maximum 20 MB per file. Uploaded files are stored locally.",
        )
        submit_uploads = st.form_submit_button("Add PDFs to knowledge base")

    if submit_uploads:
        if not uploaded_files:
            st.warning("Choose at least one PDF to upload.")
        else:
            notices: list[tuple[str, str]] = []
            for uploaded_file in uploaded_files:
                try:
                    source, chunk_count = index_uploaded_pdf(
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        DEFAULT_DOCS_DIR,
                        DEFAULT_DB_DIR,
                    )
                    notices.append(
                        ("success", f"Indexed {source} ({chunk_count} chunks).")
                    )
                except (ValueError, RuntimeError, OSError, OpenAIError) as exc:
                    notices.append(
                        ("error", f"Could not index {uploaded_file.name}: {exc}")
                    )

            if any(level == "success" for level, _ in notices):
                st.session_state.upload_notices = notices
                get_qa_chain.clear()
                st.rerun()
            for level, message in notices:
                if level == "error":
                    st.error(message)

for level, message in st.session_state.pop("upload_notices", []):
    if level == "success":
        st.success(message)
    else:
        st.error(message)

try:
    qa_chain = get_qa_chain(str(DEFAULT_DB_DIR))
except (FileNotFoundError, ValueError, RuntimeError) as exc:
    st.error(str(exc))
    st.info(
        "Set OPENAI_API_KEY, upload a PDF from the sidebar, or add PDFs under "
        "docs/ and run 02_embed_store.py."
    )
    st.stop()

if "history" not in st.session_state:
    st.session_state.history = []

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("sources"):
            with st.expander("Sources"):
                for source in message["sources"]:
                    st.write(f"- {source}")

query = st.chat_input("Ask a question about your documents...")
if query:
    st.session_state.history.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        with st.spinner("Searching your documents..."):
            result = qa_chain.invoke(query)
        answer = result["result"]
        sources = list(
            dict.fromkeys(
                f"{document.metadata.get('source', 'unknown')} "
                f"(page {int(document.metadata.get('page', 0)) + 1})"
                for document in result["source_documents"]
            )
        )
        st.write(answer)
        with st.expander("Sources"):
            for source in sources:
                st.write(f"- {source}")
    st.session_state.history.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )
