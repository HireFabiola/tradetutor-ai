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

## Milestone 7 — Minimal LLM Workflow (No RAG, No UI)
- Combined system prompt (M6) + error handling (M3) into a looped test script covering 4 on-topic questions + 1 off-topic/advice-fishing question.
- Bug caught: missing comma between adjacent string literals silently concatenated two list items into one garbled question — good reminder that Python auto-joins adjacent string literals with no error.
- Checkpoint met: all on-topic questions answered coherently; off-topic guardrail held (no stock recommended), though response got verbose/repetitive rather than clean — noted on the pinned tone follow-up list.
- Week 2 checkpoint reached: working terminal tutor, no RAG/UI yet.

## Milestone 9 — Environment Fix — Intel Mac / Python 3.14 / ML Stack Conflicts
- Attempting `uv add sentence-transformers` (Milestone 9) failed: torch 2.14 has no wheel for macOS x86_64 (Intel) — only Apple Silicon, Linux, Windows.
- Root cause was two separate gaps stacking: Python 3.14 has no cp314 wheels for any older (Intel-compatible) torch version either.
- Fix, layer by layer:
  1. Pinned Python 3.12 (`uv python pin 3.12`) — required editing `requires-python` in pyproject.toml first, since it was still set to >=3.14 from uv init.
  2. Pinned torch<2.3 — last version with Intel Mac wheels.
  3. Pinned transformers<5 — newer transformers requires torch>=2.4/2.5.
  4. Pinned sentence-transformers<6.0 — v6.0+ requires transformers>=5.0, creating a circular constraint if not pinned together.
  5. Pinned numpy<2 — torch 2.2.2 was compiled against NumPy 1.x; NumPy 2.x caused a "may crash" warning on import (not yet a hard failure, but a real risk of a hard-to-diagnose runtime crash later).
- Verified clean with `uv run python -c "import sentence_transformers; print('ok')"` — no warnings, no errors.
- Lesson: diagnosing "no wheel for this platform" errors often means walking UP the dependency chain (torch -> transformers -> sentence-transformers) one incompatibility at a time, not just downgrading the one package that errored first.

## Milestone 9 — Embeddings in Isolation (extended validation)
- Initial test (2 sentences: stop-loss vs. diversification) confirmed the model captures semantic similarity correctly — query about single-trade protection scored 0.63 against the stop-loss sentence vs. 0.38 against diversification, with zero word overlap between query and match. Deleted as scratch work after this confirmed the core concept.
- Follow-up test (3 chunks: ratio, stop-loss, win rate; 3 queries) surfaced a real limitation: the ratio chunk's generic wording ("the money you're risking... to the money you could earn") won against ALL three queries, including ones that should have favored stop-loss/win rate specifically.
- Diagnosis: generic, broad-vocabulary chunks act as a "default winner" against varied query phrasings on a small (22M param) embedding model — not a bug, a real precision limitation of all-MiniLM-L6-v2 on closely-related concepts.
- Fix attempted: tightened the ratio chunk's wording to be more specific (named the actual calculation and inputs rather than a vague description). Result: 2 of 3 queries now match correctly; win-rate query flipped to the right chunk, comparison query became strongly/correctly matched.
- Remaining failure (protection query still favors ratio over stop-loss): root-caused to vocabulary mismatch — the SHORTENED test sentence for stop-loss uses mechanism language ("executes automatically") rather than purpose language ("protects," "limits your loss"), while the real knowledge_stop_loss.md file already uses the more matching phrasing. Expect this to resolve once Milestone 10 embeds the full real documents instead of single hand-picked test sentences.
- Lesson: chunk wording quality directly affects retrieval quality — this is controllable, not just a model limitation to accept. Combined with top-k retrieval (k=2-3, already planned for Milestone 10) and richer real content (more chunks per concept), expect meaningfully better discrimination than this 3-sentence stress test could show.

---

*Add new entries above this line as you progress. Keep the format loose — the goal is to capture the moment, not write polished prose (that happens later, in the final README/presentation).* 
