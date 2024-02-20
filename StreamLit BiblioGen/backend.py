from flask import Flask, request, jsonify
from langchain.vectorstores.chroma import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
import PyPDF2

import warnings
warnings.filterwarnings("ignore")

CHROMA_PATH = 'chroma'

# reading the openai api key from the file
with open("OPENAI_API_KEY.txt", "r") as f:
    OPENAI_API_KEY = f.read().strip()

# defining the function to answer the query
embedding_function = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)  # embedding function for the model
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)  # initializing the database from the chroma

app = Flask(__name__)

@app.route('/', methods=['POST'])
def answer_query():
    try:
        data = request.get_json()
        query_text = data.get('text', '')

        # Implement your logic here
        results = db.similarity_search_with_relevance_scores(query_text, k=1)

        if not results or results[0][1] < 0.8:
            return jsonify({"error": "Paper Not Found."}), 404

        meta_data_pdf = extract_metadata(results[0][0].metadata['source'])
        citation = ama_citation(meta_data_pdf)

        if not citation:
            return jsonify({"error": "Citation Not Found."}), 404
        else:
            return jsonify({"citation": citation}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

def extract_metadata(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfFileReader(pdf_file)
        metadata = reader.getDocumentInfo()
        return metadata

def ama_citation(metadata):
    author_list = metadata.get('/Author', '').split('; ')
    author_list = ', '.join(authors for authors in author_list if authors)
    
    title = metadata.get('/Title', '')
    year = metadata.get('/CreationDate', '').split(':')[1][:4]
    journal = metadata.get('/Subject', '').split(';')[0]
    doi = metadata.get('/DOI', '')
    
    ama_parts = [author_list, title, journal, year, doi]
    ama_parts = [part for part in ama_parts if part]
    ama_citation = '. '.join(ama_parts)
    
    return ama_citation

if __name__ == '__main__':
    app.run()
