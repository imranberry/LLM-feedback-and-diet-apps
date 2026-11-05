import pytest
from pydantic import ValidationError

from feedback_analyzer import streamlined as s


def test_field_budget():
    assert len(s.LocationFeedbackAnalysis.model_fields) <= 10
    assert len(s.LocationFeedbackInput.model_fields) <= 10


def test_input_validation():
    assert s.LocationFeedbackInput(place_name=" A ", feedback_text="x", location="  ").location is None
    with pytest.raises(ValidationError):
        s.LocationFeedbackInput(place_name="", feedback_text="x")
    with pytest.raises(ValidationError):
        s.LocationFeedbackInput(place_name="A", feedback_text="x" * 5001)


def test_get_response(monkeypatch):
    class Chain:
        def invoke(self, payload):
            assert payload["location"] == "Not provided"
            return s.LocationFeedbackAnalysis(place_name="guess", overall_sentiment="positive", summary="ok")

    monkeypatch.setattr(s, "_chain", Chain())
    out = s.get_response(s.LocationFeedbackInput(place_name="Real", feedback_text="good"))
    assert out.place_name == "Real"


def test_wrong_type(monkeypatch):
    class Chain:
        def invoke(self, _):
            return "nope"

    monkeypatch.setattr(s, "_chain", Chain())
    with pytest.raises(TypeError):
        s.get_response(s.LocationFeedbackInput(place_name="A", feedback_text="b"))
