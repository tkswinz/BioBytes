# Binary File Compression API

This document describes the new compression and decompression API endpoints that provide standalone binary file compression functionality.

## Overview

The compression API provides two endpoints:
- `/compress`: Compress any binary file using zlib compression
- `/decompress`: Decompress files that were compressed with the `/compress` endpoint

These are useful as preprocessing/postprocessing steps before further encoding or for general file size reduction.

## Endpoints

### POST `/compress`

Compress a binary file using zlib compression.

#### Parameters

- **file** (required): The binary file to compress
  - Type: `file` (form data)
  - Description: Any binary file (text, images, documents, etc.)

#### Response

- **Success (200)**: Returns the compressed file as a binary download
  - Content-Type: `application/octet-stream`
  - Filename: `{original_name}.compressed`

- **Error (400)**: JSON error response
  ```json
  {
    "error": "No file provided"
  }
  ```

### POST `/decompress`

Decompress a binary file that was compressed with zlib.

#### Parameters

- **file** (required): The compressed binary file to decompress
  - Type: `file` (form data)
  - Description: File compressed with the `/compress` endpoint

- **original_extension** (optional): The original file extension
  - Type: `string` (form data)
  - Default: `bin`
  - Description: Extension for the decompressed file (e.g., 'txt', 'jpg')

#### Response

- **Success (200)**: Returns the decompressed file as a binary download
  - Content-Type: `application/octet-stream`
  - Filename: `{original_name}.{extension}`

- **Error (400)**: JSON error response
  ```json
  {
    "error": "Decompression failed: [error details]"
  }
  ```

## Usage Examples

### Using curl

```bash
# Compress a text file
curl -X POST -F "file=@sample.txt" http://localhost:5000/compress -o sample.compressed

# Decompress the file back
curl -X POST -F "file=@sample.compressed" -F "original_extension=txt" http://localhost:5000/decompress -o sample_restored.txt

# Compress an image
curl -X POST -F "file=@image.jpg" http://localhost:5000/compress -o image.compressed

# Decompress the image back
curl -X POST -F "file=@image.compressed" -F "original_extension=jpg" http://localhost:5000/decompress -o image_restored.jpg

# Compress any binary file
curl -X POST -F "file=@document.pdf" http://localhost:5000/compress -o document.compressed
```

### Using Python requests

```python
import requests

# Compress a file
with open('sample.txt', 'rb') as f:
    response = requests.post('http://localhost:5000/compress', files={'file': f})

if response.status_code == 200:
    with open('sample.compressed', 'wb') as f:
        f.write(response.content)
    print("File compressed successfully!")
    
    # Decompress the file
    with open('sample.compressed', 'rb') as f:
        response = requests.post('http://localhost:5000/decompress', 
                               files={'file': f},
                               data={'original_extension': 'txt'})
    
    if response.status_code == 200:
        with open('sample_restored.txt', 'wb') as f:
            f.write(response.content)
        print("File decompressed successfully!")
else:
    print(f"Error: {response.json()}")
```

### Using JavaScript/HTML

```html
<form id="compressForm">
    <input type="file" id="fileInput" name="file" required>
    <button type="submit">Compress File</button>
</form>

<form id="decompressForm">
    <input type="file" id="compressedFileInput" name="file" required>
    <input type="text" id="extensionInput" name="original_extension" placeholder="Original extension (e.g., txt, jpg)">
    <button type="submit">Decompress File</button>
</form>

<script>
document.getElementById('compressForm').onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    const file = document.getElementById('fileInput').files[0];
    formData.append('file', file);
    
    const response = await fetch('/compress', {
        method: 'POST',
        body: formData
    });
    
    if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = file.name + '.compressed';
        a.click();
    } else {
        console.error('Compression failed');
    }
};

document.getElementById('decompressForm').onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    const file = document.getElementById('compressedFileInput').files[0];
    const extension = document.getElementById('extensionInput').value || 'bin';
    formData.append('file', file);
    formData.append('original_extension', extension);
    
    const response = await fetch('/decompress', {
        method: 'POST',
        body: formData
    });
    
    if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = file.name.replace('.compressed', '') + '.' + extension;
        a.click();
    } else {
        console.error('Decompression failed');
    }
};
</script>
```

## Performance Notes

- **Compression Ratio**: Varies by file type and content
  - Text files: Typically compress to 10-30% of original size
  - Already compressed files (JPG, ZIP, etc.): May not compress significantly
  - Binary data with patterns: Good compression
  - Random data: Poor compression

- **File Size Limits**: Depends on server configuration and available memory

## Integration with Other APIs

The compressed file can be used with other endpoints in the pipeline:

1. **Compress** → `/compress` → Get compressed binary file
2. **Fountain Encode** → `/fountain_encode` → Encode compressed data into droplets
3. **Add ECC** → `/add_ecc` → Add error correction to droplets
4. **Encode to DNA** → `/encode_to_fasta` → Convert to DNA sequences
5. **Decode from DNA** → Process in reverse order
6. **Decompress** → `/decompress` → Get original file back

## Complete Workflow Example

```bash
# 1. Start with an original file
echo "Hello, BioBytes!" > original.txt

# 2. Compress the file
curl -X POST -F "file=@original.txt" http://localhost:5000/compress -o original.compressed

# 3. Encode compressed file into fountain droplets
curl -X POST -F "binary_file=@original.compressed" http://localhost:5000/fountain_encode -o droplets.json

# 4. Add error correction to droplets
curl -X POST -F "droplets_file=@droplets.json" http://localhost:5000/add_ecc -o ecc_droplets.json

# 5. Convert to DNA sequences
curl -X POST -F "ecc_droplets_file=@ecc_droplets.json" http://localhost:5000/encode_to_fasta -o dna.fasta

# [At this point, your data is stored as DNA sequences]
# [Decoding process would reverse these steps]

# 6. After decoding back to compressed binary, decompress
curl -X POST -F "file=@recovered.compressed" -F "original_extension=txt" http://localhost:5000/decompress -o recovered.txt
```

## Technical Details

- **Compression Algorithm**: zlib (RFC 1950)
- **Implementation**: Uses Python's built-in `zlib.compress()` function
- **Compression Level**: Default (level 6 - balanced speed/compression)
- **Format**: Raw compressed binary data (not gzip format)