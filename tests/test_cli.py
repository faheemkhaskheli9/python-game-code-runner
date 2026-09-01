"""Tests for the Phase 1 CLI."""
from __future__ import annotations

from pathlib import Path

from src.main import main

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_run_code_ok(capsys):
    rc = main(["run", "--code", "print(2 ** 10)"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "1024" in captured.out
    assert "--- ok ---" in captured.err


def test_run_rejects_escape(capsys):
    rc = main(["run", "--code", "().__class__.__bases__"])
    assert rc == 3
    assert "rejected" in capsys.readouterr().err


def test_run_reports_runtime_error(capsys):
    rc = main(["run", "--code", "1/0"])
    assert rc == 2
    assert "ZeroDivisionError" in capsys.readouterr().err


def test_run_file(capsys, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    rc = main(["run", "--file", "examples/safe_moves.py"])
    assert rc == 0
    assert "final position" in capsys.readouterr().out


def test_run_missing_file(capsys, tmp_path):
    rc = main(["run", "--file", str(tmp_path / "nope.py")])
    assert rc == 1
    assert "not found" in capsys.readouterr().err
