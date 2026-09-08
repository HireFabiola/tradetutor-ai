# TradeTutor AI

**An educational AI application for teaching foundational trading concepts through lessons, retrieval-augmented Q&A, and intelligent practice scenarios.**

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Being Solved](#problem-being-solved)
- [Intended Users](#intended-users)
- [MVP Scope](#mvp-scope)
- [Core User Workflow](#core-user-workflow)
- [MVP Features](#mvp-features)
- [Technology Stack](#technology-stack)
- [High-Level Architecture](#high-level-architecture)
- [Folder Structure](#folder-structure)
- [Educational & Safety Boundaries](#educational--safety-boundaries)
- [Testing Strategy](#testing-strategy)
- [Future Enhancements](#future-enhancements)
- [Development Setup](#development-setup)

---

## Project Overview

TradeTutor AI is an intelligent tutoring system designed to teach users foundational trading concepts through an adaptive learning flow. The application combines educational content, AI-powered retrieval-augmented generation (RAG), deterministic calculations, and metacognitive reflection to build deep understanding of trading principles.

**Mission:** To provide accessible, misconception-free trading education that develops practical risk management skills and conceptual reasoning.

---

## Problem Being Solved

- **Poor trading education:** Many online resources lack structured pedagogy and misconception detection
- **Conceptual gaps:** Users learn disconnected facts without integrated reasoning frameworks
- **Risk blindness:** New traders often lack intuition for risk/reward relationships and position sizing
- **No feedback loop:** Learning is passive; there's limited opportunity to practice with expert evaluation

TradeTutor AI addresses these by combining:
- Structured lessons on risk management fundamentals
- AI-powered Q&A for personalized clarification
- Deterministic practice scenarios with real-world relevance
- Rubric-based evaluation of reasoning
- Automated misconception detection

---

## Intended Users

Primary Users: Beginner and aspiring traders who want a structured, educational environment for learning foundational trading and risk-management concepts.

Secondary Users: Self-directed learners who want guided practice, AI-supported explanations, and feedback to strengthen their understanding of trading concepts.

**Not intended for:** Active traders seeking advanced strategies; financial advisors; automated trading systems

---

## MVP Scope

### Focus: **Risk Management Fundamentals**

The MVP teaches core concepts only:
- Position sizing strategies
- Risk/reward ratios
- Stop-loss determination
- Portfolio diversification principles
- Psychological biases in trading (loss aversion, overconfidence)

**Out of Scope (MVP):**
- Chart technical analysis
- Fundamental analysis
- Options strategies
- Real market data integration
- Multi-asset portfolios
- Backtesting systems
- Live trading

---

## Core User Workflow

```
1. Lesson
The user completes a structured lesson covering a core Risk Management Fundamentals concept.

↓

2. User Q&A
The user can ask questions about the lesson or request clarification on concepts they do not fully understand.

↓

3. Relevant Content Retrieval from ChromaDB
The system searches the embedded educational knowledge base and retrieves content relevant to the user's question.

↓

4. RAG-Grounded LLM Response
The retrieved content is provided as context to the open-source/open-weight LLM, which generates an educational response grounded in the approved course material.

↓

5. Practice Scenario
The user receives a realistic but fictional trading scenario designed to test application of the lesson's risk-management concepts.

↓

6. Deterministic Python Calculation
The user completes a numerical task, such as calculating a risk/reward ratio or appropriate position size. A deterministic Python function calculates or validates the correct result rather than relying on the LLM for arithmetic.

↓

7. Written Reasoning Response
The user explains the reasoning behind their answer, allowing the system to assess conceptual understanding in addition to numerical accuracy.

↓

8. Rubric Evaluation
The user's written reasoning is evaluated against defined learning criteria to determine whether they demonstrated understanding of the targeted concept.

↓

9. Misconception Identification & Feedback
The system identifies potential misconceptions or gaps in understanding and provides targeted educational feedback or remediation.

↓

10. Progress Tracking
The user's results, demonstrated mastery, identified misconceptions, and learning progress are stored in SQLite for use throughout the learning experience.
```

---

## MVP Features

### Core Functionality
- **Lesson Content:** Pre-written, pedagogically structured lessons on risk management
- **RAG-Powered Q&A:** Users ask free-form questions; retrieval-augmented LLM answers with citations to knowledge base
- **Practice Scenarios:** Realistic, bounded trading situations with embedded numerical questions
- **Deterministic Calculations:** Python functions validate risk/reward calculations and position sizing
- **Reasoning Evaluation:** Rubric-based assessment of written explanations
- **Misconception Detection:** Pattern-based identification of common errors (e.g., "confusing reward with probability")
- **Progress Tracking:** SQLite records of user responses, scores, and remediation history

### Non-MVP Features (Excluded)
- User authentication (assumed single-user or local deployment)
- Real-time market data
- Multi-currency support
- Mobile app
- Multiplayer features
- Gamification (badges, leaderboards)
- Advanced analytics dashboards

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python |
| **Environment & Dependency Management** | `uv` |
| **User Interface** | Streamlit |
| **LLM** | Open-source/open-weight (e.g., Mistral, Llama 2, or similar via Ollama/local inference) |
| **Embeddings** | SentenceTransformers (local, no API calls) |
| **Vector Database** | ChromaDB (lightweight, in-process) |
| **Persistent Storage** | SQLite (user progress, app state) |
| **Calculations** | Native Python (deterministic, no external services) |
| **Data Validation** | Pydantic (structured schemas for scenarios, responses) |
| **Testing** | pytest (unit and integration tests) |

**Rationale:**
- All components are open-source and can run locally (no cloud dependencies, low cost)
- Deterministic calculations ensure reproducible, auditable results
- SQLite provides sufficient scalability for educational MVP
- Streamlit enables rapid UI iteration
- Local LLM and embeddings protect user privacy

---

## High-Level Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                     STREAMLIT UI LAYER                       │
│   Lesson • Q&A • Practice Scenario • Reasoning • Feedback    │
└─────────────────────────────┬────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
     ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
     │  RAG / AI      │ │  CALCULATION   │ │   DATABASE     │
     │  SERVICE       │ │  SERVICE       │ │   SERVICE      │
     │                │ │                │ │                │
     │ • ChromaDB     │ │ • Position     │ │ • User         │
     │ • Embeddings   │ │   Sizing       │ │   Progress     │
     │ • Local LLM    │ │ • Risk/Reward  │ │ • App State    │
     │ • RAG Q&A      │ │ • Numerical    │ │ • Responses    │
     │ • Rubric Eval  │ │   Validation   │ │ • Scores       │
     │ • Misconception│ │                │ │ • Misconception│
     │   Detection    │ │                │ │   Records      │
     └───────┬────────┘ └───────┬────────┘ └───────┬────────┘
             │                  │                  │
             └──────────────────┼──────────────────┘
                                │
                                ▼
              ┌────────────────────────────────┐
              │   KNOWLEDGE & APPLICATION DATA │
              │                                │
              │ • Lesson Content               │
              │ • RAG Knowledge Documents      │
              │ • SQLite Application Data      │
              └────────────────────────────────┘
```

---

## Folder Structure

```
tradetutor-ai/
├── app/                              # Main application code
│   ├── __init__.py
│   ├── ui/                           # Streamlit pages & UI components
│   │   └── .gitkeep                  # (To be filled: home.py, lesson.py, etc.)
│   ├── rag/                          # Retrieval-augmented generation
│   │   └── .gitkeep                  # (To be filled: retriever.py, embedder.py)
│   ├── services/                     # Business logic services
│   │   └── .gitkeep                  # (To be filled: lesson_service.py, etc.)
│   ├── calculations/                 # Deterministic trading math
│   │   └── .gitkeep                  # (To be filled: position_sizing.py, risk_reward.py)
│   └── database/                     # Data access & ORM
│       └── .gitkeep                  # (To be filled: models.py, queries.py)
├── data/                             # Educational & knowledge content
│   ├── lessons/                      # Lesson content (YAML, JSON, or markdown)
│   │   └── .gitkeep
│   └── knowledge/                    # Knowledge base documents (for RAG ingestion)
│       └── .gitkeep
├── tests/                            # Test suite
│   └── .gitkeep                      # (To be filled: test_*.py files)
├── docs/                             # Documentation (architecture, design, etc.)
│   └── .gitkeep
├── README.md                         # This file
├── .gitignore                        # Git ignore rules
└── pyproject.toml                    # Project metadata & dependencies (to be created)
```

---

## Educational & Safety Boundaries

### In Scope
- ✅ Teaching risk management concepts
- ✅ Explaining why positions should be sized carefully
- ✅ Discussing psychological biases in trading
- ✅ Evaluating reasoning quality using rubrics
- ✅ Identifying misconceptions and offering remediation

### Out of Scope / Responsible AI
- ❌ **No endorsement of specific securities or trading advice** ("Buy this stock")
- ❌ **No guarantees of returns** or profit claims
- ❌ **No advice on personal finances** (defer to qualified advisors)
- ❌ **No automation of real trading** (educational purpose only)
- ❌ **No encouragement of risky behavior** (scenarios emphasize prudent risk management)

**Implementation:**
- Scenarios are clearly fictional ("Imagine you are...") with no reference to real tickers
- Lesson content includes repeated disclaimers: "This is educational only"
- Misconception detection flags overconfidence and risk tolerance misalignment

---

## Testing Strategy

### Unit Tests
- **Calculations:** Verify position sizing, risk/reward, and stop-loss logic
- **Pydantic models:** Ensure scenario and response validation
- **Utilities:** Test data parsing, transformations

### Integration Tests
- **RAG pipeline:** Verify retrieval and LLM response quality
- **Workflow end-to-end:** User input → calculation → evaluation → progress update
- **Database:** User state persistence and retrieval

### Manual/Acceptance Tests
- Streamlit UI flow (lesson → Q&A → scenario → feedback)
- Misconception detection accuracy
- Rubric evaluation consistency

**Tools:** pytest, pytest-cov (optional, for coverage reports)

---

## Future Enhancements

⚠️ **Not part of MVP—explicitly deferred:**

- **Advanced Topics:** Options pricing, volatility, derivative hedging
- **Technical Analysis:** Chart patterns, indicator interpretation
- **Multi-Asset Portfolios:** Correlation, rebalancing, asset allocation
- **Backtesting Framework:** Historical performance simulation
- **Real Market Integration:** Live prices, actual trading pairs
- **Authentication & Multiuser:** User accounts, role-based access
- **Mobile App:** iOS/Android companion
- **Gamification:** Badges, leaderboards, achievement tracking
- **AI-Powered Tutoring:** Adaptive lesson sequencing based on misconceptions
- **Video Content:** Animated lessons, expert interviews
- **Peer Collaboration:** Discussion forums, peer review of reasoning
- **Advanced Analytics:** Learning trajectory prediction, knowledge gap analysis
- **Export & Certification:** Downloadable progress reports, learning badges

---

## Development Setup

### Prerequisites
- Python 3.11+ (check with `python --version`)
- `uv` package manager installed (see [uv docs](https://docs.astral.sh/uv/))

### Initial Setup (Perform These Steps)

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd tradetutor-ai
   ```

2. **Initialize the Python environment using `uv`:**
   ```bash
   uv init
   ```

3. **Install dependencies (add as needed):**
   - Core dependencies will include: `streamlit`, `pydantic`, `chromadb`, `sentence-transformers`, `pytest`
   - See `pyproject.toml` once created for full list

4. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate  # macOS/Linux
   # or
   .venv\Scripts\activate     # Windows
   ```

5. **Run tests to verify setup:**
   ```bash
   pytest tests/
   ```

6. **Launch the Streamlit app (once implemented):**
   ```bash
   streamlit run app/ui/home.py
   ```

### Project Files to Create
- `pyproject.toml` — Project metadata and dependency definitions
- Lesson content in `data/lessons/`
- Knowledge base documents in `data/knowledge/`
- Streamlit pages in `app/ui/`
- Modules in `app/{rag,services,calculations,database}/`

---

## Contributing & License

(To be defined per capstone requirements)

---

## Questions or Issues?

Refer to documentation in the `docs/` folder or open an issue in the repository.

---

**Last Updated:** 2026-09-08  
**Status:** MVP Defined — Initial Project Scaffolding in Progress
