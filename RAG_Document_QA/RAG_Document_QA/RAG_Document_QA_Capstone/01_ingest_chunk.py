"""Step 1: load PDFs from docs/ and split them into overlapping chunks."""

import argparse
from pathlib import Path

from rag_core import DEFAULT_DOCS_DIR, load_and_split_documents


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs", type=Path, default=DEFAULT_DOCS_DIR)
    args = parser.parse_args()

    chunks = load_and_split_documents(args.docs)
    print(f"Loaded and split documents into {len(chunks)} chunks")
    print(f"Sample: {chunks[0].page_content[:200]}")


if __name__ == "__main__":
    main()
