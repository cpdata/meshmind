"""Administrative CLI helpers for MeshMind."""
from __future__ import annotations

import argparse
import json
import sys
from typing import TextIO

from meshmind.core.config import settings
from meshmind.core.observability import telemetry
from meshmind.db.factory import create_graph_driver
from meshmind.models.registry import PredicateRegistry


def register_admin_subcommands(subparsers: argparse._SubParsersAction) -> None:
    """Attach admin subcommands to the CLI parser."""

    admin_parser = subparsers.add_parser("admin", help="Administrative commands")
    admin_sub = admin_parser.add_subparsers(dest="admin_command")

    predicate_parser = admin_sub.add_parser(
        "predicates", help="Manage the predicate registry"
    )
    predicate_parser.add_argument("--list", action="store_true", help="List predicates")
    predicate_parser.add_argument("--add", metavar="LABEL", help="Add a predicate label")
    predicate_parser.add_argument(
        "--remove", metavar="LABEL", help="Remove a predicate label if present"
    )
    predicate_parser.set_defaults(func=handle_predicates)

    maintenance_parser = admin_sub.add_parser(
        "maintenance", help="Inspect maintenance telemetry"
    )
    maintenance_parser.add_argument(
        "--reset", action="store_true", help="Reset telemetry after printing"
    )
    maintenance_parser.set_defaults(func=handle_maintenance)

    graph_parser = admin_sub.add_parser(
        "graph", help="Validate graph backend connectivity"
    )
    graph_parser.add_argument(
        "--backend",
        default=settings.GRAPH_BACKEND,
        help="Backend to test (memory, sqlite, memgraph, neo4j)",
    )
    graph_parser.set_defaults(func=handle_graph_check)


def handle_predicates(args: argparse.Namespace, stream: TextIO | None = None) -> None:
    """Apply predicate registry operations based on CLI flags."""

    stream = stream or sys.stdout
    updated = False
    if args.add:
        PredicateRegistry.add(args.add)
        print(f"Registered predicate: {args.add}", file=stream)
        updated = True
    if args.remove:
        removed = PredicateRegistry.remove(args.remove)
        status = "Removed" if removed else "Not present"
        print(f"{status} predicate: {args.remove}", file=stream)
        updated = True
    if args.list or not updated:
        labels = sorted(PredicateRegistry.all())
        print(json.dumps({"predicates": labels}, indent=2), file=stream)


def handle_maintenance(args: argparse.Namespace, stream: TextIO | None = None) -> None:
    """Print maintenance telemetry and optionally reset it."""

    stream = stream or sys.stdout
    snapshot = telemetry.snapshot()
    print(json.dumps(snapshot, indent=2, sort_keys=True), file=stream)
    if args.reset:
        telemetry.reset()
        print("Telemetry reset", file=stream)


def handle_graph_check(args: argparse.Namespace, stream: TextIO | None = None) -> int:
    """Try to instantiate the requested graph driver and verify connectivity."""

    stream = stream or sys.stdout
    try:
        driver = create_graph_driver(backend=args.backend)
    except Exception as exc:  # pragma: no cover - best effort logging
        print(f"Failed to create driver: {exc}", file=sys.stderr)
        return 1

    verify = getattr(driver, "verify_connectivity", None)
    if callable(verify):
        try:
            ok = bool(verify())
        except Exception as exc:  # pragma: no cover - depends on backend state
            print(f"Connectivity check failed: {exc}", file=sys.stderr)
            return 2
        else:
            result = "ok" if ok else "unknown"
            print(json.dumps({"backend": args.backend, "status": result}), file=stream)
            return 0

    print(
        json.dumps({"backend": args.backend, "status": "unsupported"}),
        file=stream,
    )
    return 0
