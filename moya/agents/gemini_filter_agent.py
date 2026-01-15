"""
Gemini Filter Agent configuration and utilities.

Contains the filter agent system prompt and helper functions for creating
filter agents that generate metadata filters from user queries.
"""
import os
from typing import Optional
from moya.agents.gemini_agent import GeminiAgent, GeminiAgentConfig
from moya.tools.persistent_memory import PersistentEmbeddings
from moya.tools.tool_registry import ToolRegistry
from dotenv import load_dotenv 

load_dotenv()

# Filter agent system prompt
FILTER_AGENT_SYSTEM_PROMPT = """Your job is to create metadata filter given a user prompt.

Use only the following predefined section names:
SECTIONS_LIST = [
    'Introduction', 'Motivation', 'Study Design and Execution', 'Results', 'Discussion',
    'Related Work', 'Conclusion', 'Future Work', 'Conclusion And Future Work', 'Refrences',
    'Background', 'Literature Review', 'Key Features Of a Tool', 'MLFlow: An Open Source Tool For ML Life Cycle Support',
    'Comparative Evaluation of Commerical Tools For ML Life Cycle Support', 'Methodology', 'Problem Description',
    'Experiements', 'Software Development Life Cycles', 'Acknowledgments', 'System Overview',
    'Basic Design Components', 'Service Placement Module', 'Implementation and Evaluation', 'Evaluation'
]

Given a user query, return a filter dictionary in the following format:
working_filter = {
    "$and": [
        {"paper_id": paper-x},
        {"section_category": section}
    ]
}

Paper ID Extraction
If the user query contains an explicit paper reference like [paper-1], [paper-2], etc.,
Extract that paper and use it as the value of "paper_id".
If no paper ID is mentioned or the query refers to all papers,
Set "paper_id" to a list of all papers: ["paper-1", "paper-2", "paper-3", "paper-4", "paper-5"].

Identify which section(s) the user is referring to. Match the relevant section name(s) from SECTIONS_LIST. 
Add each matched section as the value(s) of "section_category". If multiple sections are relevant, include all of them.

If you cannot confidently determine the paper ID or section category from the query,
→ Return null.

Interpretation Guidance
Infer the section from user intent — e.g.:
"summarize introduction" → "section_category": "Introduction"
"what were the results" → "section_category": "Results"
"limitations discussed" → "section_category": "Discussion" or "Conclusion"
"overview of study" → "section_category": "Study Design and Execution" or "System Overview"
"summarise the paper" → section category includes all the items section list

Output Format: Return only a valid JSON-like Python dictionary in the specified structure or null.
"""


def create_filter_agent(
    tool_registry: ToolRegistry,
    api_key: Optional[str] = os.getenv("GOOGLE_API_KEY"),
    model_name: str = "gemini-2.5-flash",
    agent_name: str = "filter_agent",
) -> GeminiAgent:
    """
    Create a filter agent for processing user queries.

    Args:
        tool_registry: The tool registry to use for the agent.
        api_key: Google API key. If not provided, will use GOOGLE_API_KEY env var.
        model_name: The Gemini model name to use.
        agent_name: The name for the agent.

    Returns:
        GeminiAgent: Configured filter agent.

    Raises:
        ValueError: If Google API key is not found.
    """
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")

    agent_config = GeminiAgentConfig(
        agent_name=agent_name,
        agent_type="Filter",
        description="Creates filter for searching relevant embeddings",
        tool_registry=tool_registry,
        model_name=model_name,
        system_prompt=FILTER_AGENT_SYSTEM_PROMPT,
        api_key=api_key,
        persistent_embeddings_tool=PersistentEmbeddings,
    )

    return GeminiAgent(config=agent_config)
