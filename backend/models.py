from typing import Literal, Optional
from pydantic import BaseModel, Field

MobilityNeed = Literal["none", "wheelchair", "mobility_impaired", "visually_impaired"]
Intent = Literal["exit_route", "restroom", "food", "transport", "unknown"]


class FanProfile(BaseModel):
    seat_zone: str = Field(..., description="e.g. 'Zone 1'")
    mobility_need: MobilityNeed = "none"
    preferred_language: Optional[str] = Field(
        default=None, description="ISO code, e.g. 'es'. If None, auto-detected from message."
    )


class ChatRequest(BaseModel):
    message: str
    profile: FanProfile


class ChatResponse(BaseModel):
    detected_language: str
    detected_intent: Intent
    recommendation: Optional[str] = None
    reasoning: Optional[str] = None
    reply: str