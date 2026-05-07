import os
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# =========================
# CONFIG — edit here only
# =========================

ACTUATORS = [
    {
        "label":        "Pancake (14:1)",
        "folder":       "/home/surya/odrive_testing/actuator-testbench/Actuator_Data/CPG_PANCAKE_M6C12_14/efficiency_test_strider_drive",
        "linestyle":    "-",     # solid lines
        "col_speed":    "test_velocity",   # RPM column name (may differ per actuator)
    },
    {
        "label":        "CPG (14:1)",
        "folder":       "/home/surya/odrive_testing/actuator-testbench/Actuator_Data/CPG_Strider/Efficiency_Test_new_driver",
        "linestyle":    "--",    # dashed lines
        "col_speed":    "load_velocity",
    },
]

# Shared column names (override per-actuator above if they differ)
COL_TIME    = "time_s"
COL_TORQUE  = "loadcell_torque_nm"

# Hold-phase time window [start, end) seconds
T_START, T_END = 13, 15

ABS_TORQUE = True
ABS_SPEED  = True

# Plot formatting
FIGSIZE         = (14.0, 5.5)
DPI             = 180
LINEWIDTH       = 1.8
MARKERSIZE      = 5.0
LEGEND_FONTSIZE = 8
GRID_STYLE      = (":", 0.6)
Y_MIN, Y_MAX    = 60, 100
Y_TICKS         = np.arange(60, 101, 5)

SAVE_PATH = "efficiency_comparison.png"
SAVE_DPI  = 300
# =========================


def rpm_to_rad_s(rpm):
    return rpm * 2.0 * math.pi / 60.0


def parse_cmd_from_filename(filename):
    base = os.path.splitext(filename)[0]
    t_str, r_str = base.split("_", 1)
    return float(t_str), float(r_str)   # cmd_torque [Nm], cmd_speed [RPM]


# Shared colormap: one color per unique RPM value across both datasets
all_rpms = set()
actuator_data = []

for act in ACTUATORS:
    by_rpm = defaultdict(list)   # rpm -> [(cmd_torque, mech_eff), ...]
    folder = act["folder"]
    col_speed = act["col_speed"]

    for fn in sorted(os.listdir(folder)):
        if not fn.endswith(".csv"):
            continue
        try:
            cmd_torque, cmd_rpm = parse_cmd_from_filename(fn)
            cmd_speed_rad_s = rpm_to_rad_s(cmd_rpm)

            df  = pd.read_csv(os.path.join(folder, fn))
            win = df[(df[COL_TIME] >= T_START) & (df[COL_TIME] < T_END)]
            if win.empty:
                print(f"  [SKIP] {fn}: empty hold window")
                continue

            avg_torque    = win[COL_TORQUE].mean()
            avg_speed_rpm = win[col_speed].mean()

            if ABS_TORQUE: avg_torque    = abs(avg_torque)
            if ABS_SPEED:  avg_speed_rpm = abs(avg_speed_rpm)

            meas_speed_rad_s = rpm_to_rad_s(avg_speed_rpm)
            denom = cmd_torque * cmd_speed_rad_s

            if denom == 0:
                continue

            mech_eff = (avg_torque * meas_speed_rad_s) / denom * 100.0  # percent

            if np.isnan(mech_eff):
                print(f"  [NaN]  {fn}: skipped")
                continue

            by_rpm[cmd_rpm].append((cmd_torque, mech_eff))
            all_rpms.add(cmd_rpm)

        except Exception as e:
            print(f"  [ERR]  {fn}: {e}")

    actuator_data.append(by_rpm)

# Build color map: same RPM → same color in both subplots
rpms_sorted = sorted(all_rpms)
cmap   = plt.get_cmap("tab10", len(rpms_sorted))
rpm_color = {rpm: cmap(i) for i, rpm in enumerate(rpms_sorted)}

# ---- Plot ----
fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, dpi=DPI, sharey=True)
fig.suptitle("Mechanical Efficiency vs Commanded Torque", fontsize=13, fontweight="bold")

for ax, act, by_rpm in zip(axes, ACTUATORS, actuator_data):
    for rpm in rpms_sorted:
        if rpm not in by_rpm:
            continue
        pts = sorted(by_rpm[rpm], key=lambda x: x[0])
        torques = [p[0] for p in pts]
        effs    = [p[1] for p in pts]

        ax.plot(
            torques, effs,
            marker='o' if act["linestyle"] == "-" else 's',
            linestyle=act["linestyle"],
            linewidth=LINEWIDTH,
            markersize=MARKERSIZE,
            color=rpm_color[rpm],
            label=f"{int(rpm)} rpm",
        )

    ax.set_title(act["label"], fontsize=11, fontweight="bold")
    ax.set_xlabel("Commanded Torque (Nm)", fontsize=10)
    ax.set_ylabel("Mechanical Efficiency (%)", fontsize=10)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.set_yticks(Y_TICKS)
    ax.grid(True, which="both", linestyle=GRID_STYLE[0], linewidth=GRID_STYLE[1])
    ax.legend(fontsize=LEGEND_FONTSIZE, frameon=True, loc="lower right")

plt.tight_layout()
plt.savefig(SAVE_PATH, dpi=SAVE_DPI, bbox_inches="tight")
print(f"Saved: {SAVE_PATH}")