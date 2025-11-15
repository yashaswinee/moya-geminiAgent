"""
PersistentEmbeddings for Moya.

A tool that interacts with ChromaDB to store and retrieve
document embeddings for semantic search and retrieval.
"""

from typing import Optional, List, Dict, Any
from moya.tools.tool_registry import ToolRegistry
from moya.tools.tool import Tool
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import chromadb
from pathlib import Path
import json
from chromadb.utils import embedding_functions


CHROMA_PATH = "./TSE-Project/enhanced_embeddings"
COLLECTION_NAME = "research_paper_sections"

class PersistentEmbeddings:
    """
    Provides persistent embedding operations, including:
      - Storing document chunks with embeddings
      - Retrieving relevant documents via semantic search
      - Managing multiple collections
    """

    _vectorstore: Optional[Chroma] = None
    _embeddings: Optional[HuggingFaceEmbeddings] = None
    _client: Optional[chromadb.PersistentClient] = None
    _model_name: str = 'all-MiniLM-L6-v2'
    _chroma_embed_func: Optional[embedding_functions.SentenceTransformerEmbeddingFunction] = None


    @classmethod
    def initialize(
        cls, 
        model_name: str = _model_name, 
        ) -> None:
        
        """Initializes the Chroma Client, Embeddings, and VectorStore."""
        # Ensure the ChromaDB path exists
        chroma_path = Path(CHROMA_PATH)
        if not chroma_path.is_dir():
            raise FileNotFoundError(
            f"ChromaDB path not found: {chroma_path.resolve()}. "
            "Please ensure the path is correct and the directory exists."
        )
        
        cls._embeddings_folder = CHROMA_PATH
        cls._model_name = model_name
                
        # Initialize embeddings model
        cls._embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        cls._chroma_embed_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=model_name
        )

        # Initialize ChromaDB client
        cls._client = chromadb.PersistentClient(path=cls._embeddings_folder)
        
        cls._vectorstore = Chroma(
            client=cls._client,
            collection_name=COLLECTION_NAME,
            embedding_function=cls._embeddings
        )
        
        try:
            cls._client.get_collection(name=COLLECTION_NAME)
        except ValueError:
            print(f"Collection '{COLLECTION_NAME}' not found. It will be created.")
            
        
    # --- CHROMADB QUERY FUNCTION ---
    @classmethod
    def query_chroma_for_answer(
        cls, 
        query_text: str, 
        where_filter: Dict[str, Any] = None, 
        k: int = 3
    ) -> Dict[str, Any]:
        """
        Connects to the persistent ChromaDB and queries the collection,
        filtering results to a specific paper ID.
        """

        # Get the existing collection
        collection = cls._client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=cls._chroma_embed_func
        )
        
        results = collection.query(
            query_texts=[query_text],
            n_results=k,
            where=where_filter,
            include=['documents', 'metadatas']
        )
        
        return results


    @staticmethod
    def search_by_paper(
        query: str, 
        paper_id: str | List[str], 
        section_category: str | List[str], 
        k: int = 5) -> str:
        """
        Searches the embeddings with filter conditions and returns a list of context strings.

        :param query: The natural language search query.
        :param paper_id: The extracted paper ID or list of IDs (e.g., ["paper-1"]).
        :param section_category: The extracted section name(s) (e.g., ["Introduction"]).
        :param k: The number of results to retrieve.
        :return: A list of relevant document content strings.
        """

        where_filter = {
            "$and": [
                {"paper_id": paper_id},
                {"section_category": section_category}
            ]
        }
        
        results = PersistentEmbeddings.query_chroma_for_answer(query, where_filter=where_filter, k=k)        
        results_updated = results.get('documents', [[]])

        return results_updated[0]
    

    @staticmethod
    def configure_persistent_tools(tool_registry: ToolRegistry) -> None:
        """
        Register the PersistentEmbeddings tools with the tool registry.

        Parameters:
            - tool_registry: The tool registry to register tools with
        """
        tool_registry.register_tool(Tool(
            name = "search_by_paper",
            function=PersistentEmbeddings.search_by_paper
        ))
        
        