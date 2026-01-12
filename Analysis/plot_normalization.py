import os
import pandas as pd

# ===== Root input folder to process (contains multiple subfolders) =====
input_root_folder = '/Users/yang/Desktop/EPoN Spectrometer/CCS100 Spectrum Data_R110+citric/analysis/100000'
output_root_folder = '/Users/yang/Desktop/EPoN Spectrometer/R110+citric_normal/100000'

os.makedirs(output_root_folder, exist_ok=True)

# ===== Baseline range =====
baseline_min = 570
baseline_max = 740

# ===== Iterate over all subfolders in the root folder =====
subfolders = [
    name for name in os.listdir(input_root_folder)
    if os.path.isdir(os.path.join(input_root_folder, name)) and not name.startswith(".")
]

print("📁 Detected subfolders:")
for s in subfolders:
    print(" -", s)

print("\nStarting processing...\n")

# ========== Main loop: process each subfolder ==========
for sub in subfolders:

    input_folder = os.path.join(input_root_folder, sub)
    output_folder = os.path.join(output_root_folder, sub)
    os.makedirs(output_folder, exist_ok=True)

    # Get all CSV files in the current subfolder
    files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]

    if not files:
        print(f"⚠ No CSV files found in subfolder {sub}, skipping.")
        continue

    print(f"\n🔷 Processing subfolder: {sub}")

    for fname in files:

        fpath = os.path.join(input_folder, fname)
        df = pd.read_csv(fpath)

        # Assume first column is wavelength, second column is intensity
        wavelength = df.iloc[:, 0]
        intensity = df.iloc[:, 1]

        # Calculate baseline mean
        mask = (wavelength >= baseline_min) & (wavelength <= baseline_max)
        baseline_mean = intensity[mask].mean()

        # Baseline correction
        corrected_intensity = intensity - baseline_mean

        # Build new DataFrame
        corrected_df = pd.DataFrame({
            df.columns[0]: wavelength,
            f"{df.columns[1]} (baseline corrected)": corrected_intensity
        })

        # Save to the corresponding output subfolder
        save_path = os.path.join(output_folder, fname)
        corrected_df.to_csv(save_path, index=False)

        print(f"  ✔ Processed {fname} | baseline mean = {baseline_mean:.4f}")

print("\n🎉 All files have been processed!")
