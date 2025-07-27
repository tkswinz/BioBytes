import sys
from PIL import Image

# Binary to DNA mapping
BIN_TO_DNA = {'00': 'A', '01': 'C', '10': 'G', '11': 'T'}
DNA_TO_BIN = {v: k for k, v in BIN_TO_DNA.items()}

def image_to_binary(image_path):
    with open(image_path, 'rb') as f:
        data = f.read()
    return ''.join(f'{byte:08b}' for byte in data)

def binary_to_dna(binary_str):
    dna = ''
    for i in range(0, len(binary_str), 2):
        chunk = binary_str[i:i+2]
        if len(chunk) < 2:
            chunk = chunk.ljust(2, '0')
        dna += BIN_TO_DNA[chunk]
    return dna

def dna_to_binary(dna_str):
    return ''.join(DNA_TO_BIN[base] for base in dna_str)

def binary_to_image(binary_str, output_path):
    byte_data = bytearray(int(binary_str[i:i+8], 2) for i in range(0, len(binary_str), 8))
    with open(output_path, 'wb') as f:
        f.write(byte_data)

def encode(image_path, dna_path, binary_path):
    binary = image_to_binary(image_path)
    with open(binary_path, 'w') as f:
        f.write(binary)

    dna = binary_to_dna(binary)

    with open(dna_path, 'w') as f:
        f.write(dna)
    print(f"Encoded {image_path} to {dna_path}")

def decode(dna_path, output_image_path):
    with open(dna_path, 'r') as f:
        dna = f.read().strip()
    binary = dna_to_binary(dna)
    binary_to_image(binary, output_image_path)
    print(f"Decoded {dna_path} to {output_image_path}")

def main():
    if len(sys.argv) < 4:
        print("Usage: python dna_image_storage.py encode <image> <dna.txt> | decode <dna.txt> <output_image>")
        return
    command = sys.argv[1]
    if command == 'encode':
        encode(sys.argv[2], sys.argv[3], sys.argv[4])
    elif command == 'decode':
        decode(sys.argv[2], sys.argv[3])
    else:
        print("Unknown command. Use 'encode' or 'decode'.")

if __name__ == "__main__":
    main()
