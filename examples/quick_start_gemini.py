"""
Interactive chat example using GeminiAgent with conversation memory.
"""
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv

from moya.agents.gemini_filter_agent import create_filter_agent

if TYPE_CHECKING:
    from moya.agents.gemini_agent import GeminiAgent
from moya.orchestrators.simple_orchestrator import SimpleOrchestrator
from moya.registry.agent_registry import AgentRegistry
from moya.tools.ephemeral_memory import EphemeralMemory
from moya.tools.persistent_memory import PersistentEmbeddings
from moya.tools.tool_registry import ToolRegistry

# Configuration constants
PAPERS_FOLDER = "TSE-Project/research_papers"
EMBEDDINGS_FILE = "TSE-Project/enhanced_embeddings/chroma.sqlite3"
MODEL_NAME = "all-MiniLM-L6-v2"
GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_THREAD_ID = "gemini_conversation"
DEFAULT_AGENT_NAME = "filter_agent"
EXIT_COMMANDS = {"exit", "quit"}

load_dotenv()


def setup_memory_components() -> ToolRegistry:
    """
    Set up memory components and configure tools.

    Returns:
        ToolRegistry: Configured tool registry with memory tools.
    """
    tool_registry = ToolRegistry()
    EphemeralMemory.configure_memory_tools(tool_registry)
    PersistentEmbeddings.configure_persistent_tools(tool_registry)
    return tool_registry


def initialize_persistent_embeddings() -> None:
    """Initialize the persistent embeddings system."""
    try:
        PersistentEmbeddings.initialize(model_name=MODEL_NAME)
    except Exception as e:
        print(f"Error initializing persistent embeddings: {e}", file=sys.stderr)
        raise


def create_filter_agent_instance(tool_registry: ToolRegistry) -> "GeminiAgent":  # type: ignore
    """
    Create a filter agent instance for processing user queries.

    Args:
        tool_registry: The tool registry to use for the agent.

    Returns:
        GeminiAgent: Configured filter agent.
    """
    return create_filter_agent(
        tool_registry=tool_registry,
        model_name=GEMINI_MODEL,
        agent_name=DEFAULT_AGENT_NAME,
    )


def setup_orchestrator() -> SimpleOrchestrator:
    """
    Set up the multi-agent orchestrator with all components.

    Returns:
        SimpleOrchestrator: Configured orchestrator instance.

    Raises:
        Exception: If initialization fails.
    """
    try:
        # Initialize persistent embeddings
        initialize_persistent_embeddings()

        # Set up shared components
        tool_registry = setup_memory_components()

        # Create agents
        filter_agent = create_filter_agent_instance(tool_registry)

        # Set up agent registry
        registry = AgentRegistry()
        registry.register_agent(filter_agent)

        # Create the orchestrator
        orchestrator = SimpleOrchestrator(
            agent_registry=registry,
            default_agent_name=DEFAULT_AGENT_NAME,
        )

        return orchestrator
    except Exception as e:
        print(f"Error setting up orchestrator: {e}", file=sys.stderr)
        raise


def print_papers() -> None:
    """Print available papers and usage instructions."""
    papers_path = Path(PAPERS_FOLDER)
    print("\nAvailable papers:")
    print("-" * 50)
    if papers_path.exists():
        for i, paper in enumerate(papers_path.glob("*.pdf"), 1):
            print(f"{i}. {paper.name}")
    else:
        print("Papers folder not found!")

    print(
        "You may ask to summarise paper completely or section-wise, "
        "or ask for gaps in research papers."
    )
    print("\ntemplate: [paper-{i}] <query>\n")
    print("-" * 50)


def main() -> None:
    """Run an interactive chat session with the Gemini agent."""
    try:
        print_papers()

        orchestrator = setup_orchestrator()
        thread_id = DEFAULT_THREAD_ID

        print("Starting Gemini chat (type 'exit' to quit)")
        print("-" * 50)

        while True:
            user_message = input("\nYou: ").strip()

            if not user_message:
                continue

            if user_message.lower() in EXIT_COMMANDS:
                print("\nGoodbye!")
                break

            # Get available agents
            agents = orchestrator.agent_registry.list_agents()
            if not agents:
                print("\nNo agents available!")
                continue

            # Store user message
            try:
                EphemeralMemory.store_message(
                    thread_id=thread_id, sender="user", content=user_message
                )
            except Exception as e:
                print(f"\nError storing message: {e}", file=sys.stderr)
                continue

            # Get session summary (for potential future use)
            try:
                session_summary = EphemeralMemory.get_thread_summary(thread_id)
            except Exception as e:
                print(f"\nWarning: Could not get session summary: {e}", file=sys.stderr)
                session_summary = None

            # Get response from orchestrator
            print("\nAssistant: ", end="", flush=True)
            try:
                response = orchestrator.orchestrate(
                    thread_id=thread_id,
                    user_message=user_message,
                    stream_callback=None,
                )
                print(response)
                print()

                # Store assistant response
                EphemeralMemory.store_message(
                    thread_id=thread_id, sender="system", content=response
                )
            except Exception as e:
                print(f"\nError getting response: {e}", file=sys.stderr)
                continue

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
