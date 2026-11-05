import pytest
from pydantic import ValidationError

from validation_demo.review import INVALID_REVIEW_JSON, VALID_REVIEW_JSON, Review


def test_valid_review():
    assert Review.model_validate_json(VALID_REVIEW_JSON).review_id == "R00042"


def test_invalid_review_reports_all_four_fields():
    with pytest.raises(ValidationError) as exc:
        Review.model_validate_json(INVALID_REVIEW_JSON)
    assert {e["loc"][0] for e in exc.value.errors()} == {"review_id", "rating", "date", "text"}
