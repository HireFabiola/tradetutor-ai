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

## Milestone 10 — ChromaDB Storage & Retrieval ✅ COMPLETE
- Built and verified `load_chunks()` to read Markdown, split content into paragraph-level chunks on blank lines, remove empty chunks, and filter heading-only lines so markdown headers are not embedded as low-value entries.
- Built and verified `load_all_chunks()` to auto-discover `.md` files in `data/lessons/` and `data/knowledge/`, preserve each chunk's source filename as metadata, and load 18 total chunks across 3 files.
- Loaded the `all-MiniLM-L6-v2` model and confirmed that each chunk is represented as a 384-dimensional vector; embedding matrix shape is `(18, 384)`.
- Manually tested semantic retrieval before ChromaDB: embedded a query, computed cosine similarity against all 18 chunk embeddings, ranked by similarity, and verified that relevant stop-loss and risk/reward chunks were returned even without exact wording matches.
- Confirmed that similarity scores are comparative and should not be treated as a universal relevance threshold.
- Installed ChromaDB and resolved the Intel macOS dependency issue by pinning `onnxruntime==1.22.1` after the default resolver selected a version without a compatible `x86_64` wheel.
- Created persistent ChromaDB storage in `data/chroma_db`, opened the `tradetutor_knowledge` collection, and stored all 18 chunks with unique IDs, text, embeddings, and source metadata.
- Verified persistence by restarting the Python process, reopening the same collection, and confirming `collection.count()` still returned 18 records even after the in-memory embedding array was no longer present.
- Built `app/rag/retriever.py` to load the same embedding model, connect to the persisted collection, embed a learner question, and retrieve the top 3 matching chunks by vector similarity.
- Validated retrieval against the manual cosine-similarity baseline: the same three chunks were returned in the same order for both the risk/reward and stop-loss questions, confirming the persisted ChromaDB retrieval layer was working as expected.
- Tested a new question, "Why is win rate important when evaluating a trading strategy?", and confirmed ChromaDB retrieved relevant win-rate educational content, showing retrieval works beyond the original validation examples.
- Reinforced the key concept: embeddings represent semantic meaning numerically, but the query and stored documents must use the same model and occupy the same embedding space for meaningful search results.
- Final milestone takeaway: TradeTutor now has a working persistent semantic retrieval layer that can take educational content from Markdown files, embed it, store it in ChromaDB, and retrieve the relevant educational chunks for learner questions.
- Next milestone: Milestone 11 — connect retrieval to the LLM via RAG, passing the retrieved context into the Ollama prompt so the model can answer with grounded educational guidance.

## Milestone 11 — Connect Retrieval to the LLM (RAG)
- Problem, discovered through real testing and not assumption: the first working version passed `retriever.py` output directly to the LLM with no relevance gate. Five real test questions (2 covered, 1 off-topic but trading-adjacent, 1 borderline, 1 investment-advice-seeking) showed the local model would confidently hallucinate plausible-sounding details when the retrieved context was weak — for example, inventing a "15:1 to 20:1 = very good" ratio guideline that appears nowhere in the content, and fabricating margin-call/leverage explanations for position sizing despite no source material on that topic.
- Iteration 1 — prompt-only fix failed: tightened the system prompt to forbid unsupported numerical ranges/performance claims, reinstated the strict context-only rule, and re-added the Milestone 6 "BEFORE ANSWERING" off-topic check. It did not solve the underlying issue. The model still hallucinated on position sizing and also incorrectly refused legitimate, well-covered questions that had strong retrieval matches. This confirmed that asking a 1B local model to judge whether context is sufficient via prompt instructions alone is unreliable.
- Iteration 2 — deterministic code-level fix worked: moved the relevance decision out of the prompt and into code. Added `is_context_relevant(distances)` to check whether the best ChromaDB distance is below a fixed threshold (1.0, chosen empirically from real test data: known-good matches were mostly in the 0.3-0.8 range, known-bad ones in 1.1-1.5). If the best match exceeds the threshold, the LLM is never called and a canned fallback message is returned instead. This closes the hallucination path entirely, because the model cannot invent an answer when it never sees the question.
- Re-ran all five tests after the fix: stop-loss answered correctly and grounded; position sizing was correctly short-circuited with no hallucination; risk/reward ratio answered correctly; the "good ratio" question answered without fabricating numbers though the reasoning remained a bit muddled; stock-advice question was correctly blocked without giving advice.
- Fallback-message iteration: the first attempt created separate messages for "topic not covered yet" and "asking for investment advice" and realized that would require an extra keyword-routing layer. Simplified to a single blended fallback message that names the lesson's scope, says the question may be covered in a later module, and explicitly states the investment-advice boundary. One code path instead of two — simpler and more robust for the MVP.
- Lesson: when a small local model's judgment is the single point of failure for something safety-critical or accuracy-critical, do not keep re-prompting around it. Move the decision into deterministic code wherever a reliable signal exists. Prompt engineering can improve tone and framing (Milestone 6), but it did not reliably fix a judgment call with real consequences here. Three iterations, each validated with real test output, led to the final fix.

## Milestone 12 — Practice Scenario & Rubric Evaluation
- Wrote "The Meridian Trade" — a fictional company (Meridian Robotics), embedded-style prices (entry $60, stop-loss $54, target $78, woven into narrative prose rather than listed as a bare table) so the user has to extract the numbers themselves. Clean round numbers by design: risk=$6, reward=$18, ratio=3.0 exactly, verified against `risk_reward_ratio(60, 54, 78) -> 3.0`.
- Bug caught before writing the rubric: the original scenario task only asked the user to "calculate the risk/reward ratio" — no prompt for written reasoning at all, despite `ScenarioAnswer` (Milestone 5) requiring both `numeric_answer` and `reasoning_text`. Added an explicit reasoning prompt ("explain your reasoning — how you calculated it, and what that ratio tells you about this trade") so there is actually something for the rubric to evaluate.
- Rubric scope decision: originally sketched 4 criteria, 3 of which re-checked arithmetic already covered by `risk_reward_ratio()` (risk amount, reward amount, ratio correctness) rather than testing reasoning specifically. Also caught that some sketched criteria (misconception-awareness, ratio-direction understanding) were not actually invited by the scenario's question as written. Decided a rubric should only score what the prompt actually asks for, not add hidden expectations. Kept the prompt narrow (Option A) rather than widening it to match a more ambitious rubric, and logged "multiple scenario variants / higher difficulty levels" as a Section 5 optional enhancement instead of scope-creeping the MVP.
- Final rubric in `app/services/evaluation_service.py` is 3 deterministic criteria: `calculation_process` checks whether the reasoning text includes the risk/reward dollar amounts; `interpretation` checks for interpretive phrasing like "for every" or "per dollar" instead of only restating the ratio; `terminology` checks for risk/reward vocabulary using word lists rather than a single exact string.
- Bug found via deliberate adversarial testing: a "middle" case ("I risked $6 and could earn $18, so the ratio is 3 to 1") was a decent, correct answer by human judgment, but scored only 1.0/3.0 because the terminology check required the literal word "reward," which the sentence never used. This confirmed the milestone's warned-about failure mode: exact keyword matching misses valid reasoning phrased differently. Fixed by widening the check to word lists covering common forms and synonyms (risk/risked/risking; reward/earn/gain/profit), not single literal strings. Re-tested: the middle case moved to 2.0/3.0.
- Testing checkpoint: 4 cases (strong / middle / weak / off-topic) now score in line with manual human judgment.
- Known limitation, accepted for the MVP: `calculation_process` still uses substring matching on the raw digits (e.g. "6") for the risk/reward figures, so it could false-positive if the same digit appears for an unrelated reason in the reasoning text. This is low practical risk for a single fixed scenario with distinctive numbers ($6, $18), so it was deferred rather than broadened into a larger solution.

## Milestone 13 — Misconception Detection & Progress Persistence
- Added misconception detection and SQLite persistence so TradeTutor can now evaluate a learner's answer beyond whether the final number is correct and save the results of each attempt.
- In `evaluation_service.py`, added two misconceptions tied directly to the Risk Management lesson: `ratio_implies_certainty` for learners who assume a favorable risk/reward ratio guarantees a profitable trade, and `risk_reward_swapped` for learners who reverse risk and reward values in their explanation.
- Initially explored simpler text matching, but found it could produce false positives. For the risk/reward swap detector, moved to a more precise regex-based approach that looks for numbers near the words risk and reward, then compares those values against the actual scenario values. Tested both positive and negative cases so valid reasoning is not flagged accidentally.
- Created `app/database/db.py` and persistent SQLite storage at `data/tradetutor.db`. Each row in `learner_attempts` represents one learner attempt and stores the scenario ID, numeric answer, numeric correctness, written reasoning, rubric score, detected misconceptions, and timestamp.
- Implemented and tested `initialize_database()`, `save_attempt()`, and `get_attempts()`. Moved timestamp generation into `save_attempt()` so the database layer owns when an attempt is recorded instead of requiring the rest of the application to supply that value.
- During integration, noticed the new attempt service would duplicate risk and reward calculations already handled in `risk_reward.py`. Refactored the calculation module to expose `calculate_risk()`, `calculate_reward()`, and `risk_reward_ratio()` so deterministic trading math stays in one source of truth.
- Created `app/services/attempt_service.py` with `process_attempt()` to orchestrate the full learner-attempt workflow: learner answer -> deterministic risk/reward calculation -> numeric correctness check -> reasoning rubric evaluation -> misconception detection -> SQLite persistence. The service coordinates the other modules without duplicating their responsibilities.
- End-to-end test used the Meridian Robotics scenario ($60 entry, $54 stop-loss, $78 target), where the correct risk/reward ratio is 3.0. A strong response produced `numeric_correct=True`, rubric score `3.0 / 3.0`, and no misconceptions. A second response calculated 3.0 correctly but claimed the ratio guaranteed profitability; TradeTutor produced `numeric_correct=True`, rubric score `2.0 / 3.0`, and `["ratio_implies_certainty"]`.
- Confirmed both attempts persisted successfully in SQLite with automatically generated timestamps.
- Key takeaway: numeric correctness, reasoning quality, and misconceptions need to be stored separately. A learner can arrive at the correct numerical answer while still misunderstanding the underlying concept.
- Final milestone takeaway: TradeTutor now has a complete backend learner-evaluation pipeline that can calculate the authoritative answer, evaluate reasoning, identify targeted misconceptions, and persist the learner's attempt for future progress tracking.

## Milestone 14 — UI/UX Refinement and Styling
- Shifted focus from backend capability to learner-facing presentation: the goal was to make the Streamlit MVP feel more cohesive, readable, and aligned with the approved TradeTutor AI visual mockup without changing the existing retrieval, calculation, evaluation, or persistence behavior.
- Established a consistent visual identity around a cream background, navy/teal/warm-orange accents, rounded cards, custom button styling, stronger typography, and a right-aligned TradeTutor AI brand mark at the top of the page.
- Added a gradient lesson hero for the Risk/Reward Ratios module to make the first screen feel more like a guided learning experience instead of a plain technical demo.
- Reworked the lesson video section into three columns for the HeyGen lesson segments, with a styled section header and individual video titles. Removed duplicate embeds so each lesson part appears once.
- Added a Key Takeaways card for the three core formulas: risk = entry - stop-loss, reward = target - entry, and risk/reward ratio = reward / risk. Included the important safety reminder that a favorable ratio does not guarantee a successful trade.
- Styled the Ask TradeTutor area with a dedicated AI Tutor header while keeping the existing question input and RAG-powered answer flow intact. Improved text, input, and button contrast for readability.
- Refined the Meridian Robotics practice interface with a dedicated practice header, three color-coded scenario cards (entry $60, stop-loss $54, target $78), and a clearer two-column input layout for the numeric answer and written reasoning.
- Refined the feedback experience into three columns: numeric answer correctness, reasoning rubric score, and misconception detection. Kept the feedback conditional so learners only see evaluation after submitting, and used Streamlit session state to preserve the result across reruns.
- Issue caught: raw HTML rendered as a Markdown code block when multiline HTML was indented too deeply. Fixed by adjusting the multiline string formatting and using `textwrap.dedent()` consistently.
- Lesson learned: CSS alone does not create new UI structure. The Streamlit layout and HTML blocks have to support the visual design; styling only changes what already exists.
- Debugging checkpoint: used a temporary visual test message to confirm Streamlit was executing the expected `home.py` file before spending more time investigating why styling changes were not appearing.
- Maintainability issue surfaced: keeping a large global CSS block inside the Python app made the UI harder to iterate on. Follow-up refactor extracted the stylesheet into `app/ui/styles.css` and loaded it from `home.py` with `pathlib.Path`, preserving the current appearance while separating styling from application logic.
- Verified the stylesheet refactor with `python3 -m py_compile app/ui/home.py` and checks that the CSS loader runs after `st.set_page_config()` and before the first UI components render.
- Next UI follow-ups: refine the hero with the approved TradeTutor avatar, improve video framing and visual consistency, review responsive behavior, and handle evaluator-quality issues separately during functional testing.
- Key takeaway: good application architecture includes the presentation layer. Separating styling from application logic makes future UI work easier without disturbing the working backend pipeline.

---

*Add new entries above this line as you progress. Keep the format loose — the goal is to capture the moment, not write polished prose (that happens later, in the final README/presentation).* 
