"""
Interactive chat example using GeminiAgent with conversation memory.
"""
import os
from dotenv import load_dotenv
from moya.tools.ephemeral_memory import EphemeralMemory
from moya.memory.in_memory_repository import InMemoryRepository
from moya.tools.tool_registry import ToolRegistry
from moya.registry.agent_registry import AgentRegistry
from moya.classifiers.llm_classifier import LLMClassifier
from moya.orchestrators.simple_orchestrator import SimpleOrchestrator
from moya.agents.gemini_agent import GeminiAgent, GeminiAgentConfig
from moya.tools.persistent_memory import PersistentEmbeddings
from pathlib import Path


load_dotenv()
papers_folder = "TSE-Project/research_papers"
embeddings_file = "TSE-Project/enhanced_embeddings/chroma.sqlite3"
model_name = 'all-MiniLM-L6-v2'
gemini_model = 'gemini-2.5-flash'

def setup_memory_components():
    tool_registry = ToolRegistry()
    EphemeralMemory.configure_memory_tools(tool_registry)
    PersistentEmbeddings.configure_persistent_tools(tool_registry)
    return tool_registry

def initialize_persistent_embeddings():
    """Initialize the persistent embeddings system."""
    PersistentEmbeddings.initialize(
        model_name=model_name,
    )

def create_filter_agent(tool_registry: ToolRegistry) -> GeminiAgent:
    """Create filters based on user query."""
    system_prompt = """
        Your job is to create metadata filter given a user prompt. 
        
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


        Identify which section(s) the user is referring to. Match the relevant section name(s) from SECTIONS_LIST. Add each matched section as the value(s) of "section_category". If multiple sections are relevant, include all of them.


        If you cannot confidently determine the paper ID or section category from the query,
        → Return null.


        Interpretation Guidance
        Infer the section from user intent — e.g.:
        “summarize introduction” → "section_category": "Introduction"
        “what were the results” → "section_category": "Results"
        “limitations discussed” → "section_category": "Discussion" or "Conclusion"
        “overview of study” → "section_category": "Study Design and Execution" or "System Overview"
        "summarise the paper" → section category includes all the items section list

        Output Format: Return only a valid JSON-like Python dictionary in the specified structure or null.

    """

    agent_config = GeminiAgentConfig(
        agent_name="filter_agent",
        agent_type="Filter",
        description="Creates filter for searching relevant embeddings",
        tool_registry=tool_registry,
        model_name=gemini_model,
        system_prompt=system_prompt,
        api_key=os.getenv("GOOGLE_API_KEY"),
        persistent_embeddings_tool=PersistentEmbeddings
    )
    
    return GeminiAgent(config=agent_config)

def setup_orchestrator():
    """Set up the multi-agent orchestrator with all components."""
    
    # init persistent embeddings
    initialize_persistent_embeddings()
    
    # Set up shared components 
    tool_registry = setup_memory_components()
        
    # Create agents
    filter_agent = create_filter_agent(tool_registry)

    # Set up agent registry
    registry = AgentRegistry()
    registry.register_agent(filter_agent)
    
    # Create the orchestrator
    orchestrator = SimpleOrchestrator(
        agent_registry=registry,
        default_agent_name="filter_agent"
    )

    return orchestrator

def print_papers():
    papers_path = Path(papers_folder)
    print("\nAvailable papers:")
    print("-" * 50)
    if papers_path.exists():
        for i, paper in enumerate(papers_path.glob("*.pdf"), 1):
            print(f"{i}. {paper.name}")
    else:
        print("Papers folder not found!")
    
    print("You may ask to summarise paper completely or section-wise, or ask for gaps in research papers.")
    print("\ntemplate: [paper-{i}] <query>\n")
    print("-" * 50)

def main():
    """Run an interactive chat session with the Gemini agent."""
    print_papers()
    
    orchestrator = setup_orchestrator()
    thread_id = "gemini_conversation"
    
    print("Starting Gemini chat (type 'exit' to quit)")
    print("-" * 50)


    while True:
        user_message = input("\nYou: ").strip()
        
        if user_message.lower() == 'exit':
            print("\nGoodbye!")
            break

         # Get available agents
        agents = orchestrator.agent_registry.list_agents()
        if not agents:
            print("\nNo agents available!")
            continue
        

        # Get the last used agent or default to the first one
        last_agent = orchestrator.agent_registry.get_agent(agents[0].name)

        # Store user message first
        EphemeralMemory.store_message(thread_id=thread_id, sender="user", content=user_message) 

        session_summary = EphemeralMemory.get_thread_summary(thread_id)

        # Print Assistant prompt and get response
        print("\nAssistant: ", end="", flush=True)
        response = orchestrator.orchestrate(
            thread_id=thread_id,
            user_message=user_message,
            stream_callback=None
        )

        
        print(response)
        print()
        EphemeralMemory.store_message(thread_id=thread_id, sender="system", content=response)

        
if __name__ == "__main__":
    main()
