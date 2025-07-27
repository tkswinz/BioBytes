import random
from typing import List, Tuple
import zlib
from PIL import Image
import io

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

def binary_to_dna(binary_str):
    dna = ''
    for i in range(0, len(binary_str), 2):
        chunk = binary_str[i:i+2]
        if len(chunk) < 2:
            chunk = chunk.ljust(2, '0')
        dna += BIN_TO_DNA[chunk]
    return dna

def readFile(path):
    with open(path, 'rb') as file:
        return file.read()

def writeFile(path, binary):
    with open(path, 'w') as file:
        file.write(binary)

def writeCompressedBinary(input_data: bytes, output_filename: str):
    compressed_data = zlib.compress(input_data)
    with open(output_filename, 'wb') as f:
        f.write(compressed_data)
    return compressed_data;   

def readAndDecompress(filename: str) -> bytes:
    with open(filename, 'rb') as f:
        compressed = f.read()
    return zlib.decompress(compressed)


# Example Usage
if __name__ == "__main__":
    
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

    # Simulate 20% data loss
    received_droplets = random.sample(droplets, int(len(droplets) * 0.8))

    # Decode
    try:
        # fountain decoding
        decoded = fountain_decode(received_droplets, chunk_size, num_chunks, len(message))
        print("✅ Decoding successful!")

        # Decompress + Deserialize
        with open("compressed_output1.bin", 'wb') as f:
            f.write(decoded)

        binary_data1 =  readAndDecompress("compressed_output1.bin")

        with open("binary1.dat", 'wb') as f:
            f.write(binary_data1)


        binary_to_image(binary_data1, "output_image.jpg")
   

    except Exception as e:
        print("❌ Decoding failed:", str(e))
