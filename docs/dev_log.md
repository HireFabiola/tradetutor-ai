# Development Log

> Running notes on decisions, issues, and fixes as I build TradeTutor AI. Kept short — a few lines per entry, added right after something notable happens. This feeds directly into the "Challenges & Lessons Learned" section of the final documentation and presentation.

---

## Milestone 0 — Environment & Project Skeleton
- Set up project with `uv init` inside an already-created folder structure (created folders manually first, then initialized uv separately, on purpose — wanted hands-on practice with the init step rather than having it scaffolded for me).
- Confirmed on `uv 0.12.15`, Python 3.14.6 (system default via `uv init`).
- Noted: 3.14 is very new — some ML/AI libraries (ChromaDB, sentence-transformers, Ollama client) may lag on day-one support. Decision: stay on 3.14 for now, with `uv python pin 3.12 && uv sync` as a fast, low-cost fallback if an install breaks later (uv makes this reversible in ~1 command).
- Verified reproducibility: rebuilt `.venv` from scratch with `uv sync` after deleting it — confirmed a clean checkout works.

## Milestone 1 — Ollama Setup
- Installed Ollama via direct download from ollama.com (not Homebrew) — simpler for this project's scope, no need for a package manager just for one install.
- **Issue:** initially pulled `gemma4:26b` (18GB, 26B parameters) instead of the intended `llama3.2:3b`. On 8GB RAM, this caused a full system-wide slowdown — 5+ minutes with no response, and other applications became sluggish too.
- **Diagnosis:** used Activity Monitor's Memory tab to confirm high memory pressure / swap usage — the model was too large for available RAM, forcing the system to swap to disk.
- **Fix:** killed the process (`killall ollama`), waited for memory to recover, then pulled and ran `llama3.2:1b` instead. Response time was immediately much better.
- **Cleanup:** removed the oversized model with `ollama rm gemma4:26b` to free disk space.
- **Decision:** `llama3.2:1b` is the confirmed model for this project going forward — matches the 8GB RAM hardware constraint identified during planning.
- **Lesson:** verify the exact model name before pulling, especially when several similarly-named or auto-suggested options are visible (e.g., cloud-tagged models requiring a subscription vs. free local models). A quick `ollama list` after pulling would have caught the mismatch immediately.

## Milestone 2 — (not yet started)

## Milestone 5 — Input Validation With Pydantic
- Built `ScenarioAnswer` with `Field()` constraints (`numeric_answer > 0`, `reasoning_text` 15-200 chars) and a `model_validator` cross-field check for stop-loss == entry price.
- Caught and fixed an indentation bug where instantiation code was nested inside the class body instead of after it.
- Verified all three paths: valid input passes, cross-field validation error fires, single-field validation error fires.
- Design note: validated whether `entry_price`/`stop_loss_price` belong on `ScenarioAnswer` itself or a separate `Scenario` model, since the MVP has only one fixed scenario — decided to keep it simple for now, revisit if dynamic scenario generation becomes a real post-MVP enhancement.

## Milestone 6 — Local LLM Client Hardening
- Built the first local LLM client in `app/rag/llm_client.py` using the Ollama Python library and a small `llama3.2:1b` default model.
- Added user-facing error handling so connection failures and invalid model responses no longer fail silently.
- Confirmed the function returns friendly guidance instead of crashing when Ollama is unavailable or the model config is wrong.
- Design note: keep model communication logic separate from UI code so the Q&A flow can be tested independently and swapped later without rewriting the app layer.

---

*Add new entries above this line as you progress. Keep the format loose — the goal is to capture the moment, not write polished prose (that happens later, in the final README/presentation).* 
