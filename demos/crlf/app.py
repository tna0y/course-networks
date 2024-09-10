import logging
from flask import Flask, request, render_template, url_for, Response
import os
import sqlite3

app = Flask(__name__, template_folder='templates')
UPLOAD_FOLDER = 'uploads'
DATABASE = 'files.db'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - Flask - %(levelname)s - %(message)s')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content_type TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/', methods=['GET'])
def index():
    logging.info("Rendering upload page")
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    content_type = request.form['content_type']
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO files (filename, content_type) VALUES (?, ?)', (file.filename, content_type))
            file_id = cursor.lastrowid
            conn.commit()

        logging.info(f"File uploaded successfully: {file.filename} with content type: {content_type}")
        file_url = f"http://127.0.0.1:8080/{file_id}"
        return render_template('success.html', url=file_url)

@app.route('/download/<int:file_id>', methods=['GET'])
def download_file(file_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT filename, content_type FROM files WHERE id = ?', (file_id,))
        row = cursor.fetchone()
        if row:
            filename, content_type = row
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(file_path, 'rb') as file:
                file_content = file.read()
            headers = {
                'Content-Type': content_type
            }
            logging.info(f"File downloaded successfully: {filename}")
            response = Response(file_content, status=200, headers=headers)
            return response
    logging.warning(f"File not found: {file_id}")
    return "File not found", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
