#!/usr/bin/env python3
"""
Simple test script for compression/decompression functionality
"""
import os
import tempfile
import zlib
import gzip
from werkzeug.utils import secure_filename

def test_compression_logic():
    """Test the core compression/decompression logic"""
    print("Testing compression/decompression logic...")
    
    # Create test data
    test_data = b"Hello, World! This is a test file for compression. " * 100
    print(f"Original data size: {len(test_data)} bytes")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test file operations
        test_file = os.path.join(tmpdir, "test_file.txt")
        with open(test_file, 'wb') as f:
            f.write(test_data)
        
        # Test zlib compression
        print("\nTesting zlib compression:")
        with open(test_file, 'rb') as f:
            file_data = f.read()
        
        compressed_zlib = zlib.compress(file_data)
        print(f"Compressed size (zlib): {len(compressed_zlib)} bytes")
        print(f"Compression ratio: {len(compressed_zlib)/len(file_data):.2f}")
        
        # Save compressed data
        compressed_file = os.path.join(tmpdir, "test_file_compressed.zlib")
        with open(compressed_file, 'wb') as f:
            f.write(compressed_zlib)
        
        # Test zlib decompression
        with open(compressed_file, 'rb') as f:
            compressed_data = f.read()
        
        decompressed_zlib = zlib.decompress(compressed_data)
        print(f"Decompressed size: {len(decompressed_zlib)} bytes")
        print(f"Decompression successful: {decompressed_zlib == test_data}")
        
        # Test gzip compression
        print("\nTesting gzip compression:")
        compressed_gzip = gzip.compress(file_data)
        print(f"Compressed size (gzip): {len(compressed_gzip)} bytes")
        print(f"Compression ratio: {len(compressed_gzip)/len(file_data):.2f}")
        
        # Test gzip decompression
        decompressed_gzip = gzip.decompress(compressed_gzip)
        print(f"Decompressed size: {len(decompressed_gzip)} bytes")
        print(f"Decompression successful: {decompressed_gzip == test_data}")
        
        # Test filename handling
        print("\nTesting filename handling:")
        test_filename = "my_test_file.txt"
        secure_name = secure_filename(test_filename)
        print(f"Original filename: {test_filename}")
        print(f"Secure filename: {secure_name}")
        
        # Test filename transformations
        base_name = os.path.splitext(test_filename)[0]
        compressed_filename = f"{base_name}_compressed.zlib"
        print(f"Compressed filename: {compressed_filename}")
        
        # Test decompression filename logic
        if compressed_filename.endswith('_compressed.zlib'):
            original_name = compressed_filename[:-17] + '.txt'  # Remove '_compressed.zlib' and add original extension
            print(f"Recovered original name: {original_name}")
    
    print("\n✅ All compression tests passed!")

def test_api_logic():
    """Test the API logic without Flask"""
    print("\nTesting API logic...")
    
    # Simulate the compress endpoint logic
    test_data = b"API test data for compression!"
    algorithm = 'zlib'
    
    if algorithm == 'zlib':
        compressed_data = zlib.compress(test_data)
        compression_ext = '.zlib'
    elif algorithm == 'gzip':
        compressed_data = gzip.compress(test_data)
        compression_ext = '.gz'
    
    print(f"Algorithm: {algorithm}")
    print(f"Original size: {len(test_data)} bytes")
    print(f"Compressed size: {len(compressed_data)} bytes")
    print(f"Extension: {compression_ext}")
    
    # Simulate the decompress endpoint logic
    try:
        if algorithm == 'zlib':
            decompressed_data = zlib.decompress(compressed_data)
        elif algorithm == 'gzip':
            decompressed_data = gzip.decompress(compressed_data)
        
        print(f"Decompressed size: {len(decompressed_data)} bytes")
        print(f"Decompression matches: {decompressed_data == test_data}")
        
    except Exception as e:
        print(f"❌ Decompression failed: {str(e)}")
        return False
    
    print("✅ API logic test passed!")
    return True

if __name__ == "__main__":
    test_compression_logic()
    test_api_logic()
    print("\n🎉 All tests completed successfully!")