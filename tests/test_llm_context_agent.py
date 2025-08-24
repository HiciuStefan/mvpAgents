
import sys
import os

# Add the project root to the Python path to solve ModuleNotFoundError
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
import json
from unittest.mock import patch, MagicMock

# It's important to patch the object where it's LOOKED UP, not where it's defined.
# The llm_context_agent module imports llm from its own namespace, so we patch it there.
LLM_OBJECT_TO_PATCH = "context.context_agent.llm_context_agent.llm"

# Mock data for the tests
MOCK_USER_CONTEXT = {"user": "test"}
MOCK_RAG_CONTEXT = "rag context"
MOCK_BATCH_CONTENT = [{"type": "email", "subject": "Test Email"}]

# This is a valid response from the LLM that should pass validation
VALID_LLM_RESPONSE = [
    {
        "original_item": {"type": "email", "subject": "Test Email"},
        "analysis": {
            "short_description": "Test",
            "actionable": True,
            "priority_level": "medium",
            "opportunity_type": "Client request",
            "suggested_action": "Review",
            "relevance": "A test item.",
            "suggested_reply": "This is a test reply."
        }
    }
]

# This response is invalid because it's missing the required 'priority_level' field
INVALID_LLM_RESPONSE = [
    {
        "original_item": {"type": "email", "subject": "Test Email"},
        "analysis": {
            "short_description": "Test",
            "actionable": True,
            # "priority_level" is missing
            "opportunity_type": "Client request",
            "suggested_action": "Review",
            "relevance": "A test item.",
            "suggested_reply": "This is a test reply."
        }
    }
]

@pytest.fixture(autouse=True)
def setup_llm_context_agent():
    # This fixture will run before each test function in this file
    # We need to import the function to be tested here, AFTER the patch context might be active
    global get_llm_analysis
    from context.context_agent.llm_context_agent import get_llm_analysis


@patch(LLM_OBJECT_TO_PATCH)
def test_get_llm_analysis_valid_json(mock_llm_invoke):
    """
    Tests the happy path where the LLM returns a valid JSON
    that passes Pydantic validation.
    """
    # Configure the mock to return a valid JSON string
    mock_response = MagicMock()
    mock_response.content = json.dumps(VALID_LLM_RESPONSE)
    mock_llm_invoke.invoke.return_value = mock_response

    # Call the function
    result = get_llm_analysis(MOCK_USER_CONTEXT, MOCK_RAG_CONTEXT, MOCK_BATCH_CONTENT)

    # Assertions
    assert isinstance(result, list)
    assert len(result) == 1
    # Check if a key from the analysis is present
    assert result[0]['analysis']['priority_level'] == 'medium'
    print("\n✅ Test with valid data passed.")


@patch(LLM_OBJECT_TO_PATCH)
def test_get_llm_analysis_invalid_pydantic_schema(mock_llm_invoke):
    """
    Tests the failure case where the LLM returns a JSON that is structurally
    valid but fails Pydantic schema validation (e.g., a field is missing).
    """
    # Configure the mock to return an invalid JSON string
    mock_response = MagicMock()
    mock_response.content = json.dumps(INVALID_LLM_RESPONSE)
    mock_llm_invoke.invoke.return_value = mock_response

    # Call the function
    result = get_llm_analysis(MOCK_USER_CONTEXT, MOCK_RAG_CONTEXT, MOCK_BATCH_CONTENT)

    # Assertions: The function should return an empty list on Pydantic validation failure
    assert result == []
    print("\n✅ Test with invalid data correctly returned an empty list.")

