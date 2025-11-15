import re
import os
from pypdf import PdfReader
from typing import List, Dict, Tuple, Any
import fitz
import chromadb
from chromadb.utils import embedding_functions
import sys

PDF_PATH = "./research_papers/Pranavasri et al. - 2024 - Exploratory Study of oneM2M-Based Interoperability Architectures for IoT A Smart City Perspective.pdf"
FOLDER_PATH = "./research_papers/"
PAPER_ID = "paper-1"
CHROMA_PATH = "./enhanced_embeddings"
TARGET_PAPER_ID = "paper-1"

SECTIONS_LIST = [
    'Abstract', 'Introduction', 'Motivation', 'Study Design and Execution', 'Results', 'Discussion',
    'Related Work', 'Conclusion', 'Future Work', 'Conclusion And Future Work', 'Refrences',
    'Background', 'Literature Review', 'Key Features Of a Tool', 'MLFlow: An Open Source Tool For ML Life Cycle Support',
    "Comparative Evaluation of Commerical Tools For ML Life Cycle Support", 'Methodology', 'Problem Description',
    'Experiements', 'Software Development Life Cycles', 'Acknowledgments', 'System Overview',
    'Basic Design Components', 'Service Placement Module', 'Implementation and Evaluation', 'Evaluation',
]

def _create_section_regex(sections: List[str]) -> re.Pattern:
    """Creates a robust regex pattern for matching section headers."""
    # 1. Escape special characters in titles and join them with OR
    escaped_sections = [re.escape(s.strip()) for s in sections if s.strip()]
    if not escaped_sections:
        return None

    # Sort titles by length descending to prioritize matching longer, more specific titles
    escaped_sections.sort(key=len, reverse=True)
    title_group = '|'.join(escaped_sections)

    # 2. Define the prefix pattern for numbering (e.g., 1., 2.1, I, II., A.)
    # This matches optional spaces, followed by common numbering patterns, and then optional space/dot
    numbering_prefix = r'(\s*(\d+(\.\d+)*|[IVXLCDM]+\.?|[A-Z]\.?)\s+)?'
    
    # 3. Combine to look for: Start of line -> Optional Numbering -> Section Title -> End of string
    pattern = r'^\s*' + numbering_prefix + r'(' + title_group + r')\s*$'
    
    # Use re.IGNORECASE for case-insensitive matching
    return re.compile(pattern, re.IGNORECASE)

def chunk_pdf_by_sections(
    filepath: str, 
    paper_id: str, 
    sections: List[str] = SECTIONS_LIST
) -> List[Dict[str, Any]]:
    """
    Reads a PDF, chunks its content based on predefined section titles, 
    and then sub-chunks those into 2000-word segments for embedding.
    
    Args:
        filepath: Path to the PDF file.
        paper_id: A unique identifier for the paper.
        sections: A list of predefined section titles to use as delimiters.
        
    Returns:
        A flat list of final, word-limited document chunks.
    """
    
    section_regex = _create_section_regex(sections)
    if not section_regex:
        print("Error: Section list is empty or could not create regex.")
        return []

    doc = fitz.open(filepath)
    section_boundaries: List[Dict[str, Any]] = []
    
    for page_num, page in enumerate(doc, start=1):
        text_blocks = page.get_text("blocks")
        
        for block_idx, block in enumerate(text_blocks):
            block_text = block[4].strip()
            
            for line in block_text.split('\n'):
                line = line.strip()
                
                match = section_regex.match(line)
                
                if match:
                    matched_title = ""
                    
                    for i in range(len(match.groups()), 0, -1):
                        if match.group(i) in sections:
                            matched_title = match.group(i).strip()
                            break

                    
                    if not matched_title:
                       
                        for section_name in sections:

                            title_search = re.search(re.escape(section_name), line, re.IGNORECASE)
                            if title_search:
                                matched_title = section_name.strip()
                                break


                    if matched_title and matched_title.lower() not in [h['section_category'].lower() for h in section_boundaries]:

                        section_boundaries.append({
                            'text': line,
                            'page': page_num,
                            'section_category': matched_title,
                            'block_idx': block_idx,
                            'line_start_idx': block_text.find(line)
                        })
                        break 

    doc.close()

    if not section_boundaries:
        doc = fitz.open(filepath)
        full_text = "".join(page.get_text() for page in doc)
        doc.close()
        return [{
            "chunk_text": full_text.strip(),
            "section_category": "Full Document",
            "page_number": 1,
            "paper_id": paper_id,
        }]
    
    semantic_chunks = []
    
    doc = fitz.open(filepath)
    all_blocks = []
    for page_num in range(1, doc.page_count + 1):
        page = doc[page_num - 1]
        blocks = page.get_text("blocks")
        for block in blocks:
            # Store (page_num, block_idx, block_text)
            all_blocks.append((page_num, block[4].strip()))
    doc.close()
    
    chunk_starts = []
    for boundary in section_boundaries:
        start_index = -1
        for i, (p_num, b_text) in enumerate(all_blocks):
            if p_num == boundary['page'] and boundary['text'].strip() in b_text.strip():
                start_index = i
                break
        
        if start_index != -1 and start_index not in [c['start_block_index'] for c in chunk_starts]:
            chunk_starts.append({
                'start_block_index': start_index,
                'section_category': boundary['section_category'],
                'page_number': boundary['page']
            })

    chunk_starts.sort(key=lambda x: x['start_block_index'])
    
    for i in range(len(chunk_starts)):
        start_meta = chunk_starts[i]
        start_index = start_meta['start_block_index']
        end_index = chunk_starts[i+1]['start_block_index'] if i + 1 < len(chunk_starts) else len(all_blocks)
        
        chunk_text_parts = [all_blocks[j][1] for j in range(start_index, end_index)]
        semantic_chunks.append({
            "chunk_text": "\n\n".join(chunk_text_parts).strip(),
            "section_category": start_meta['section_category'],
            "page_number": start_meta['page_number'],
            "paper_id": paper_id,
        })
        
    
    final_chunks = []
    WORD_LIMIT = 200
    
    for large_chunk in semantic_chunks:
        full_text = large_chunk['chunk_text']
        words = full_text.split()
        
        start_word_index = 0
        sub_chunk_count = 0
        
        while start_word_index < len(words):
            end_word_index = min(start_word_index + WORD_LIMIT, len(words))
            sub_chunk_words = words[start_word_index:end_word_index]
            sub_chunk_text = " ".join(sub_chunk_words).strip()
            
            if sub_chunk_text:
                sub_chunk_count += 1
                
                final_chunks.append({
                    "chunk_text": sub_chunk_text,
                    "section_category": large_chunk['section_category'],
                    "page_number": large_chunk['page_number'], 
                    "paper_id": large_chunk['paper_id'],
                    "sub_chunk_index": sub_chunk_count 
                })
            
            start_word_index = end_word_index
            
    return final_chunks

def get_pdf_text_for_demo(filepath: str) -> str:
    """Helper to extract initial text for demo."""
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text() + "\n--- Page Break ---\n"
        doc.close()
        return text
    except Exception as e:
        return f"Error reading PDF for demo: {e}"



# --- CHROMADB EMBEDDING FUNCTION ---
COLLECTION_NAME = "research_paper_sections"

def embed_chunks_to_chroma(chunks: List[Dict[str, Any]], paper_id = "paper-1"):
    """Initializes ChromaDB, creates or connects to a collection, and embeds the chunks."""
    
    print(f"Connecting to persistent ChromaDB at: {CHROMA_PATH}")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        embed_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    except Exception as e:
        print(f"Warning: Could not initialize SentenceTransformer. Fallback to basic. Error: {e}")
        # Use a simple mock function if SentenceTransformer is not available for a demo
        class MockEmbedFunc:
            def __call__(self, texts): return [[0.0] * 384 for _ in texts]
        embed_func = MockEmbedFunc()
    
    # Create or get the collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_func,
    )

    # Prepare data for ChromaDB format
    documents = [chunk['chunk_text'] for chunk in chunks]
    metadatas = [
        {
            "paper_id": chunk['paper_id'],
            "section_category": chunk['section_category'],
            "page_number": chunk['page_number'],
            "chunk_number": i
        }
        for i, chunk in enumerate(chunks)
    ]

    print(f"Adding {len(documents)} chunks to Chroma collection '{COLLECTION_NAME}'...")
    ids = [f"{PAPER_ID}-{i}-{chunk['section_category'].replace(' ', '_')}" for i, chunk in enumerate(chunks)]

    # Add data to ChromaDB
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"Successfully added {collection.count()} total documents (including previous ones) to the database.")
    print("Database is persistent and stored at: " + CHROMA_PATH)
    print("\n--- Example Chunk Metadata ---")
    if metadatas:
        print(metadatas[0])


# --- CHROMADB QUERY FUNCTION ---
def query_chroma_for_answer(query_text: str, where_filter: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Connects to the persistent ChromaDB and queries the collection,
    filtering results to a specific paper ID.
    """
    print(f"Connecting to persistent ChromaDB at: {CHROMA_PATH}")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        embed_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    except Exception as e:
        print(f"Warning: Could not initialize SentenceTransformer. Using mock embedding. Error: {e}")
        class MockEmbedFunc:
            def __call__(self, texts): return [[0.0] * 384 for _ in texts]
        embed_func = MockEmbedFunc()

    # Get the existing collection
    collection = client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_func
    )

    print(f"Querying collection '{COLLECTION_NAME}' for paper '{TARGET_PAPER_ID}'...")
    results = collection.query(
        query_texts=[query_text],
        n_results=3, # Retrieve top 3 most relevant chunks
        where=where_filter if where_filter is not None else {}
    )
    return results


if __name__ == "__main__":
    i = 1
    if not os.path.isdir(FOLDER_PATH):
        print(f"ERROR: Directory not found at path: {FOLDER_PATH}")
    else:
        for filename in os.listdir(FOLDER_PATH):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(FOLDER_PATH, filename)
                paper_id = "paper-" + str(i)
                print(f"\n--- Processing: {filename} ---")
                
                # 1. Chunk the PDF
                processed_chunks = chunk_pdf_by_sections(pdf_path, paper_id)
                
                if processed_chunks:
                    # 2. Embed and Store in ChromaDB
                    embed_chunks_to_chroma(processed_chunks, paper_id=paper_id)
                else:
                    print(f"No valid chunks were generated for {filename}. Check the PDF content and section list.")
                i = i+1

    # Example of how to query after embedding
    user_query = "Give a summary of introduction"
    working_filter = {
        "$and": [
            {"paper_id": TARGET_PAPER_ID},
            {"section_category": "Introduction"}
        ]
    }
    
    
    retrieval_results = query_chroma_for_answer(user_query, where_filter=working_filter)

    print("\n" + "="*70)
    print(f"| Retrieval Results for Query: '{user_query}'")
    print("="*70)

    if not retrieval_results['documents'] or not retrieval_results['documents'][0]:
        print("No documents found matching the query and filter criteria.")
    else:
        # Loop through the retrieved documents (chunks) and their metadata
        for i in range(len(retrieval_results['documents'][0])):
            doc_id = retrieval_results['ids'][0][i]
            metadata = retrieval_results['metadatas'][0][i]
            document_text = retrieval_results['documents'][0][i]
            distance = retrieval_results['distances'][0][i]

            print(f"\n--- Result {i+1} (Distance: {distance:.4f}) ---")
            print(f"Chunk ID: {doc_id}")
            print(f"Section: {metadata['section_category']}")
            print(f"Page: {metadata['page_number']}")
            print(f"Text Snippet:")
            print(document_text.replace('\n', ' '))
            print("-" * 20)
