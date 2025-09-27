from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, List
import google.generativeai as genai
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
import torch

load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Initialize embedding model (runs once)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

class ChatState(TypedDict):
    messages: List[str]
    document_chunks: List[str]  # New field

model = genai.GenerativeModel("gemini-2.0-flash-lite")

def retrieve_relevant_chunks(query: str, chunks: List[str], top_k: int = 3) -> str:
    if not chunks:
        return ""
    # Encode query and chunks
    query_emb = embedding_model.encode(query, convert_to_tensor=True)
    chunk_embs = embedding_model.encode(chunks, convert_to_tensor=True)
    # Compute cosine similarities
    cos_scores = util.cos_sim(query_emb, chunk_embs)[0]
    top_results = torch.topk(cos_scores, k=min(top_k, len(chunks)))
    relevant = [chunks[idx] for idx in top_results.indices]
    return "\n\n".join(relevant)

def bot_node(state: ChatState):
    user_message = state["messages"][-1]
    document_chunks = state.get("document_chunks", [])

    # Retrieve only relevant parts
    context = retrieve_relevant_chunks(user_message, document_chunks)

    if context:
        prompt = f"""You are an expert coding assistant. Use the following context to answer the question.
If the context doesn't contain the answer, say "I don't know based on the provided document."

Context:
{context}

Question: {user_message}

Answer:"""
    else:
        prompt = f"""You are an expert coding assistant. Answer the following question clearly and concisely.

Question: {user_message}

Answer:"""

    try:
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.3}  # Lower temp for factual answers
        )
        reply = (response.text or "⚠ No reply generated.").strip()
    except Exception as e:
        reply = f"⚠ Error: {e}"

    # Return updated state (append bot reply)
    return {
        "messages": state["messages"] + [reply],
        "document_chunks": document_chunks
    }

memory = MemorySaver()
graph = StateGraph(ChatState)
graph.add_node("bot", bot_node)
graph.set_entry_point("bot")
graph.add_edge("bot", END)

chat_app = graph.compile(checkpointer=memory)
