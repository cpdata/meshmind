#!/usr/bin/env python3
"""
Command-line interface for MeshMind.
"""
import argparse
import sys

from meshmind.cli.ingest import ingest_command
from meshmind.core.bootstrap import bootstrap_encoders, bootstrap_entities
from meshmind.core.config import settings


def main():
    parser = argparse.ArgumentParser(
        prog="meshmind", description="MeshMind CLI"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Ingest command
    ingest_parser = subparsers.add_parser(
        "ingest", help="Ingest content files or directories"
    )
    ingest_parser.add_argument(
        "-n", "--namespace", required=True, help="Namespace for new memories"
    )
    ingest_parser.add_argument(
        "-e", "--embedding-model", default=None,
        help="Embedding model to use (default from settings)"
    )
    ingest_parser.add_argument(
        "-i", "--instructions", default="Extract key facts as Memory objects.",
        help="Instructions for the extraction LLM prompt"
    )
    ingest_parser.add_argument(
        "paths", nargs="+", help="Paths to files or directories to ingest"
    )

    args = parser.parse_args()

    # Ensure default encoders and entities are registered before executing commands
    bootstrap_entities()
    bootstrap_encoders()

    missing = settings.missing()
    if missing:
        for group, keys in missing.items():
            print(
                f"Warning: missing configuration for {group}: {', '.join(keys)}",
                file=sys.stderr,
            )

    if args.command == "ingest":
        ingest_command(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
