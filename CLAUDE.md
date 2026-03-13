# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python application that uses the Google Gemini API to build delta objects for insurance claim open items, then applies those deltas to open items state.

## Architecture

- **Gemini integration**: Calls Gemini API to analyze claim data and produce structured delta objects describing changes to open items
- **Delta model**: Represents additions, modifications, and removals to claim open items as a serializable delta object
- **State application**: Applies delta objects to the current open items state to produce updated state

## Build & Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python -m claim_state_delta

# Run all tests
pytest

# Run a single test
pytest tests/test_<module>.py::<TestClass>::<test_name> -v

# Lint
ruff check .

# Format
ruff format .
```

## Key Conventions

- Use `google-cloud-aiplatform` (Vertex AI) SDK for Gemini API access
- Pydantic models for delta and state schemas
- Gemini responses should be parsed into typed delta objects, not used as raw strings
- Delta application must be idempotent — applying the same delta twice yields the same result
