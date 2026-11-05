## 1. Output Model Design

The output model represents the structured analysis produced from feedback about a place. One analysis corresponds to one submitted feedback item. It is implemented as the Pydantic model `LocationFeedback` and is enforced through `model.with_structured_output(LocationFeedback)`.

### `LocationFeedback`

Field Type Required? Description and validation `location` `LocationDetails` object Yes Geographic details of the place being reviewed. The object is always returned; its fields are empty strings when unknown. `location.city` string Yes (within `location`) City mentioned or identified from the input. Return an empty string if it is not provided or cannot be identified confidently. `location.area` string Yes (within `location`) Neighborhood or specific area mentioned. Return an empty string if it is not provided or cannot be identified confidently. `overall_sentiment` enum: `positive`, `negative`, `neutral`, `mixed` Yes Overall sentiment expressed in the feedback. Must be one of the listed values. `feedback_summary` string Yes Concise summary of the user's feedback. Must be supported by the input. `topics` array of `TopicFeedback` Yes Topics mentioned and their individual sentiments. Topics should not be duplicated. `topics[].topic` string Yes, per topic Main topic being discussed (free text, no controlled vocabulary). `topics[].sentiment` enum: `positive`, `negative`, `neutral`, `mixed` Yes, per topic Sentiment expressed about that topic. `mixed_opinions` array of strings Yes Statements expressing conflicting or mixed opinions. Use an empty list when there are none.

### Relationships and output rules

- The top-level object describes one feedback submission about one place.
- `location` is a nested object (`LocationDetails`) containing `city` and `area`.
- `topics` is a list of nested `TopicFeedback` objects, each with its own sentiment. A topic's sentiment can differ from the overall sentiment.
- `mixed_opinions` is a list because feedback may contain several conflicting or mixed statements.
- When feedback contains both positive and negative opinions, both are preserved (in separate topics and in `mixed_opinions`), and `overall_sentiment` is `mixed` where appropriate.
- Use only information supported by the supplied input. Do not invent geographic details.
- The output does not echo `place_name`; it is used only as analysis context.
- The output does not include scores, evidence snippets, action items, urgency, language, confidence, or limitations.
- Output is returned in the required schema and must be an instance of `LocationFeedback`; any other type raises a `TypeError`.

## 2. Input Model Design

The input model is the Pydantic model `LocationInput`.

### `LocationInput`

Field Type Required? Description and validation `place_name` string Yes Name of the place or service being reviewed (e.g. "Restaurants", "Roads and public transport"). `location` string Yes Geographic location associated with the feedback, as a single free-text string (e.g. "Yaba, Lagos"). `feedback` string Yes The user's feedback about the place or service.

### Input validation and behavior

1. All three fields are required by the Pydantic model.
2. `get_response` additionally rejects any field that is empty or whitespace-only (checked with `.strip()`), raising `ValueError` with a message such as "Place name cannot be empty." The values themselves are passed to the model as given, not trimmed.
3. There is no maximum length on `feedback`.
4. City and area are extracted by the model from `location` and the feedback text. They are not separate input fields. If they cannot be identified confidently, they are returned as empty strings rather than guessed.
5. The app analyzes only the supplied text. It does not use live map data, coordinates, or geocoding.
6. If the feedback contains multiple opinions, they are kept in separate topics, and `overall_sentiment` is `mixed` when appropriate.
7. There are no optional inputs such as language, address, region, country, or analysis focus.

### Error handling

- `ValueError`: input validation failed (empty `place_name`, `location`, or `feedback`). Printed as "Input validation error" and re-raised.
- `TypeError`: the model did not return a `LocationFeedback` object.
- Any other exception (model invocation or output validation failure): printed as "Extraction failed" and re-raised.
- `main()` catches exceptions per example, so one failure does not stop the others.

## 3. Examples

These are the two examples built into the app. Outputs are illustrative; actual model output may vary in wording.

### Example 1 - Mixed feedback (food vs. service)

**Sample input**

```json
{
  "place_name": "Restaurants",
  "location": "Yaba, Lagos",
  "feedback": "The food was excellent and affordable, but the service was slow. I would return for the food, although the waiting time needs improvement."
}
```

**Illustrative output**

```json
{
  "location": {
    "city": "Lagos",
    "area": "Yaba"
  },
  "overall_sentiment": "mixed",
  "feedback_summary": "The reviewer enjoyed the excellent, affordable food and would return for it, but found the service slow and wants shorter waiting times.",
  "topics": [
    { "topic": "food quality", "sentiment": "positive" },
    { "topic": "affordability", "sentiment": "positive" },
    { "topic": "service speed", "sentiment": "negative" }
  ],
  "mixed_opinions": [
    "The food was excellent and affordable, but the service was slow.",
    "I would return for the food, although the waiting time needs improvement."
  ]
}
```

### Example 2 - Mixed feedback (roads and transport)

**Sample input**

```json
{
  "place_name": "Roads and public transport",
  "location": "Ikeja, Lagos",
  "feedback": "The roads are convenient and well connected, but traffic congestion makes commuting stressful. Public transport is accessible, though it can be overcrowded. Overall, the area has advantages and disadvantages."
}
```

**Illustrative output**

```json
{
  "location": {
    "city": "Lagos",
    "area": "Ikeja"
  },
  "overall_sentiment": "mixed",
  "feedback_summary": "The reviewer finds the roads convenient and well connected and public transport accessible, but is frustrated by traffic congestion and overcrowding.",
  "topics": [
    { "topic": "road connectivity", "sentiment": "positive" },
    { "topic": "traffic congestion", "sentiment": "negative" },
    { "topic": "public transport", "sentiment": "mixed" }
  ],
  "mixed_opinions": [
    "The roads are convenient and well connected, but traffic congestion makes commuting stressful.",
    "Public transport is accessible, though it can be overcrowded.",
    "Overall, the area has advantages and disadvantages."
  ]
}
```