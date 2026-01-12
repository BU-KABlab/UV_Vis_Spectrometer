import os
import pandas as pd

# --- Please replace with your own paths ---

# 1. Main Background folder (minuend)
main_background_folder = '/Users/yang/Desktop/EPoN Spectrometer/R110-modified/600s/back'

# 2. Main Sample folder (subtrahend)
main_sample_folder = '/Users/yang/Desktop/EPoN Spectrometer/R110-modified/600s/sample'

# 3. Main Output folder (result output)
main_output_folder = '/Users/yang/Desktop/EPoN Spectrometer/R110-modified/600s/analysis'

# Ensure the main output folder exists
os.makedirs(main_output_folder, exist_ok=True)

# ----------------------------

# 1. Get all subfolder names in the main Sample folder
# Use the Sample subfolder list as the reference for processing
subfolders_to_process = [
    d for d in os.listdir(main_sample_folder)
    if os.path.isdir(os.path.join(main_sample_folder, d))
]

print(f"--- 🚀 Found {len(subfolders_to_process)} subfolder groups to process ---")

# 2. Iterate over each subfolder name
for subfolder_name in subfolders_to_process:
    # Construct full paths for the current subfolder group
    folder1 = os.path.join(main_background_folder, subfolder_name)  # Background (minuend)
    folder2 = os.path.join(main_sample_folder, subfolder_name)      # Sample (subtrahend)
    output_folder = os.path.join(main_output_folder, subfolder_name)  # NetSample (output)

    # Check whether the Background folder exists (ensure a complete group)
    if not os.path.exists(folder1):
        print(f"\n⚠️ Warning: Background folder '{subfolder_name}' is missing. Skipping this group.")
        continue

    # Ensure the current output subfolder exists
    os.makedirs(output_folder, exist_ok=True)
    print(f"\n✅ Processing folder group: **{subfolder_name}**")

    # 3. Iterate over all CSV files in folder2 (Sample)
    processed_count = 0
    for filename in os.listdir(folder2):
        if filename.endswith('.csv'):
            file1_path = os.path.join(folder1, filename)  # Background file
            file2_path = os.path.join(folder2, filename)  # Sample file

            # Ensure both Background and Sample files exist
            if os.path.exists(file1_path) and os.path.exists(file2_path):
                try:
                    df1 = pd.read_csv(file1_path)
                    df2 = pd.read_csv(file2_path)

                    # Check whether both files have at least two columns
                    if df1.shape[1] < 2 or df2.shape[1] < 2:
                        print(f"⚠️ Fewer than 2 columns detected, skipping: {filename}")
                        continue

                    # Check whether data lengths match (recommended to avoid row mismatch issues)
                    if len(df1) != len(df2):
                        print(f"⚠️ Row count mismatch ({len(df1)} vs {len(df2)}), skipping: {filename}")
                        continue

                    # Copy wavelength / first column
                    result_df = df2.iloc[:, [0]].copy()

                    # Subtraction: Sample second column (index 1) minus Background second column
                    diff = df2.iloc[:, 1] - df1.iloc[:, 1]

                    # Set negative values to 0 (original logic)
                    diff[diff < 0] = 0

                    # Add result as the new second column
                    result_df[df2.columns[1]] = diff

                    # Save file
                    output_path = os.path.join(output_folder, filename)
                    result_df.to_csv(output_path, index=False)
                    # print(f"  > Generated: {filename}")
                    processed_count += 1
                except Exception as e:
                    print(f"❌ Error while processing file {filename}: {e}")
                    continue
            else:
                print(f"⚠️ Missing corresponding file: {filename} (in Background or Sample)")

    print(f"🎉 Group '{subfolder_name}' processing complete. {processed_count} files generated.")

print("\n=== ✨ All subfolder groups have been processed! ===")
