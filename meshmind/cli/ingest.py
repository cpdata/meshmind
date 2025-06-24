"""
CLI ingest command: load files/folders → extract → preprocess → store.
"""
import os
import sys

from meshmind.client import MeshMind
from meshmind.core.types import Memory

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

    # Extraction
    mm = MeshMind()
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