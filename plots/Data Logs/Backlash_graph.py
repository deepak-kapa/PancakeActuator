#!/usr/bin/env python3
# plot_backlash.py

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np   # use numpy instead of deprecated pd.np

# ============ CONFIG ============
CSV_FILE = "../Actuator_Data/CPG_MAD_M6C12_14/CPG_MAD_M6C12_14_BACKLASH_DATA/sine_vel_2.500tps_2.00s_processed.csv"     # path to your CSV
TIME_COL = "time_s"            # x-axis column
BACKLASH_COL = "backlash_rad"  # y-axis column
OUT_PNG = "../Actuator_Data/CPG_MAD_M6C12_14/CPG_MAD_M6C12_14_PLOTS/CPG_Backlash_2.5.png"  # output image file name

# Plot appearance
POINT_SIZE = 8      # size of scatter points
X_TICK_STEP = 0.5   # step size for x-axis ticks (set None for auto)
Y_TICK_STEP = 0.1   # step size for y-axis ticks (set None for auto)
# =================================

def main():
    # Load CSV
    df = pd.read_csv(CSV_FILE)

    if TIME_COL not in df.columns or BACKLASH_COL not in df.columns:
        raise ValueError(f"CSV must have '{TIME_COL}' and '{BACKLASH_COL}' columns")

    x = df[TIME_COL]
    y = df[BACKLASH_COL]

    # Create scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, s=POINT_SIZE, c="blue", alpha=0.7, label="Backlash")

    plt.xlabel("Time [s]")
    plt.ylabel("Backlash [rad]")
    plt.title("Backlash vs Time")
    # plt.legend()

    # Control ticks
    plt.xlim(x.min(), x.max())
    plt.ylim(y.min(), y.max())

    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()

    # Save and notify
    plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    print(f"Saved plot as: {OUT_PNG}")

if __name__ == "__main__":
    main()
