import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).resolve().parent
SSPG_File1 = BASE_DIR / "cpg_backlash_sine_vel_2.500tps_2.00s.csv"
CPG_File2 = BASE_DIR / "cpg_pancake_sine_vel_2.500tps_2.00s.csv"
OUTPUT_PLOT = BASE_DIR.parent.parent / "backlash_comparison.png"

# Column names
x_col = "time_s"
y_col = "backlash_rad"

# Standardized paper-style formatting (matching other updated plots)
PAPER_FIGSIZE = (7.6, 4.6)
AXIS_LABEL_FONTSIZE = 16
TICK_FONTSIZE = 14
LEGEND_FONTSIZE = 12
LINEWIDTH = 2.6

df_sspg = pd.read_csv(SSPG_File1)
df_cpg = pd.read_csv(CPG_File2)

# Compute averages
avg_sspg = df_sspg[y_col].mean()
avg_cpg = df_cpg[y_col].mean()

max_sspg = df_sspg[y_col].max()
max_cpg = df_cpg[y_col].max()

min_sspg = df_sspg[y_col].min()
min_cpg = df_cpg[y_col].min()

print(f"Average CPG backlash_rad: {avg_sspg:.6f} rad")
print(f"Average Pancake CPG backlash_rad:  {avg_cpg:.6f} rad")

print(f"Maximum CPG backlash_rad: {max_sspg:.6f} rad")
print(f"Maximum Pancake CPG backlash_rad:  {max_cpg:.6f} rad")

print(f"Minimum CPG backlash_rad: {min_sspg:.6f} rad")
print(f"Minimum Pancake CPG backlash_rad:  {min_cpg:.6f} rad")

print(f"CPG backlash_rad: {max_sspg-min_sspg:.6f} rad, {(max_sspg-min_sspg)*(180/np.pi):.6f} deg")
print(f"Pancake CPG backlash_rad:  {max_cpg-min_cpg:.6f} rad, {(max_cpg-min_cpg)*(180/np.pi):.6f} deg")

# Plot
# Sort by time (important!)
df_sspg = df_sspg.sort_values(by=x_col)
df_cpg  = df_cpg.sort_values(by=x_col)

# Plot as continuous lines
plt.figure(figsize=PAPER_FIGSIZE)

plt.plot(df_sspg[x_col], df_sspg[y_col],
         label="CPG (14:1)",
         linewidth=LINEWIDTH,
         color="#1f77b4",
         alpha=0.95)

plt.plot(df_cpg[x_col], df_cpg[y_col],
         label="Pancake CPG (14:1)",
         linewidth=LINEWIDTH,
         color="#ff7f0e",
         alpha=0.95)

# Labels
plt.xlabel("Time (s)", fontsize=AXIS_LABEL_FONTSIZE, fontweight="bold")
plt.ylabel("Backlash (rad)", fontsize=AXIS_LABEL_FONTSIZE, fontweight="bold")

plt.legend(
    fontsize=LEGEND_FONTSIZE,
    loc="upper left",
    frameon=True,
    borderpad=0.35,
    labelspacing=0.25,
    handlelength=1.4,
    handletextpad=0.45,
)
plt.tick_params(axis="both", which="major", labelsize=TICK_FONTSIZE)

plt.tight_layout()
plt.savefig(OUTPUT_PLOT, dpi=300, bbox_inches="tight")
print(f"Plot saved to {OUTPUT_PLOT}")
plt.show()

