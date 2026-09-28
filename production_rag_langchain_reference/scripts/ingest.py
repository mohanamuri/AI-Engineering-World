#!/usr/bin/env python
"""
Ingestion pipeline: Load, chunk, embed, and index documents.

Example script to ingest documents into the RAG system.

Usage:
    python scripts/ingest.py --directory ./data --tenant demo-tenant
"""

import argparse
from pathlib import Path
from app.ingestion.loaders import load_documents_from_directory
from app.ingestion.chunker import split_documents
from app.retrieval.vectorstore import index_documents
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into RAG system")
    parser.add_argument(
        "--directory",
        default="./data",
        help="Directory containing documents",
    )
    parser.add_argument(
        "--tenant",
        default="demo-tenant",
        help="Tenant ID for multi-tenancy",
    )
    args = parser.parse_args()

    # Validate directory exists
    if not Path(args.directory).exists():
        logger.error("directory_not_found", directory=args.directory)
        return 1

    # Step 1: Load documents
    logger.info("loading_documents", directory=args.directory)
    documents = load_documents_from_directory(args.directory)

    if not documents:
        logger.warning("no_documents_found", directory=args.directory)
        return 0

    logger.info("documents_loaded", count=len(documents))

    # Step 2: Chunk documents
    logger.info("chunking_documents")
    chunks = split_documents(documents)
    logger.info("documents_chunked", count=len(chunks))

    # Step 3: Index in vector store
    logger.info("indexing_documents", tenant_id=args.tenant)
    index_documents(chunks, tenant_id=args.tenant)
    logger.info("documents_indexed", count=len(chunks), tenant_id=args.tenant)

    print(f"✓ Successfully indexed {len(chunks)} chunks for tenant '{args.tenant}'")
    return 0


if __name__ == "__main__":
    exit(main())
