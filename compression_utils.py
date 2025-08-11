"""
Simple binary compression utilities using zlib
"""
import zlib

def compress_binary_data(input_data: bytes) -> bytes:
    """
    Compress binary data using zlib compression.
    
    Args:
        input_data: The binary data to compress
        
    Returns:
        bytes: The compressed binary data
    """
    return zlib.compress(input_data)

def decompress_binary_data(compressed_data: bytes) -> bytes:
    """
    Decompress binary data using zlib decompression.
    
    Args:
        compressed_data: The compressed binary data
        
    Returns:
        bytes: The decompressed binary data
    """
    return zlib.decompress(compressed_data)