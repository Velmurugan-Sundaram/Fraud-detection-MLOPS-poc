#!/usr/bin/env python3
"""
Merge dataset chunks downloaded from GitHub Releases
"""

import pandas as pd
import os
import glob

def merge_dataset_chunks(dataset_dir="dataset", chunk_pattern="creditcard_part_*.csv"):
    """
    Merge all dataset chunks into a single file
    
    Args:
        dataset_dir (str): Directory containing the chunks
        chunk_pattern (str): Pattern to match chunk files
    
    Returns:
        str: Path to the merged file
    """
    
    # Find all chunk files
    chunk_files = glob.glob(os.path.join(dataset_dir, chunk_pattern))
    chunk_files.sort()  # Ensure correct order
    
    if not chunk_files:
        print(f"No chunk files found with pattern: {chunk_pattern}")
        return None
    
    print(f"Found {len(chunk_files)} chunk files:")
    total_size = 0
    for i, filepath in enumerate(chunk_files, 1):
        size_mb = os.path.getsize(filepath) / 1024**2
        total_size += size_mb
        print(f"  {i}. {os.path.basename(filepath)} - {size_mb:.2f} MB")
    
    print(f"Total size of chunks: {total_size:.2f} MB")
    
    # Merge chunks
    print("\nMerging chunks...")
    chunks = []
    for filepath in chunk_files:
        chunk = pd.read_csv(filepath)
        chunks.append(chunk)
    
    merged_df = pd.concat(chunks, ignore_index=True)
    
    # Save merged file
    output_file = os.path.join(dataset_dir, "creditcard.csv")
    merged_df.to_csv(output_file, index=False)
    
    print(f"\nMerged dataset saved to: {output_file}")
    print(f"Merged shape: {merged_df.shape}")
    print(f"Merged size: {merged_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    return output_file

if __name__ == "__main__":
    import sys
    
    dataset_dir = sys.argv[1] if len(sys.argv) > 1 else "dataset"
    chunk_pattern = sys.argv[2] if len(sys.argv) > 2 else "creditcard_part_*.csv"
    
    merge_dataset_chunks(dataset_dir, chunk_pattern)