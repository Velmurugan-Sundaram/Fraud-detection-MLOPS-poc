#!/usr/bin/env python3
"""
Simple dataset splitter that doesn't require pandas
"""

import os
import math

def split_csv_file(input_file, output_dir, max_size_mb=20):
    """
    Split a CSV file into smaller chunks
    
    Args:
        input_file (str): Path to the large CSV file
        output_dir (str): Directory to save the chunks
        max_size_mb (int): Maximum size per chunk in MB
    """
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get file size
    file_size = os.path.getsize(input_file)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"Input file: {input_file}")
    print(f"File size: {file_size_mb:.2f} MB")
    print(f"Target chunk size: {max_size_mb} MB")
    
    # Calculate approximate number of lines per chunk
    # Read first few lines to estimate line size
    with open(input_file, 'r', encoding='utf-8') as f:
        header = f.readline()
        sample_lines = []
        for i in range(100):  # Read 100 sample lines
            line = f.readline()
            if not line:
                break
            sample_lines.append(line)
    
    # Estimate average line size
    if sample_lines:
        avg_line_size = sum(len(line.encode('utf-8')) for line in sample_lines) / len(sample_lines)
    else:
        print("File appears to be empty!")
        return []
    
    # Calculate lines per chunk
    target_bytes_per_chunk = max_size_mb * 1024 * 1024 * 0.9  # Use 90% of target
    lines_per_chunk = max(1, int(target_bytes_per_chunk / avg_line_size))
    
    print(f"Estimated average line size: {avg_line_size:.2f} bytes")
    print(f"Lines per chunk: {lines_per_chunk}")
    
    # Count total lines
    with open(input_file, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f)
    
    print(f"Total lines: {total_lines}")
    
    # Calculate number of chunks
    num_chunks = math.ceil((total_lines - 1) / lines_per_chunk)  # -1 for header
    print(f"Number of chunks needed: {num_chunks}")
    
    # Split the file
    chunk_files = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        # Read header
        header = f.readline()
        
        for chunk_num in range(num_chunks):
            chunk_filename = f"creditcard_part_{chunk_num+1:03d}.csv"
            chunk_path = os.path.join(output_dir, chunk_filename)
            
            with open(chunk_path, 'w', encoding='utf-8') as chunk_file:
                # Write header to each chunk
                chunk_file.write(header)
                
                # Write lines for this chunk
                for i in range(lines_per_chunk):
                    line = f.readline()
                    if not line:
                        break
                    chunk_file.write(line)
            
            # Check chunk size
            chunk_size = os.path.getsize(chunk_path) / (1024 * 1024)
            print(f"Chunk {chunk_num+1}/{num_chunks}: {chunk_filename} - {chunk_size:.2f} MB")
            chunk_files.append(chunk_filename)
    
    # Create manifest
    manifest_path = os.path.join(output_dir, "dataset_manifest.txt")
    with open(manifest_path, 'w') as f:
        f.write(f"Dataset: {input_file}\n")
        f.write(f"Total lines: {total_lines}\n")
        f.write(f"Number of chunks: {num_chunks}\n")
        f.write(f"Max size per chunk: {max_size_mb} MB\n\n")
        f.write("Chunks:\n")
        for i, filename in enumerate(chunk_files, 1):
            f.write(f"{i}. {filename}\n")
    
    print(f"\nManifest saved to: {manifest_path}")
    print(f"All chunks saved to: {output_dir}")
    
    return chunk_files

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python simple_split.py <input_file> <output_dir> [max_size_mb]")
        print("Example: python simple_split.py dataset/creditcard.csv dataset_chunks 20")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    max_size_mb = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        sys.exit(1)
    
    split_csv_file(input_file, output_dir, max_size_mb)