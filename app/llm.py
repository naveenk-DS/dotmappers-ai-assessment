import json

import ollama

# Configuration

MODEL_NAME = "llama3.2"

SYSTEM_PROMPT = """
You are a natural-language query parser for a customer support ticket
analytics system.

Your job is ONLY to understand the user's question and convert it into
structured JSON.

Available columns:
- ticket_id
- created_at
- category
- priority
- status
- response_time_hrs
- resolution_time_hrs
- agent_id
- customer_rating
- issue_summary

Supported operations:
- COUNT
- AVERAGE
- SUM
- MIN
- MAX
- LIST
- GROUP_BY

Possible filter fields:
- category
- priority
- status
- agent_id

Possible metrics:
- response_time_hrs
- resolution_time_hrs
- customer_rating

Return ONLY valid JSON.

JSON format:

{
    "operation": "COUNT",
    "metric": null,
    "group_by": null,
    "filters": {},
    "time_period": null
}

Examples:

Question:
How many tickets are currently open?

Return:
{
    "operation": "COUNT",
    "metric": null,
    "group_by": null,
    "filters": {
        "status": "Open"
    },
    "time_period": null
}

Question:
What is the average customer rating for Technical category tickets?

Return:
{
    "operation": "AVERAGE",
    "metric": "customer_rating",
    "group_by": null,
    "filters": {
        "category": "Technical"
    },
    "time_period": null
}

Question:
Which agent has the lowest average customer rating?

Return:
{
    "operation": "AVERAGE",
    "metric": "customer_rating",
    "group_by": "agent_id",
    "filters": {},
    "time_period": null
}
"""

# Ollama Connection

def ask_llm(question: str) -> str:
 
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": question.strip(),
                },
            ],
        )
    except Exception as exc:
        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running and the model "
            f"'{MODEL_NAME}' is available."
        ) from exc

    return response["message"]["content"]


# ---------------------------------------------------------------------------
# JSON Parsing
# ---------------------------------------------------------------------------

def parse_llm_response(response: str) -> dict:

    if not response or not response.strip():
        raise ValueError("LLM returned an empty response.")

    cleaned_response = response.strip()

    # Remove markdown JSON code fences if the model adds them.
    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response[7:]

    elif cleaned_response.startswith("```"):
        cleaned_response = cleaned_response[3:]

    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3]

    cleaned_response = cleaned_response.strip()

    try:
        parsed = json.loads(cleaned_response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "LLM returned invalid JSON."
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError(
            "LLM response must be a JSON object."
        )

    return parsed


# ---------------------------------------------------------------------------
# Intent Validation
# ---------------------------------------------------------------------------

def validate_intent(intent: dict) -> dict:

    required_fields = [
        "operation",
        "metric",
        "group_by",
        "filters",
        "time_period",
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in intent
    ]

    if missing_fields:
        raise ValueError(
            "LLM response is missing fields: "
            + ", ".join(missing_fields)
        )

    allowed_operations = {
        "COUNT",
        "AVERAGE",
        "SUM",
        "MIN",
        "MAX",
        "LIST",
        "GROUP_BY",
    }

    operation = intent["operation"]

    if operation not in allowed_operations:
        raise ValueError(
            f"Unsupported operation returned by LLM: {operation}"
        )

    if not isinstance(intent["filters"], dict):
        raise ValueError(
            "LLM filters must be a JSON object."
        )

    return intent

# Main Query Understanding Function

def understand_question(question: str) -> dict:

    raw_response = ask_llm(question)

    intent = parse_llm_response(raw_response)

    validated_intent = validate_intent(intent)

    return validated_intent

# Local Test

if __name__ == "__main__":
    question = input("Enter your question: ").strip()

    try:
        intent = understand_question(question)

        print("\nLLM Intent:")
        print(json.dumps(intent, indent=4))

    except Exception as exc:
        print(f"\nError: {exc}")