#!/usr/bin/env python3
"""
Comprehensive test for compression/decompression API functionality
"""
import os
import sys
import tempfile
import zlib
import gzip
import subprocess
import time
import requests
import json
from pathlib import Path

def test_api_endpoints():
    """Test the compression API endpoints with HTTP requests"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing API endpoints...")
    
    # Test basic functionality endpoint
    try:
        response = requests.get(f"{base_url}/test", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ /test endpoint working - zlib ratio: {data['zlib']['compression_ratio']}")
        else:
            print(f"❌ /test endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not reach test server: {e}")
        return False
    
    # Create test file
    test_content = b"This is a comprehensive test for the compression API. " * 50
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file_path = f.name
    
    try:
        # Test compression with zlib
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {'algorithm': 'zlib'}
            response = requests.post(f"{base_url}/compress", files=files, data=data, timeout=10)
        
        if response.status_code == 200:
            compressed_content = response.content
            print(f"✅ Zlib compression successful: {len(test_content)} -> {len(compressed_content)} bytes")
            
            # Test decompression
            compressed_file_path = test_file_path + '_compressed.zlib'
            with open(compressed_file_path, 'wb') as f:
                f.write(compressed_content)
            
            with open(compressed_file_path, 'rb') as f:
                files = {'file': f}
                data = {'algorithm': 'zlib', 'original_filename': 'restored.txt'}
                response = requests.post(f"{base_url}/decompress", files=files, data=data, timeout=10)
            
            if response.status_code == 200:
                decompressed_content = response.content
                if decompressed_content == test_content:
                    print("✅ Zlib decompression successful - content matches original")
                else:
                    print("❌ Zlib decompression failed - content mismatch")
                    return False
            else:
                print(f"❌ Zlib decompression failed with status {response.status_code}")
                return False
            
            os.unlink(compressed_file_path)
        else:
            print(f"❌ Zlib compression failed with status {response.status_code}")
            return False
        
        # Test compression with gzip
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {'algorithm': 'gzip'}
            response = requests.post(f"{base_url}/compress", files=files, data=data, timeout=10)
        
        if response.status_code == 200:
            compressed_content = response.content
            print(f"✅ Gzip compression successful: {len(test_content)} -> {len(compressed_content)} bytes")
            
            # Test decompression
            compressed_file_path = test_file_path + '_compressed.gz'
            with open(compressed_file_path, 'wb') as f:
                f.write(compressed_content)
            
            with open(compressed_file_path, 'rb') as f:
                files = {'file': f}
                data = {'algorithm': 'gzip'}
                response = requests.post(f"{base_url}/decompress", files=files, data=data, timeout=10)
            
            if response.status_code == 200:
                decompressed_content = response.content
                if decompressed_content == test_content:
                    print("✅ Gzip decompression successful - content matches original")
                else:
                    print("❌ Gzip decompression failed - content mismatch")
                    return False
            else:
                print(f"❌ Gzip decompression failed with status {response.status_code}")
                return False
            
            os.unlink(compressed_file_path)
        else:
            print(f"❌ Gzip compression failed with status {response.status_code}")
            return False
        
        print("✅ All API endpoint tests passed!")
        return True
        
    finally:
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)

def test_error_handling():
    """Test API error handling"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing error handling...")
    
    # Test missing file
    try:
        response = requests.post(f"{base_url}/compress", timeout=5)
        if response.status_code == 400 and "No file provided" in response.json().get('error', ''):
            print("✅ Missing file error handled correctly")
        else:
            print("❌ Missing file error not handled correctly")
            return False
    except Exception as e:
        print(f"❌ Error testing missing file: {e}")
        return False
    
    # Test invalid algorithm
    try:
        test_content = b"test"
        with tempfile.NamedTemporaryFile() as f:
            f.write(test_content)
            f.flush()
            
            with open(f.name, 'rb') as file:
                files = {'file': file}
                data = {'algorithm': 'invalid'}
                response = requests.post(f"{base_url}/compress", files=files, data=data, timeout=5)
        
        if response.status_code == 400 and "Invalid compression algorithm" in response.json().get('error', ''):
            print("✅ Invalid algorithm error handled correctly")
        else:
            print("❌ Invalid algorithm error not handled correctly")
            return False
    except Exception as e:
        print(f"❌ Error testing invalid algorithm: {e}")
        return False
    
    print("✅ Error handling tests passed!")
    return True

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🚀 Starting comprehensive compression API tests...\n")
    
    # Start test server
    print("📡 Starting test server...")
    server_process = subprocess.Popen(
        [sys.executable, "test_compression_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.path.dirname(__file__)
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Run tests
        api_success = test_api_endpoints()
        error_success = test_error_handling()
        
        if api_success and error_success:
            print("\n🎉 All comprehensive tests passed!")
            return True
        else:
            print("\n❌ Some tests failed!")
            return False
            
    finally:
        # Stop server
        server_process.terminate()
        server_process.wait(timeout=5)
        print("📡 Test server stopped")

if __name__ == "__main__":
    # Install requests if not available (it should be available in most environments)
    try:
        import requests
    except ImportError:
        print("requests module not available, skipping HTTP tests")
        sys.exit(0)
    
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)