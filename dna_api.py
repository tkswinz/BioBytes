from flask import Flask, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename
from fountaincodev2 import addECCInDroplets, encode_image_to_dna, decode_dna_to_image, image_to_binary, writeCompressedBinary, fountain_encode, compressAndEncode, add_error_correction, encode_droplets_to_dna, save_dna_to_fasta
import tempfile
import json
import math
import base64
from flasgger import Swagger

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

app = Flask(__name__)

template = {
    "swagger": "2.0",
    "info": {
        "title": "BioBytes DNA Storage API",
        "description": "API for encoding and decoding data into DNA sequences.",
        "version": "1.0.0"
    },
    "tags": [
        {
            "name": "Encoding APIs",
            "description": "Pipeline for encoding files into DNA."
        },
        {
            "name": "Decoding APIs",
            "description": "Pipeline for decoding DNA back to files."
        },
        {
            "name": "Encode",
            "description": "Full end-to-end encoding."
        }
    ]
}
swagger = Swagger(app, template=template)

@app.route("/", methods=["GET", "POST"])
def lambda_handler(event=None, context=None):
    logger.info("Lambda function invoked index()")
    return "Flask says Hello!!"


@app.route('/encode', methods=['POST'])
def encode():
    """
    Encode an image to a DNA sequence.
    ---
    tags:
      - Encode

    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: The image to encode.
      - name: chunk_size
        in: formData
        type: integer
        default: 32
        description: The size of each data chunk.
      - name: ecc_bytes
        in: formData
        type: integer
        default: 10
        description: The number of error correction bytes.
      - name: redundancy_factor
        in: formData
        type: number
        default: 1.5
        description: The redundancy factor for the fountain code.
    responses:
      200:
        description: The DNA sequence in FASTA format.
        content:
          application/octet-stream:
            schema:
              type: string
              format: binary
    """
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
    """
    Decode a DNA sequence from a FASTA file to an image.
    ---
    tags:
      - Decoding APIs
    parameters:
      - name: fasta
        in: formData
        type: file
        required: true
        description: The FASTA file with the DNA sequence.
      - name: chunk_size
        in: formData
        type: integer
        default: 32
        description: The size of each data chunk.
      - name: num_chunks
        in: formData
        type: integer
        required: true
        description: The total number of chunks.
      - name: ecc_bytes
        in: formData
        type: integer
        default: 10
        description: The number of error correction bytes.
    responses:
      200:
        description: The decoded image file.
        content:
          image/jpeg:
            schema:
              type: string
              format: binary
    """
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

@app.route('/binarize', methods=['POST'])
def binarize():
    """
    1. Binarize Image
    ---
    tags:
      - Encoding APIs
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: The image to binarize.
    responses:
      200:
        description: The binary representation of the image.
        content:
          application/octet-stream:
            schema:
              type: string
              format: binary
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    image = request.files['image']
    filename = secure_filename(image.filename)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Save the uploaded image to a temporary path
        image_path = os.path.join(tmpdir, filename)
        image.save(image_path)

        # Convert the image to a binary string
        binary_data = image_to_binary(image_path)

        # Save the binary string to a temporary file
        binary_file_path = os.path.join(tmpdir, f"{os.path.splitext(filename)[0]}.bin")
        with open(binary_file_path, 'w') as f:
            f.write(binary_data)

        # Send the binary file as a downloadable attachment
        return send_file(binary_file_path, as_attachment=True, download_name=f"{os.path.splitext(filename)[0]}.bin")

@app.route('/fountain_encode', methods=['POST'])
def fountain_encode_api():
    """ 
    2. Fountain Encode
    ---
    tags:
      - Encoding APIs
    parameters:
      - name: binary_file
        in: formData
        type: file
        required: true
        description: The binary file to encode.
      - name: chunk_size
        in: formData
        type: integer
        default: 32
        description: The size of each data chunk.
      - name: redundancy_factor
        in: formData
        type: number
        default: 1.5
        description: The redundancy factor for the fountain code.
    responses:
      200:
        description: A JSON object containing the droplets and the number of chunks.
        content:
          application/json:
            schema:
              type: object
              properties:
                num_chunks:
                  type: integer
                droplets:
                  type: array
                  items:
                    type: array
    """
    if 'binary_file' not in request.files:
        return jsonify({'error': 'No binary file provided'}), 400

    binary_file = request.files['binary_file']
    chunk_size = int(request.form.get('chunk_size', 32))
    redundancy_factor = float(request.form.get('redundancy_factor', 1.5))
    filename = secure_filename(binary_file.filename)

    with tempfile.TemporaryDirectory() as tmpdir:
        binary_path = os.path.join(tmpdir, filename)
        binary_file.save(binary_path)

        droplets, num_chunks = compressAndEncode(binary_path, chunk_size, redundancy_factor)
        print(num_chunks)
        if droplets is None:
            return jsonify({'error': 'Encoding failed'}), 500

        # Prepare droplets for JSON serialization
        serializable_droplets = [
            ([indices], base64.b64encode(droplet).decode('utf-8'))
            for indices, droplet in droplets
        ]

        droplets_path = os.path.join(tmpdir, 'droplets.json')
        with open(droplets_path, 'w') as f:
            json.dump(serializable_droplets, f)

        return send_file(droplets_path, as_attachment=True, download_name='droplets.json')


        # response_data = {
        #     "num_chunks": num_chunks,
        #     "droplets": serializable_droplets
        # }

        # return jsonify(response_data)

@app.route('/add_ecc', methods=['POST'])
def add_ecc_api():
    """
    3. Add Error Correction
    ---
    tags:
      - Encoding APIs
    parameters:
      - name: droplets_file
        in: formData
        type: file
        required: true
        description: The JSON file containing the droplets.
      - name: ecc_bytes
        in: formData
        type: integer
        default: 10
        description: The number of error correction bytes.
    responses:
      200:
        description: A FASTA file containing the DNA sequences with error correction.
        content:
          application/octet-stream:
            schema:
              type: string
              format: binary
    """
    if 'droplets_file' not in request.files:
        return jsonify({'error': 'No droplets file provided'}), 400

    droplets_file = request.files['droplets_file']
    ecc_bytes = int(request.form.get('ecc_bytes', 10))
    filename = secure_filename(droplets_file.filename)

    with tempfile.TemporaryDirectory() as tmpdir:
        droplets_path = os.path.join(tmpdir, filename)
        droplets_file.save(droplets_path)

        with open(droplets_path, 'r') as f:
            serializable_droplets = json.load(f)

        droplets = [
            (tuple(indices), base64.b64decode(droplet))
            for indices, droplet in serializable_droplets
        ]
        if not droplets:
            return jsonify({'error': 'No droplets found in the file'}), 400
        

        ecc_droplets = addECCInDroplets(droplets, ecc_bytes)
        # Serialize ecc_droplets to a JSON file
        serializable_ecc_droplets = [
            (list(indices), base64.b64encode(droplet).decode('utf-8'))
            for indices, droplet in ecc_droplets
        ]
        droplets_path = os.path.join(tmpdir, 'droplets.json')
        with open(droplets_path, 'w') as f:
            json.dump(serializable_ecc_droplets, f)

        return send_file(droplets_path, as_attachment=True, download_name='droplets.json')

@app.route('/encode_to_fasta', methods=['POST'])
def encode_to_fasta_api():
    """
    4. Encode to FASTA
    ---
    tags:
      - Encoding APIs
    parameters:
      - name: ecc_droplets_file
        in: formData
        type: file
        required: true
        description: The JSON file containing the droplets with ECC.
    responses:
      200:
        description: A FASTA file containing the DNA sequences.
        content:
          application/octet-stream:
            schema:
              type: string
              format: binary
    """
    if 'ecc_droplets_file' not in request.files:
        return jsonify({'error': 'No ECC droplets file provided'}), 400

    ecc_droplets_file = request.files['ecc_droplets_file']
    filename = secure_filename(ecc_droplets_file.filename)

    with tempfile.TemporaryDirectory() as tmpdir:
        ecc_droplets_path = os.path.join(tmpdir, filename)
        ecc_droplets_file.save(ecc_droplets_path)

        with open(ecc_droplets_path, 'r') as f:
            serializable_droplets = json.load(f)

        ecc_droplets = [
            (indices[0], base64.b64decode(droplet))
            for indices, droplet in serializable_droplets
        ]

        dna_sequences = encode_droplets_to_dna(ecc_droplets)
        
        fasta_path = os.path.join(tmpdir, 'dna_encoded.fasta')
        save_dna_to_fasta(dna_sequences, fasta_path)

        return send_file(fasta_path, as_attachment=True, download_name='dna_encoded.fasta')



if __name__ == '__main__':
    app.run(debug=True)
