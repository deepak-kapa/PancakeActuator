import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==============================
# EDIT THESE
# ==============================
FOLDER_PATH = "/home/surya/odrive_testing/actuator-testbench/Actuator_Data/CPG_PANCAKE_M6C12_14/endurance eff"

TIME_COL = "time_s"   # <-- ADD THIS
LOADCELL_TORQUE_COL = "loadcell_torque_nm"
TEST_VEL_COL = "test_velocity"
# ==============================


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

    # -------------------------------
    # NEW: Filter between 11–16 sec
    # -------------------------------
    df_window = df[(df[TIME_COL] >= 11.2) & (df[TIME_COL] <= 16)]

    if df_window.empty:
        raise ValueError(f"No data between 11–16s in {csv_path}")

    avg_loadcell_torque = df_window[LOADCELL_TORQUE_COL].mean()
    avg_test_vel_rpm = df_window[TEST_VEL_COL].mean()
    # -------------------------------

    avg_test_vel_rad = rpm_to_rad_per_sec(avg_test_vel_rpm)
    cmd_vel_rad = rpm_to_rad_per_sec(cmd_rpm)

    mech_eff = (avg_loadcell_torque * avg_test_vel_rad) / (
        cmd_torque * cmd_vel_rad
    )

    return mech_eff


def main():
    hours_list = []
    eff_list = []

    for file in os.listdir(FOLDER_PATH):
        if not file.endswith(".csv"):
            continue

        cmd_torque, cmd_rpm, hours = extract_from_filename(file)
        csv_path = os.path.join(FOLDER_PATH, file)

        mech_eff = compute_efficiency(csv_path, cmd_torque, cmd_rpm) 

        hours_list.append(hours)
        eff_list.append(mech_eff)

    hours_list, eff_list = zip(*sorted(zip(hours_list, eff_list)))

    plt.figure(figsize=(8, 6))
    plt.plot(hours_list, eff_list, marker="o")
    plt.xlabel("Time (hours)")
    plt.ylabel("Mechanical Efficiency")
    plt.yticks(np.arange(.9, 1.01, .01))
    plt.xticks(np.arange(1, 13, 1))
    plt.title("CPG_Pancake")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("endurance_eff", dpi=600)


if __name__ == "__main__":
    main()