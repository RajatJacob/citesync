from flask import Flask, request, jsonify
from langchain.vectorstores.chroma import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
import PyPDF2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Add CORS middleware

# declaring the path for the chroma database
CHROMA_PATH = "chroma"

# reading the openai api key from the file
with open("OPENAI_API_KEY.txt", "r") as f:
    OPENAI_API_KEY = f.read().strip()

# defining the function to answer the query
embedding_function = OpenAIEmbeddings(openai_api_key = OPENAI_API_KEY) # embedding function for the model
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function) # initializing the database from the chroma

def extract_metadata(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfFileReader(pdf_file)
        metadata = reader.getDocumentInfo()
        return metadata

def ama_citation(metadata):
    author_list = ''
    if '/Author' in metadata:
        authors = metadata['/Author'].split('; ')
        author_list = ', '.join(authors)
    
    title = metadata.get('/Title', '')
    year = metadata.get('/CreationDate', '').split(':')[1][:4]
    journal = metadata.get('/Subject', '').split(';')[0]
    doi = metadata.get('/DOI', '')
    
    ama_parts = [author_list, title, journal, year, doi]
    ama_parts = [part for part in ama_parts if part]
    ama_citation = '. '.join(ama_parts)
    
    return ama_citation

def answer_query(query_text):
    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=2) # searching the database for the query text and getting the top 2 results
    if len(results) == 0 or results[0][1] < 0.7: # if no results are found or the relevance score is less than 0.7
        return(f"Unable to find matching results. Ask another question.") # return the message - prevents hallucinations

    meta_data_pdf = extract_metadata(results[0][0].metadata['source'])
    citation = ama_citation(meta_data_pdf)
    response_text = f"Source Paper:\n{results[0][0].metadata['source']}\n\nCitation:\n{citation}"
    return response_text # returning the response from the model

@app.route('/run-script', methods=['POST'])
def run_script():
    data = request.json
    input_text = data['input']
    output = answer_query(input_text)
    return jsonify(output=output)

if __name__ == '__main__':
    app.run(debug=True)
