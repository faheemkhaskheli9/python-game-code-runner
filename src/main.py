"""CLI for the sandboxed Python executor.

    python -m src.main run --file examples/safe_moves.py
    python -m src.main run --code "print(sum(range(10)))"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.sandbox import SandboxConfig, run


def _cmd_run(args: argparse.Namespace) -> int:
    if args.code is not None:
        source = args.code
    else:
        path = Path(args.file)
        if not path.is_file():
            print(f"error: file not found: {path}", file=sys.stderr)
            return 1
        source = path.read_text(encoding="utf-8")

    result = run(source, SandboxConfig(max_output_chars=args.max_output))

    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")

    if result.ok:
        print("--- ok ---", file=sys.stderr)
        return 0
    if result.rejected_reason:
        print(f"--- rejected: {result.rejected_reason} ---", file=sys.stderr)
        return 3
    print(f"--- error [{result.error_type}]: {result.error} ---", file=sys.stderr)
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="game-code-runner", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("run", help="Execute a submission in the sandbox.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--file")
    g.add_argument("--code")
    p.add_argument("--max-output", type=int, default=10_000, dest="max_output")
    p.set_defaults(func=_cmd_run)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
