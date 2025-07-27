# DNA Image Storage Example

This project demonstrates encoding a sample image file into a DNA sequence and decoding the DNA sequence back to retrieve the original image.

## Features
- Encode any image file (e.g., PNG, JPG) into a DNA sequence
- Decode a DNA sequence back into the original image file
- Simple CLI usage

## Usage
1. Place your sample image in the project directory.
2. Run the script to encode the image to DNA.
3. Run the script to decode the DNA back to an image.

## Requirements
- Python 3.x
- Pillow (for image handling)

## Setup
Install dependencies:
```bash
pip install pillow
```

## Example
```bash
python dna_image_storage.py encode sample.png dna.txt
python dna_image_storage.py decode dna.txt output.png
```

## Error Correction Codes (ECC)
To ensure robust data storage and retrieval, error correction codes add redundancy and parity checks to handle potential errors during DNA synthesis and sequencing.

**Popular ECC methods:**
- **Reed-Solomon codes:** Widely used for correcting multiple errors in data blocks.
- **Fountain codes (e.g., DNA Fountain):** Rateless codes that provide flexible and efficient error correction, especially useful for DNA data storage.
