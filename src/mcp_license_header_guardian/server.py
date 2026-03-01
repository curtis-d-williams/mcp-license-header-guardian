# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import os
import subprocess
from typing import Any, Dict, List

from fastmcp import FastMCP


mcp = FastMCP("mcp-license-header-guardian")


def canonical_json(obj: Any) -> str:
    """
    Deterministic JSON serialization helper for callers and tests.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _repo_path_is_valid(repo_path: str) -> bool:
    return isinstance(repo_path, str) and len(repo_path.strip()) > 0


def _fail_closed(details: str, repo_path: str, output: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "tool": "check_license_header",
        "repo_path": repo_path,
        "ok": False,
        "fail_closed": True,
        "details": details,
        "output": output,
    }


def _run_git_ls_files(repo_path: str) -> List[str]:
    try:
        proc = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_path,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except Exception as e:
        raise RuntimeError(f"git_exec_error:{type(e).__name__}") from e

    if proc.returncode != 0:
        raise RuntimeError("git_ls_files_failed")

    files = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    files.sort()
    return files


def _first_n_lines_contains_required_marker(path: str, n: int = 5) -> bool:
    try:
        with open(path, "rb") as f:
            raw = f.read(8192)
    except Exception:
        return False

    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()[:n]
    for line in lines:
        if "Copyright" in line or "SPDX-License-Identifier" in line:
            return True
    return False


@mcp.tool()
def check_license_header(repo_path: str) -> Dict[str, Any]:
    """
    Deterministic, network-free, read-only Tier 1 guardian.

    Checks .py files tracked by git to ensure the first 5 lines contain
    "Copyright" OR "SPDX-License-Identifier".
    """
    if not _repo_path_is_valid(repo_path):
        return _fail_closed("fail-closed: invalid_repo_path", repo_path)

    abs_repo = os.path.abspath(repo_path)

    try:
        tracked = _run_git_ls_files(abs_repo)
    except RuntimeError as e:
        return _fail_closed(f"fail-closed: {str(e)}", repo_path, output={"files_missing_header": [], "notes": ["git ls-files failed"]})

    py_files = [p for p in tracked if p.endswith(".py")]
    missing: List[str] = []

    for rel in py_files:
        full = os.path.join(abs_repo, rel)
        if not _first_n_lines_contains_required_marker(full, n=5):
            missing.append(rel)

    missing.sort()

    output = {
        "files_missing_header": missing,
        "notes": [
            "scope: tracked .py files only",
            "rule: first 5 lines contain Copyright OR SPDX-License-Identifier",
            "listing: git ls-files",
        ],
    }

    if missing:
        return {
            "tool": "check_license_header",
            "repo_path": repo_path,
            "ok": False,
            "fail_closed": True,
            "details": "fail-closed: missing_license_header",
            "output": output,
        }

    return {
        "tool": "check_license_header",
        "repo_path": repo_path,
        "ok": True,
        "fail_closed": False,
        "details": "ok",
        "output": output,
    }


def main() -> None:
    mcp.run()
