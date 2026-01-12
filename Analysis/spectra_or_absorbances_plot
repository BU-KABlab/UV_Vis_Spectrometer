import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# ==== Modify to your CSV folder path ====
folder_path = '/Users/yang/Desktop/MOF Cat data/CCS100 Spectrum Data MOFCat Calibration/analysis/UiO_66-1'

# Get all CSV files named with numeric values
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

files = [f for f in os.listdir(folder_path) if f.endswith('.csv') and is_number(f[:-4])]

files.sort(key=lambda x: float(x[:-4]))  # Sort by concentration

# Get concentration values
concentrations = [float(f[:-4]) for f in files]
vmin, vmax = min(concentrations), max(concentrations)

# Custom red gradient colormap (gradually increasing saturation)
colors = [(1.0, 0.8 - 0.6 * (i / (len(concentrations)-1)), 0.8 - 0.6 * (i / (len(concentrations)-1)))
          for i in range(len(concentrations))]

# Alternatively, use the Reds colormap from matplotlib (remove the lightest part)
from matplotlib.cm import get_cmap
cmap = get_cmap("Reds")
custom_cmap = [cmap(0.3 + 0.7 * (i / (len(concentrations)-1))) for i in range(len(concentrations))]

# Start plotting
plt.figure(figsize=(12, 6))

for i, fname in enumerate(files):
    conc = float(fname[:-4])
    filepath = os.path.join(folder_path, fname)
    df = pd.read_csv(filepath)

    wavelength = df.iloc[:, 0]
    intensity = df.iloc[:, 1]

    color = custom_cmap[i]
    plt.plot(wavelength, intensity, color=color, linewidth=0.8, label=f"{conc:g} µM")

# Plot formatting
# plt.title("Absorbance vs Wavelength for Different Concentrations", fontsize=14)
plt.title("Absorbance Plot for All Samples", fontsize=14)

plt.xlabel("Wavelength (nm)")
plt.ylabel("Absorbance")
plt.xlim(400, 420)
plt.ylim(0, 1.5)

# # Show only part of the legend (e.g., every 5 concentrations)
# if len(concentrations) > 20:
#     handles, labels = plt.gca().get_legend_handles_labels()
#     plt.legend(handles[::5], labels[::5], title="Concentration", bbox_to_anchor=(1.05, 1), loc='upper left')
# else:
#     plt.legend(title="Concentration", bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()
