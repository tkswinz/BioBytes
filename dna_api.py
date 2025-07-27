from flask import Flask, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename
from fountaincodev2 import encode_image_to_dna, decode_dna_to_image
import tempfile

app = Flask(__name__)

@app.route('/encode', methods=['POST'])
def encode():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    image = request.files['image']
    chunk_size = int(request.form.get('chunk_size', 32))
    ecc_bytes = int(request.form.get('ecc_bytes', 10))
    redundancy_factor = float(request.form.get('redundancy_factor', 1.5))
    filename = secure_filename(image.filename)
    with tempfile.TemporaryDirectory() as tmpdir:
        image_path = os.path.join(tmpdir, filename)
        fasta_path = os.path.join(tmpdir, 'output.fasta')
        image.save(image_path)
        encode_image_to_dna(image_path, fasta_path, chunk_size, ecc_bytes, redundancy_factor)
        return send_file(fasta_path, as_attachment=True, download_name='dna_encoded.fasta')

@app.route('/decode', methods=['POST'])
def decode():
    if 'fasta' not in request.files:
        return jsonify({'error': 'No FASTA file provided'}), 400
    fasta = request.files['fasta']
    chunk_size = int(request.form.get('chunk_size', 32))
    num_chunks = int(request.form.get('num_chunks'))
    ecc_bytes = int(request.form.get('ecc_bytes', 10))
    filename = secure_filename(fasta.filename)
    with tempfile.TemporaryDirectory() as tmpdir:
        fasta_path = os.path.join(tmpdir, filename)
        image_path = os.path.join(tmpdir, 'decoded_image.jpg')
        fasta.save(fasta_path)
        success = decode_dna_to_image(fasta_path, image_path, chunk_size, num_chunks, ecc_bytes)
        if not success:
            return jsonify({'error': 'Decoding failed'}), 500
        return send_file(image_path, as_attachment=True, download_name='decoded_image.jpg')

if __name__ == '__main__':
    app.run(debug=True)
