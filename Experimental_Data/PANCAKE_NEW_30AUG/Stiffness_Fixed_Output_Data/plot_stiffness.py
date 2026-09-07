#!/usr/bin/env python3
# plot_stiffness.py
# Plots encoder deflection vs output torque from one or two stiffness_test CSVs.
# Adds linear regression lines for positive and negative torque regions.

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ============ CONFIG ============
# Set CSV_FILE_2 = None to plot only one file.
CSV_FILE_1 = "/home/surya/odrive_testing/actuator-testbench/Actuator_Data/Pancake_NEW_2SEP/Stiffness_Fixed_Output/stiffness_20260905_222755.csv"
CSV_FILE_2 = None  # "../Actuator_Data/Stiffness_Test/stiffness_2.csv"

LABEL_1 = "Actuator 1"
LABEL_2 = "Actuator 2"
COLOR_1 = "blue"
COLOR_2 = "red"

GEAR_RATIO = 14  # divide encoder_pos_rad by this to get output deflection

OUT_PNG = "stiffness.png"
# =================================

X_COL = "output_torque_Nm"
Y_COL = "encoder_pos_rad"


def load_and_plot(ax, csv_path, label, color):
    df = pd.read_csv(csv_path)

    for col in [X_COL, Y_COL]:
        if col not in df.columns:
            raise ValueError(f"{csv_path} is missing column '{col}'. Found: {list(df.columns)}")

    x = df[X_COL].values
    y = df[Y_COL].values / GEAR_RATIO

    ax.plot(x, y, color=color, linewidth=1.5, alpha=0.7, label=label)

    for mask, label_suffix in [(x > 0, "pos fit"), (x < 0, "neg fit")]:
        xm, ym = x[mask], y[mask]
        if len(xm) > 1:
            m, b = np.polyfit(xm, ym, 1)
            xf = np.linspace(xm.min(), xm.max(), 100)
            ax.plot(xf, m * xf + b, color=color, linestyle=":", linewidth=2)


def main():
    fig, ax = plt.subplots(figsize=(8, 6))

    load_and_plot(ax, CSV_FILE_1, LABEL_1, COLOR_1)
    if CSV_FILE_2:
        load_and_plot(ax, CSV_FILE_2, LABEL_2, COLOR_2)

    ax.set_xlabel("Output Torque [Nm]")
    ax.set_ylabel("Output Deflection [rad]")
    ax.set_title("Stiffness: Encoder Deflection vs Output Torque")
    ax.grid(True)
    ax.legend()
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
