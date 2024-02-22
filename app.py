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

    files = request.files.getlist("file")
    all_files = set([file.filename for file in files])
    success = set()
    for file in files:
        if file.filename == '':
            pass

        if file and file.filename and file.filename.endswith('.pdf'):
            file_path = 'papers/' + file.filename
            file.save(file_path)
            try:
                add_file_to_store(file_path=file_path)
                success.add(file.filename)
            except Exception:
                pass
    return jsonify({
        'successful': list(success),
        'failed': list(all_files-success)
    })


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
