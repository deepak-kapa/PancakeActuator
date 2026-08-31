import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from pathlib import Path

# Paper-friendly styling: compact figure footprint with larger typography.
PAPER_FIGSIZE = (7.6, 4.6)
TITLE_FONTSIZE = 18
AXIS_LABEL_FONTSIZE = 16
TICK_FONTSIZE = 14
LEGEND_FONTSIZE = 12
RAW_LINEWIDTH = 1.6
RAW_MARKERSIZE = 3
FIT_LINEWIDTH = 2.4

def _fit_line(x, y):
    """Return dict with slope m, intercept b, and R2; None if not enough points."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size < 2:
        return None
    m, b = np.polyfit(x, y, 1)
    yhat = m * x + b
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return {"m": m, "b": b, "r2": r2}

def _read_with_fallback(primary_path, fallback_path):
    """Read CSV from primary path, otherwise fallback path."""
    primary = Path(primary_path)
    fallback = Path(fallback_path)
    if primary.exists():
        print(f"Using: {primary}")
        return pd.read_csv(primary)
    print(f"Primary missing, using fallback: {fallback}")
    return pd.read_csv(fallback)

# Prefer canonical transmission stiffness files (these match published values).
cpg_df = _read_with_fallback(
    r"plots\hardware_results\transmission_stiffness\transmission_stiffness_cpg.csv",
    r"plots\Data Logs\stiffness\cpg_stiffness_20250908_172725.csv"
)
pancake_df = _read_with_fallback(
    r"plots\hardware_results\transmission_stiffness\transmission_stiffness_pancake_cpg.csv",
    r"plots\Data Logs\stiffness\pancake_stiffness_20251223_174012.csv"
)
pancake_without_sun_df = _read_with_fallback(
    r"plots\Data Logs\stiffness\pancake_without_sun_stiffness_20260421_143737.csv",
    r"plots\Data Logs\stiffness\pancake_without_sun_stiffness_20260421_143737.csv"
)

# Divide encoder positions by 14 for CPG and Pancake CPG
cpg_df['encoder_pos_rad'] = cpg_df['encoder_pos_rad'] / 14
pancake_df['encoder_pos_rad'] = pancake_df['encoder_pos_rad'] / 14

# Apply offset correction to CPG to center the data
cpg_max = cpg_df['encoder_pos_rad'].max()
cpg_min = cpg_df['encoder_pos_rad'].min()
cpg_offset = (cpg_max + cpg_min) / 2
cpg_df['encoder_pos_rad'] = cpg_df['encoder_pos_rad'] - cpg_offset

print(f"CPG - Original range: [{cpg_min:.6f}, {cpg_max:.6f}]")
print(f"CPG offset applied: {cpg_offset:.6f}")
print(f"CPG corrected range: [{cpg_df['encoder_pos_rad'].min():.6f}, {cpg_df['encoder_pos_rad'].max():.6f}]")

# Apply offset correction to Pancake CPG to center the data
pancake_max = pancake_df['encoder_pos_rad'].max()
pancake_min = pancake_df['encoder_pos_rad'].min()
pancake_offset = (pancake_max + pancake_min) / 2
pancake_df['encoder_pos_rad'] = pancake_df['encoder_pos_rad'] - pancake_offset

print(f"\nPancake CPG - Original range: [{pancake_min:.6f}, {pancake_max:.6f}]")
print(f"Pancake CPG offset applied: {pancake_offset:.6f}")
print(f"Pancake CPG corrected range: [{pancake_df['encoder_pos_rad'].min():.6f}, {pancake_df['encoder_pos_rad'].max():.6f}]")

# For pancake_without_sun, correct the offset to center the data
# Calculate the max and min encoder positions
max_pos = pancake_without_sun_df['output_pos_rad'].max()
min_pos = pancake_without_sun_df['output_pos_rad'].min()

# Calculate the offset that centers the data
offset = (max_pos + min_pos) / 2

# Apply the offset to center the data
pancake_without_sun_df_corrected = pancake_without_sun_df.copy()
pancake_without_sun_df_corrected['output_pos_rad'] = pancake_without_sun_df['output_pos_rad'] - offset

print(f"\nPancake without sun - Original range: [{min_pos:.6f}, {max_pos:.6f}]")
print(f"Pancake without sun offset applied: {offset:.6f}")
print(f"Pancake without sun corrected range: [{pancake_without_sun_df_corrected['output_pos_rad'].min():.6f}, {pancake_without_sun_df_corrected['output_pos_rad'].max():.6f}]")

def calculate_stiffness(torque, deflection):
    """Calculate forward/backward fits and mean stiffness = (forward + backward) / 2."""
    # Separate positive and negative torques
    pos_mask = torque > 0
    neg_mask = torque < 0
    
    # Forward stiffness (positive torque)
    fit_pos = _fit_line(torque[pos_mask], deflection[pos_mask]) if pos_mask.any() else None
    
    # Backward stiffness (negative torque)
    fit_neg = _fit_line(torque[neg_mask], deflection[neg_mask]) if neg_mask.any() else None

    k_pos = (1.0 / fit_pos["m"]) if (fit_pos is not None and fit_pos["m"] != 0) else np.nan
    k_neg = (1.0 / fit_neg["m"]) if (fit_neg is not None and fit_neg["m"] != 0) else np.nan
    mean_stiffness = (k_pos + k_neg) / 2.0 if (np.isfinite(k_pos) and np.isfinite(k_neg)) else np.nan

    return fit_pos, fit_neg, mean_stiffness

# Create the plot
fig, ax = plt.subplots(figsize=PAPER_FIGSIZE)

# Colors for each actuator
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
datasets = [
    (cpg_df, 'CPG', colors[0]),
    (pancake_df, 'Pancake CPG', colors[1]),
    (pancake_without_sun_df_corrected, 'Pancake CPG (without sun)', colors[2])
]

# Plot all three stiffness curves with slope lines
legend_handles = []
legend_labels = []
for i, (df, label, color) in enumerate(datasets):
    torque = df['output_torque_Nm'].values
    deflection = df['encoder_pos_rad'].values if label != 'Pancake CPG (without sun)' else df['output_pos_rad'].values
    
    # Calculate stiffness values using proper linear fits
    fit_pos, fit_neg, mean_stiffness = calculate_stiffness(torque, deflection)
    avg_stiffness = mean_stiffness if np.isfinite(mean_stiffness) else np.inf
    plot_label = None

    # Plot raw measurements as continuous dashed lines with small dot markers
    line, = ax.plot(
        torque,
        deflection,
        marker='.',
        linestyle='--',
        linewidth=RAW_LINEWIDTH,
        markersize=RAW_MARKERSIZE,
        label=plot_label,
        color=color,
        alpha=0.95
    )

    # Compact legend entries with direct stiffness values.
    if label in ('CPG', 'Pancake CPG', 'Pancake CPG (without sun)'):
        stiffness_text = f"{label}: {avg_stiffness:.0f} Nm/rad" if np.isfinite(avg_stiffness) else f"{label}: inf Nm/rad"
        legend_handles.append(line)
        legend_labels.append(stiffness_text)

    # Bridge the sweep seam near 0 Nm so the curve is continuous at torque ~= 0.
    if torque.size >= 2 and abs(float(torque[0])) <= 0.5 and abs(float(torque[-1])) <= 0.5:
        ax.plot(
            [float(torque[-1]), float(torque[0])],
            [float(deflection[-1]), float(deflection[0])],
            linestyle='--',
            linewidth=RAW_LINEWIDTH,
            color=color,
            alpha=0.95
        )
    
    # Plot slope lines (dashed)
    def draw_fit(fit, torque_subset, color_line):
        if fit is None or torque_subset.size == 0:
            return
        torque_line = np.linspace(float(torque_subset.min()), float(torque_subset.max()), 100)
        deflection_line = fit["m"] * torque_line + fit["b"]
        ax.plot(torque_line, deflection_line, linestyle='--', linewidth=FIT_LINEWIDTH, color=color_line, alpha=0.95)
    
    # Draw fits
    torque_pos = torque[torque > 0]
    torque_neg = torque[torque < 0]
    draw_fit(fit_pos, torque_pos, color)
    draw_fit(fit_neg, torque_neg, color)
    
    # Print stiffness values
    def print_fit(name, fit):
        if fit is None:
            print(f"{name}: not enough points")
        else:
            stiffness = (1.0 / fit["m"]) if fit["m"] != 0 else np.inf
            print(f"{name}: slope={fit['m']:.6f} rad/Nm, intercept={fit['b']:.6f}, R2={fit['r2']:.4f}, "
                  f"stiffness~{stiffness:.2f} Nm/rad")
    
    print(f"\n{label}:")
    print_fit("  Forward", fit_pos)
    print_fit("  Backward", fit_neg)
    if np.isfinite(mean_stiffness):
        print(f"  Mean (F+B)/2 stiffness: {mean_stiffness:.2f} Nm/rad")
    else:
        print("  Mean (F+B)/2 stiffness: not enough points")

ax.set_xlabel('Output Torque (Nm)', fontsize=AXIS_LABEL_FONTSIZE, fontweight='bold')
ax.set_ylabel('Encoder Position (rad)', fontsize=AXIS_LABEL_FONTSIZE, fontweight='bold')
ax.tick_params(axis='both', labelsize=TICK_FONTSIZE)
ax.legend(
    legend_handles,
    legend_labels,
    loc='upper left',
    fontsize=11,
    frameon=True,
    borderpad=0.35,
    labelspacing=0.25,
    handlelength=1.4,
    handletextpad=0.45,
)

plt.tight_layout()
plt.savefig(r'plots\stiffness_comparison.png', dpi=300, bbox_inches='tight')
print("\nPlot saved to plots/stiffness_comparison.png")
plt.show()


