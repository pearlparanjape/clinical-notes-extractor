import json
from pydantic import ValidationError
from src.schemas import Demographics, Symptom

PROMPT_TEMPLATE = """Extract patient demographics from the clinical note below.

Return ONLY a JSON object with these exact fields:
- "sex": "male" or "female", or null if not stated
- "age": age in years as a number, or null if not stated
- "weight_kg": weight in kilograms as a number, or null if not stated
- "height_cm": height in centimeters as a number, or null if not stated
- "bmi": body mass index as a number, or null if not stated

Return nothing but the JSON — no explanation, no markdown fences.

Clinical note:
{note}
"""


def extract_demographics(note: str, client) -> dict:
    """Return a dict describing the outcome so failures can be surveyed:
    success -> {"status": "ok", "data": {...}}
    failure -> {"status": "error", "stage": ..., "error": ..., "raw": ...}
    """
    prompt = PROMPT_TEMPLATE.format(note=note)
    raw_response = client.complete(prompt)

    # clean markdown fences
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
        cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

    # parse JSON
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "stage": "json_parse",
            "error": str(e),
            "raw": raw_response,
        }

    # validate against schema
    try:
        demo = Demographics(**data)
        return {"status": "ok", "data": demo.model_dump()}
    except ValidationError as e:
        return {
            "status": "error",
            "stage": "validation",
            "error": str(e),
            "raw": raw_response,
        }


SYMPTOM_PROMPT_TEMPLATE = """Extract all symptoms from the clinical note below.

Return ONLY a JSON array (a list) of symptom objects. Each object must have:
- "name": the symptom, e.g. "chest pain"
- "negated": true if the note says the patient does NOT have it
   (e.g. "denies chest pain"), else false
- "explicit": false if inferred from a description
   (e.g. "winded walking" -> shortness of breath), else true
- "onset_or_duration": e.g. "3 days", or null if not stated
- "severity": "mild"/"moderate"/"severe", or null if not stated

If there are no symptoms, return an empty list: []
Return nothing but the JSON array — no explanation, no markdown fences.

Clinical note:
{note}
"""


def extract_symptoms(note: str, client) -> dict:
    """Extract a LIST of symptoms. Returns a structured result dict."""
    prompt = SYMPTOM_PROMPT_TEMPLATE.format(note=note)
    raw_response = client.complete(prompt)

    # clean markdown fences (robust)
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
        cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

    # parse JSON
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "stage": "json_parse",
            "error": str(e),
            "raw": raw_response,
        }

    # validate — data is a LIST, so validate each item
    try:
        symptoms = [Symptom(**item) for item in data]
        return {"status": "ok", "data": [s.model_dump() for s in symptoms]}
    except (ValidationError, TypeError) as e:
        return {
            "status": "error",
            "stage": "validation",
            "error": str(e),
            "raw": raw_response,
        }
