# SPDX-License-Identifier: MIT

from mcp_license_header_guardian.server import check_license_header, canonical_json


def test_check_license_header_is_deterministic() -> None:
    out1 = check_license_header(".")
    out2 = check_license_header(".")
    assert canonical_json(out1) == canonical_json(out2)


def test_output_schema_is_stable() -> None:
    out = check_license_header(".")
    assert set(out.keys()) == {"tool", "repo_path", "ok", "fail_closed", "details", "output"}
