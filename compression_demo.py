#!/usr/bin/env python3
"""
Demo script for the new compression API endpoints
This script demonstrates the functionality without requiring Flask to be running
"""

import sys
import os
sys.path.append('/home/runner/work/BioBytes/BioBytes')

from compression_utils import compress_binary_data, decompress_binary_data

def demo_compression_api():
    """Demo the compression API functionality"""
    
    print("🧬 BioBytes Compression API Demo")
    print("=" * 40)
    
    # Create a sample file
    demo_content = """
# BioBytes Demo File
This is a demonstration file for the compression API.

The compression API provides:
- File compression using zlib
- File decompression 
- Support for any binary file type
- Integration with the DNA storage pipeline

Key features:
✅ High compression ratios for text files
✅ Handles any binary data
✅ Data integrity verification
✅ Error handling for invalid data
✅ RESTful API endpoints

Perfect for reducing file sizes before DNA encoding!
""" * 10  # Repeat for better compression demonstration
    
    print(f"📄 Original content length: {len(demo_content)} characters")
    
    # Convert to bytes
    original_data = demo_content.encode('utf-8')
    print(f"📊 Original data size: {len(original_data)} bytes")
    
    # Compress (simulating /compress API)
    print("\n🗜️  Compressing data...")
    compressed_data = compress_binary_data(original_data)
    compression_ratio = len(compressed_data) / len(original_data) * 100
    
    print(f"✅ Compressed size: {len(compressed_data)} bytes")
    print(f"📈 Compression ratio: {compression_ratio:.1f}% of original")
    print(f"💾 Space saved: {len(original_data) - len(compressed_data)} bytes ({100-compression_ratio:.1f}% reduction)")
    
    # Decompress (simulating /decompress API)
    print("\n📤 Decompressing data...")
    try:
        decompressed_data = decompress_binary_data(compressed_data)
        print(f"✅ Decompressed size: {len(decompressed_data)} bytes")
        
        # Verify integrity
        if decompressed_data == original_data:
            print("✅ Data integrity verified - perfect match!")
        else:
            print("❌ Data integrity check failed!")
            return False
            
    except Exception as e:
        print(f"❌ Decompression failed: {e}")
        return False
    
    # Save demo files
    print("\n💾 Creating demo files...")
    with open('/tmp/demo_original.txt', 'wb') as f:
        f.write(original_data)
    
    with open('/tmp/demo_compressed.bin', 'wb') as f:
        f.write(compressed_data)
    
    with open('/tmp/demo_decompressed.txt', 'wb') as f:
        f.write(decompressed_data)
    
    print("📁 Demo files created:")
    print(f"  - /tmp/demo_original.txt ({len(original_data)} bytes)")
    print(f"  - /tmp/demo_compressed.bin ({len(compressed_data)} bytes)")  
    print(f"  - /tmp/demo_decompressed.txt ({len(decompressed_data)} bytes)")
    
    return True

def demo_binary_compression():
    """Demo compression with different data types"""
    
    print("\n" + "=" * 40)
    print("🔢 Binary Data Compression Demo")
    
    # Test different data types
    test_cases = [
        ("Random text", "The quick brown fox jumps over the lazy dog. " * 100),
        ("JSON data", '{"name": "BioBytes", "type": "DNA Storage", "compression": "zlib"}' * 50),
        ("Repetitive data", "ATCGATCGATCGATCG" * 200),  # DNA-like sequence
        ("Mixed content", "ABC123!@#abc123!@#" * 100),
    ]
    
    for name, content in test_cases:
        data = content.encode('utf-8')
        compressed = compress_binary_data(data)
        ratio = len(compressed) / len(data) * 100
        
        print(f"\n{name}:")
        print(f"  Original: {len(data):,} bytes")
        print(f"  Compressed: {len(compressed):,} bytes ({ratio:.1f}%)")
        print(f"  Savings: {len(data) - len(compressed):,} bytes")

def main():
    """Main demo function"""
    
    success = demo_compression_api()
    
    if success:
        demo_binary_compression()
        
        print("\n" + "=" * 40)
        print("🎉 Demo completed successfully!")
        print("\nTo use the API:")
        print("1. Start the Flask server: python dna_api.py")
        print("2. Use curl or any HTTP client to POST files to /compress and /decompress")
        print("3. Check COMPRESSION_API.md for detailed usage examples")
        print("\nThe compression API is ready for DNA storage workflows! 🧬")
    else:
        print("\n❌ Demo failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()