from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
PAGES_FILE = '/data/pages.json'
UPLOAD_DIR = '/data/docs'
ALLOWED_EXT = {'.html', '.htm', '.pdf'}

os.makedirs(UPLOAD_DIR, exist_ok=True)

def load_pages():
    if not os.path.exists(PAGES_FILE):
        return []
    with open(PAGES_FILE, 'r') as f:
        return json.load(f)

def save_pages(pages):
    with open(PAGES_FILE, 'w') as f:
        json.dump(pages, f, indent=2)

@app.route('/api/pages', methods=['GET'])
def get_pages():
    return jsonify(load_pages())

@app.route('/api/pages', methods=['POST'])
def set_pages():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'expected array'}), 400
    save_pages(data)
    return jsonify({'ok': True})

@app.route('/api/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'no file'}), 400
    f = request.files['file']
    if not f.filename:
        return jsonify({'error': 'empty filename'}), 400
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        return jsonify({'error': f'not allowed: {ext}'}), 400
    # Sicherer Dateiname
    filename = os.path.basename(f.filename)
    filename = ''.join(c for c in filename if c.isalnum() or c in '._- ')
    dest = os.path.join(UPLOAD_DIR, filename)
    f.save(dest)
    return jsonify({'ok': True, 'path': f'./docs/{filename}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
