from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document  
from get_embedding_function import get_embedding_function
from langchain.vectorstores.chroma import Chroma
import argparse
import os
import shutil

CHROMA_PATH = "chroma"
DATA_PATH = "data"

def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()


def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80,length_function=len,is_separator_regex=False)
    return text_splitter.split_documents(documents)




def add_to_chroma(chunks: list[Document]):
    # Load the existing database
    db = Chroma(
        persist_directory=CHROMA_PATH, 
        embedding_function=get_embedding_function()
    )

    # Get all existing items
    existing_items = db.get(include=['metadatas'])
    existing_ids = set(existing_items["ids"])
    
    # Find which PDFs currently exist in the data directory
    current_pdfs = set(os.path.join(DATA_PATH, f) for f in os.listdir(DATA_PATH) if f.endswith('.pdf'))
    
    # Remove entries for PDFs that no longer exist
    ids_to_delete = []
    for idx, metadata in zip(existing_items["ids"], existing_items["metadatas"]):
        pdf_path = metadata.get("source")
        if pdf_path and pdf_path not in current_pdfs:
            ids_to_delete.append(idx)
    
    if ids_to_delete:
        print(f"Removing {len(ids_to_delete)} entries for deleted PDFs")
        db.delete(ids_to_delete)

    # Add new documents
    chunks_with_ids = calculate_chunk_ids(chunks)
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("No new documents to add")


def calculate_chunk_ids(chunks):

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    try:
        # First clear the data directory
        if os.path.exists(DATA_PATH):
            files = [f for f in os.listdir(DATA_PATH) if f.endswith('.pdf')]
            for file in files:
                os.remove(os.path.join(DATA_PATH, file))
            print(f"Removed {len(files)} PDF files from {DATA_PATH}")

        # Then clear the Chroma database
        if os.path.exists(CHROMA_PATH):
            # First delete all collections
            db = Chroma(
                persist_directory=CHROMA_PATH,
                embedding_function=get_embedding_function()
            )
            # Get collection name and delete it
            collection_name = db._collection.name
            db._client.delete_collection(name=collection_name)
            
            # Close the database connection
            db = None

            # Remove the database directory
            shutil.rmtree(CHROMA_PATH)
            
        return True
    except Exception as e:
        print(f"Error during database reset: {e}")
        return False


def main():

    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("Clearing Database")
        clear_database()

    # Create (or update) the data store.
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)


    
if __name__ == "__main__":
    main()