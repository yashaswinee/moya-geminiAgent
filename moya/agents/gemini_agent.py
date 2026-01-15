"""
GeminiAgent for Moya.

An Agent that uses Google's Gemini API to generate responses.
"""

import traceback
import google.generativeai as genai
from dataclasses import dataclass
from typing import Any, Dict, Optional
from moya.agents.agent import Agent, AgentConfig
from moya.agents.gemini_summarizer_agent import create_summarizer_prompt
from moya.agents.gemini_agent_helpers import (
    parse_filter_response,
    extract_filter_values,
    retrieve_documents_by_filter,
    perform_general_search,
    flatten_documents,
)


@dataclass
class GeminiAgentConfig(AgentConfig):
    """
    Configuration data for a GeminiAgent.
    """
    model_name: str = "gemini-2.5-flash"
    api_key: str = None
    generation_config: Optional[Dict[str, Any]] = None
    persistent_embeddings_tool: Any = None

class GeminiAgent(Agent):
    """
    A simple Google Gemini-based agent that uses the Gemini API.
    """

    def __init__(   
        self,
        config: GeminiAgentConfig
    ):
        """
        Initialize the GeminiAgent.

        :param config: Configuration for the agent.
        """
        super().__init__(config=config)
        self.model_name = config.model_name
        
        if not config.api_key:
            raise ValueError("Google API key is required for GeminiAgent.")
            
        # googlegenai initialization
        genai.configure(api_key=config.api_key)
        
        # generation config
        self.generation_config = config.generation_config or {
            "temperature": self.llm_config.get("temperature", 0.7),
            "top_p": self.llm_config.get("top_p", 1.0),
            "top_k": self.llm_config.get("top_k", 40),
            "max_output_tokens": self.llm_config.get("max_tokens", 2048),
        }
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config
        )
        self.system_prompt = config.system_prompt
        # conversation per thread id
        self.conversations = {}
        self.persistent_embeddings = config.persistent_embeddings_tool

    def setup(self) -> None:
        """
        Set up the agent (check API connectivity, etc.).
        """
        try:
            # api test
            response = self.model.generate_content("test")
            if not response:
                raise Exception("Unable to connect to Gemini API")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Gemini client: {str(e)}")

    def _get_conversation(self, thread_id, conversation_key="main"):
        """Get or create a conversation for a specific thread and key."""
        key = f"{thread_id}_{conversation_key}"
        if key not in self.conversations:
            convo = self.model.start_chat(history=[])
            self.conversations[key] = convo
        return self.conversations[key]

    def handle_message(self, message: str, **kwargs) -> str:
        """Generate answer from user message by extracting filters and summarizing documents."""
        thread_id = kwargs.get("thread_id", "default")
        
        try:
            # Step 1: Generate filter JSON from user message (use separate conversation)
            filter_prompt = f"""{self.system_prompt}, User Query: {message}"""
            filter_convo = self._get_conversation(thread_id, "filter")
            filter_response = filter_convo.send_message(filter_prompt)
            
            # Parse filter response
            filter_dict = parse_filter_response(filter_response.text)
            paper_ids, sections = extract_filter_values(filter_dict)
            
            # Step 2: Retrieve documents from ChromaDB using filters
            if paper_ids:
                all_doc_contents = retrieve_documents_by_filter(
                    self.persistent_embeddings, message, paper_ids, sections
                )
            else:
                print("No paper_ids specified, doing general search")
                all_doc_contents = perform_general_search(
                    self.persistent_embeddings, message
                )

            # Check if any content was found
            if not all_doc_contents:
                return "I couldn't find relevant information to answer your question."

            # Step 3: Generate final answer using retrieved documents (use separate conversation)
            context = flatten_documents(all_doc_contents)
            final_prompt = create_summarizer_prompt(context=context, user_query=message)
            
            # Use a separate conversation for the final answer to avoid filter JSON in history
            answer_convo = self._get_conversation(thread_id, "answer")
            answer_response = answer_convo.send_message(final_prompt)
            return answer_response.text

        except Exception as e:
            print(f"Filter agent error: {str(e)}")
            traceback.print_exc()
            return '{"$and": []}'

    def handle_message_stream(self, message: str, **kwargs):
        """
        Calls the Gemini API to handle the user's message with streaming support.
        """
        pass
