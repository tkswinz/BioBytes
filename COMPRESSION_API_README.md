# Compression and Decompression API Implementation

## Overview

This implementation adds standalone compression and decompression API endpoints to the BioBytes DNA Storage platform. These endpoints allow users to compress and decompress files independently of the DNA encoding/decoding pipeline.

## New API Endpoints

### POST /compress

Compresses an uploaded file using the specified algorithm.

**Parameters:**
- `file` (required): The file to compress (multipart/form-data)
- `algorithm` (optional): Compression algorithm - `zlib` (default) or `gzip`

**Response:**
- Success (200): Returns the compressed file as a download
- Error (400): Invalid parameters or missing file
- Error (500): Compression failed

**Example usage:**
```bash
curl -X POST -F "file=@myfile.txt" -F "algorithm=zlib" \
     http://localhost:5000/compress -o myfile_compressed.zlib
```

### POST /decompress

Decompresses a previously compressed file.

**Parameters:**
- `file` (required): The compressed file to decompress (multipart/form-data)
- `algorithm` (required): Compression algorithm used - `zlib` or `gzip`
- `original_filename` (optional): Desired filename for the decompressed file

**Response:**
- Success (200): Returns the decompressed file as a download
- Error (400): Invalid parameters or missing file
- Error (500): Decompression failed

**Example usage:**
```bash
curl -X POST -F "file=@myfile_compressed.zlib" -F "algorithm=zlib" \
     -F "original_filename=myfile.txt" \
     http://localhost:5000/decompress -o myfile_restored.txt
```

## Supported Compression Algorithms

### zlib
- Better compression ratios (smaller output files)
- Faster compression/decompression
- Custom file extension: `.zlib`
- Recommended for most use cases

### gzip
- Standard format compatible with gzip command-line tools
- Slightly larger output but widely supported
- Standard file extension: `.gz`
- Good for interoperability

## Implementation Files

### Core Implementation
- `dna_api.py` - Main API with new compression endpoints added
- Updated Swagger documentation with new "Compression APIs" tag

### Testing Infrastructure
- `test_compression_api.py` - Unit tests for compression logic
- `test_compression_server.py` - Minimal standalone test server
- `comprehensive_test.py` - Full integration tests with HTTP requests
- `demo_compression_api.py` - Interactive demonstration script

### Configuration
- `.gitignore` - Updated to exclude build artifacts and temporary files

## Testing Results

All tests pass successfully:

✅ **Unit Tests:**
- Basic compression/decompression logic
- File handling and filename transformations
- Algorithm selection and validation

✅ **Integration Tests:**
- HTTP endpoint functionality
- File upload/download mechanics
- Error handling for edge cases
- Round-trip compression/decompression verification

✅ **Performance Tests:**
- zlib: ~97% compression ratio on repetitive text
- gzip: ~96% compression ratio on repetitive text
- Perfect data integrity (original == decompressed)

## Error Handling

The implementation includes comprehensive error handling:

- **Missing file**: Returns 400 with clear error message
- **Invalid algorithm**: Returns 400 with supported algorithm list
- **Empty filename**: Returns 400 with validation error
- **Decompression failure**: Returns 500 with detailed error message
- **File I/O errors**: Proper exception handling with cleanup

## Usage in DNA Storage Pipeline

These compression endpoints can be used to optimize the DNA storage process:

1. **Pre-encoding compression**: Compress files before DNA encoding to reduce storage requirements
2. **Post-decoding decompression**: Decompress files after DNA decoding to restore original data
3. **Standalone usage**: Use for general file compression needs independent of DNA storage

## Example Workflow

```bash
# 1. Compress a large file before DNA encoding
curl -X POST -F "file=@large_dataset.csv" -F "algorithm=zlib" \
     http://localhost:5000/compress -o dataset_compressed.zlib

# 2. Encode the compressed file to DNA (using existing endpoints)
curl -X POST -F "image=@dataset_compressed.zlib" \
     http://localhost:5000/encode -o dataset_dna.fasta

# 3. Later: decode DNA back to compressed file (using existing endpoints)
curl -X POST -F "fasta=@dataset_dna.fasta" -F "num_chunks=1234" \
     http://localhost:5000/decode -o dataset_decoded_compressed.zlib

# 4. Decompress to get original file
curl -X POST -F "file=@dataset_decoded_compressed.zlib" -F "algorithm=zlib" \
     -F "original_filename=large_dataset.csv" \
     http://localhost:5000/decompress -o dataset_restored.csv
```

## Benefits

1. **Storage Optimization**: Reduce file sizes before DNA encoding
2. **Flexibility**: Use compression independently of DNA pipeline
3. **Algorithm Choice**: Select best compression method for your data
4. **Error Recovery**: Robust error handling and validation
5. **Interoperability**: Standard compression formats for compatibility

## Deployment Notes

- The implementation uses Python's built-in `zlib` and `gzip` modules
- No additional dependencies required beyond existing Flask setup
- Temporary files are automatically cleaned up using `tempfile.TemporaryDirectory`
- All file operations are secure using `werkzeug.utils.secure_filename`

## Future Enhancements

Potential improvements for future versions:
- Support for additional compression algorithms (bz2, lzma)
- Batch compression for multiple files
- Compression level parameters for fine-tuning
- Integration with cloud storage services
- Compression statistics and analytics