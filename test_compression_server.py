"""
Minimal Flask API for testing compression endpoints without heavy dependencies
"""
from flask import Flask, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename
import tempfile
import zlib
import gzip

app = Flask(__name__)

template = {
    "swagger": "2.0",
    "info": {
        "title": "BioBytes DNA Storage API - Compression Test",
        "description": "API for testing compression and decompression functionality.",
        "version": "1.0.0"
    },
    "tags": [
        {
            "name": "Compression APIs",
            "description": "Standalone compression and decompression utilities."
        }
    ]
}

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "BioBytes Compression API Test Server",
        "endpoints": {
            "/compress": "POST - Compress a file",
            "/decompress": "POST - Decompress a file",
            "/test": "GET - Test basic functionality"
        }
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test basic compression functionality"""
    test_data = b"Hello, this is a test message for compression!"
    
    # Test zlib
    compressed_zlib = zlib.compress(test_data)
    decompressed_zlib = zlib.decompress(compressed_zlib)
    
    # Test gzip
    compressed_gzip = gzip.compress(test_data)
    decompressed_gzip = gzip.decompress(compressed_gzip)
    
    return jsonify({
        "status": "success",
        "test_data_size": len(test_data),
        "zlib": {
            "compressed_size": len(compressed_zlib),
            "compression_ratio": round(len(compressed_zlib) / len(test_data), 3),
            "decompression_success": decompressed_zlib == test_data
        },
        "gzip": {
            "compressed_size": len(compressed_gzip),
            "compression_ratio": round(len(compressed_gzip) / len(test_data), 3),
            "decompression_success": decompressed_gzip == test_data
        }
    })

@app.route('/compress', methods=['POST'])
def compress_file():
    """
    Compress a file using the specified compression algorithm.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    uploaded_file = request.files['file']
    algorithm = request.form.get('algorithm', 'zlib').lower()
    
    if algorithm not in ['zlib', 'gzip']:
        return jsonify({'error': 'Invalid compression algorithm. Use "zlib" or "gzip"'}), 400
    
    if uploaded_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(uploaded_file.filename)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save uploaded file
        input_path = os.path.join(tmpdir, filename)
        uploaded_file.save(input_path)
        
        # Read file data
        with open(input_path, 'rb') as f:
            file_data = f.read()
        
        # Compress data based on algorithm
        if algorithm == 'zlib':
            compressed_data = zlib.compress(file_data)
            compression_ext = '.zlib'
        elif algorithm == 'gzip':
            compressed_data = gzip.compress(file_data)
            compression_ext = '.gz'
        
        # Save compressed data
        base_name = os.path.splitext(filename)[0]
        compressed_filename = f"{base_name}_compressed{compression_ext}"
        compressed_path = os.path.join(tmpdir, compressed_filename)
        
        with open(compressed_path, 'wb') as f:
            f.write(compressed_data)
        
        return send_file(compressed_path, as_attachment=True, download_name=compressed_filename)

@app.route('/decompress', methods=['POST'])
def decompress_file():
    """
    Decompress a file using the specified compression algorithm.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    uploaded_file = request.files['file']
    algorithm = request.form.get('algorithm', 'zlib').lower()
    original_filename = request.form.get('original_filename', '')
    
    if algorithm not in ['zlib', 'gzip']:
        return jsonify({'error': 'Invalid compression algorithm. Use "zlib" or "gzip"'}), 400
    
    if uploaded_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(uploaded_file.filename)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save uploaded compressed file
        input_path = os.path.join(tmpdir, filename)
        uploaded_file.save(input_path)
        
        # Read compressed data
        with open(input_path, 'rb') as f:
            compressed_data = f.read()
        
        try:
            # Decompress data based on algorithm
            if algorithm == 'zlib':
                decompressed_data = zlib.decompress(compressed_data)
            elif algorithm == 'gzip':
                decompressed_data = gzip.decompress(compressed_data)
            
            # Determine output filename
            if original_filename:
                output_filename = secure_filename(original_filename)
            else:
                # Try to guess original filename by removing compression extensions
                base_name = filename
                if base_name.endswith('.zlib'):
                    base_name = base_name[:-6]
                elif base_name.endswith('.gz'):
                    base_name = base_name[:-3]
                elif base_name.endswith('_compressed.zlib'):
                    base_name = base_name[:-17]
                elif base_name.endswith('_compressed.gz'):
                    base_name = base_name[:-14]
                output_filename = f"{base_name}_decompressed"
            
            # Save decompressed data
            output_path = os.path.join(tmpdir, output_filename)
            with open(output_path, 'wb') as f:
                f.write(decompressed_data)
            
            return send_file(output_path, as_attachment=True, download_name=output_filename)
            
        except Exception as e:
            return jsonify({'error': f'Decompression failed: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting BioBytes Compression API Test Server...")
    print("Available endpoints:")
    print("  GET  /test - Test basic functionality")
    print("  POST /compress - Compress a file")
    print("  POST /decompress - Decompress a file")
    app.run(debug=True, host='0.0.0.0', port=5000)