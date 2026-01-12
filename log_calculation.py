import os
import pandas as pd
import numpy as np

# --- Please replace with your own paths ---

# Main data folder: parent folder containing all subfolders (e.g., DMNP-30s/NetSample/)
main_data_folder = '/Users/yang/Desktop/MOF Cat data/CCS100 Spectrum Data MOFCat/analysis/15min'

# Define the reference file name
REFERENCE_FILENAME = '0.csv'

# ----------------------------

# 1. Iterate over all items in the main folder
for subfolder_name in os.listdir(main_data_folder):
    # Construct the full path of the current subfolder
    subfolder_path = os.path.join(main_data_folder, subfolder_name)

    # Check whether the current item is a folder
    if not os.path.isdir(subfolder_path):
        continue  # Skip files or other non-folder items

    print(f"\n--- 🚀 Processing folder: **{subfolder_name}** ---")

    # 2. Construct the reference file path for the current group
    reference_file_path = os.path.join(subfolder_path, REFERENCE_FILENAME)

    # Check whether the reference file exists
    if not os.path.exists(reference_file_path):
        print(f"⚠️ Warning: Reference file '{REFERENCE_FILENAME}' not found in folder '{subfolder_name}'. Skipping this folder.")
        continue

    # 3. Read the reference file (used only to obtain row count and column information)
    try:
        reference_df = pd.read_csv(reference_file_path)
        if reference_df.shape[1] < 2:
            print(f"⚠️ Warning: {REFERENCE_FILENAME} has fewer than 2 columns. Skipping this folder.")
            continue
        col2_name = reference_df.columns[1]
        # Extract reference column values for subsequent sample file calculations
        ref_values = reference_df.iloc[:, 1].to_numpy()
        print(f"✅ Reference file loaded: {REFERENCE_FILENAME}, reference column name: {col2_name}")
    except Exception as e:
        print(f"❌ Error while reading reference file {REFERENCE_FILENAME}: {e}. Skipping this folder.")
        continue

    # 4. Iterate over all CSV files in the subfolder
    processed_count = 0
    for filename in os.listdir(subfolder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(subfolder_path, filename)

            # Skip the reference file itself; it will be handled separately after the loop
            if filename == REFERENCE_FILENAME:
                continue

            # Read the current sample file
            try:
                sample_df = pd.read_csv(file_path)
            except Exception as e:
                print(f"❌ Error while reading file {filename}: {e}")
                continue

            # Check whether column structure and row count are consistent
            if list(reference_df.columns) != list(sample_df.columns):
                print(f"⚠️ Skipping {filename}: column names do not match")
                continue
            if len(reference_df) != len(sample_df):
                print(f"⚠️ Skipping {filename}: row count mismatch ({len(reference_df)} vs {len(sample_df)})")
                continue

            # Get current sample values (second column)
            sample_values = sample_df.iloc[:, 1].to_numpy()

            # Initialize result array
            result = np.zeros_like(ref_values, dtype=float)

            # Compute the ratio and take log10 (consistent with original logic)
            with np.errstate(divide='ignore', invalid='ignore'):
                ratio = ref_values / sample_values
                valid = (sample_values != 0) & (ratio > 0)
                result[valid] = np.log10(ratio[valid])

            # Replace the second column of the sample file
            sample_df.iloc[:, 1] = result

            # Save (overwrite)
            sample_df.to_csv(file_path, index=False)
            print(f"  > Processed and overwritten: {filename}")
            processed_count += 1

    # 5. [New step] Process the 0.csv file
    try:
        # Re-read 0.csv
        ref_df_to_update = pd.read_csv(reference_file_path)

        # Replace all values in the second column with 0
        ref_df_to_update.iloc[:, 1] = 0.0

        # Save (overwrite)
        ref_df_to_update.to_csv(reference_file_path, index=False)
        print(f"🎉 Successfully set all values in the second column of '{REFERENCE_FILENAME}' to 0.")

    except Exception as e:
        print(f"❌ Warning: Unable to process or overwrite {REFERENCE_FILENAME}: {e}")

    if processed_count == 0:
        print(f"👉 No additional files were processed in folder '{subfolder_name}'.")
    else:
        print(f"🎉 Folder '{subfolder_name}' processing complete. {processed_count} sample files overwritten.")

print("\n=== ✨ All subfolders have been processed! ===")
