# mcp-license-header-guardian

Deterministic, network-free, read-only MCP guardian that enforces license headers in tracked Python files (Tier 1).

## What this repo is for

Use this repository as the starting point for new guardians.

It provides:
- A frozen V1 contract (`docs/V1_CONTRACT.md`)
- Canonical output examples (`docs/EXAMPLE_OUTPUTS.md`)
- Determinism guardrails (pytest)

## Invariants (do not violate under V1)

- One tool only: `check_license_header`
- Output schema keys are fixed
- Fail-closed on invalid input or internal error
- No timestamps, randomness, environment metadata
- No network calls
- No repo mutation / disk writes

If you need any of the above, declare V2.

## Local development

Install editable:

python3 -m pip install -e .

Run tests:

pytest -q

Print canonical JSON output:

python3 -c "from mcp_license_header_guardian.server import check_license_header, canonical_json; print(canonical_json(check_license_header('.')))"

## MCP server

Run:

mcp-license-header-guardian

