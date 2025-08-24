# Refactoring Plan for llm_context_agent.py

The `llm_context_agent.py` file is currently too large and handles multiple responsibilities, making it difficult to read, maintain, and test. This plan outlines a refactoring strategy to break it down into smaller, more focused modules.

## Current Structure Analysis

The file currently handles:
1.  **LLM Client Initialization:** Configures and creates the `AzureChatOpenAI` client.
2.  **Prompt Definition:** Contains large, hardcoded string constants for the system header and JSON instructions.
3.  **Core Logic (`get_llm_analysis`):**
    -   Prompt construction.
    -   LLM API call.
    -   Response parsing and validation (JSON extraction, Pydantic validation).
    -   Post-processing of results.
    -   Error handling.

## Proposed Refactoring

The proposal is to split the existing file into several specialized modules:

### 1. `prompts.py`
-   **Responsibility:** Store the large prompt text constants.
-   **Contents:**
    -   `SYSTEM_HEADER`
    -   `JSON_INSTRUCTIONS`
-   **Benefit:** Separates configuration (prompts) from logic, making prompts easier to manage.

### 2. `llm_client.py`
-   **Responsibility:** Handle the LLM client lifecycle.
-   **Contents:**
    -   A function (e.g., `get_llm_client()`) that initializes, configures, and returns the `AzureChatOpenAI` client instance.
-   **Benefit:** Centralizes LLM connection details, making it easy to change or configure the client in one place.

### 3. `response_parser.py`
-   **Responsibility:** Parse and validate the raw response from the LLM.
-   **Contents:**
    -   A function (e.g., `parse_and_validate_response(response_content: str) -> list`) that handles:
        -   Extracting the JSON string from the response (including regex fallbacks).
        -   Parsing the JSON string into Python objects.
        -   Validating the data against the `LLMOutputItem` Pydantic schema.
-   **Benefit:** Encapsulates the complex and error-prone parsing logic.

### 4. `post_processor.py`
-   **Responsibility:** Clean up and enrich the validated data.
-   **Contents:**
    -   A function (e.g., `post_process_results(results: list, original_batch: list) -> list`) that performs final checks and data completion (e.g., filling in default values for `suggested_action`).
-   **Benefit:** Isolates the business logic for data transformation.

### 5. `llm_context_agent.py` (Refactored)
-   **Responsibility:** Orchestrate the end-to-end process.
-   **Contents:**
    -   The main `get_llm_analysis` function will be significantly simplified. It will import and call functions from the new modules in the correct order:
        1.  Get the LLM client from `llm_client.py`.
        2.  Build the prompt using templates from `prompts.py`.
        3.  Call the LLM.
        4.  Parse the response using `response_parser.py`.
        5.  Post-process the results using `post_processor.py`.
        6.  Return the final, clean data.
-   **Benefit:** The main file becomes a high-level workflow, making the overall process much easier to understand at a glance.

## Summary of Benefits
-   **Improved Readability:** Each file will be short and have a clear purpose.
-   **Enhanced Maintainability:** Changes to one area (e.g., prompt adjustments) are isolated and less likely to break other parts of the system.
-   **Better Testability:** Each module can be unit-tested independently.
