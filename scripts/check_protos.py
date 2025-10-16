"""Verify generated protobuf bindings are up to date."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile

PROTO_DIR = Path(__file__).resolve().parent.parent / "meshmind" / "protos"
PROTO_FILE = PROTO_DIR / "memory_service.proto"
GENERATED = ["memory_service_pb2.py", "memory_service_pb2_grpc.py"]


def main() -> None:
    if not PROTO_FILE.exists():
        raise SystemExit(f"Missing proto definition: {PROTO_FILE}")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        command = [
            sys.executable,
            "-m",
            "grpc_tools.protoc",
            f"--proto_path={PROTO_DIR}",
            f"--python_out={tmp_path}",
            f"--grpc_python_out={tmp_path}",
            str(PROTO_FILE),
        ]
        subprocess.check_call(command)
        drift = []
        for filename in GENERATED:
            target = PROTO_DIR / filename
            candidate = tmp_path / filename
            if not target.exists():
                drift.append(filename)
                continue
            if target.read_text(encoding="utf-8") != candidate.read_text(encoding="utf-8"):
                drift.append(filename)
        if drift:
            joined = ", ".join(drift)
            raise SystemExit(
                "Outdated protobuf bindings detected: "
                f"{joined}. Run `python scripts/generate_protos.py` and commit the results."
            )
    print("Protobuf bindings are up to date.", file=sys.stderr)


if __name__ == "__main__":
    main()
