import os
import streamlit as st
from dotenv import load_dotenv
import traceback
import json
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Path for storing chat history
CHAT_HISTORY_DIR = "chat_history"
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
CHAT_HISTORY_FILE = os.path.join(CHAT_HISTORY_DIR, "chat_history.json")

# Functions for chat history persistence
def save_chat_history(messages):
    """Save chat history to a JSON file"""
    data = {
        "messages": messages,
        "last_updated": datetime.now().isoformat()
    }
    try:
        with open(CHAT_HISTORY_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving chat history: {str(e)}")

def load_chat_history():
    """Load chat history from a JSON file"""
    default_message = [{"role": "assistant", "content": "Hello! I'm your research assistant. Ask me questions..."}]
    
    if not os.path.exists(CHAT_HISTORY_FILE):
        return default_message
    
    try:
        with open(CHAT_HISTORY_FILE, 'r') as f:
            data = json.load(f)
            messages = data.get("messages", [])
            if not messages:
                return default_message
            return messages
    except Exception as e:
        st.error(f"Error loading chat history: {str(e)}")
        return default_message

try:
    # Check if database exists
    storage_path = "./chroma"
    if not os.path.exists(storage_path):
        st.warning("No vector database found. Please place documents in the 'documents' folder and build the database.")
        
        if st.button("Build Database"):
            with st.spinner("Processing documents and building index..."):
                try:
                    from DB.create_db import generate_data_store
                    generate_data_store()
                    st.success("Database built successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error building database: {str(e)}")
                    st.code(traceback.format_exc())
                    st.stop()
    else:
        # Initialize the RAG system
        from RAG.rag import retrieve_info
        
        # Initialize the index
        with st.spinner("Loading knowledge base..."):
            index = retrieve_info()
        
        # Streamlit application
        st.title("LIT Review System")

        # Sidebar for configuration
        with st.sidebar:
            st.header("Settings")
            show_sources = st.checkbox("Show Sources", value=True)
            
            if st.button("Clear Chat History"):
                st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]
                save_chat_history(st.session_state.messages)
                st.rerun()

        # Initialize chat history from persistent storage
        if "messages" not in st.session_state:
            st.session_state.messages = load_chat_history()

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # User input
        prompt = st.chat_input("Ask a question about your DOCs")

        # Display function for sources
        def display_sources(response):
            if not show_sources:
                return
                
            source_docs = response.get("source_documents", [])
            if not source_docs:
                return
            
            st.markdown("### Sources")
            
            for i, doc in enumerate(source_docs):
                source = doc.metadata.get('source', 'Unknown source')
                source_name = os.path.basename(source)
                
                with st.expander(f"Source {i+1}: {source_name}"):
                    # Show relevant text snippet
                    st.markdown("#### Relevant passage:")
                    st.markdown(doc.page_content)
                    
                    # Add download button for the full document if it exists
                    # Use a unique key for each download button based on source and index
                    button_key = f"download_{i}_{source_name.replace('.', '_')}"
                    
                    if os.path.exists(source):
                        with open(source, "rb") as file:
                            btn = st.download_button(
                                label=f"Download {source_name}",
                                data=file,
                                file_name=source_name,
                                mime="application/octet-stream",
                                key=button_key
                            )

        # Process user input
        if prompt:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Save chat history immediately
            save_chat_history(st.session_state.messages)
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
                
            # Generate assistant response
            with st.chat_message("assistant"):
                with st.spinner("Researching..."):
                    try:
                        # Get response from the chat engine
                        response = index.chat(prompt)
                        
                        # Extract the answer
                        answer = response.get('answer', 'I could not find an answer in the provided docs.')
                        st.write(answer)
                        
                        # Show sources if enabled
                        display_sources(response)
                        
                        # Add response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        # Save updated chat history
                        save_chat_history(st.session_state.messages)
                        
                    except Exception as e:
                        error_msg = f"Error generating response: {str(e)}"
                        st.error(error_msg)
                        st.code(traceback.format_exc())
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        # Save chat history with error message
                        save_chat_history(st.session_state.messages)

        # Add footer
        st.markdown("---")
        st.caption("Research Paper RAG powered by LangChain, ChromaDB and LLama3")

        # Sidebar info about chat persistence
        with st.sidebar:
            st.markdown("---")
            if os.path.exists(CHAT_HISTORY_FILE):
                try:
                    with open(CHAT_HISTORY_FILE, 'r') as f:
                        data = json.load(f)
                        last_updated = data.get("last_updated", "Unknown")
                        st.caption(f"Chat history last saved: {last_updated}")
                        message_count = len(data.get("messages", []))
                        st.caption(f"Total messages: {message_count}")
                except:
                    pass

except Exception as e:
    st.error(f"Application Error: {str(e)}")
    st.code(traceback.format_exc())