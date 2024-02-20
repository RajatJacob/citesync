from flask import Flask, request, jsonify, render_template
from main import get_paper_details

app = Flask(__name__)


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
        except:
            return jsonify({'error': 'Couldn\'t process PDF file.'}), 500
        return 'File uploaded successfully'
    else:
        return jsonify({
            'error': 'Invalid file format. Please upload a PDF file'
        }), 400
