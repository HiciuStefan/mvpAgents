from pydantic import BaseModel, Field
from typing import Literal, Dict, Any, List

class AnalysisModel(BaseModel):
    """
    Pydantic model for the 'analysis' object returned by the LLM.
    """
    short_description: str = Field(
        ...,
        max_length=50,
        description="A short summary of the item (max 50 characters)."
    )
    actionable: bool = Field(
        ...,
        description="Set to true if the item is actionable, false otherwise."
    )
    priority_level: Literal["high", "medium", "low", "neutral"] = Field(
        ...,
        description="The priority level for the actionable item."
    )
    opportunity_type: str = Field(
        ...,
        description="For actionable items, the type of opportunity (e.g., 'New business opportunity')."
    )
    suggested_action: str = Field(
        ...,
        description="A concrete next step for actionable items."
    )
    relevance: str = Field(
        ...,
        max_length=100,
        description="Explanation of why the item is important (max 100 characters)."
    )
    suggested_reply: str = Field(
        ...,
        description="A draft reply for the item."
    )

class LLMOutputItem(BaseModel):
    """
    Pydantic model for a single item in the list returned by the LLM.
    """
    original_item: Dict[str, Any] = Field(
        ...,
        description="The full original item from the input array."
    )
    analysis: AnalysisModel = Field(
        ...,
        description="The analysis of the item provided by the LLM."
    )

# The final output from the LLM is a list of these items.
# You can validate a raw list of dictionaries from the LLM like this:
#
# from your_llm_module import get_llm_response
#
# raw_output = get_llm_response() # This is a list of dicts
# validated_output = [LLMOutputItem.model_validate(item) for item in raw_output]
#
