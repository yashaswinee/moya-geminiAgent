"""
GeminiAgent for Moya.

An Agent that uses Google's Gemini API to generate responses.
"""

import os
import re
import google.generativeai as genai
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Iterator
from moya.agents.agent import Agent, AgentConfig
import json
import google.generativeai as genai


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

    def _get_conversation(self, thread_id):
        """Get or create a conversation for a specific thread."""
        if thread_id not in self.conversations:
            convo = self.model.start_chat(history=[])
            self.conversations[thread_id] = convo
        return self.conversations[thread_id]

    def handle_message(self, message: str, **kwargs) -> str:
        """Generate filter JSON from user message."""
        thread_id = kwargs.get("thread_id", "default")
        
        try:            
            # Build prompt for filter generation
            filter_prompt = f"""{self.system_prompt}, User Query: {message}"""
            
            # Get conversation
            convo = self._get_conversation(thread_id)
            
            # Make Gemini API call
            response = convo.send_message(filter_prompt)
                        
            # Extract text from response
            filter_string = response.text.strip()
            
            # Clean up response (remove markdown code blocks if present)
            filter_string = filter_string.replace("```json", "").replace("```", "").strip()
            
            try:
                filter_dict = json.loads(filter_string)
            except json.JSONDecodeError:
                filter_dict = {"$and": []}
            
            
            # Extract paper_id and section_category from the parsed dict
            paper_ids = [item.get("paper_id") for item in filter_dict.get("$and", []) if "paper_id" in item]
            sections = [item.get("section_category") for item in filter_dict.get("$and", []) if "section_category" in item]
                        
            if type(sections[0]) == list:
                sections=sections[0]

            if type(paper_ids[0]) == list:
                paper_ids=paper_ids[0]

            # Collect all retrieved documents
            all_doc_contents = []

            # Loop through all paper_ids
            for paper_id in paper_ids:
                # Loop through all sections for each paper
                for section in sections:
                    try:
                        
                        retrieved_docs = self.persistent_embeddings.search_by_paper(
                            query=message,
                            paper_id=paper_id,
                            section_category=section,
                            k=3
                        )

                        # Add to collection
                        all_doc_contents.append(retrieved_docs)
                        
                    except Exception as e:
                        print(f"Error retrieving docs for {paper_id} ... {section}: {str(e)}")
                        continue            
                            
            # If no papers/sections specified, do a general search
            if not paper_ids:
                print("No paper_ids specified, doing general search")
                try:
                    retrieved_docs = self.persistent_embeddings.search(
                        query=message,
                        k=5
                    )
                    docs_data = json.loads(retrieved_docs)
                    doc_contents = [result['content'] for result in docs_data.get('results', [])]
                    all_doc_contents.extend(doc_contents)
                except Exception as e:
                    print(f"Error in general search: {str(e)}")

            # Check if any content
            if not all_doc_contents:
                return "I couldn't find relevant information to answer your question."


            # Flatten the list of documents if it's a list of lists
            flat_docs = []
            for item in all_doc_contents:
                if isinstance(item, list):
                    # Assuming the items inside the inner list are strings or can be converted to strings
                    string_items = [str(sub_item) for sub_item in item]
                    flat_docs.extend(string_items)
                else:
                    # Assuming the item itself is a string or can be converted to one
                    flat_docs.append(str(item))

            all_doc_contents = flat_docs
            
            context = all_doc_contents

            
            # final prompt
            final_prompt = (
                f"You are an expert summariser. Use the provided context to answer the user's question.\n"
                f"Context: {context}\n"
                f"User Query: {message}"
            )

            # Get conversation and send message
            convo = self._get_conversation(thread_id) 
            response = convo.send_message(final_prompt)
                                
            return response.text

        except Exception as e:
            print(f"Filter agent error: {str(e)}")
            import traceback
            traceback.print_exc()
            return '{"$and": []}'

    def handle_message_stream(self, message: str, **kwargs):
        """
        Calls the Gemini API to handle the user's message with streaming support.
        """
        pass
