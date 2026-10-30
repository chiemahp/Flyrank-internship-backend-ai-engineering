"""Focused unit tests for the capstone's document handling."""

import hashlib
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from langchain_core.documents import Document

import rag_core


class DocumentChunkingTests(unittest.TestCase):
    def test_split_documents_keeps_page_and_source_metadata(self) -> None:
        document = Document(
            page_content="This sentence is long enough to make several chunks.",
            metadata={"source": "docs/example.pdf", "page": 2},
        )

        chunks = rag_core.split_documents([document], chunk_size=18, chunk_overlap=3)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk.metadata["page"] == 2 for chunk in chunks))
        self.assertTrue(all("example.pdf" in chunk.metadata["source"] for chunk in chunks))

    def test_split_documents_rejects_invalid_chunk_settings(self) -> None:
        with self.assertRaises(ValueError):
            rag_core.split_documents([], chunk_size=10, chunk_overlap=10)


class UploadTests(unittest.TestCase):
    @patch("rag_core.store_chunks")
    @patch("rag_core.PyPDFLoader")
    @patch("rag_core.PdfReader")
    def test_upload_safely_stores_and_indexes_pdf(
        self, reader: Mock, loader: Mock, store_chunks: Mock
    ) -> None:
        reader.return_value.pages = [object()]
        loader.return_value.load.return_value = [
            Document(
                page_content="Uploaded PDF contains useful project information.",
                metadata={"source": "uploaded.pdf", "page": 0},
            )
        ]
        content = b"%PDF-1.4 test bytes"

        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source, chunk_count = rag_core.index_uploaded_pdf(
                r"..\final report.pdf",
                content,
                docs_dir=root / "docs",
                persist_directory=root / "chroma_db",
            )

            stored_file = root / "docs" / "uploads" / (
                f"{hashlib.sha256(content).hexdigest()}-final_report.pdf"
            )
            self.assertTrue(stored_file.is_file())
            self.assertEqual(chunk_count, 1)
            self.assertEqual(Path(source), stored_file)
            store_chunks.assert_called_once()

    def test_upload_rejects_non_pdf_header(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(ValueError, "valid PDF header"):
                rag_core.index_uploaded_pdf(
                    "notes.pdf", b"not a PDF", docs_dir=Path(temporary_directory)
                )

    def test_upload_rejects_wrong_extension(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(ValueError, r"\.pdf extension"):
                rag_core.index_uploaded_pdf(
                    "notes.txt",
                    b"%PDF-1.4 test",
                    docs_dir=Path(temporary_directory),
                )

    def test_upload_rejects_oversized_file_before_writing(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            docs_dir = Path(temporary_directory) / "docs"
            content = b"%PDF-" + b"x" * rag_core.MAX_PDF_UPLOAD_BYTES
            with self.assertRaisesRegex(ValueError, "20 MB"):
                rag_core.index_uploaded_pdf("large.pdf", content, docs_dir=docs_dir)
            self.assertFalse(docs_dir.exists())


class ConfigurationTests(unittest.TestCase):
    def test_vectorstore_requires_api_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY"):
                rag_core.get_vectorstore()


if __name__ == "__main__":
    unittest.main()
