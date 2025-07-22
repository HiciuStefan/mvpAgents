
import json
from jsonschema import validate, ValidationError

def validate_json(json_data, schema):
    """
    Validates a JSON object against a given schema.

    Args:
        json_data (dict): The JSON object to validate.
        schema (dict): The JSON schema to validate against.

    Returns:
        bool: True if the JSON is valid, False otherwise.
        str: A message indicating success or the validation error.
    """
    try:
        validate(instance=json_data, schema=schema)
        return True, "JSON is valid."
    except ValidationError as e:
        return False, f"JSON validation error: {e.message}"
