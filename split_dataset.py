#!/usr/bin/env python3
"""
Split large dataset file into smaller chunks for GitHub Releases
"""

import pandas as pd
import os
import math

def split_dataset(input_file, output_dir, max_size_mb=20):
    """
    Split a large CSV file into smaller chunks
    
    Args:
        input_file (str): Path to the large CSV file
        output_dir (str): Directory to save the chunks
        max_size_mb (int): Maximum size per chunk in MB
    """
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the dataset
    print(f"Reading dataset from {input_file}...")
    df = pd.read_csv(input_file)
    total_rows = len(df)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Total size: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Calculate rows per chunk based on size
    # Estimate: each row is roughly (total_size_mb / total_rows) MB
    estimated_row_size_mb = (df.memory_usage(deep=True).sum() / 1024**2) / total_rows
    rows_per_chunk = max(1, int((max_size_mb * 0.8) / estimated_row_size_mb))  # Use 80% of max size
    
    print(f"Estimated row size: {estimated_row_size_mb:.4f} MB")
    print(f"Rows per chunk: {rows_per_chunk}")
    
    # Calculate number of chunks
    num_chunks = math.ceil(total_rows / rows_per_chunk)
    print(f"Number of chunks needed: {num_chunks}")
    
    # Split and save chunks
    chunk_files = []
    for i in range(num_chunks):
        start_idx = i * rows_per_chunk
        end_idx = min((i + 1) * rows_per_chunk, total_rows)
        
        chunk = df.iloc[start_idx:end_idx]
        chunk_filename = f"creditcard_part_{i+1:03d}.csv"
        chunk_path = os.path.join(output_dir, chunk_filename)
        
        chunk.to_csv(chunk_path, index=False)
        
        # Check file size
        file_size_mb = os.path.getsize(chunk_path) / 1024**2
        print(f"Chunk {i+1}/{num_chunks}: {chunk_filename} - {file_size_mb:.2f} MB")
        
        chunk_files.append(chunk_filename)
    
    # Create a manifest file
    manifest_path = os.path.join(output_dir, "dataset_manifest.txt")
    with open(manifest_path, 'w') as f:
        f.write(f"Dataset: {input_file}\n")
        f.write(f"Total rows: {total_rows}\n")
        f.write(f"Number of chunks: {num_chunks}\n")
        f.write(f"Max size per chunk: {max_size_mb} MB\n\n")
        f.write("Chunks:\n")
        for i, filename in enumerate(chunk_files, 1):
            f.write(f"{i}. {filename}\n")
    
    print(f"\nManifest saved to: {manifest_path}")
    print(f"All chunks saved to: {output_dir}")
    
    return chunk_files

def merge_chunks(input_dir, output_file):
    """
    Merge split chunks back into a single file
    
    Args:
        input_dir (str): Directory containing the chunks
        output_file (str): Path to save the merged file
    """
    
    # Find all chunk files
    chunk_files = [f for f in os.listdir(input_dir) if f.startswith('creditcard_part_') and f.endswith('.csv')]
    chunk_files.sort()  # Ensure correct order
    
    if not chunk_files:
        print("No chunk files found!")
        return
    
    print(f"Found {len(chunk_files)} chunk files:")
    for i, filename in enumerate(chunk_files, 1):
        print(f"  {i}. {filename}")
    
    # Merge chunks
    print("\nMerging chunks...")
    merged_df = pd.concat([pd.read_csv(os.path.join(input_dir, f)) for f in chunk_files])
    
    # Save merged file
    merged_df.to_csv(output_file, index=False)
    
    print(f"Merged dataset saved to: {output_file}")
    print(f"Merged shape: {merged_df.shape}")
    print(f"Merged size: {merged_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python split_dataset.py split <input_file> [output_dir] [max_size_mb]")
        print("  python split_dataset.py merge <input_dir> <output_file>")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "split":
        input_file = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else "dataset_chunks"
        max_size_mb = int(sys.argv[4]) if len(sys.argv) > 4 else 20
        
        split_dataset(input_file, output_dir, max_size_mb)
        
    elif action == "merge":
        input_dir = sys.argv[2]
        output_file = sys.argv[3]
        
        merge_chunks(input_dir, output_file)
        
    else:
        print("Invalid action. Use 'split' or 'merge'")
        sys.exit(1)