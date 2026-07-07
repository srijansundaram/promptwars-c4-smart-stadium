from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.models import ChatRequest, ChatResponse
from backend.stadium_data import load_stadium_state
from backend.decision_engine import get_recommendation
from backend.llm_service import detect_intent_and_language, phrase_reply

app = FastAPI(title="Stadium Companion — Prompt Wars Challenge 4")

# CORS kept open for demo purposes only; restrict origins before any
# real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://stadium-companion-762488706590.europe-west1.run.app",
        "http://localhost:8000",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    """Simple liveness check for uptime monitoring / deployment platforms."""
    return {"status": "ok"}

@app.get("/ops/summary")
def ops_summary():
    """Lightweight operational intelligence view for venue staff:
    a snapshot of crowd density and status across all gates."""
    state = load_stadium_state()
    gates = state["gates"]
    critical = [name for name, g in gates.items() if g["crowd_level"] == "critical"]
    closed = [name for name, g in gates.items() if g["status"] != "open"]
    return {
        "total_gates": len(gates),
        "critical_crowd_gates": critical,
        "closed_gates": closed,
        "transport_status": state["transport"],
    }

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Handles a fan's natural-language query: detects intent + language,
    computes a context-aware recommendation, and returns it phrased in
    the fan's own language."""
    state = load_stadium_state()

    intent, detected_language = detect_intent_and_language(req.message)
    language = req.profile.preferred_language or detected_language

    recommendation, reasoning = get_recommendation(intent, req.profile, state)
    reply = phrase_reply(recommendation, reasoning, language)

    return ChatResponse(
        detected_language=language,
        detected_intent=intent,
        recommendation=recommendation,
        reasoning=reasoning,
        reply=reply,
    )


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")