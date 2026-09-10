#!/usr/bin/env python3
# plot_backlash.py
# Plots encoder deflection vs time for any number of stiffness_test CSVs,
# and shows a per-cycle max / min / peak-to-peak (backlash) summary table
# with the average across cycles for each actuator.

import math

import pandas as pd
import matplotlib.pyplot as plt

# ============ CONFIG ============
ACTUATORS = [
    {
        "csv": "/home/surya/odrive_testing/actuator-testbench/Actuator_Data/CPG_NEW_2SEP/backlash_new_test/backlash_20260910_021113.csv",
        "label": "CPG_Pancake_1",
        "color": "blue",
    },
    {
        "csv": "/home/surya/odrive_testing/actuator-testbench/Actuator_Data/CPG_NEW_2SEP/backlash_new_test/backlash_20260910_021631.csv",
        "label": "CPG_Pancake_2",
        "color": "red",
    },
    {
        "csv": "/home/surya/odrive_testing/actuator-testbench/Actuator_Data/CPG_NEW_2SEP/backlash_new_test/backlash_20260910_022140.csv",
        "label": "CPG_Pancake_3",
        "color": "green",
    },
        {
        "csv": "/home/surya/odrive_testing/actuator-testbench/Actuator_Data/CPG_NEW_2SEP/backlash_new_test/backlash_20260910_022425.csv",
        "label": "CPG_Pancake_4",
        "color": "yellow",
    },
        {
        "csv": "/home/surya/odrive_testing/actuator-testbench/Actuator_Data/CPG_NEW_2SEP/backlash_new_test/backlash_20260910_023122.csv",
        "label": "CPG_Pancake_5",
        "color": "pink",
    },
        {
        "csv": "/home/surya/odrive_testing/actuator-testbench/Actuator_Data/CPG_NEW_2SEP/backlash_new_test/backlash_20260910_023525.csv",
        "label": "CPG_Pancake_6",
        "color": "black",
    },
]

GEAR_RATIO = 14  # divide encoder_pos_rad by this to get output deflection

OUT_PNG = "backlash.png"
# =================================

X_COL = "time_s"
Y_COL = "encoder_pos_rad"
CYCLE_COL = "cycle"  # optional; if absent the whole file is treated as one cycle


def load_and_plot(ax, csv_path, label, color):
    """Plot deflection vs time and return per-cycle (cycle, max, min, diff) stats."""
    df = pd.read_csv(csv_path)

    for col in [X_COL, Y_COL]:
        if col not in df.columns:
            raise ValueError(f"{csv_path} is missing column '{col}'. Found: {list(df.columns)}")

    x = df[X_COL].values
    y = df[Y_COL].values / GEAR_RATIO
    ax.plot(x, y, color=color, linewidth=1.5, alpha=0.7, label=label)

    stats = []
    if CYCLE_COL in df.columns:
        for cyc in sorted(df[CYCLE_COL].unique()):
            yc = df.loc[df[CYCLE_COL] == cyc, Y_COL].values / GEAR_RATIO
            y_max, y_min = yc.max(), yc.min()
            stats.append((int(cyc), y_max, y_min, y_max - y_min))
    else:
        # No cycle column in this CSV -> treat the whole file as a single cycle.
        y_max, y_min = y.max(), y.min()
        stats.append((1, y_max, y_min, y_max - y_min))

    return stats


def fmt_rad_deg(value_rad):
    """'0.0602 (3.45°)' — value in rad with the degree equivalent in brackets."""
    return f"{value_rad:.4f} ({math.degrees(value_rad):.2f}°)"


def build_table(ax_table, all_stats):
    """all_stats: list of (label, [(cycle, max, min, diff), ...])"""
    rows = []
    for label, stats in all_stats:
        for cyc, y_max, y_min, diff in stats:
            rows.append([label, f"{cyc}", fmt_rad_deg(y_max), fmt_rad_deg(y_min), fmt_rad_deg(diff)])
        avg_diff = sum(s[3] for s in stats) / len(stats)
        rows.append([label, "Avg", "-", "-", fmt_rad_deg(avg_diff)])

    ax_table.axis("off")
    table = ax_table.table(
        cellText=rows,
        colLabels=["Actuator", "Cycle", "Max [rad (deg)]", "Min [rad (deg)]", "Diff (P2P) [rad (deg)]"],
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.4)


def main():
    fig, (ax, ax_table) = plt.subplots(
        2, 1, figsize=(9, 8.5), gridspec_kw={"height_ratios": [3, 1.6]}
    )

    all_stats = []
    for actuator in ACTUATORS:
        if actuator["csv"]:
            stats = load_and_plot(ax, actuator["csv"], actuator["label"], actuator["color"])
            all_stats.append((actuator["label"], stats))

    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Output Deflection [rad]")
    ax.set_title("Backlash: Encoder Deflection vs Time")
    ax.grid(True)
    ax.legend()

    build_table(ax_table, all_stats)

    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    print(f"Saved: {OUT_PNG}")

    for label, stats in all_stats:
        avg_diff = sum(s[3] for s in stats) / len(stats)
        detail = ", ".join(f"cycle {c} diff={d:.4f}" for c, _, _, d in stats)
        print(f"{label}: {detail}, avg diff={avg_diff:.4f}")


if __name__ == "__main__":
    main()