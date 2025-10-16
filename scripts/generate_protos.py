"""Regenerate MeshMind protobuf bindings in-place."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

PROTO_DIR = Path(__file__).resolve().parent.parent / "meshmind" / "protos"
PROTO_FILE = PROTO_DIR / "memory_service.proto"


def main() -> None:
    if not PROTO_FILE.exists():
        raise SystemExit(f"Missing proto definition: {PROTO_FILE}")
    command = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"--proto_path={PROTO_DIR}",
        f"--python_out={PROTO_DIR}",
        f"--grpc_python_out={PROTO_DIR}",
        str(PROTO_FILE),
    ]
    subprocess.check_call(command)

    grpc_file = PROTO_DIR / "memory_service_pb2_grpc.py"
    if grpc_file.exists():
        text = grpc_file.read_text(encoding="utf-8")
        text = text.replace(
            "import memory_service_pb2 as",
            "from . import memory_service_pb2 as",
        )
        grpc_file.write_text(text, encoding="utf-8")

    print("Regenerated protobuf bindings", file=sys.stderr)


if __name__ == "__main__":
    main()
