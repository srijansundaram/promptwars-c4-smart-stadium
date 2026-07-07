import pytest
from backend.models import FanProfile
from backend.decision_engine import (
    recommend_exit_route,
    recommend_restroom,
    recommend_food,
    recommend_transport,
)
from backend.stadium_data import load_stadium_state

state = load_stadium_state()


def test_exit_route_excludes_inaccessible_gates_for_wheelchair_users():
    profile = FanProfile(seat_zone="Zone 3", mobility_need="wheelchair")
    gate, reasoning = recommend_exit_route(profile, state)
    assert gate != "Gate C"  # Gate C is not accessible
    assert "accessible" in reasoning


def test_exit_route_excludes_closed_gates():
    profile = FanProfile(seat_zone="Zone 3", mobility_need="none")
    gate, _ = recommend_exit_route(profile, state)
    assert gate != "Gate D"  # Gate D is closed


def test_exit_route_avoids_critical_crowd_when_alternative_exists():
    profile = FanProfile(seat_zone="Zone 2", mobility_need="none")
    gate, _ = recommend_exit_route(profile, state)
    assert gate != "Gate B"  # Gate B is critically crowded


def test_restroom_respects_accessibility_requirement():
    profile = FanProfile(seat_zone="Zone 1", mobility_need="wheelchair")
    result, _ = recommend_restroom(profile, state)
    assert "R2" not in result  # R2 is not accessible


def test_food_prefers_shorter_queue():
    profile = FanProfile(seat_zone="Zone 2", mobility_need="none")
    result, reasoning = recommend_food(profile, state)
    assert "Fan Fare Snacks" in result  # short queue, same zone


def test_transport_returns_valid_option():
    profile = FanProfile(seat_zone="Zone 1", mobility_need="none")
    result, _ = recommend_transport(profile, state)
    assert result in ("Metro", "Shuttle")


def test_unknown_zone_does_not_crash():
    profile = FanProfile(seat_zone="Zone 99", mobility_need="none")
    gate, reasoning = recommend_exit_route(profile, state)
    assert isinstance(gate, str)