import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Constants
CHROMA_PATH = "chroma"
EMBEDDING_MODEL = "text-embedding-ada-002"  # Use older model for compatibility
LLM_MODEL = "gpt-4o-mini"  # Use appropriate model

def retrieve_info():
    """
    Set up and return a semantic search engine for research papers.
    Returns an enhanced index for RAG capabilities.
    """
    logger.info("Initializing semantic search capabilities...")
    
    # Initialize embedding function
    embedding_function = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=api_key
    )
    
    # Initialize Chroma DB with the embedding function
    try:
        db = Chroma(
            persist_directory=CHROMA_PATH, 
            embedding_function=embedding_function
        )
        logger.info(f"Successfully loaded vector store from {CHROMA_PATH}")
        
        # Create an enhanced retriever
        return EnhancedIndex(db)
        
    except Exception as e:
        logger.error(f"Error initializing ChromaDB: {str(e)}")
        raise

class EnhancedIndex:
    """Custom class to wrap the vector database with additional functionality"""
    
    def __init__(self, vector_db):
        self.vector_db = vector_db
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0,
            openai_api_key=api_key
        )
    
    def chat(self, query):
        """Handle chat interaction with semantic search capabilities"""
        from langchain.chains import ConversationalRetrievalChain
        from langchain.memory import ConversationBufferMemory
        
        # Configure the retriever with standard parameters
        retriever = self.vector_db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}  # Fixed number of results
        )
        
        # Initialize conversation memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"  # Explicitly set output key
        )
        
        # Create the chat engine with the configured retriever
        chat_engine = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,  # Include source documents
            output_key="answer"  # Explicitly set output key
        )
        
        # Get the response
        return chat_engine({"question": query})

if __name__ == "__main__":
    # Test the retriever directly
    retriever = retrieve_info()
    query = "What are the main topics in the research papers?"
    result = retriever.chat(query)
    
    print(f"Query: '{query}'")
    print(f"Response: {result.get('answer', 'No response')}")
    
    if "source_documents" in result:
        print(f"\nFound {len(result['source_documents'])} source documents:")
        for i, doc in enumerate(result["source_documents"]):
            print(f"\nDocument {i+1}:")
            print(f"Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"Content preview: {doc.page_content[:150]}...")