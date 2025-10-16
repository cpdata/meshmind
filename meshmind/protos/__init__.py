"""Generated gRPC protocol buffers for MeshMind."""

from importlib import resources

__all__ = ["data_path"]


def data_path(*parts: str) -> str:
    """Return an absolute path to packaged proto/data files."""

    with resources.as_file(resources.files(__package__).joinpath(*parts)) as path:
        return str(path)
