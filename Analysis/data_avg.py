import os
import pandas as pd

# === Modify paths ===
# Base folder path containing multiple subfolders
base_folder = '/Users/yang/Desktop/EPoN Spectrometer/CCS100 Spectrum Data_R110+citric-2/analysis/100000'

# Output folder
output_folder = '/Users/yang/Desktop/EPoN Spectrometer/R110+Citric/100000'
os.makedirs(output_folder, exist_ok=True)

# Get all subfolders (exclude hidden folders)
subfolders = [os.path.join(base_folder, d) for d in os.listdir(base_folder)
              if os.path.isdir(os.path.join(base_folder, d)) and not d.startswith('.')]

# Get the list of CSV filenames from the first subfolder
reference_folder = subfolders[0]
csv_files = [f for f in os.listdir(reference_folder) if f.endswith('.csv')]

# Compute the average for each CSV filename
for fname in csv_files:
    dfs = []
    for sub in subfolders:
        fpath = os.path.join(sub, fname)
        if os.path.exists(fpath):
            df = pd.read_csv(fpath)
            dfs.append(df)
        else:
            print(f"Warning: {fname} not found in {sub}")

    # Only process if the file exists in at least one subfolder
    if dfs:
        # Assume the first column is Wavelength and the second column is Intensity
        wavelength = dfs[0].iloc[:, 0]
        intensities = [df.iloc[:, 1] for df in dfs]

        # Calculate the mean
        mean_intensity = pd.concat(intensities, axis=1).mean(axis=1)

        # Create the output DataFrame
        avg_df = pd.DataFrame({
            'Wavelength (nm)': wavelength,
            'Mean Intensity (a.u.)': mean_intensity
        })

        # Save the result
        save_path = os.path.join(output_folder, fname)
        avg_df.to_csv(save_path, index=False)

        print(f"Saved averaged file: {save_path}")

print("✅ Averaging completed!")
