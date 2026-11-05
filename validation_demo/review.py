"""Pydantic validation demo: a strict `Review` model rejecting a bad JSON payload.

Run with:  python -m validation_demo
"""
import datetime

from pydantic import BaseModel, Field, ValidationError


class Review(BaseModel):
    review_id: str = Field(description="The ID of the review", pattern=r"^R\d{5}$")
    rating: str = Field(
        description="The rating of the review", pattern=r"^★{1,5}☆{0,4} \(\d stars\)$"
    )
    date: datetime.date = Field(
        description="The date of the review",
        json_schema_extra={"format_hint": "YYYY-MM-DD"},
    )
    text: str = Field(description="The text of the review", min_length=1, max_length=1000)


VALID_REVIEW_JSON = """
{"review_id": "R00042", "rating": "★★★☆☆ (3 stars)", "date": "2026-11-05", "text": "Great place."}
"""

INVALID_REVIEW_JSON = """
{"review_id": "", "rating": 3, "date": "1 month ago", "text": ""}
"""


def main() -> None:
    print("Valid payload:")
    print(Review.model_validate_json(VALID_REVIEW_JSON), "\n")

    print("Invalid payload:")
    try:
        Review.model_validate_json(INVALID_REVIEW_JSON)
    except ValidationError as e:
        print(f"{e.error_count()} validation errors")
        for err in e.errors():
            print(f"  - {'.'.join(map(str, err['loc']))}: {err['msg']}")


if __name__ == "__main__":
    main()
