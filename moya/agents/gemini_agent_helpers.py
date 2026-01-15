"""
Helper functions for GeminiAgent.

Contains utility functions for parsing filters, extracting values,
and retrieving documents.
"""
import json
from typing import Any, Dict, List, Tuple


def parse_filter_response(response_text: str) -> Dict[str, Any]:
    """
    Parse filter JSON from Gemini response.

    Args:
        response_text: The raw text response from Gemini API.

    Returns:
        Dict containing parsed filter, or default empty filter on error.
    """
    filter_string = response_text.strip()
    filter_string = filter_string.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(filter_string)
    except json.JSONDecodeError:
        return {"$and": []}


def extract_filter_values(filter_dict: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Extract paper_ids and sections from filter dictionary.

    Args:
        filter_dict: The parsed filter dictionary.

    Returns:
        Tuple of (paper_ids, sections) lists.
    """
    paper_ids = [
        item.get("paper_id") 
        for item in filter_dict.get("$and", []) 
        if "paper_id" in item
    ]
    sections = [
        item.get("section_category") 
        for item in filter_dict.get("$and", []) 
        if "section_category" in item
    ]
    
    # Unwrap if wrapped in a list
    if paper_ids and isinstance(paper_ids[0], list):
        paper_ids = paper_ids[0]
    if sections and isinstance(sections[0], list):
        sections = sections[0]
        
    return paper_ids, sections


def retrieve_documents_by_filter(
    persistent_embeddings: Any,
    query: str,
    paper_ids: List[str],
    sections: List[str]
) -> List[Any]:
    """
    Retrieve documents based on paper_id and section filters.

    Args:
        persistent_embeddings: The persistent embeddings tool instance.
        query: The search query string.
        paper_ids: List of paper IDs to filter by.
        sections: List of section categories to filter by.

    Returns:
        List of retrieved document contents.
    """
    all_doc_contents = []
    
    for paper_id in paper_ids:
        for section in sections:
            try:
                retrieved_docs = persistent_embeddings.search_by_paper(
                    query=query,
                    paper_id=paper_id,
                    section_category=section,
                    k=3
                )
                all_doc_contents.append(retrieved_docs)
            except Exception as e:
                print(f"Error retrieving docs for {paper_id} ... {section}: {str(e)}")
                continue
    
    return all_doc_contents


def perform_general_search(persistent_embeddings: Any, query: str) -> List[Any]:
    """
    Perform general search when no paper_ids are specified.

    Args:
        persistent_embeddings: The persistent embeddings tool instance.
        query: The search query string.

    Returns:
        List of document contents from general search.
    """
    try:
        retrieved_docs = persistent_embeddings.search(query=query, k=5)
        docs_data = json.loads(retrieved_docs)
        return [result['content'] for result in docs_data.get('results', [])]
    except Exception as e:
        print(f"Error in general search: {str(e)}")
        return []


def flatten_documents(doc_contents: List[Any]) -> List[str]:
    """
    Flatten nested document lists into a single list of strings.

    Args:
        doc_contents: List of documents (may be nested).

    Returns:
        Flattened list of string documents.
    """
    flat_docs = []
    for item in doc_contents:
        if isinstance(item, list):
            flat_docs.extend([str(sub_item) for sub_item in item])
        else:
            flat_docs.append(str(item))
    return flat_docs
