"""Restricted in-process executor for user-submitted Python.

Phase 1 scope: run untrusted code with a curated builtin set, an import
allow-list, and an AST pre-pass that rejects the usual introspection-based
escapes (``__class__`` / ``__subclasses__`` / ``__globals__`` / ``__import__``
...). stdout is captured and any exception is returned as structured data
rather than propagated.

NOT covered here (Phase 1 issue #2): hard CPU-time and memory limits. This
executor cannot stop an infinite loop -- that requires the subprocess +
``resource`` rlimit wrapper added in issue #2. Treat this layer as
defence-in-depth, not a complete jail.
"""
from __future__ import annotations

import ast
import builtins as _py_builtins
import io
from contextlib import redirect_stdout
from dataclasses import dataclass, field

DEFAULT_ALLOWED_IMPORTS = frozenset({"math", "random", "statistics", "itertools", "functools"})

# Names that must never appear in submitted code (dangerous callables / hooks).
_FORBIDDEN_NAMES = frozenset(
    {
        "eval", "exec", "compile", "open", "input", "__import__",
        "globals", "locals", "vars", "getattr", "setattr", "delattr",
        "breakpoint", "help", "memoryview",
    }
)
# Attribute names that expose the object graph / interpreter internals.
_FORBIDDEN_ATTRS = frozenset(
    {
        "__class__", "__bases__", "__mro__", "__subclasses__", "__globals__",
        "__code__", "__closure__", "__dict__", "__builtins__", "__import__",
        "__getattribute__", "__subclasshook__", "__reduce__", "__reduce_ex__",
        "__base__", "__loader__", "__spec__",
    }
)

_SAFE_BUILTIN_NAMES = (
    "abs all any ascii bin bool bytearray bytes callable chr complex dict divmod "
    "enumerate filter float format frozenset hash hex int isinstance issubclass "
    "iter len list map max min next object oct ord pow print range repr reversed "
    "round set slice sorted str sum tuple type zip True False None "
    "ArithmeticError AssertionError AttributeError Exception IndexError KeyError "
    "LookupError NameError NotImplementedError OverflowError RuntimeError "
    "StopIteration TypeError ValueError ZeroDivisionError"
).split()


class SandboxRejected(Exception):
    """Raised when submitted code is rejected before execution."""


@dataclass(frozen=True)
class SandboxConfig:
    allowed_imports: frozenset[str] = DEFAULT_ALLOWED_IMPORTS
    max_output_chars: int = 10_000


@dataclass
class SandboxResult:
    ok: bool
    stdout: str = ""
    error: str | None = None
    error_type: str | None = None
    rejected_reason: str | None = None
    variables: dict = field(default_factory=dict)


class _Guard(ast.NodeVisitor):
    def __init__(self, allowed_imports: frozenset[str]) -> None:
        self.allowed_imports = allowed_imports

    def _reject(self, node: ast.AST, msg: str) -> None:
        raise SandboxRejected(f"line {getattr(node, 'lineno', '?')}: {msg}")

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root not in self.allowed_imports:
                self._reject(node, f"import of {alias.name!r} is not allowed")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        root = (node.module or "").split(".")[0]
        if root not in self.allowed_imports:
            self._reject(node, f"import from {node.module!r} is not allowed")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in _FORBIDDEN_ATTRS or (
            node.attr.startswith("__") and node.attr.endswith("__")
        ):
            self._reject(node, f"access to attribute {node.attr!r} is not allowed")
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in _FORBIDDEN_NAMES:
            self._reject(node, f"use of {node.id!r} is not allowed")
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global) -> None:
        self._reject(node, "'global' is not allowed")

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        self._reject(node, "'nonlocal' is not allowed")


def _safe_builtins(allowed_imports: frozenset[str]) -> dict:
    safe = {name: getattr(_py_builtins, name) for name in _SAFE_BUILTIN_NAMES}

    def _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        root = name.split(".")[0]
        if level != 0 or root not in allowed_imports:
            raise ImportError(f"import of {name!r} is not allowed in the sandbox")
        return __import__(name, globals, locals, fromlist, level)

    safe["__import__"] = _guarded_import
    return safe


def _extract_vars(namespace: dict) -> dict:
    simple = (int, float, str, bool, list, tuple, dict, set, type(None))
    return {
        k: v
        for k, v in namespace.items()
        if not k.startswith("_") and isinstance(v, simple)
    }


def run(code: str, config: SandboxConfig | None = None) -> SandboxResult:
    cfg = config or SandboxConfig()

    try:
        tree = ast.parse(code, filename="<submission>", mode="exec")
    except SyntaxError as exc:
        return SandboxResult(
            ok=False, error=f"{exc.msg} (line {exc.lineno})", error_type="SyntaxError"
        )

    try:
        _Guard(cfg.allowed_imports).visit(tree)
    except SandboxRejected as exc:
        return SandboxResult(ok=False, rejected_reason=str(exc), error_type="SandboxRejected")

    namespace: dict = {"__builtins__": _safe_builtins(cfg.allowed_imports)}
    buffer = io.StringIO()
    compiled = compile(tree, filename="<submission>", mode="exec")

    try:
        with redirect_stdout(buffer):
            exec(compiled, namespace)  # noqa: S102 - restricted namespace, AST-vetted
    except BaseException as exc:  # noqa: BLE001 - surface everything as data
        out = buffer.getvalue()[: cfg.max_output_chars]
        return SandboxResult(
            ok=False,
            stdout=out,
            error=str(exc) or exc.__class__.__name__,
            error_type=exc.__class__.__name__,
            variables=_extract_vars(namespace),
        )

    out = buffer.getvalue()
    truncated = len(out) > cfg.max_output_chars
    return SandboxResult(
        ok=True,
        stdout=out[: cfg.max_output_chars] + ("\n...[truncated]" if truncated else ""),
        variables=_extract_vars(namespace),
    )
