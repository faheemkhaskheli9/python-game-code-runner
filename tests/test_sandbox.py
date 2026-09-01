"""Tests for the restricted in-process executor."""
from __future__ import annotations

from pathlib import Path

import pytest

from src.sandbox import SandboxConfig, run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_safe_code_runs_and_captures_stdout():
    res = run("total = sum(range(5))\nprint('total', total)")
    assert res.ok
    assert res.stdout.strip() == "total 10"
    assert res.variables["total"] == 10
    assert res.error is None


def test_allowed_import_math():
    res = run("import math\nprint(math.factorial(5))")
    assert res.ok
    assert res.stdout.strip() == "120"


def test_runtime_exception_returned_as_data_not_raised():
    res = run("print('before')\nx = 1 / 0\nprint('after')")
    assert not res.ok
    assert res.error_type == "ZeroDivisionError"
    assert "before" in res.stdout
    assert "after" not in res.stdout


def test_syntax_error_is_clean():
    res = run("def broken(:\n    pass")
    assert not res.ok
    assert res.error_type == "SyntaxError"


@pytest.mark.parametrize(
    "code",
    [
        "import os",
        "from subprocess import run as r",
        "open('/etc/passwd')",
        "eval('1+1')",
        "exec('x=1')",
        "__import__('os')",
        "().__class__.__bases__[0].__subclasses__()",
        "print(print.__globals__)",
        "getattr(1, 'real')",
        "global y",
    ],
)
def test_dangerous_code_is_rejected_before_execution(code):
    res = run(code)
    assert not res.ok
    assert res.rejected_reason is not None or res.error_type in {
        "SandboxRejected",
        "ImportError",
        "NameError",
    }


def test_blocked_escape_example_file_is_rejected():
    code = (REPO_ROOT / "examples" / "blocked_escape.py").read_text(encoding="utf-8")
    res = run(code)
    assert not res.ok
    assert res.rejected_reason is not None
    assert "attribute" in res.rejected_reason
    assert "__bases__" in res.rejected_reason or "__class__" in res.rejected_reason


def test_safe_example_file_runs():
    code = (REPO_ROOT / "examples" / "safe_moves.py").read_text(encoding="utf-8")
    res = run(code)
    assert res.ok, res.error
    assert "distance from origin" in res.stdout


def test_output_is_truncated():
    res = run("print('x' * 50)", SandboxConfig(max_output_chars=10))
    assert res.ok
    assert "[truncated]" in res.stdout
    assert len(res.stdout) < 40


def test_import_hook_blocks_disallowed_module_at_runtime():
    # importlib is not in the AST name-list check, but the guarded __import__
    # still refuses it.
    res = run("import importlib")
    assert not res.ok
