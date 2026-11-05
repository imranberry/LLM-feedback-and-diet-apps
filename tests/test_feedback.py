import pytest
from pydantic import ValidationError

from feedback_analyzer import analyzer
from feedback_analyzer.analyzer import (
    LocationFeedbackAnalysis,
    LocationFeedbackInput,
    get_response,
)


def test_input_strips_and_cleans():
    d = LocationFeedbackInput(place_name="  Cafe ", feedback_text=" nice ", city="  ", analysis_focus=[" a ", ""])
    assert d.place_name == "Cafe" and d.city is None and d.analysis_focus == ["a"]


def test_empty_required_fields_rejected():
    with pytest.raises(ValidationError):
        LocationFeedbackInput(place_name="  ", feedback_text="x")


def test_feedback_length_limit():
    with pytest.raises(ValidationError):
        LocationFeedbackInput(place_name="p", feedback_text="x" * 5001)


def test_get_response_overrides_place_name(monkeypatch):
    class FakeChain:
        def invoke(self, _):
            return LocationFeedbackAnalysis(
                place_name="model guess", overall_sentiment="mixed", summary="ok", urgency="low"
            )

    monkeypatch.setattr(analyzer, "_chain", FakeChain())
    out = get_response(LocationFeedbackInput(place_name="Real Name", feedback_text="fine"))
    assert out.place_name == "Real Name"


def test_wrong_type_raises(monkeypatch):
    class BadChain:
        def invoke(self, _):
            return {"not": "a model"}

    monkeypatch.setattr(analyzer, "_chain", BadChain())
    with pytest.raises(TypeError):
        get_response(LocationFeedbackInput(place_name="p", feedback_text="f"))
