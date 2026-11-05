# Location Feedback Analysis Model Design

This document details the streamlined, production-ready input and output model designs optimized to stay strictly under the 10-field maximum limit.

---

## 1. Input Model Design (`LocationFeedbackInput`)

| Field | Type | Required? | Description and Validation |
| :--- | :--- | :--- | :--- |
| `place_name` | string | Yes | Name of the place. Trim whitespace; cannot be empty. |
| `feedback_text` | string | Yes | Feedback text to analyze (max 5,000 characters). |
| `location` | string | No | Combined location details (e.g., "Lagos, Nigeria"). |

---

## 2. Output Model Design (`LocationFeedbackAnalysis`)

| Field | Type | Required? | Description and Validation |
| :--- | :--- | :--- | :--- |
| `place_name` | string | Yes | Name of the place being reviewed. |
| `location` | string | No | Combined location details matching or inferred from input. |
| `overall_sentiment` | enum | Yes | `positive`, `mixed`, `negative`, `neutral` |
| `summary` | string | Yes | Short, neutral summary grounded strictly in the text. |
| `topics` | array | Yes | **Nested structure** containing `Topic` objects (see below). |
| `action_items` | array [str] | Yes | Practical improvement suggestions. Empty array if none. |
| `limitations` | array [str] | Yes | Ambiguities or missing context. Empty array if none. |

### Nested `Topic` Object Structure
* **`name`** (string, Required): Short label (e.g., `cleanliness`, `staff`, `wait_time`).
* **`sentiment`** (enum, Required): `positive`, `mixed`, `negative`, `neutral`.

---

## 3. Implementation Example

### Sample Input
```json
{
  "place_name": "Harbor View Café",
  "feedback_text": "The coffee was great and the staff were friendly, but we waited 40 minutes for our food and the tables were sticky.",
  "location": "Lagos, Nigeria"
}
```

### Streamlined Output
```json
{
  "place_name": "Harbor View Café",
  "location": "Lagos, Nigeria",
  "overall_sentiment": "mixed",
  "summary": "The reviewer liked the coffee and staff but was dissatisfied with the 40-minute food wait and sticky tables.",
  "topics": [
    { "name": "food_and_drink", "sentiment": "positive" },
    { "name": "staff", "sentiment": "positive" },
    { "name": "wait_time", "sentiment": "negative" },
    { "name": "cleanliness", "sentiment": "negative" }
  ],
  "action_items": [
    "Review kitchen service times during busy periods.",
    "Improve table-cleaning checks between customers."
  ],
  "limitations": [
    "The feedback does not establish if this wait time is a recurring issue."
  ]
}
```
