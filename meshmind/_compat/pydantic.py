"""Compatibility helpers for environments without :mod:`pydantic`."""
from __future__ import annotations

from dataclasses import MISSING
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Union, get_args, get_origin, get_type_hints
from uuid import UUID

try:  # pragma: no cover - prefer real pydantic when available
    from pydantic import BaseModel as _RealBaseModel  # type: ignore
    from pydantic import Field  # type: ignore
    from pydantic import ValidationError  # type: ignore

    BaseModel = _RealBaseModel
except ImportError:  # pragma: no cover - exercised in constrained sandboxes
    Field = None  # type: ignore

    class ValidationError(Exception):
        """Fallback validation error raised by the compatibility layer."""

    class _FieldInfo:
        __slots__ = ("default", "default_factory")

        def __init__(self, default: Any = MISSING, default_factory: Optional[Any] = None) -> None:
            self.default = default
            self.default_factory = default_factory

        def default_value(self) -> Any:
            if self.default_factory is not None:
                return self.default_factory()
            if self.default is MISSING:
                return None
            return self.default

    def Field(*, default: Any = MISSING, default_factory: Optional[Any] = None) -> _FieldInfo:  # type: ignore[override]
        return _FieldInfo(default=default, default_factory=default_factory)

    _T = TypeVar("_T", bound="BaseModel")

    class BaseModel:
        """Tiny subset of :class:`pydantic.BaseModel` used in the project."""

        def __init__(self, **data: Any) -> None:
            hints = get_type_hints(self.__class__)
            for name, annotation in hints.items():
                value = data.pop(name, MISSING)
                if value is MISSING:
                    default_obj = getattr(self.__class__, name, MISSING)
                    if isinstance(default_obj, _FieldInfo):
                        value = default_obj.default_value()
                    elif default_obj is not MISSING:
                        value = default_obj
                    else:
                        value = None
                value = self._coerce(annotation, value)
                setattr(self, name, value)
            for key, value in data.items():
                setattr(self, key, value)

        @classmethod
        def _coerce(cls, annotation: Any, value: Any) -> Any:
            if value is None:
                return None

            origin = get_origin(annotation)
            if origin is Union:
                for candidate in get_args(annotation):
                    try:
                        return cls._coerce(candidate, value)
                    except Exception:
                        continue
                return value

            if annotation in (str, int, float, bool):
                return annotation(value)

            if annotation is UUID:
                if isinstance(value, UUID):
                    return value
                return UUID(str(value))

            if annotation is datetime:
                if isinstance(value, datetime):
                    return value
                return datetime.fromisoformat(str(value))

            if origin is list:
                inner = get_args(annotation)[0] if get_args(annotation) else Any
                return [cls._coerce(inner, item) for item in value]

            if origin is dict:
                key_type, val_type = (Any, Any)
                args = get_args(annotation)
                if len(args) == 2:
                    key_type, val_type = args
                return {
                    cls._coerce(key_type, k): cls._coerce(val_type, v)
                    for k, v in value.items()
                }

            return value

        def dict(self, *, exclude_none: bool = False) -> Dict[str, Any]:
            data = dict(self.__dict__)
            if exclude_none:
                data = {k: v for k, v in data.items() if v is not None}
            return data

        def model_dump(self, *, exclude_none: bool = False) -> Dict[str, Any]:
            return self.dict(exclude_none=exclude_none)

        def model_copy(self: _T, *, update: Optional[Dict[str, Any]] = None) -> _T:
            payload = self.dict()
            if update:
                payload.update(update)
            return self.__class__(**payload)

        @classmethod
        def schema(cls) -> Dict[str, Any]:
            hints = get_type_hints(cls)
            properties: Dict[str, Any] = {}
            required: List[str] = []
            for name, annotation in hints.items():
                properties[name] = {"type": _schema_type(annotation)}
                required.append(name)
            return {"type": "object", "properties": properties, "required": required}

        def __repr__(self) -> str:  # pragma: no cover - debug helper
            params = ", ".join(f"{k}={v!r}" for k, v in self.dict().items())
            return f"{self.__class__.__name__}({params})"

    def _schema_type(annotation: Any) -> str:
        origin = get_origin(annotation)
        if origin is list:
            return "array"
        if origin is dict:
            return "object"
        if annotation in (int, float):
            return "number"
        if annotation is bool:
            return "boolean"
        return "string"

__all__ = ["BaseModel", "Field", "ValidationError"]
