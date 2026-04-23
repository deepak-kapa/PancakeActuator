import os
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# =========================
# CONFIG — edit here only
# =========================
INPUT_FOLDER = "C:/Users/jvira/Documents/Actuator_Optimization_3D_printed/Actuator_Optimization_3D_printed/plots/hardware_results/pancake/CPG_PANCAKE_M6C12_14/efficiency test_parsed"          # folder with files named "<torque>_<rpm>.csv"

# Column names in your CSVs (RPM in CSV for speed; we convert to rad/s)
COL = {
    "time": "time_s",
    "meas_torque": "loadcell_torque_nm",
    "meas_speed_rpm": "test_velocity",   # measured speed in RPM (CSV); will convert to rad/s
    "voltage": "test_voltage",
    "phase_current": "test_current",
}

# Time window [start, end) for averaging (seconds)
T_START, T_END = 14.0, 19.0

# Handle signs from opposing motors etc.
ABS_TORQUE = True
ABS_SPEED = True

# Plot formatting
FIGSIZE = (8.0, 5.0)
DPI = 180
LINEWIDTH = 1.6
MARKERSIZE = 4.5
LEGEND_FONTSIZE = 9
GRID_STYLE = (":", 0.7)

# Show efficiencies as 0-1 (False) or 0-100% (True)
PLOT_AS_PERCENT = True
# =========================


def rpm_to_rad_s(rpm: float) -> float:
    return (rpm * 2.0 * math.pi) / 60.0


def parse_cmd_from_filename(filename: str):
    """
    Expect '<torque>_<rpm>.csv' where:
      torque => commanded torque [Nm]
      rpm    => commanded speed [RPM]
    Returns: (cmd_torque [Nm], cmd_speed_rad_s [rad/s])
    """
    base = os.path.splitext(filename)[0]
    t_str, r_str = base.split("_", 1)
    cmd_torque = float(t_str)
    cmd_speed_rad_s = rpm_to_rad_s(float(r_str))
    return cmd_torque, cmd_speed_rad_s


# Collect per-commanded speed series: speed_rad_s -> list of (cmd_torque, mech_eff, total_eff)
by_speed = defaultdict(list)

for fn in os.listdir(INPUT_FOLDER):
    if not fn.endswith(".csv"):
        continue

    try:
        cmd_torque, cmd_speed_rad_s = parse_cmd_from_filename(fn)

        # Load CSV
        path = os.path.join(INPUT_FOLDER, fn)
        df = pd.read_csv(path)

        # Guard: required columns
        required = [COL["time"], COL["meas_torque"], COL["meas_speed_rpm"], COL["voltage"], COL["phase_current"]]
        if not all(c in df.columns for c in required):
            print(f"Skipping {fn}: missing one of required columns {required}")
            continue

        # Time window
        win = df[(df[COL["time"]] >= T_START) & (df[COL["time"]] < T_END)]
        if win.empty:
            print(f"Skipping {fn}: no samples in {T_START}-{T_END}s")
            continue

        # Averages in window
        avg_torque = win[COL["meas_torque"]].mean()
        avg_speed_rpm = win[COL["meas_speed_rpm"]].mean()
        avg_v = win[COL["voltage"]].mean()
        avg_i = win[COL["phase_current"]].mean()

        if ABS_TORQUE:
            avg_torque = abs(avg_torque)
        if ABS_SPEED:
            avg_speed_rpm = abs(avg_speed_rpm)

        # Convert measured speed to rad/s
        meas_speed_rad_s = rpm_to_rad_s(avg_speed_rpm)

        # Denominators
        denom_mech = cmd_torque * cmd_speed_rad_s
        denom_elec = avg_v * avg_i

        # Compute efficiencies (guard divide-by-zero)
        mech_eff = (avg_torque * meas_speed_rad_s  ) / denom_mech if denom_mech != 0 else np.nan
        total_eff = (avg_torque * meas_speed_rad_s  ) / denom_elec if denom_elec != 0 else np.nan

        # Optional: scale to percent for plotting
        if PLOT_AS_PERCENT:
            mech_eff *= 100.0
            total_eff *= 100.0

        # Store
        by_speed[cmd_speed_rad_s].append((cmd_torque, mech_eff, total_eff))

    except Exception as e:
        print(f"Skipping {fn}: {e}")

# ---- Plot ----
# ---- Plot ----
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)

# Make sure each speed gets consistent color
from itertools import cycle
import matplotlib.cm as cm

speeds_sorted = sorted(by_speed.keys())
colors = cm.get_cmap("tab10", len(speeds_sorted))  # distinct colors

for idx, speed_rad_s in enumerate(speeds_sorted):
    pts_sorted = sorted(by_speed[speed_rad_s], key=lambda x: x[0])  # sort by torque
    torques = [p[0] for p in pts_sorted]
    mech = [p[1] for p in pts_sorted]
    total = [p[2] for p in pts_sorted]

    color = colors(idx)

    # Solid = mechanical
    ax.plot(
        torques, mech,
        marker='o', linestyle='-',
        linewidth=LINEWIDTH, markersize=MARKERSIZE,
        color=color, label=f"{speed_rad_s:.1f} rad/s mech"
    )

    # Dashed = total, same color
    ax.plot(
        torques, total,
        marker='s', linestyle='--',
        linewidth=LINEWIDTH, markersize=MARKERSIZE,
        color=color, label=f"{speed_rad_s:.1f} rad/s total"
    )

ax.set_xlabel("Torque (Nm)")
ax.set_ylabel("Efficiency (%)" if PLOT_AS_PERCENT else "Efficiency (fraction)")
ax.set_title("Efficiency vs Torque (grouped by commanded speed)")
ax.grid(True, which="both", linestyle=GRID_STYLE[0], linewidth=GRID_STYLE[1])

ax.set_ylim(0, 100)
ax.set_yticks(np.arange(0, 101, 20))

# Legend inside
ax.legend(fontsize=LEGEND_FONTSIZE, ncol=1, frameon=True, loc="best")

plt.tight_layout()
plt.show()
