#!/usr/bin/env python3
"""
Simple dataset merger that doesn't require pandas
"""

import os
import glob

def merge_csv_chunks(dataset_dir="dataset", chunk_pattern="creditcard_part_*.csv", output_file="creditcard.csv"):
    """
    Merge CSV chunks into a single file
    
    Args:
        dataset_dir (str): Directory containing the chunks
        chunk_pattern (str): Pattern to match chunk files
        output_file (str): Name of the output file
    
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
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        total_size += size_mb
        print(f"  {i}. {os.path.basename(filepath)} - {size_mb:.2f} MB")
    
    print(f"Total size of chunks: {total_size:.2f} MB")
    
    # Output file path
    output_path = os.path.join(dataset_dir, output_file)
    
    # Merge chunks
    print("\nMerging chunks...")
    total_lines = 0
    
    with open(output_path, 'w', encoding='utf-8') as outfile:
        first_chunk = True
        
        for i, chunk_file in enumerate(chunk_files, 1):
            print(f"  Processing chunk {i}/{len(chunk_files)}: {os.path.basename(chunk_file)}")
            
            with open(chunk_file, 'r', encoding='utf-8') as infile:
                if first_chunk:
                    # For the first chunk, write everything (including header)
                    for line in infile:
                        outfile.write(line)
                        total_lines += 1
                    first_chunk = False
                else:
                    # For subsequent chunks, skip the header and write only data
                    header_skipped = False
                    for line in infile:
                        if not header_skipped:
                            header_skipped = True
                            continue
                        outfile.write(line)
                        total_lines += 1
    
    # Check final file size
    final_size = os.path.getsize(output_path) / (1024 * 1024)
    
    print(f"\nMerged dataset saved to: {output_path}")
    print(f"Total lines in merged file: {total_lines:,}")
    print(f"Merged size: {final_size:.2f} MB")
    
    return output_path

if __name__ == "__main__":
    import sys
    
    dataset_dir = sys.argv[1] if len(sys.argv) > 1 else "dataset"
    chunk_pattern = sys.argv[2] if len(sys.argv) > 2 else "creditcard_part_*.csv"
    output_file = sys.argv[3] if len(sys.argv) > 3 else "creditcard.csv"
    
    merge_csv_chunks(dataset_dir, chunk_pattern, output_file)