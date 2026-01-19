import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# === Set paths ===
data_folder = '/Users/yang/Desktop/MOF Cat data/CCS100 Spectrum Data MOFCat Calibration/analysis/UiO_66-1'
output_file = '/Users/yang/Desktop/MOF Cat data/CCS100 Spectrum Data MOFCat Calibration/analysis/best_wavelength.csv'

# === Manually set wavelength range for calculation ===
target_range = (400, 420)  # Search for the best wavelength only within this range

# === Manually set window size for wavelength averaging
window = 5
# Half window must be an integer
half_window = np.floor(window/2)

# === Step 1: Get all sample files and concentrations, and add the (0, 0) data point ===
# === Step 1: Get all sample files and concentrations, and add the (0, 0) data point ===

# Check whether the filename is numeric (integer or float)
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# Filter: filenames must be numeric
sample_files = sorted(
    [f for f in os.listdir(data_folder) if f.endswith('.csv') and is_number(os.path.splitext(f)[0])],
    key=lambda x: float(os.path.splitext(x)[0])
)

# Original concentrations (float)
concentrations_original = np.array([float(os.path.splitext(f)[0]) for f in sample_files])

# Add zero concentration
concentrations_all = np.insert(concentrations_original, 0, 0.0)

abs_matrix = []
wavelengths = None

for file in sample_files:
    path = os.path.join(data_folder, file)
    df = pd.read_csv(path)
    df = df.sort_values(by=df.columns[0]).reset_index(drop=True)

    if wavelengths is None:
        wavelengths = df.iloc[:, 0].values  # wavelength

    abs_matrix.append(df.iloc[:, 1].values)

abs_matrix_original = np.array(abs_matrix)

# For each wavelength, insert a row of zeros at the beginning of the absorbance matrix
# (representing zero absorbance at zero concentration)
abs_matrix = np.insert(abs_matrix_original, 0, 0, axis=0)
wavelengths = np.array(wavelengths)

# === Step 2: Residual-based linear fitting (restricted wavelength range) ===
r2_scores = []
mean_abs = []
valid_conc_list = []
valid_abs_list = []
models = []

# Get indices corresponding to the wavelength range
wl_mask = (wavelengths >= target_range[0]) & (wavelengths <= target_range[1])
indices_to_check = np.where(wl_mask)[0]

# Note: since (0, 0) has already been added, filtering abs_values > 0 is no longer needed

for i in range(len(wavelengths)):
    if i not in indices_to_check:
        r2_scores.append(0)
        mean_abs.append(0)
        valid_conc_list.append([])
        valid_abs_list.append([])
        models.append(None)
        continue

    # Window bounds centered around index i and extend by half_window. 
    #   +1 due to python indexing cutting off last value in window
    i_min = max(0, i - half_window)
    i_max = min(len(wavelengths), i + half_window + 1)

    # Mean computed over range of wavelengths for robustness
    abs_values = np.mean(abs_matrix[:, i_min:i_max], axis=1)

    conc_values = concentrations_all

    # In this modified version, absorbance <= 0 points are not filtered
    abs_valid = abs_values
    conc_valid = conc_values

    # Although (0,0) ensures at least one point, keep a minimum of 2 points for safety
    if len(abs_valid) < 2:
        r2_scores.append(0)
        mean_abs.append(0)
        valid_conc_list.append([])
        valid_abs_list.append([])
        models.append(None)
        continue

    X = conc_valid.reshape(-1, 1)
    y = abs_valid.reshape(-1, 1)

    # First fit (including all data, including (0,0))
    model = LinearRegression().fit(X, y)
    y_pred = model.predict(X)
    residuals = (y - y_pred).flatten()
    std_res = np.std(residuals)

    # Residual filtering ((0,0) also participates in residual calculation and filtering)
    inlier_mask = np.abs(residuals) <= 2 * std_res
    X_inliers = X[inlier_mask]
    y_inliers = y[inlier_mask]

    if len(y_inliers) < 2:
        r2_scores.append(0)
        mean_abs.append(0)
        valid_conc_list.append([])
        valid_abs_list.append([])
        models.append(None)
        continue

    # Second fit (inliers only, including (0,0) if it is an inlier)
    model2 = LinearRegression().fit(X_inliers, y_inliers)
    r2_scores.append(model2.score(X_inliers, y_inliers))
    mean_abs.append(np.mean(y_inliers))
    valid_conc_list.append(X_inliers.flatten())
    valid_abs_list.append(y_inliers.flatten())
    models.append(model2)

r2_array = np.array(r2_scores)
mean_abs_array = np.array(mean_abs)

# === Step 3: Find the best wavelength ===
# (Logic unchanged, but candidate data now include (0,0) or its residual-filtered version)
min_r2_threshold = 0.9
threshold_abs_min = 0.00
threshold_abs_max = 2.0

candidates = [
    (i, wavelengths[i], r2_array[i], mean_abs_array[i], len(valid_conc_list[i]))
    for i in indices_to_check
    if (
            r2_array[i] >= min_r2_threshold and
            threshold_abs_min < mean_abs_array[i] < threshold_abs_max and
            len(valid_conc_list[i]) >= 5
    )
]

if not candidates:
    raise RuntimeError("No wavelength meets all conditions in the specified range.")

# Best wavelength selection logic: maximize sample count first, then maximize R²
best_idx, best_wavelength, best_r2, best_mean_abs, _ = max(
    candidates, key=lambda x: (x[4], x[2])
)

# === Step 4: Save the best result ===
col_name = 'Absorbance at {:.3f} nm'.format(best_wavelength)
df_out = pd.DataFrame({
    'Concentration (µg/mL)': valid_conc_list[best_idx],
    col_name: valid_abs_list[best_idx]
})
df_out.to_csv(output_file, index=False)

print("Best wavelength: {:.3f} nm".format(best_wavelength))
print("R² = {:.4f}, Avg absorbance = {:.4f}".format(best_r2, best_mean_abs))
print("Result saved: {}".format(output_file))
print("Number of valid samples = {}".format(len(valid_conc_list[best_idx])))

# === Step 5: Plot R² distribution (only wavelengths within the range) ===
plt.figure(figsize=(10, 6))
plt.plot(wavelengths[wl_mask], r2_array[wl_mask], label='R² vs Wavelength')
plt.axvline(best_wavelength, color='red', linestyle='--', label='Best λ')
plt.xlim(target_range[0], target_range[1])
plt.xlabel('Wavelength (nm)')
plt.ylabel('R²')
plt.title('Linearity after Residual Filtering (Specified Range)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


# === Step 6: Plot best-wavelength fit (scatter plot) ===
def plot_fit(idx):
    X = valid_conc_list[idx]
    y = valid_abs_list[idx]
    model = models[idx]
    if model is None or len(X) == 0:
        print("No valid data for this wavelength.")
        return

    # Locate the (0,0) point
    is_zero_zero = (X == 0) & (y == 0)

    # Separate the (0,0) point from other points
    X_zero = X[is_zero_zero]
    y_zero = y[is_zero_zero]
    X_other = X[~is_zero_zero]
    y_other = y[~is_zero_zero]

    X_for_predict = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
    y_pred = model.predict(X_for_predict)

    slope = model.coef_[0][0]
    intercept = model.intercept_[0]
    r2 = model.score(X.reshape(-1, 1), y)

    plt.figure(figsize=(8, 6))

    # Plot non-(0,0) points
    plt.scatter(X_other, y_other, color='blue', label='Data Points (Non-Zero)')
    # Highlight the (0,0) point
    if len(X_zero) > 0:
        plt.scatter(X_zero, y_zero, color='green', marker='D', s=80, label='(0, 0) Point')

    plt.plot(X_for_predict, y_pred, color='red',
             label='y = {:.4f}x + {:.4f}\nR² = {:.4f}'.format(slope, intercept, r2))
    plt.xlabel('Concentration (µM)')
    plt.ylabel('Absorbance')
    plt.title('Linear Fit at {:.3f} nm'.format(wavelengths[idx]))
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


plot_fit(best_idx)

# === Step 7: Interactive inspection of other wavelengths (within range only) ===
while True:
    user_input = input("\nEnter another wavelength to view (or press Enter to exit): ").strip()
    if not user_input:
        print("Exit.")
        break
    try:
        target_wl = float(user_input)
        closest_idx = np.argmin(np.abs(wavelengths - target_wl))
        if not (target_range[0] <= wavelengths[closest_idx] <= target_range[1]):
            print("Wavelength {:.3f} nm is outside the specified range.".format(wavelengths[closest_idx]))
            continue
        print("Closest wavelength: {:.3f} nm".format(wavelengths[closest_idx]))
        plot_fit(closest_idx)
    except ValueError:
        print("Invalid input. Try again.")
