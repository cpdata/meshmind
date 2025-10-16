#!/usr/bin/env python3
"""
Command-line interface for MeshMind.
"""
import argparse
import sys

from meshmind.api.grpc_server import serve_forever
from meshmind.api.memory_manager import MemoryManager
from meshmind.api.service import MemoryService
from meshmind.cli.admin import register_admin_subcommands
from meshmind.cli.ingest import ingest_command
from meshmind.core.bootstrap import bootstrap_encoders, bootstrap_entities
from meshmind.core.config import settings
from meshmind.db.factory import create_graph_driver
from meshmind.llm_client import build_default_llm_client


def serve_grpc_command(args: argparse.Namespace) -> None:
    """Start the MeshMind gRPC server using the configured settings."""

    backend = args.backend or settings.GRAPH_BACKEND
    driver = create_graph_driver(backend=backend)
    manager = MemoryManager(driver)
    service = MemoryService(
        manager,
        llm_client_factory=lambda: build_default_llm_client(settings),
    )

    try:
        serve_forever(
            service,
            host=args.host,
            port=args.port,
            shutdown_grace=args.shutdown_grace,
        )
    finally:
        closer = getattr(driver, "close", None)
        if callable(closer):
            closer()


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
        "--embedding-endpoint",
        default=None,
        help="Override the endpoint URL for embedding requests",
    )
    ingest_parser.add_argument(
        "-i", "--instructions", default="Extract key facts as Memory objects.",
        help="Instructions for the extraction LLM prompt"
    )
    ingest_parser.add_argument(
        "--llm-base-url",
        default=None,
        help="Override the base URL for the LLM provider",
    )
    ingest_parser.add_argument(
        "--llm-api-key",
        default=None,
        help="Override the API key used for LLM calls",
    )
    ingest_parser.add_argument(
        "--extraction-model",
        default=None,
        help="Model identifier for the extraction step",
    )
    ingest_parser.add_argument(
        "--extraction-endpoint",
        default=None,
        help="Endpoint URL for extraction requests",
    )
    ingest_parser.add_argument(
        "--rerank-model",
        default=None,
        help="Model identifier for reranking",
    )
    ingest_parser.add_argument(
        "--rerank-endpoint",
        default=None,
        help="Endpoint URL for reranking requests",
    )
    ingest_parser.add_argument(
        "paths", nargs="+", help="Paths to files or directories to ingest"
    )
    ingest_parser.set_defaults(func=ingest_command)

    register_admin_subcommands(subparsers)

    serve_grpc_parser = subparsers.add_parser(
        "serve-grpc", help="Run the MeshMind gRPC service"
    )
    serve_grpc_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Interface to bind the gRPC server (default: 0.0.0.0)",
    )
    serve_grpc_parser.add_argument(
        "--port",
        type=int,
        default=50051,
        help="Port to bind the gRPC server (default: 50051)",
    )
    serve_grpc_parser.add_argument(
        "--backend",
        default=None,
        help="Graph backend to use (overrides GRAPH_BACKEND when provided)",
    )
    serve_grpc_parser.add_argument(
        "--shutdown-grace",
        type=float,
        default=5.0,
        help="Seconds to wait for in-flight RPCs during shutdown",
    )
    serve_grpc_parser.set_defaults(func=serve_grpc_command)

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

    func = getattr(args, "func", None)
    if callable(func):
        result = func(args)
        return result

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
