# Stadium Companion — Prompt Wars Challenge 4: Smart Stadiums & Tournament Operations

## Vertical
A GenAI-enabled assistant for **fans navigating a FIFA World Cup 2026 stadium**,
with a specific focus on fans who are non-native English speakers and/or have
an accessibility need (wheelchair, mobility impairment, visual impairment).

## Approach & Logic
Rather than covering every operational area shallowly, this solution focuses
on one high-value, well-defined slice: **context-aware, multilingual,
accessibility-first navigation and amenity guidance**.

The system is split into two deliberately separate layers:

1. **Decision engine** (`backend/decision_engine.py`) — a deterministic,
   rules-based module with no LLM involvement. Given a fan's profile
   (seat zone, mobility need) and the live stadium state (crowd density per
   gate, gate open/closed status, restroom/food queue lengths, transport
   crowd + departure times), it scores and selects the best option for:
   exit routes, restrooms, food stalls, and transport.
   Keeping this deterministic makes it auditable and unit-testable — a
   requirement for real operational trust, and directly testable per the
   evaluation criteria.

2. **LLM layer** (`backend/llm_service.py`) — handles only language
   understanding (what does the fan want, what language are they speaking)
   and language generation (phrasing the decision engine's output naturally
   in the fan's language), using Groq's free-tier API (Llama 3.3 70B). It
   never makes the actual recommendation decision itself — this avoids the
   common failure mode of LLM hallucination affecting safety-relevant
   routing decisions.

## How It Works
1. Fan enters their seat zone and mobility need, and types a question in
   any language (e.g. "¿Dónde está el baño más cercano?").
2. `/chat` endpoint detects intent + language (via Groq's API if configured,
   otherwise a keyword-based + `langdetect` fallback).
3. The decision engine computes the best recommendation using live mock
   stadium data (`data/stadium_state.json`).
4. The LLM layer phrases the response in the fan's detected language.
5. The frontend (`frontend/index.html`) displays the reply along with the
   detected intent/language for transparency, with accessible markup
   (semantic form/landmarks, visible focus states, `aria-live` regions)
   and a visible error state if the backend is unreachable.

## Screenshots

**Exit routing — accessibility-aware context switching:**
Same seat zone, same question — the recommended gate changes depending on
mobility need, because the objectively "best" gate (shortest distance +
lowest crowd) isn't wheelchair-accessible.

*Without a mobility need — Gate C recommended (best combined score):*
![No wheelchair](screenshots/exit_no_wheelchair.png)

*With wheelchair selected — Gate C is excluded, Gate E recommended instead:*
![Wheelchair](screenshots/exit_wheelchair.png)

**Multilingual support:**
Fan asks in Spanish, receives a fully translated, context-aware reply.
![Spanish query](screenshots/spanish_query.png)

**Error handling:**
Graceful, visible failure message when the backend is unreachable —
no silent hang.
![Error state](screenshots/error_state.png)

## Assumptions
- Live stadium state (crowd density, gate status, queue lengths) is mocked
  via a static JSON file (`data/stadium_state.json`) rather than a real IoT
  feed, since no live FIFA data source is available for this challenge.
  The decision engine's interface is designed so a real live-data feed could
  be swapped in without changing any decision logic.
- The app runs fully without an API key (rule-based fallback for both intent
  detection and reply phrasing), so it can be evaluated without requiring
  a secret to be configured. Setting `GROQ_API_KEY` in `.env` (free, no
  credit card required — console.groq.com/keys) enables full multilingual
  LLM-based understanding and phrasing.
- Scope is limited to fan-facing navigation/amenities/transport rather than
  attempting to also cover volunteer/organizer/venue-staff workflows, to
  keep the logic deep and well-tested rather than broad and shallow.

## Setup & Run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: add your free GROQ_API_KEY
uvicorn backend.main:app --reload
```
Open http://localhost:8000 in your browser.

## Testing
```bash
pytest tests/ -v
```
7 tests covering: accessibility exclusion, closed-gate exclusion, crowd
avoidance, restroom accessibility, queue-based food/transport selection,
and unknown-input resilience.

## Security Notes
- No API keys are hardcoded; `.env` is gitignored.
- CORS is fully open (`*`) for local demo purposes only — this should be
  restricted to specific origins before any production deployment.
- All external input (fan message, profile) is validated via Pydantic models.
- Frontend escapes all user-provided text before rendering (XSS prevention).

## Limitations / Future Work
- Real-time stadium data integration (replacing the mock JSON).
- Persisting chat history per fan session.
- Voice input for accessibility (visually impaired fans).
- Extending to volunteer/organizer operational-intelligence dashboards.