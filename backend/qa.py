import os
import numpy as np
from typing import List, Dict, Any
import openai
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()

# Set OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

def build_embeddings(texts: List[str]) -> List[np.ndarray]:
    """
    Generate embeddings for a list of texts.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors
    """
    try:
        # If OpenAI API key is available, use it
        if openai.api_key:
            try:
                embeddings = []
                for text in texts:
                    response = openai.embeddings.create(
                        input=text,
                        model="text-embedding-ada-002"
                    )
                    embeddings.append(response.data[0].embedding)
                return embeddings
            except Exception as e:
                print(f"OpenAI API error in embeddings: {e}")
                # Fall back to placeholder implementation
        
        # Placeholder implementation - returns random vectors
        print("Using placeholder embeddings (random vectors)")
        return [np.random.rand(384) for _ in texts]
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return [np.zeros(384) for _ in texts]  # Return zero vectors on error

def semantic_search(query: str, embeddings: List[np.ndarray], top_k: int = 3) -> List[int]:
    """
    Find the most relevant clauses for a given query using semantic search.
    
    Args:
        query: The user's question
        embeddings: List of clause embeddings
        top_k: Number of top results to return
        
    Returns:
        Indices of the top_k most relevant clauses
    """
    try:
        # If OpenAI API key is available, use it
        if openai.api_key:
            try:
                response = openai.embeddings.create(
                    input=query,
                    model="text-embedding-ada-002"
                )
                query_embedding = response.data[0].embedding
            except Exception as e:
                print(f"OpenAI API error in query embedding: {e}")
                # Fall back to placeholder implementation
                query_embedding = np.random.rand(384)
        else:
            # Placeholder implementation - random query vector
            print("Using placeholder query embedding (random vector)")
            query_embedding = np.random.rand(384)
        
        # Convert embeddings to numpy arrays if they aren't already
        embeddings_array = np.array([np.array(emb) for emb in embeddings])
        
        # Calculate cosine similarity between query and all clauses
        similarities = cosine_similarity([query_embedding], embeddings_array)[0]
        
        # Get indices of top_k most similar clauses
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return top_indices.tolist()
    except Exception as e:
        print(f"Error in semantic search: {e}")
        # Return first few indices as fallback
        return list(range(min(top_k, len(embeddings))))

def generate_answer(question: str, relevant_clauses: List[Dict[str, Any]]) -> str:
    """
    Generate an answer to the user's question based on relevant clauses.
    
    Args:
        question: The user's question
        relevant_clauses: List of relevant clause dictionaries
        
    Returns:
        Generated answer
    """
    try:
        # Prepare context from relevant clauses
        context = "\n\n".join([
            f"Clause {clause['clause_id']}:\n{clause['original_text']}\nSummary: {clause['summary']}"
            for clause in relevant_clauses
        ])
        
        # If OpenAI API key is available, use it
        if openai.api_key:
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a legal assistant. Answer the user's question based on the provided legal clauses. Reference specific clauses in your answer."},
                        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
                    ],
                    max_tokens=300
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI API error in answer generation: {e}")
                # Fall back to heuristic implementation
        
        # Placeholder implementation
        clause_ids = [clause["clause_id"] for clause in relevant_clauses]
        return f"Based on {', '.join(clause_ids)}, the answer to your question '{question}' would involve analyzing the relevant legal provisions. Please refer to these clauses for more information."
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "I'm unable to answer this question at the moment. Please try again later."

# Optional: Add a vector database implementation
# This is a simple in-memory implementation, but you could use FAISS or ChromaDB
class SimpleVectorDB:
    def __init__(self):
        self.vectors = []
        self.metadata = []
    
    def add_vectors(self, vectors: List[np.ndarray], metadata: List[Dict[str, Any]]):
        self.vectors.extend(vectors)
        self.metadata.extend(metadata)
    
    def search(self, query_vector: np.ndarray, top_k: int = 3) -> List[Dict[str, Any]]:
        similarities = cosine_similarity([query_vector], self.vectors)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [self.metadata[i] for i in top_indices]