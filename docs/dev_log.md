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

---

*Add new entries above this line as you progress. Keep the format loose — the goal is to capture the moment, not write polished prose (that happens later, in the final README/presentation).* 
