"""Step 2: ingest PDFs, embed chunks, and upsert them into persistent Chroma."""

import argparse
from pathlib import Path

from rag_core import DEFAULT_DB_DIR, DEFAULT_DOCS_DIR, load_and_split_documents, store_chunks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs", type=Path, default=DEFAULT_DOCS_DIR)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_DIR)
    args = parser.parse_args()

    chunks = load_and_split_documents(args.docs)
    vectorstore = store_chunks(chunks, args.db)
    print(f"Upserted {len(chunks)} chunks; collection now has {vectorstore._collection.count()}")


if __name__ == "__main__":
    main()
