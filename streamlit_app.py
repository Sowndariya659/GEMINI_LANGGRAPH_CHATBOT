import streamlit as st
import requests
import uuid
import io
from PyPDF2 import PdfReader
import textwrap

st.set_page_config(page_title="🧠 Coding Help Bot", layout="centered")
st.title("🧠 Coding Help Bot with Smart PDF Support")

# Initialize session state
if "history" not in st.session_state:
    st.session_state["history"] = []
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = str(uuid.uuid4())
if "document_chunks" not in st.session_state:
    st.session_state["document_chunks"] = []  # Will hold list of text chunks

def chunk_text(text, max_chunk_size=500):
    """Split text into overlapping chunks."""
    sentences = text.split(". ")
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


# Sidebar for file upload
with st.sidebar:
    st.header("📁 Upload Code/Doc PDF")
    uploaded_file = st.file_uploader("Choose a PDF (e.g., docs, tutorials, code guides)", type=["pdf"])
    if uploaded_file:
        try:
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            chunks = chunk_text(text)
            st.session_state["document_chunks"] = chunks
            st.success(f"✅ PDF loaded! ({len(chunks)} chunks)")
        except Exception as e:
            st.error(f"❌ Error reading PDF: {e}")
            st.session_state["document_chunks"] = []

# Chat input
user_input = st.chat_input("Ask a coding question...")

if user_input:
    # Always treat as coding question
    st.session_state["history"].append(("You", user_input))

    # Send to backend: include user question + chunks (backend will do retrieval)
    payload = {
        "user_message": user_input,
        "thread_id": st.session_state["thread_id"],
        "document_chunks": st.session_state["document_chunks"]  # Pass chunks to backend
    }

    try:
        resp = requests.post(
            "http://127.0.0.1:8000/chat",
            json=payload,
            timeout=45
        )
        resp.raise_for_status()
        bot_reply = resp.json()["response"]
    except Exception as e:
        bot_reply = f"⚠ Backend error: {e}"

    st.session_state["history"].append(("Bot", bot_reply))

# Display chat history
for sender, msg in st.session_state["history"]:
    with st.chat_message("user" if sender == "You" else "assistant"):
        st.markdown(msg)
