"""
CLI ingest command: load files/folders → extract → preprocess → store.
"""
from __future__ import annotations
import os
import sys

from meshmind.client import MeshMind
from meshmind.core.config import settings
from meshmind.core.types import Memory
from meshmind.llm_client import build_llm_config_from_settings

def ingest_command(args):
    """
    Ingest command implementation.

    :param args: Parsed command-line arguments
    """
    # Collect text contents from provided paths
    contents = []
    for path in args.paths:
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, 'r', encoding='utf-8') as f:
                            contents.append(f.read())
                    except Exception as e:
                        print(f"Warning: could not read {fpath}: {e}", file=sys.stderr)
        else:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    contents.append(f.read())
            except Exception as e:
                print(f"Warning: could not read {path}: {e}", file=sys.stderr)
    if not contents:
        print("No content found to ingest.", file=sys.stderr)
        sys.exit(1)

    models_override: dict[str, str] = {}
    base_urls_override: dict[str, str] = {}
    if getattr(args, "embedding_model", None):
        models_override["embedding"] = args.embedding_model
    if getattr(args, "extraction_model", None):
        models_override["extraction"] = args.extraction_model
    if getattr(args, "rerank_model", None):
        models_override["rerank"] = args.rerank_model

    if getattr(args, "llm_base_url", None):
        base_urls_override["default"] = args.llm_base_url
    if getattr(args, "embedding_endpoint", None):
        base_urls_override["embedding"] = args.embedding_endpoint
    if getattr(args, "extraction_endpoint", None):
        base_urls_override["extraction"] = args.extraction_endpoint
    if getattr(args, "rerank_endpoint", None):
        base_urls_override["rerank"] = args.rerank_endpoint

    overrides_models = models_override or None
    overrides_base = base_urls_override or None
    api_key_override = getattr(args, "llm_api_key", None) or None
    llm_config = build_llm_config_from_settings(settings).override(
        models=overrides_models,
        base_urls=overrides_base,
        api_key=api_key_override,
    )

    # Extraction
    mm = MeshMind(llm_config=llm_config)
    memories = mm.extract_memories(
        instructions=args.instructions,
        namespace=args.namespace,
        entity_types=[Memory],
        content=contents,
    )

    # Preprocess
    memories = mm.deduplicate(memories)
    memories = mm.score_importance(memories)
    memories = mm.compress(memories)

    # Store
    mm.store_memories(memories)
    print(f"Ingested {len(memories)} memories into namespace '{args.namespace}'.")