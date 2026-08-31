import os

import matplotlib.pyplot as plt
import pandas as pd

# Paper-friendly styling: compact figure footprint with larger typography.
PAPER_FIGSIZE = (7.6, 4.6)
TITLE_FONTSIZE = 18
AXIS_LABEL_FONTSIZE = 16
TICK_FONTSIZE = 14
LEGEND_FONTSIZE = 12
STATS_FONTSIZE = 11
DATA_LINEWIDTH = 2.6
CMD_LINEWIDTH = 2.8

# Define the data directory
data_dir = r"plots\Data Logs\peak torque"

# CSV file paths with labels
csv_files = {
    "CPG": os.path.join(data_dir, "CPG_peak_torque_37.0Nm_20260416_014758.csv"),
    "Pancake CPG": os.path.join(data_dir, "Pancake_peak_torque_37.0Nm_20260418_170953.csv"),
    "Pancake CPG (without sun)": os.path.join(data_dir, "pancake_winthout_sun_peak_torque_37.0Nm_20260424_150804.csv"),
}

# Create figure with 1 subplot
fig, ax1 = plt.subplots(figsize=PAPER_FIGSIZE)

# Color palette
colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

# Plot load cell torques and collect statistics
stats = {}
for (label, filepath), color in zip(csv_files.items(), colors):
    df = pd.read_csv(filepath)
    ax1.plot(df["time_s"], df["loadcell_torque_nm"], label=label, linewidth=DATA_LINEWIDTH, color=color)

    # Calculate peak torque
    peak_torque = df["loadcell_torque_nm"].max()
    peak_time = df[df["loadcell_torque_nm"] == peak_torque]["time_s"].values[0]

    # Find stable region where commanded torque is flat at ~37 Nm.
    flat_region = df[df["cmd_output_torque_nm"] > 36.5]

    if len(flat_region) > 0:
        mean_torque = flat_region["loadcell_torque_nm"].mean()
    else:
        mean_torque = df["loadcell_torque_nm"].mean()

    stats[label] = {
        "peak_torque": peak_torque,
        "peak_time": peak_time,
        "mean_torque": mean_torque,
        "color": color,
    }

# Plot commanded output torque (only once since it's the same for all)
df_first = pd.read_csv(list(csv_files.values())[0])
ax1.plot(
    df_first["time_s"],
    df_first["cmd_output_torque_nm"],
    label="Commanded Output Torque",
    linewidth=CMD_LINEWIDTH,
    color="black",
    linestyle="--",
)

ax1.set_xlabel("Time (s)", fontsize=AXIS_LABEL_FONTSIZE, fontweight="bold")
ax1.set_ylabel("Torque (Nm)", fontsize=AXIS_LABEL_FONTSIZE, fontweight="bold")
ax1.tick_params(axis="both", labelsize=TICK_FONTSIZE)
ax1.legend(loc="best", fontsize=LEGEND_FONTSIZE)

plt.tight_layout()
plt.savefig(r"plots\torque_comparison.png", dpi=300, bbox_inches="tight")
print("Plot saved to plots/torque_comparison.png")
plt.show()

