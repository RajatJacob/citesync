# import the required libraries
from langchain.vectorstores.chroma import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from main import get_paper_details

CHROMA_PATH = "chroma"
PROMPT_TEMPLATE = """
Here is some information:

{context}

---------

Answer the question based on the above: {question}
"""

# with open("OPENAI_API_KEY.txt", "r") as f:
#     OPENAI_API_KEY = f.read().strip()

embedding_function = HuggingFaceBgeEmbeddings(
    model_name='sentence-transformers/all-MiniLM-L6-v2')
db = Chroma(persist_directory=CHROMA_PATH,
            embedding_function=embedding_function)


class CitationNotFound(BaseException):
    pass


def get_paper_details_from_path(file_path) -> dict:
    paper = get_paper_details(file_path=file_path)
    if paper is None:
        raise CitationNotFound
    publisher_node = paper.publisher.single()
    publisher = None if publisher_node is None else publisher_node.name
    author_names = [
        {
            'given_name': author_node.given_name,
            'family_name': author_node.family_name
        }
        for author_node in paper.authors
    ]
    return {
        'title': paper.title,
        'doi': paper.doi,
        'publisher': publisher,
        'year': paper.year,
        'month': paper.month,
        'authors': author_names,
        'subject': paper.subject
    }


def get_citation_from_path(file_path: str) -> str:
    details = get_paper_details_from_path(file_path=file_path)
    authors = ', '.join([
        ' '.join(
            filter(bool, [
                author.get('given_name'),
                author.get('family_name')
            ])
        ) for author in details.get('authors', [])])
    return '. '.join([
        authors, details['title'], details['subject'], str(
            details['year']), details['doi']
    ])


def get_source_paper(query_text: str) -> str:
    results = db.similarity_search_with_relevance_scores(query_text, k=2)
    print("RESULTS\n\n", results)
    if len(results) == 0 or results[0][1] < 0.3:
        raise CitationNotFound

    source = results[0][0].metadata['source']
    return source


def get_ama_citation(query_text) -> str:
    source = get_source_paper(query_text=query_text)
    return get_citation_from_path(source)
