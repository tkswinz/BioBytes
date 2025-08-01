import random
from typing import List, Tuple
import zlib
from PIL import Image
import io
from reedsolo import RSCodec

# Binary to DNA mapping
BIN_TO_DNA = {'00': 'A', '01': 'C', '10': 'G', '11': 'T'}
DNA_TO_BIN = {v: k for k, v in BIN_TO_DNA.items()}

def binary_to_image(binary_str, output_path):
    byte_data = bytearray(int(binary_str[i:i+8], 2) for i in range(0, len(binary_str), 8))
    with open(output_path, 'wb') as f:
        f.write(byte_data)

# Helper: Pad chunk to fixed size
def pad_chunk(chunk: bytes, size: int) -> bytes:
    return chunk + b'\x00' * (size - len(chunk))

# XOR multiple byte arrays
def xor_bytes(arrays: List[bytes], size: int) -> bytes:
    result = bytearray(pad_chunk(arrays[0], size))
    for arr in arrays[1:]:
        arr_padded = pad_chunk(arr, size)
        for i in range(size):
            result[i] ^= arr_padded[i]
    return bytes(result)

def binary_to_dna(data):
    mapping = {'00':'A', '01':'C', '10':'G', '11':'T'}
    bits = ''.join(f"{byte:08b}" for byte in data)
    dna = ''.join(mapping[bits[i:i+2]] for i in range(0, len(bits), 2))
    return dna

# Fountain Encode
def fountain_encode(data: bytes, chunk_size: int, num_droplets: int) -> Tuple[List[Tuple[int, bytes]], int]:
    chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    num_chunks = len(chunks)
    droplets = []

    for _ in range(num_droplets):
        seed = random.randint(0, 2**32 - 1)
        random.seed(seed)
        degree = random.randint(1, min(3, num_chunks))
        indices = random.sample(range(num_chunks), degree)
        selected_chunks = [chunks[i] for i in indices]
        payload = xor_bytes(selected_chunks, chunk_size)
        droplets.append((seed, payload))
    
    return droplets, num_chunks

# Fountain Decode
def fountain_decode(droplets: List[Tuple[int, bytes]], chunk_size: int, num_chunks: int, original_length: int) -> bytes:
    chunks = [None] * num_chunks
    equations = []

    for seed, payload in droplets:
        random.seed(seed)
        degree = random.randint(1, min(3, num_chunks))
        indices = random.sample(range(num_chunks), degree)
        equations.append((indices, bytearray(payload)))

    progress = True
    while progress:
        progress = False
        for indices, payload in equations:
            known = [(i, chunks[i]) for i in indices if chunks[i] is not None]
            unknown = [i for i in indices if chunks[i] is None]
            if len(unknown) == 1:
                i = unknown[0]
                for j, value in known:
                    for k in range(len(payload)):
                        payload[k] ^= value[k]
                chunks[i] = bytes(payload)
                progress = True

    if any(c is None for c in chunks):
        raise ValueError("Decoding failed: Not enough droplets.")

    return b''.join(chunks)[:original_length]



def image_to_binary(image_path):
    with open(image_path, 'rb') as f:
        data = f.read()
    return ''.join(f'{byte:08b}' for byte in data)

# def binary_to_dna(binary_str):
#     dna = ''
#     for i in range(0, len(binary_str), 2):
#         chunk = binary_str[i:i+2]
#         if len(chunk) < 2:
#             chunk = chunk.ljust(2, '0')
#         dna += BIN_TO_DNA[chunk]
#     return dna

def readFile(path):
    with open(path, 'rb') as file:
        return file.read()

def writeFile(path, binary):
    with open(path, 'w') as file:
        file.write(binary)

def writeCompressedBinary(input_data: bytes, output_filename: str):
    compressed_data = zlib.compress(input_data)
    #with open(output_filename, 'wb') as f:
     #   f.write(compressed_data)
    return compressed_data;   

def readAndDecompress(filename: str) -> bytes:
    with open(filename, 'rb') as f:
        compressed = f.read()
    return zlib.decompress(compressed)

def add_error_correction(data: bytes, ecc_bytes: int = 10) -> bytes:
    rsc = RSCodec(ecc_bytes)
    return rsc.encode(data)

import struct

def encode_droplets_to_dna(ecc_droplets) -> List[str]:
    dna_sequences = []


    for seed, payload in ecc_droplets:
        # Serialize metadata: store the seed as 4 bytes (unsigned int)
        meta = struct.pack('I', seed)
        full_payload = meta + payload  # Metadata + ECC-protected data

        dna_seq = binary_to_dna(full_payload)
        dna_sequences.append(dna_seq)

    return dna_sequences

def save_dna_to_fasta(dna_sequences: List[str], filename: str = "dna_droplets.fasta"):
    with open(filename, 'w') as f:
        for i, seq in enumerate(dna_sequences):
            f.write(f">droplet_{i}\n")
            f.write(f"{seq}\n")


# --- Decoding from FASTA ---
def dna_to_binary(dna: str) -> bytes:
    """Convert a DNA string back to bytes."""
    mapping = {'A': '00', 'C': '01', 'G': '10', 'T': '11'}
    bits = ''.join(mapping[base] for base in dna)
    # Pad bits to a multiple of 8
    if len(bits) % 8 != 0:
        bits += '0' * (8 - len(bits) % 8)
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

def load_dna_from_fasta(filename: str) -> list:
    """Load DNA sequences from a FASTA file."""
    sequences = []
    with open(filename, 'r') as f:
        seq = ''
        for line in f:
            if line.startswith('>'):
                if seq:
                    sequences.append(seq.strip())
                    seq = ''
            else:
                seq += line.strip()
        if seq:
            sequences.append(seq.strip())
    return sequences

def remove_error_correction(data: bytes, ecc_bytes: int = 10) -> bytes:
    rsc = RSCodec(ecc_bytes)
    return rsc.decode(data)[0]

def decode_dna_fasta_to_image(fasta_file: str, output_image: str, chunk_size: int, ecc_bytes: int = 10):
    # 1. Load DNA sequences
    dna_sequences = load_dna_from_fasta(fasta_file)

    # 2. Convert DNA to binary, extract seed and payload, remove ECC
    droplets = []
    for dna_seq in dna_sequences:
        binary = dna_to_binary(dna_seq)
        if len(binary) < 4:
            continue  # skip invalid
        seed = int.from_bytes(binary[:4], 'little')
        payload_ecc = binary[4:]
        try:
            payload = remove_error_correction(payload_ecc, ecc_bytes)
        except Exception:
            continue  # skip if ECC fails
        droplets.append((seed, payload))

    # 3. Use known num_chunks from encoding (should be passed as argument)
    if not droplets:
        print("No valid droplets found.")
        return

    # 4. Fountain decode (single attempt with known num_chunks)
    try:
        # num_chunks should be passed as an argument for robust decoding
        # For now, infer from global or pass as needed
        from inspect import currentframe
        frame = currentframe()
        # Try to get num_chunks from caller's local variables
        num_chunks = frame.f_back.f_locals.get('num_chunks', None)
        if num_chunks is None:
            print("num_chunks not found. Please pass num_chunks as an argument.")
            return
        decoded = fountain_decode(droplets, chunk_size, num_chunks, chunk_size * num_chunks)
        try:
            decompressed = zlib.decompress(decoded)
            # Save decompressed binary
            with open("binary1.dat", 'wb') as f:
                f.write(decompressed)
            # Save as image
            binary_to_image(decompressed, output_image)
            print(f"✅ Decoding and decompression successful! Image saved as {output_image}")
            return
        except Exception:
            print("Decompression failed after decoding.")
            return
    except Exception as e:
        print(f"❌ Decoding failed: {e}")

def binary_to_image(binary_str, output_path):
    byte_data = bytearray(int(binary_str[i:i+8], 2) for i in range(0, len(binary_str), 8))
    with open(output_path, 'wb') as f:
        f.write(byte_data)

# Example Usage
if __name__ == "__main__":
    
    binary = image_to_binary("DNA.jpg")
    with open("binary.dat", 'w') as f:
        f.write(binary)

    binary_data = readFile("binary.dat")
    message = writeCompressedBinary(binary_data, "compressed_output.bin")
    chunk_size = 32

    chunks = [message[i:i+chunk_size] for i in range(0, len(message), chunk_size)]
    num_chunks = len(chunks)
    print(num_chunks)
    redundancy_factor = 1.5
    num_droplets = int(num_chunks * redundancy_factor * 20)
    print(num_droplets)

    # Encode
    droplets, num_chunks = fountain_encode(message, chunk_size, num_droplets)
    print(len(droplets))


    ecc_droplets = [
        (indices, add_error_correction(droplet))
        for indices, droplet in droplets
    ]

    dna_sequences = encode_droplets_to_dna(ecc_droplets)

    save_dna_to_fasta(dna_sequences, "model_dna_encoded.fasta")


    # Decode from FASTA and reconstruct image
    decode_dna_fasta_to_image("model_dna_encoded.fasta", "output_imageFinal.jpg", chunk_size, ecc_bytes=10)


# --- API Functions ---
def encode_image_to_dna(image_path: str, fasta_output: str, chunk_size: int = 32, ecc_bytes: int = 10, redundancy_factor: float = 1.5) -> None:
    """
    Encode an image file to DNA sequences and save as FASTA.
    Args:
        image_path: Path to input image file.
        fasta_output: Path to output FASTA file.
        chunk_size: Size of each chunk in bytes.
        ecc_bytes: Number of error correction bytes per droplet.
        redundancy_factor: Redundancy multiplier for droplets.
    """
    binary = image_to_binary(image_path)
    
    #convert binary to bytes
    #binary_data = bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))
    # print(binary)

    with open("binary.dat", 'w') as f:
        f.write(binary)
    binary_data = readFile("binary.dat")
    # print(binary_data)

    message = writeCompressedBinary(binary_data, "compressed_output.bin")
    chunks = [message[i:i+chunk_size] for i in range(0, len(message), chunk_size)]
    num_chunks = len(chunks)
    print(num_chunks)
    num_droplets = int(num_chunks * redundancy_factor * 20)
    droplets, num_chunks = fountain_encode(message, chunk_size, num_droplets)
    print(num_chunks)
    ecc_droplets = [
        (indices, add_error_correction(droplet, ecc_bytes))
        for indices, droplet in droplets
    ]
    dna_sequences = encode_droplets_to_dna(ecc_droplets)
    save_dna_to_fasta(dna_sequences, fasta_output)
    return

def decode_dna_to_image(fasta_file: str, output_image: str, chunk_size: int, num_chunks: int, ecc_bytes: int = 10) -> bool:
    """
    Decode DNA sequences from FASTA and reconstruct the image.
    Args:
        fasta_file: Path to input FASTA file.
        output_image: Path to output image file.
        chunk_size: Size of each chunk in bytes (must match encoding).
        num_chunks: Number of chunks (must match encoding).
        ecc_bytes: Number of error correction bytes per droplet.
    Returns:
        True if decoding and decompression successful, else False.
    """
    dna_sequences = load_dna_from_fasta(fasta_file)
    droplets = []
    for dna_seq in dna_sequences:
        binary = dna_to_binary(dna_seq)
        if len(binary) < 4:
            continue
        seed = int.from_bytes(binary[:4], 'little')
        payload_ecc = binary[4:]
        try:
            payload = remove_error_correction(payload_ecc, ecc_bytes)
        except Exception:
            continue
        droplets.append((seed, payload))
    if not droplets:
        print("No valid droplets found.")
        return False
    try:
        decoded = fountain_decode(droplets, chunk_size, num_chunks, chunk_size * num_chunks)
        try:
            decompressed = zlib.decompress(decoded)
            with open("binary1.dat", 'wb') as f:
                f.write(decompressed)
            binary_to_image(decompressed, output_image)
            print(f"✅ Decoding and decompression successful! Image saved as {output_image}")
            return True
        except Exception:
            print("Decompression failed after decoding.")
            return False
    except Exception as e:
        print(f"❌ Decoding failed: {e}")
        return False
    

# --- API Functions ---
def compressAndEncode(binary_path: str, chunk_size: int = 32, redundancy_factor: float = 1.5) -> None:
    """
    Compress and encode a binary file into fountain code droplets.
    Args:
        binary_path: Path to the input binary file.
        chunk_size: Size of each data chunk.
        redundancy_factor: Redundancy factor for the fountain code.
    """

    with open(binary_path, 'rb') as f:
        binary_data = f.read()

    message = writeCompressedBinary(binary_data, "compressed_output.bin")
    chunks = [message[i:i+chunk_size] for i in range(0, len(message), chunk_size)]
    num_chunks = len(chunks)
    num_droplets = int(num_chunks * redundancy_factor * 20)
    droplets, num_chunks = fountain_encode(message, chunk_size, num_droplets)

    return droplets, num_chunks
    # ecc_droplets = [
    #     (indices, add_error_correction(droplet, ecc_bytes))
    #     for indices, droplet in droplets
    # ]
    # dna_sequences = encode_droplets_to_dna(ecc_droplets)
    # save_dna_to_fasta(dna_sequences, fasta_output)
    



# --- API Functions ---
def addECCInDroplets(droplets: List[Tuple[int, bytes]], ecc_bytes: int) -> List[Tuple[int, bytes]]:
    """
    Add error correction code (ECC) to each droplet.
    Args:
        droplets: List of droplets to encode.
        ecc_bytes: Number of error correction bytes to add.
    Returns:
        List of droplets with ECC added.
    """
    ecc_droplets = [
        (indices, add_error_correction(droplet, ecc_bytes))
        for indices, droplet in droplets
    ]
    return ecc_droplets
