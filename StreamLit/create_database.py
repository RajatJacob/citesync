# importing the required libraries
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
import os
import shutil

# defining the paths for the existing data and the chroma database that will be created
CHROMA_PATH = "chroma"
DATA_PATH = "Papers"

# defining the main function
def main():
    generate_data_store()

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


# defining the function to save the chunks to chroma
def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    print('Saving Chunks to Chroma...')
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    # reading the openai api key from the file
    with open('OPENAI_API_KEY.txt', 'r') as file:
        API_KEY = file.read().replace('\n', '')
    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(openai_api_key=API_KEY), persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")


if __name__ == "__main__":
    main()



