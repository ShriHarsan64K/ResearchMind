import chromadb
from chromadb.utils import embedding_functions
import os
import json
from datetime import datetime


# Initialize ChromaDB — stores everything locally in data/vectordb folder
def get_client():
    """Get ChromaDB client with local persistent storage."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'vectordb')
    os.makedirs(db_path, exist_ok=True)
    return chromadb.PersistentClient(path=db_path)


def get_collection():
    """Get or create the papers collection."""
    client = get_client()
    
    # Use sentence transformers for embeddings — runs locally, no API needed
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    collection = client.get_or_create_collection(
        name="research_papers",
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )
    
    return collection


def add_paper(paper_id: str, metadata: dict, sections: dict, brief: dict):
    """Add a paper to the vector store."""
    collection = get_collection()
    
    # Combine key text for embedding
    text_to_embed = f"""
    Title: {metadata.get('title', '')}
    Abstract: {sections.get('abstract', '')}
    Summary: {brief.get('summary', '')}
    Contributions: {brief.get('contributions', '')}
    Gaps: {brief.get('knowledge_gaps', '')}
    """
    
    # Truncate to avoid token limits
    text_to_embed = text_to_embed[:4000]
    
    # Store metadata
    stored_metadata = {
        "title": metadata.get("title", "Unknown"),
        "author": metadata.get("author", "Unknown"),
        "filename": metadata.get("filename", ""),
        "added_date": datetime.now().isoformat(),
        "word_count": str(sections.get("word_count", 0)),
        "summary": brief.get("summary", "")[:500],
        "gaps": brief.get("knowledge_gaps", "")[:500],
    }
    
    # Check if paper already exists
    existing = collection.get(ids=[paper_id])
    if existing["ids"]:
        print(f"Paper already exists: {metadata.get('title')}")
        return False
    
    collection.add(
        documents=[text_to_embed],
        metadatas=[stored_metadata],
        ids=[paper_id]
    )
    
    print(f"Added paper: {metadata.get('title')}")
    return True


def search_papers(query: str, n_results: int = 5) -> list:
    """Search for papers similar to query."""
    collection = get_collection()
    
    # Check if collection has any papers
    count = collection.count()
    if count == 0:
        return []
    
    # Limit results to available papers
    n_results = min(n_results, count)
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    papers = []
    if results["ids"] and results["ids"][0]:
        for i, paper_id in enumerate(results["ids"][0]):
            papers.append({
                "id": paper_id,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if results.get("distances") else 0
            })
    
    return papers


def get_all_papers() -> list:
    """Get all papers in the vector store."""
    collection = get_collection()
    
    count = collection.count()
    if count == 0:
        return []
    
    results = collection.get()
    
    papers = []
    for i, paper_id in enumerate(results["ids"]):
        papers.append({
            "id": paper_id,
            "metadata": results["metadatas"][i]
        })
    
    return papers


def get_paper_by_id(paper_id: str) -> dict:
    """Get a specific paper by ID."""
    collection = get_collection()
    
    result = collection.get(ids=[paper_id])
    
    if not result["ids"]:
        return None
    
    return {
        "id": result["ids"][0],
        "metadata": result["metadatas"][0],
        "document": result["documents"][0]
    }


def delete_paper(paper_id: str) -> bool:
    """Delete a paper from the vector store."""
    collection = get_collection()
    
    try:
        collection.delete(ids=[paper_id])
        print(f"Deleted paper: {paper_id}")
        return True
    except Exception as e:
        print(f"Error deleting paper: {e}")
        return False


def get_paper_count() -> int:
    """Get total number of papers stored."""
    collection = get_collection()
    return collection.count()


# Test it directly
if __name__ == "__main__":
    print("Testing Vector Store...")
    
    # Test adding a paper
    test_metadata = {
        "title": "Test Paper on Deep Learning",
        "author": "Test Author",
        "filename": "test.pdf"
    }
    
    test_sections = {
        "abstract": "This is a test paper about deep learning and neural networks.",
        "full_text": "Deep learning has revolutionized AI research.",
        "word_count": 100
    }
    
    test_brief = {
        "summary": "A paper about deep learning methods.",
        "knowledge_gaps": "Real-time processing needs improvement.",
        "contributions": "Novel neural network architecture proposed."
    }
    
    # Add test paper
    add_paper("test_001", test_metadata, test_sections, test_brief)
    
    # Search
    print("\nSearching for 'neural networks'...")
    results = search_papers("neural networks")
    for r in results:
        print(f"  Found: {r['metadata']['title']}")
    
    # Count
    print(f"\nTotal papers: {get_paper_count()}")
    
    print("\n✅ Vector Store working!")