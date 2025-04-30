from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
import shutil

from dotenv import load_dotenv  # type: ignore

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure API key is provided
if not OPENAI_API_KEY:
    raise ValueError("API key is missing. Set the API_KEY environment variable.")

CHROMA_PATH = "chroma_db"
DATA_PATH = "D:/Lit-review-Automation/app_backend/txt_output"


def generate_data_store():
    documents = load_documents(DATA_PATH)
    save_to_chroma(documents)


def load_documents(data_path):
    # Helper function to update metadata with relative paths
    documents = []
    for filename in os.listdir(data_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(data_path, filename)
            loader = TextLoader(file_path, encoding="utf-8")
            doc = loader.load()[0]  # TextLoader returns a list; we assume one doc per file

            # Add file name as metadata
            doc.metadata["source"] = filename

            # Split this document individually (to avoid overlap)
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=8000, chunk_overlap=500
            )
            chunks = splitter.split_documents([doc])
            documents.extend(chunks)

    return documents


def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks,
        OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY,
            model="text-embedding-3-large",
        ),
        persist_directory=CHROMA_PATH,
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")


if __name__ == "__main__":
    generate_data_store()
