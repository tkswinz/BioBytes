#!/usr/bin/env python3
"""
Demo script showing how to use the BioBytes Compression API
"""
import requests
import tempfile
import os
from pathlib import Path

def demonstrate_compression_api():
    """Demonstrate the compression API functionality"""
    print("🧬 BioBytes Compression API Demo")
    print("=" * 40)
    
    # API endpoint (adjust as needed for your deployment)
    base_url = "http://localhost:5000"
    
    print(f"📡 API Base URL: {base_url}")
    print()
    
    # Create a sample file to compress
    sample_text = """
    BioBytes is a revolutionary platform for DNA data storage.
    This demo shows how to use the compression API endpoints.
    
    DNA data storage has the potential to store massive amounts of data
    in a very small physical space. Compression can help optimize this
    storage even further by reducing redundancy in the data before
    encoding it into DNA sequences.
    
    The compression API supports both zlib and gzip algorithms,
    allowing users to choose the best compression method for their data.
    """ * 10  # Repeat for better compression demonstration
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_text)
        sample_file = f.name
    
    try:
        print(f"📝 Created sample file: {Path(sample_file).name}")
        print(f"   Original size: {len(sample_text.encode())} bytes")
        print()
        
        # Test basic functionality
        print("🧪 Testing basic API functionality...")
        try:
            response = requests.get(f"{base_url}/test", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ API is working!")
                print(f"   📊 Zlib compression ratio: {data['zlib']['compression_ratio']:.3f}")
                print(f"   📊 Gzip compression ratio: {data['gzip']['compression_ratio']:.3f}")
            else:
                print(f"   ❌ API test failed with status {response.status_code}")
                return
        except Exception as e:
            print(f"   ❌ Could not connect to API: {e}")
            print(f"   💡 Make sure the server is running: python3 test_compression_server.py")
            return
        
        print()
        
        # Demonstrate compression with both algorithms
        for algorithm in ['zlib', 'gzip']:
            print(f"🗜️  Testing {algorithm.upper()} compression...")
            
            # Compress the file
            with open(sample_file, 'rb') as f:
                files = {'file': f}
                data = {'algorithm': algorithm}
                response = requests.post(f"{base_url}/compress", files=files, data=data, timeout=10)
            
            if response.status_code == 200:
                compressed_data = response.content
                original_size = os.path.getsize(sample_file)
                compressed_size = len(compressed_data)
                ratio = compressed_size / original_size
                
                print(f"   ✅ Compression successful!")
                print(f"   📏 Original size: {original_size} bytes")
                print(f"   📦 Compressed size: {compressed_size} bytes")
                print(f"   📊 Compression ratio: {ratio:.3f} ({100*(1-ratio):.1f}% reduction)")
                
                # Save compressed file temporarily
                compressed_file = sample_file + f'_compressed.{algorithm}'
                with open(compressed_file, 'wb') as f:
                    f.write(compressed_data)
                
                # Test decompression
                print(f"   🔄 Testing decompression...")
                with open(compressed_file, 'rb') as f:
                    files = {'file': f}
                    data = {'algorithm': algorithm, 'original_filename': f'restored_{algorithm}.txt'}
                    response = requests.post(f"{base_url}/decompress", files=files, data=data, timeout=10)
                
                if response.status_code == 200:
                    decompressed_data = response.content
                    if decompressed_data == sample_text.encode():
                        print(f"   ✅ Decompression successful - content matches original!")
                    else:
                        print(f"   ❌ Decompression failed - content mismatch")
                else:
                    print(f"   ❌ Decompression failed with status {response.status_code}")
                
                # Clean up compressed file
                os.unlink(compressed_file)
                
            else:
                print(f"   ❌ Compression failed with status {response.status_code}")
                if response.headers.get('content-type') == 'application/json':
                    error_data = response.json()
                    print(f"   📝 Error: {error_data.get('error', 'Unknown error')}")
            
            print()
        
        # Demonstrate error handling
        print("⚠️  Testing error handling...")
        
        # Test with invalid algorithm
        with open(sample_file, 'rb') as f:
            files = {'file': f}
            data = {'algorithm': 'invalid'}
            response = requests.post(f"{base_url}/compress", files=files, data=data, timeout=5)
        
        if response.status_code == 400:
            error_data = response.json()
            print(f"   ✅ Invalid algorithm error handled: {error_data['error']}")
        else:
            print(f"   ❌ Expected 400 error, got {response.status_code}")
        
        # Test with no file
        response = requests.post(f"{base_url}/compress", timeout=5)
        if response.status_code == 400:
            error_data = response.json()
            print(f"   ✅ Missing file error handled: {error_data['error']}")
        else:
            print(f"   ❌ Expected 400 error, got {response.status_code}")
        
        print()
        print("🎉 Demo completed successfully!")
        print()
        print("💡 Usage Tips:")
        print("   - Use zlib for better compression ratios")
        print("   - Use gzip for compatibility with standard tools")
        print("   - Specify original_filename when decompressing for better file naming")
        print("   - The API preserves all file types (text, binary, images, etc.)")
        
    finally:
        # Clean up
        if os.path.exists(sample_file):
            os.unlink(sample_file)

if __name__ == "__main__":
    demonstrate_compression_api()