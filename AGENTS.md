# AGENTS.md

This repository is the TradeTutor AI project: an educational tutoring app for foundational trading concepts, risk management, and guided practice. The goal is to teach users with structured lessons, retrieval-augmented Q&A, deterministic calculations, and rubric-based feedback.

## Project intent

- Primary domain: beginner trading education, not live trading or financial advice
- Core learning areas: position sizing, risk/reward, stop-loss logic, diversification, and common trading biases
- Use local, deterministic tooling whenever possible; avoid dependence on external trading data or cloud services in the MVP
- Keep the product educational, safe, and bounded: no stock recommendations, no profit guarantees, and no real-money guidance

## Repository map

- [README.md](README.md): product vision, scope, workflow, and architecture
- [pyproject.toml](pyproject.toml): Python package metadata and project entry points
- [app/](app/): application code and feature modules
  - [app/ui/](app/ui/): Streamlit UI pages/components
  - [app/rag/](app/rag/): retrieval, embeddings, and grounding logic
  - [app/services/](app/services/): business logic and evaluation flows
  - [app/calculations/](app/calculations/): deterministic trading math functions
  - [app/database/](app/database/): SQLite and persistence logic
- [src/tradetutor_ai/](src/tradetutor_ai/): Python package entry points
- [data/lessons/](data/lessons/): lesson content and educational materials
- [data/knowledge/](data/knowledge/): knowledge-base documents for retrieval
- [tests/](tests/): unit and integration tests
- [docs/](docs/): supporting documentation

## Working conventions

- Prefer small, explicit modules over large, monolithic files
- Keep business logic separate from UI concerns
- Treat calculations as deterministic and testable; avoid using LLMs for arithmetic or validation
- Keep all trading guidance framed as educational scenarios and fictional examples, not recommendations
- Follow Python package conventions: type hints, clear function names, and readable docstrings when useful

## Development workflow

### Environment and commands

- Use `uv` for package management and environment setup
- Typical commands:
  - `uv sync`
  - `uv run pytest`
  - `uv run streamlit run app/ui/home.py`

### Testing expectations

- Add tests for deterministic calculation logic and validation rules
- Prefer real behavior over mocks for core logic and workflows
- Keep tests narrow and readable; focus on domain correctness

## Important guardrails

- Do not implement live market data, live brokerage, or automated trading features in this MVP
- Do not provide personalized financial or investment advice in generated responses
- Do not claim returns, guarantees, or risk-free outcomes
- Keep educational content consistent with the risk-management scope described in [README.md](README.md)

## When making changes

- Check [README.md](README.md) before broad design changes so the repo stays aligned with the MVP scope
- Keep feature work scoped to education, reasoning, and risk-management fundamentals
- If a new module is introduced, add it in the appropriate app subpackage rather than creating unrelated roots
- Prefer incremental, testable additions over speculative architecture changes

## Summary

This project is intentionally a small, educational, local-first MVP. Code and documentation should stay aligned with that scope, emphasize safe learning, and keep core calculations deterministic and auditable.
