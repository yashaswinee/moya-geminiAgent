"""
Gemini Summarizer Agent constants and utilities.

Contains the summarizer prompt template and helper functions for creating
summarizer prompts with context.
"""
from typing import List, Any


# Summarizer prompt template
SUMMARIZER_PROMPT_TEMPLATE = (
    "You are an expert summariser. Use the provided context to answer the user's question.\n"
    "Context: {context}\n"
    "User Query: {user_query}"
)


def create_summarizer_prompt(context: List[Any], user_query: str) -> str:
    """
    Create a summarizer prompt with context and user query.

    Args:
        context: List of context strings or objects to summarize.
        user_query: The user's query/question.

    Returns:
        str: Formatted summarizer prompt.
    """
    # Convert context to string representation
    context_str = context if isinstance(context, str) else str(context)
    
    return SUMMARIZER_PROMPT_TEMPLATE.format(
        context=context_str,
        user_query=user_query
    )
