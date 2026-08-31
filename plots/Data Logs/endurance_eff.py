import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ==============================
# Data sources
# ==============================
CPG_FOLDER_PATH = r"plots\Data Logs\Endurance\CPG_Endurance_data"
PANCAKE_FOLDER_PATH = r"plots\Data Logs\Endurance\CPG_Pancake_Endurance_data"

CPG_FOLDER_FALLBACK = "/home/surya/odrive_testing/actuator-testbench/Actuator_Data/CPG_M6C12_14/endurance eff"
PANCAKE_FOLDER_FALLBACK = "/home/surya/odrive_testing/actuator-testbench/Actuator_Data/CPG_PANCAKE_M6C12_14/endurance eff"

TIME_COL = "time_s"
LOADCELL_TORQUE_COL = "loadcell_torque_nm"
TEST_VEL_COL = "test_velocity"

# Standardized paper style (same direction as stiffness/torque plots)
PAPER_FIGSIZE = (7.6, 4.6)
AXIS_LABEL_FONTSIZE = 16
TICK_FONTSIZE = 14
LINEWIDTH = 2.6
MARKERSIZE = 5


def resolve_folder_path(primary_path, fallback_path):
    primary = Path(primary_path)
    if primary.exists():
        return primary
    fallback = Path(fallback_path)
    if fallback.exists():
        return fallback
    raise FileNotFoundError(
        f"Endurance data folder not found: '{primary}' or '{fallback}'"
    )


def rpm_to_rad_per_sec(rpm):
    return rpm * 2 * np.pi / 60.0


def extract_from_filename(filename):
    name = os.path.splitext(filename)[0]
    parts = name.split("_")

    cmd_torque = float(parts[0])
    cmd_rpm = float(parts[1])
    hours = float(parts[2])

    return cmd_torque, cmd_rpm, hours


def compute_efficiency(csv_path, cmd_torque, cmd_rpm):
    df = pd.read_csv(csv_path)

    # Use the stable section between 11.2 s and 16.0 s.
    df_window = df[(df[TIME_COL] >= 11.2) & (df[TIME_COL] <= 16.0)]

    if df_window.empty:
        raise ValueError(f"No data between 11.2-16.0 s in {csv_path}")

    avg_loadcell_torque = df_window[LOADCELL_TORQUE_COL].mean()
    avg_test_vel_rpm = df_window[TEST_VEL_COL].mean()

    avg_test_vel_rad = rpm_to_rad_per_sec(avg_test_vel_rpm)
    cmd_vel_rad = rpm_to_rad_per_sec(cmd_rpm)

    mech_eff = (avg_loadcell_torque * avg_test_vel_rad) / (
        cmd_torque * cmd_vel_rad
    )

    return mech_eff


def load_efficiency_vs_hours(data_folder):
    hours_list = []
    eff_list = []

    for file in os.listdir(data_folder):
        if not file.endswith(".csv"):
            continue

        cmd_torque, cmd_rpm, hours = extract_from_filename(file)
        csv_path = os.path.join(data_folder, file)

        mech_eff = compute_efficiency(csv_path, cmd_torque, cmd_rpm)

        hours_list.append(hours)
        eff_list.append(mech_eff)

    # Sort points by hour.
    pairs = sorted(zip(hours_list, eff_list))
    if not pairs:
        raise ValueError(f"No CSV files found in {data_folder}")
    hours_sorted, eff_sorted = zip(*pairs)
    return list(hours_sorted), list(eff_sorted)


def main():
    cpg_folder = resolve_folder_path(CPG_FOLDER_PATH, CPG_FOLDER_FALLBACK)
    pancake_folder = resolve_folder_path(PANCAKE_FOLDER_PATH, PANCAKE_FOLDER_FALLBACK)

    cpg_hours, cpg_eff = load_efficiency_vs_hours(cpg_folder)
    pancake_hours, pancake_eff = load_efficiency_vs_hours(pancake_folder)

    plt.figure(figsize=PAPER_FIGSIZE)
    plt.plot(
        cpg_hours,
        cpg_eff,
        marker="o",
        linewidth=LINEWIDTH,
        markersize=MARKERSIZE,
        color="#1f77b4",
        alpha=0.95,
        label="CPG",
    )
    plt.plot(
        pancake_hours,
        pancake_eff,
        marker="o",
        linewidth=LINEWIDTH,
        markersize=MARKERSIZE,
        color="#ff7f0e",
        alpha=0.95,
        label="Pancake CPG",
    )
    plt.xlabel("Time (hours)", fontsize=AXIS_LABEL_FONTSIZE, fontweight="bold")
    plt.ylabel("Mechanical Efficiency", fontsize=AXIS_LABEL_FONTSIZE, fontweight="bold")
    plt.tick_params(axis="both", labelsize=TICK_FONTSIZE)
    plt.yticks(np.arange(0.9, 1.01, 0.01))
    plt.xticks(np.arange(1, 13, 1))
    plt.legend(
        loc="upper left",
        fontsize=11,
        frameon=True,
        borderpad=0.35,
        labelspacing=0.25,
        handlelength=1.4,
        handletextpad=0.45,
    )
    plt.tight_layout()
    plt.savefig(r"plots\endurance_eff.png", dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
