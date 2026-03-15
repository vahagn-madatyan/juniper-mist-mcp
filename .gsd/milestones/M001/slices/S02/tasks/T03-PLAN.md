---
estimated_steps: 6
estimated_files: 2
---

# T03: Add verification tests

**Slice:** S02 — Read tools (tier1)
**Milestone:** M001

## Description

Add comprehensive verification tests for all tier1 tools. Tests verify tool registration, parameter handling, and response formatting without requiring live API credentials.

## Steps

1. Add test for verifying all 5 tier1 tools are registered in MCP server
2. Add mock-based tests for each tool to verify:
   - Tool accepts correct parameters
   - Tool validates org parameter
   - Tool formats response correctly
3. Create end-to-end verification script `scripts/verify_s02.sh`
4. Run all tests to verify slice is complete

## Must-Haves

- [ ] Test verifying 5 tier1 tools are registered
- [ ] Test verifying each tool validates org parameter
- [ ] End-to-end verification script exits 0
- [ ] All pytest tests pass

## Verification

- `pytest tests/test_server.py -v` — all tests pass
- `bash scripts/verify_s02.sh` — exits 0 with success message

## Observability Impact

- None (tests are verification only, no runtime signals added)

## Inputs

- `tests/test_server.py` — existing test patterns
- `tests/test_config.py` — existing test patterns

## Expected Output

- `tests/test_server.py` — new test functions for tier1 tools
- `scripts/verify_s02.sh` — verification script
