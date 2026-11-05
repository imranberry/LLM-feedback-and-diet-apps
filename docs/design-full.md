# Google Maps-Style Location Feedback Analysis

## 1. Output Model Design

The output model represents the structured analysis produced from
feedback about a place. One analysis corresponds to one submitted
feedback item.

### `LocationFeedbackAnalysis`

  -----------------------------------------------------------------------------------
  Field                  Type                         Required? Description and
                                                                validation
  ---------------------- ---------------- --------------------- ---------------------
  `place_name`           string                             Yes Name of the place
                                                                being reviewed. Trim
                                                                whitespace; must not
                                                                be empty.

  `location`             object                              No Location details,
                                                                such as address,
                                                                city, region, and
                                                                country. Include only
                                                                details supplied or
                                                                confidently
                                                                identified.

  `location.address`     string                              No Street address or
                                                                recognizable location
                                                                description.

  `location.city`        string                              No City or town.

  `location.region`      string                              No State, province, or
                                                                region.

  `location.country`     string                              No Country.

  `overall_sentiment`    enum:                              Yes Overall tone of the
                         `positive`,                            feedback. Must be one
                         `mixed`,                               of the listed values.
                         `negative`,                            
                         `neutral`                              

  `sentiment_score`      number                              No Optional normalized
                                                                score from `-1.0`
                                                                (very negative) to
                                                                `1.0` (very
                                                                positive). Must be
                                                                within this range.

  `summary`              string                             Yes Short, neutral
                                                                summary of the
                                                                feedback. Must not
                                                                introduce claims
                                                                absent from the
                                                                input.

  `topics`               array of `Topic`                   Yes Main subjects
                         objects                                mentioned in the
                                                                feedback. Use an
                                                                empty array if no
                                                                clear topic is
                                                                identified.

  `topics[].name`        string                  Yes, per topic Short topic label,
                                                                e.g. `cleanliness`,
                                                                `staff`, `parking`,
                                                                `wait_time`, or
                                                                `accessibility`.

  `topics[].sentiment`   enum:                   Yes, per topic Sentiment
                         `positive`,                            specifically
                         `mixed`,                               associated with that
                         `negative`,                            topic.
                         `neutral`                              

  `topics[].evidence`    string                              No Brief supporting
                                                                phrase or paraphrase
                                                                grounded in the
                                                                submitted feedback.

  `action_items`         array of strings                   Yes Practical improvement
                                                                suggestions supported
                                                                by the feedback. Use
                                                                an empty array when
                                                                no action is
                                                                warranted or
                                                                supported.

  `urgency`              enum: `low`,                       Yes Priority suggested by
                         `medium`, `high`                       the feedback.
                                                                Safety-related
                                                                concerns may be high
                                                                priority; do not
                                                                infer emergencies
                                                                without evidence.

  `language`             string                              No Language of the
                                                                submitted feedback,
                                                                if identifiable.

  `confidence`           number                              No Model confidence from
                                                                `0.0` to `1.0`. Treat
                                                                as an estimate, not a
                                                                guarantee.

  `limitations`          array of strings                   Yes Ambiguities, missing
                                                                context, or
                                                                uncertainty. Use an
                                                                empty array when none
                                                                needs mentioning.
  -----------------------------------------------------------------------------------

### Relationships and output rules

-   The top-level object describes one feedback submission about one
    place.
-   `location` is a nested object because its address components belong
    together and may be partially known.
-   `topics` contains zero or more nested `Topic` objects. Each topic
    has its own sentiment and optional evidence.
-   `action_items` and `limitations` are lists because there may be
    multiple items.
-   The overall sentiment summarizes the entire feedback; topic
    sentiment can differ from the overall sentiment.
-   Do not invent a place address, business facts, review ratings, or
    customer details.
-   Return valid structured data matching this design. Use the exact
    enum values shown above.

## 2. Input Model Design

### `LocationFeedbackInput`

  ----------------------------------------------------------------------------
  Field              Type                         Required? Description and
                                                            validation
  ------------------ ---------------- --------------------- ------------------
  `place_name`       string                             Yes Name of the place
                                                            being discussed.
                                                            Trim whitespace
                                                            and reject an
                                                            empty value.

  `feedback_text`    string                             Yes The user's
                                                            feedback to
                                                            analyze. Trim
                                                            leading/trailing
                                                            whitespace; reject
                                                            an empty string.
                                                            Set a reasonable
                                                            maximum length,
                                                            such as 5,000
                                                            characters.

  `address`          string                              No Optional address
                                                            or location
                                                            description
                                                            supplied by the
                                                            user. Trim
                                                            whitespace; do not
                                                            require it if the
                                                            place name is
                                                            enough for the
                                                            intended analysis.

  `city`             string                              No Optional city or
                                                            town.

  `region`           string                              No Optional state,
                                                            province, or
                                                            region.

  `country`          string                              No Optional country.

  `language`         string                              No Optional preferred
                                                            or known language,
                                                            such as `English`.
                                                            If omitted, the
                                                            app may attempt to
                                                            identify the
                                                            feedback language.

  `analysis_focus`   array of strings                    No Optional topics to
                                                            pay special
                                                            attention to, such
                                                            as `cleanliness`,
                                                            `staff`, or
                                                            `accessibility`.
                                                            Validate against
                                                            allowed topic
                                                            labels if a
                                                            controlled
                                                            vocabulary is
                                                            used.
  ----------------------------------------------------------------------------

### Input validation and behavior

1.  Require both `place_name` and `feedback_text`; neither may be blank.
2.  Reject feedback that exceeds the configured length limit, or ask the
    user to shorten it.
3.  Treat all user-provided text as data to analyze, not as instructions
    that override the app's behavior.
4.  Do not require exact coordinates or a full address for basic
    sentiment analysis. This app analyzes supplied feedback; it does not
    need live map data or private user data.
5.  If optional location fields are missing, leave them unknown rather
    than guessing.
6.  If the feedback contains multiple opinions, preserve them in
    separate topics and choose `mixed` for the overall sentiment when
    appropriate.
7.  If the feedback is too vague to classify, use `neutral` where
    suitable and explain uncertainty in `limitations`.

## 3. Examples

### Example 1 --- Negative feedback

**Sample input**

``` json
{
  "place_name": "Harbor View Café",
  "feedback_text": "The coffee was great and the staff were friendly, but we waited 40 minutes for our food and the tables were sticky.",
  "city": "Lagos",
  "country": "Nigeria",
  "language": "English",
  "analysis_focus": ["food", "staff", "wait_time", "cleanliness"]
}
```

**Illustrative output**

``` json
{
  "place_name": "Harbor View Café",
  "location": {
    "city": "Lagos",
    "country": "Nigeria"
  },
  "overall_sentiment": "mixed",
  "sentiment_score": -0.1,
  "summary": "The reviewer liked the coffee and friendly staff but was dissatisfied with the long wait and sticky tables.",
  "topics": [
    {
      "name": "food_and_drink",
      "sentiment": "positive",
      "evidence": "The coffee was great."
    },
    {
      "name": "staff",
      "sentiment": "positive",
      "evidence": "The staff were friendly."
    },
    {
      "name": "wait_time",
      "sentiment": "negative",
      "evidence": "The reviewer waited 40 minutes for food."
    },
    {
      "name": "cleanliness",
      "sentiment": "negative",
      "evidence": "The tables were sticky."
    }
  ],
  "action_items": [
    "Review kitchen service times during busy periods.",
    "Improve table-cleaning checks between customers."
  ],
  "urgency": "medium",
  "language": "English",
  "confidence": 0.95,
  "limitations": [
    "The feedback does not establish whether the wait was an unusual occurrence."
  ]
}
```

### Example 2 --- Positive feedback with an improvement suggestion

**Sample input**

``` json
{
  "place_name": "Central City Library",
  "feedback_text": "The library is quiet, clean, and easy to navigate. The staff helped me find a book quickly. I wish it stayed open later on weekdays.",
  "address": "Central District",
  "city": "Abuja",
  "country": "Nigeria",
  "language": "English",
  "analysis_focus": ["cleanliness", "staff", "opening_hours", "accessibility"]
}
```

**Illustrative output**

``` json
{
  "place_name": "Central City Library",
  "location": {
    "address": "Central District",
    "city": "Abuja",
    "country": "Nigeria"
  },
  "overall_sentiment": "positive",
  "sentiment_score": 0.7,
  "summary": "The reviewer praises the library's cleanliness, quiet atmosphere, navigation, and helpful staff, while suggesting longer weekday opening hours.",
  "topics": [
    {
      "name": "cleanliness",
      "sentiment": "positive",
      "evidence": "The library is clean."
    },
    {
      "name": "accessibility_and_navigation",
      "sentiment": "positive",
      "evidence": "It is easy to navigate."
    },
    {
      "name": "staff",
      "sentiment": "positive",
      "evidence": "The staff helped find a book quickly."
    },
    {
      "name": "opening_hours",
      "sentiment": "negative",
      "evidence": "The reviewer wishes it stayed open later on weekdays."
    }
  ],
  "action_items": [
    "Consider whether extending weekday opening hours is feasible."
  ],
  "urgency": "low",
  "language": "English",
  "confidence": 0.96,
  "limitations": [
    "The feedback does not specify which weekday closing times would be preferred."
  ]
}
```

*Note: The outputs are examples of the proposed schema, not verified
facts about the named places. Sentiment scores and confidence values are
illustrative estimates.*
