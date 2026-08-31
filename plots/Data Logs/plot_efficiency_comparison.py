import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Data folders in Data Logs
CPG_FOLDER = Path(r"plots\Data Logs\Efficiency\CPG_Efficiency_data")
PANCAKE_FOLDER = Path(r"plots\Data Logs\Efficiency\CPG_Pancake_efficiency_data")

# Standardized style to match other updated plots
FIGSIZE = (11.0, 4.6)
AXIS_LABEL_FONTSIZE = 16
TICK_FONTSIZE = 13
LEGEND_FONTSIZE = 10
LINEWIDTH = 2.2
MARKERSIZE = 4.0

# Analysis window for averaging (seconds) in steady-state region.
T_START = 11.2
T_END = 16.0

# Fixed rpm color mapping (kept consistent across both subplots)
RPM_COLORS = {
    20.0: "#1f77b4",   # blue
    50.0: "#e377c2",   # pink
    80.0: "#9467bd",   # purple
    110.0: "#bcbd22",  # olive
    140.0: "#17becf",  # cyan
}


def rpm_to_rad_s(rpm: float) -> float:
    return rpm * 2.0 * np.pi / 60.0


def parse_cmd_from_filename(filename: str):
    stem = Path(filename).stem
    torque_str, rpm_str = stem.split("_", 1)
    return float(torque_str), float(rpm_str)


def mechanical_efficiency_percent(csv_path: Path, cmd_torque_nm: float, cmd_rpm: float) -> float:
    df = pd.read_csv(csv_path)

    win = df[(df["time_s"] >= T_START) & (df["time_s"] < T_END)]
    if win.empty:
        return np.nan

    avg_torque = abs(win["loadcell_torque_nm"].mean())
    avg_test_rpm = abs(win["test_velocity"].mean())

    # Prefer measured commanded torque in-window when present. This avoids
    # underestimating efficiency during files where command ramps in early samples.
    if "cmd_torque_nm" in win.columns:
        denom_torque = abs(win["cmd_torque_nm"].mean())
    else:
        denom_torque = cmd_torque_nm

    cmd_speed = rpm_to_rad_s(cmd_rpm)
    meas_speed = rpm_to_rad_s(avg_test_rpm)

    denom = denom_torque * cmd_speed
    if denom == 0:
        return np.nan

    return 100.0 * (avg_torque * meas_speed) / denom


def load_series_by_rpm(folder: Path):
    by_rpm = {}
    for file in folder.iterdir():
        if file.suffix.lower() != ".csv":
            continue

        try:
            cmd_torque, cmd_rpm = parse_cmd_from_filename(file.name)
        except Exception:
            continue

        eff = mechanical_efficiency_percent(file, cmd_torque, cmd_rpm)
        if not np.isfinite(eff):
            continue

        by_rpm.setdefault(cmd_rpm, []).append((cmd_torque, eff))

    # Sort points by torque within each rpm
    for rpm in by_rpm:
        by_rpm[rpm] = sorted(by_rpm[rpm], key=lambda p: p[0])

    return by_rpm


def color_for_rpm(rpm: float):
    if rpm in RPM_COLORS:
        return RPM_COLORS[rpm]
    # Fallback for unexpected rpm values
    return "#7f7f7f"


def plot_panel(ax, by_rpm, panel_title: str, linestyle: str):
    for rpm in sorted(by_rpm.keys()):
        pts = by_rpm[rpm]
        x = [p[0] for p in pts]
        y = [p[1] for p in pts]
        ax.plot(
            x,
            y,
            linestyle=linestyle,
            marker="s" if linestyle == "--" else "o",
            linewidth=LINEWIDTH,
            markersize=MARKERSIZE,
            color=color_for_rpm(rpm),
            label=f"{int(round(rpm))} rpm",
            alpha=0.95,
        )

    ax.set_title(panel_title, fontsize=12, fontweight="bold")
    ax.set_xlabel("Commanded Torque (Nm)", fontsize=AXIS_LABEL_FONTSIZE, fontweight="bold")
    ax.tick_params(axis="both", labelsize=TICK_FONTSIZE)
    ax.set_ylim(60, 100)
    ax.legend(
        loc="lower right",
        fontsize=LEGEND_FONTSIZE,
        frameon=True,
        borderpad=0.35,
        labelspacing=0.25,
        handlelength=1.5,
        handletextpad=0.45,
    )


def main():
    if not CPG_FOLDER.exists():
        raise FileNotFoundError(f"Missing folder: {CPG_FOLDER}")
    if not PANCAKE_FOLDER.exists():
        raise FileNotFoundError(f"Missing folder: {PANCAKE_FOLDER}")

    cpg = load_series_by_rpm(CPG_FOLDER)
    pancake = load_series_by_rpm(PANCAKE_FOLDER)

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=FIGSIZE, sharey=True)

    # Match reference look: pancake solid lines, CPG dashed lines
    plot_panel(ax_left, pancake, "Pancake CPG (14:1)", linestyle="-")
    plot_panel(ax_right, cpg, "CPG (14:1)", linestyle="--")

    ax_left.set_ylabel("Mechanical Efficiency (%)", fontsize=AXIS_LABEL_FONTSIZE, fontweight="bold")

    plt.tight_layout()
    plt.savefig(r"plots\efficiency_comparison.png", dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
