import glob
import os
import subprocess

os.chdir("")
# Base path configurations
base_dir = "./assembly_results"
output_base = "./RGI_batch_results"

# Create output directory
if not os.path.exists(output_base):
    os.makedirs(output_base)

# Automatically get all scaffolds.fasta paths for each sample
# Expected directory structure: assembly_results/SAMPLE_output/scaffolds.fasta
fasta_files = glob.glob(os.path.join(base_dir, "*_output", "scaffolds.fasta"))

print(f"Found {len(fasta_files)} samples to process...")

for fasta_path in fasta_files:
    # Extract sample name from path, e.g., 'AB-6' from 'AB-6_output'
    sample_name = os.path.basename(os.path.dirname(fasta_path)).replace(
        "_output", ""
    )
    output_path = os.path.join(output_base, f"{sample_name}_RGI")

    # Check if already processed to avoid re-running
    if os.path.exists(f"{output_path}.txt"):
        print(f"Skipping existing sample: {sample_name}")
        continue

    # Construct RGI command
    # --num_threads: Adjust thread count based on your server configuration
    cmd = [
        "rgi",
        "main",
        "--input_sequence",
        fasta_path,
        "--output_file",
        output_path,
        "--input_type",
        "contig",
        "--local",
        "--num_threads",
        "8",
        "--clean",
    ]

    try:
        print(f"Analyzing sample: {sample_name}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Analysis failed for sample {sample_name}: {e}")

print("All samples processed.")
