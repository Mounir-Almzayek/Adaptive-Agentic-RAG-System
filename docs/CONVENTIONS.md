# Conventions — Adaptive Agentic RAG System

## Code and Repo Conventions

### Language and Locale

- **Code, comments, docstrings, and docs:** English.
- **User-facing copy (UI labels, errors):** English by default; Arabic only where product explicitly requires it.

### Python

- **Version:** 3.11+.
- **Style:** PEP 8; line length 100–120 acceptable. Use type hints for public functions and method signatures.
- **Imports:** Absolute imports from project root (e.g. `from adaptive_rag.core.model_factory import create_llm`). Group: stdlib → third-party → local; alphabetical within groups.
- **Naming:**
  - Modules/files: `snake_case`.
  - Classes: `PascalCase`.
  - Functions/methods/variables: `snake_case`.
  - Constants: `UPPER_SNAKE_CASE`.

### Project Layout

- Package name: `adaptive_rag` (top-level folder). All app code lives under it; `docs/` can be at repo root.
- No business logic in `app/streamlit_app.py`; only UI and calls to services.
- Config and secrets: from environment; never hardcoded. Use `config/settings.py` as single source.

### Documentation

- Each phase has one MD file under `docs/phases/` with: objectives, file-by-file tasks, acceptance criteria.
- Architecture and tech stack: `docs/ARCHITECTURE.md`, `docs/TECH_STACK.md`. Keep them updated when design changes.

### Git / Repo

- `.env` in `.gitignore`; commit `.env.example` only.
- Prefer meaningful commit messages; reference phase or ticket if applicable.

### Testing (When Added)

- Place tests in `tests/` at repo root or inside `adaptive_rag/`; mirror package structure. Use pytest. Mark integration tests if needed; keep unit tests fast.

---

## Next Step

See [GLOSSARY.md](GLOSSARY.md) for terms and abbreviations.
