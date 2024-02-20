# importing the required libraries
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
import os
import shutil

from main import get_paper_details

# defining the paths for the existing data and the chroma database that will be created
CHROMA_PATH = "chroma"
DATA_PATH = "papers"

# defining the function to generate the data store - splitting data into chunks and saving to chroma


def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)

# defining the function to load the documents - loading the markdown files scraped from Wikipedia


def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.pdf")
    documents = loader.load()
    return documents


def load_documents_from_file(file_path: str):
    return PyPDFLoader(file_path).load()


def add_file_to_store(file_path: str):
    documents = load_documents_from_file(file_path=file_path)
    chunks = split_text(documents)
    paper = get_paper_details(file_path=file_path)
    if paper is None:
        raise ValueError('No paper')
    doi = paper.doi
    for chunk in chunks:
        chunk.metadata.update({'doi': doi})
    add_to_chroma(chunks)

# defining the function to split the text into chunks - size of the chunks is 300 characters with an overlap of 100 characters


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    # printing a sample chunk to see the content and metadata
    document = chunks[10]
    print(document.page_content)
    print(document.metadata)
    # returning the chunks generated
    return chunks


def add_to_chroma(chunks: list[Document]):
    with open('OPENAI_API_KEY.txt', 'r') as file:
        API_KEY = file.read().replace('\n', '')
    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(openai_api_key=API_KEY),
        persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

# defining the function to save the chunks to chroma


def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    print('Saving Chunks to Chroma...')
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    add_to_chroma(chunks)


if __name__ == "__main__":
    generate_data_store()
