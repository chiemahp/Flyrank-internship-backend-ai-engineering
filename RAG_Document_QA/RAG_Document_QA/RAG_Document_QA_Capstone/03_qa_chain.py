"""Step 3: query the persistent RAG chain from the terminal."""

import argparse
from pathlib import Path

from rag_core import DEFAULT_DB_DIR, build_qa_chain


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "question",
        nargs="?",
        default="What are the main topics covered?",
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_DIR)
    args = parser.parse_args()

    result = build_qa_chain(args.db).invoke(args.question)
    print("Answer:", result["result"])
    print("Sources:")
    for document in result["source_documents"]:
        source = document.metadata.get("source", "unknown")
        page = int(document.metadata.get("page", 0)) + 1
        print(f"- {source}, page {page}")


if __name__ == "__main__":
    main()
