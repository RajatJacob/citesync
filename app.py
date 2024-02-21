from citation import CitationNotFound, get_ama_citation
from flask import Flask, request, jsonify, render_template
from main import get_paper_details
from create_database import add_file_to_store
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.pdf'):
        # You can save the file to a location
        file_path = 'papers/' + file.filename
        file.save(file_path)
        try:
            get_paper_details(file_path=file_path)
            add_file_to_store(file_path=file_path)
        except Exception as e:
            print("ERROR", e)
            return jsonify({'error': 'Couldn\'t process PDF file.'}), 500
        return 'File uploaded successfully'
    else:
        return jsonify({
            'error': 'Invalid file format. Please upload a PDF file'
        }), 400


@app.route('/ama', methods=['GET'])
def ama():
    query = request.args.get('q')
    if query is None:
        return jsonify({'error': 'Please provide a valid query'}), 400
    try:
        citation = get_ama_citation(query)
    except CitationNotFound:
        return jsonify({'error': 'Citation not found!'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(citation)


if __name__ == "__main__":
    app.run(debug=True)
