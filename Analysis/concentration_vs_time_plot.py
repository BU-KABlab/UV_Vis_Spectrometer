import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# ======== Path settings ========
input_file = '/Users/yang/Desktop/MOF Cat data/CCS100 Spectrum Data MOFCat/analysis/NH2_3_time-conc-2.csv'  # Change to your concentration data file path
unit = 'μM'

# ======== Read data ========
df = pd.read_csv(input_file)
time_points = df.columns  # e.g. ['30s', '360s', '900s']

# ======== Calculate mean values and 95% confidence intervals ========
means = []
ci_95 = []

for col in df.columns:
    data = df[col].dropna().astype(float)
    mean_val = data.mean()
    sem = stats.sem(data)
    ci = 1.96 * sem  # 95% confidence interval
    means.append(mean_val)
    ci95.append(ci)
    print(f"{col}: Mean concentration = {mean_val:.3f} {unit}, 95% CI = ±{ci:.3f}")

# ======== Plotting ========
x = np.arange(len(time_points))  # x-axis indices

plt.figure(figsize=(8, 6))

# Plot all raw data points (black scatter points)
for i, col in enumerate(df.columns):
    y = df[col].dropna().astype(float)
    plt.scatter(np.full(len(y), x[i]), y, color='black', alpha=0.7, s=40, label='_nolegend_')

# Plot mean values with red error bars
plt.errorbar(x, means, yerr=ci95, fmt='o', capsize=5, elinewidth=2,
             markerfacecolor='red', color='red', ecolor='red', label='Mean ± 95% CI')

# ======== Style adjustments ========
plt.xticks(x, time_points)
plt.xlabel("Time point")
plt.ylabel(f"Concentration ({unit})")
plt.title("Degeneration Product Concentration vs Time for UiO-66-NH2 MOF (300μg/mL)")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.ylim(bottom=0)
plt.tight_layout()
plt.show()
