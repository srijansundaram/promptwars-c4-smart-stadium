import os
from typing import Tuple

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

_INTENT_KEYWORDS = {
    "exit_route": ["exit", "leave", "way out", "gate", "route"],
    "restroom": ["restroom", "toilet", "bathroom", "washroom"],
    "food": ["food", "hungry", "eat", "snack", "drink"],
    "transport": ["metro", "shuttle", "bus", "train", "transport", "way home"],
}


def _get_client():
    from openai import OpenAI
    return OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)


def _fallback_detect_intent(message: str) -> str:
    lower = message.lower()
    for intent, keywords in _INTENT_KEYWORDS.items():
        if any(k in lower for k in keywords):
            return intent
    return "unknown"


def _fallback_detect_language(message: str) -> str:
    try:
        from langdetect import detect
        return detect(message)
    except Exception:
        return "en"


def detect_intent_and_language(message: str) -> Tuple[str, str]:
    if not GROQ_API_KEY:
        return _fallback_detect_intent(message), _fallback_detect_language(message)

    client = _get_client()
    prompt = f"""Classify the user's message into exactly one intent from this list:
exit_route, restroom, food, transport, unknown

Also detect the ISO 639-1 language code of the message.

Respond ONLY in this exact format, nothing else:
intent=<intent>
language=<code>

Message: "{message}\""""

    try:
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.choices[0].message.content.strip()
        intent, language = "unknown", "en"
        for line in text.splitlines():
            if line.startswith("intent="):
                intent = line.split("=", 1)[1].strip()
            elif line.startswith("language="):
                language = line.split("=", 1)[1].strip()
        return intent, language
    except Exception:
        return _fallback_detect_intent(message), _fallback_detect_language(message)


def phrase_reply(recommendation: str, reasoning: str, language: str) -> str:
    if not GROQ_API_KEY or language == "en":
        return f"{recommendation}. {reasoning}"

    client = _get_client()
    prompt = f"""Translate and naturally phrase this stadium assistant response
into language code "{language}". Keep it short, friendly, and clear.
Do not add new information.

Recommendation: {recommendation}
Reasoning: {reasoning}"""

    try:
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return f"{recommendation}. {reasoning}"