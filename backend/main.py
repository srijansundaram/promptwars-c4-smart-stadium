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
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
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