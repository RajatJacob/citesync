# import the required libraries
from langchain.vectorstores.chroma import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from main import get_paper_details

# declaring the path for the chroma database
CHROMA_PATH = "chroma"

# defining the prompt template
PROMPT_TEMPLATE = """
Here is some information:

{context}

---------

Answer the question based on the above: {question}
"""

# reading the openai api key from the file
with open("OPENAI_API_KEY.txt", "r") as f:
    OPENAI_API_KEY = f.read().strip()

# defining the function to answer the query
embedding_function = OpenAIEmbeddings(
    openai_api_key=OPENAI_API_KEY)  # embedding function for the model
# initializing the database from the chroma
db = Chroma(persist_directory=CHROMA_PATH,
            embedding_function=embedding_function)


def get_citation_from_path(file_path):
    paper = get_paper_details(file_path=file_path)
    if paper is None:
        return None
    return paper.doi


def answer_query(query_text) -> dict:
    # Search the DB.
    # searching the database for the query text and getting the top 2 results
    results = db.similarity_search_with_relevance_scores(query_text, k=2)
    # if no results are found or the relevance score is less than 0.7
    if len(results) == 0 or results[0][1] < 0.7:
        # return the message - prevents hallucinations
        return (f"Unable to find matching results. Ask another question.")

    source = results[0][0].metadata['source']
    return {
        'source_paper': source,
        'citation': get_citation_from_path(source)
    }
