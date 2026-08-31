from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D


RESULTS_DIR = Path("results")
OUTPUT_PLOT = Path("plots") / "mass_width_vs_gear_ratio_metal.png"

MOTORS = ["MAD_M6C12", "MN8014", "U10", "U12", "U8", "VT8020"]

# Style aligned with other updated figures.
FIGSIZE = (11.2, 6.4)
AXIS_LABEL_FONTSIZE = 13
TICK_FONTSIZE = 12
TITLE_FONTSIZE = 12

COLOR_MASS = "#0057B8"   # deep blue
COLOR_WIDTH = "#D94801"  # deep orange


def find_header_row(csv_path: Path) -> int:
    with csv_path.open("r", encoding="utf-8", errors="ignore") as f:
        for idx, line in enumerate(f):
            text = line.strip().lower()
            if text.startswith("iter") and "gearratio" in text and "mass" in text and "actuator_width" in text:
                return idx
    raise ValueError(f"Could not locate data header row in {csv_path}")


def load_best_by_gear_ratio(csv_path: Path) -> pd.DataFrame:
    header_row = find_header_row(csv_path)
    df = pd.read_csv(csv_path, skiprows=header_row, skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]

    # Keep numeric data rows only.
    for col in ["gearRatio", "mass", "Actuator_width", "Cost"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["gearRatio", "mass", "Actuator_width", "Cost"]).copy()

    # For each gear ratio, keep the minimum-cost design.
    idx = df.groupby("gearRatio")["Cost"].idxmin()
    out = df.loc[idx, ["gearRatio", "mass", "Actuator_width"]].sort_values("gearRatio").reset_index(drop=True)
    return out


def motor_paths(motor: str) -> tuple[Path, Path]:
    subdir = RESULTS_DIR / f"results_BruteForce_{motor}"
    normal = subdir / f"Metal_CPG_BRUTEFORCE_MIT_{motor}.csv"
    pancake = subdir / f"Pancake_Metal_CPG_BRUTEFORCE_MIT_{motor}.csv"
    return normal, pancake


def compute_avg_deltas(normal_df: pd.DataFrame, pancake_df: pd.DataFrame) -> tuple[float, float]:
    merged = pd.merge(
        normal_df[["gearRatio", "mass", "Actuator_width"]],
        pancake_df[["gearRatio", "mass", "Actuator_width"]],
        on="gearRatio",
        suffixes=("_n", "_p"),
        how="inner",
    )
    if merged.empty:
        return float("nan"), float("nan")

    delta_mass_g = (merged["mass_p"] - merged["mass_n"]).mean() * 1000.0
    delta_width_mm = (merged["Actuator_width_p"] - merged["Actuator_width_n"]).mean()
    return delta_mass_g, delta_width_mm


def padded_limits(vmin: float, vmax: float, frac: float = 0.05) -> tuple[float, float]:
    span = vmax - vmin
    if span <= 0:
        pad = 1.0
    else:
        pad = span * frac
    return vmin - pad, vmax + pad


def main():
    # Pass 1: load all motor datasets first so all subplots can share identical axes.
    all_data = {}
    x_vals = []
    mass_vals = []
    width_vals = []

    for motor in MOTORS:
        normal_path, pancake_path = motor_paths(motor)
        if not normal_path.exists() or not pancake_path.exists():
            raise FileNotFoundError(f"Missing expected files for {motor}:\n{normal_path}\n{pancake_path}")

        normal = load_best_by_gear_ratio(normal_path)
        pancake = load_best_by_gear_ratio(pancake_path)
        all_data[motor] = (normal, pancake)

        x_vals.extend(normal["gearRatio"].tolist())
        x_vals.extend(pancake["gearRatio"].tolist())
        mass_vals.extend(normal["mass"].tolist())
        mass_vals.extend(pancake["mass"].tolist())
        width_vals.extend(normal["Actuator_width"].tolist())
        width_vals.extend(pancake["Actuator_width"].tolist())

    x_lim = padded_limits(min(x_vals), max(x_vals), frac=0.03)
    mass_lim = padded_limits(min(mass_vals), max(mass_vals), frac=0.06)
    width_lim = padded_limits(min(width_vals), max(width_vals), frac=0.06)

    fig, axes = plt.subplots(2, 3, figsize=FIGSIZE, sharex=True)
    axes = axes.ravel()

    for i, (ax, motor) in enumerate(zip(axes, MOTORS)):
        normal, pancake = all_data[motor]

        ax2 = ax.twinx()

        # Mass (left y-axis, solid lines)
        ax.plot(
            normal["gearRatio"],
            normal["mass"],
            color=COLOR_MASS,
            linestyle="-",
            marker="o",
            linewidth=2.3,
            markersize=3.4,
            alpha=0.98,
        )
        ax.plot(
            pancake["gearRatio"],
            pancake["mass"],
            color=COLOR_MASS,
            linestyle="--",
            marker="o",
            linewidth=2.3,
            markersize=3.4,
            alpha=0.98,
        )

        # Width (right y-axis, dashed lines)
        ax2.plot(
            normal["gearRatio"],
            normal["Actuator_width"],
            color=COLOR_WIDTH,
            linestyle="-",
            marker="s",
            linewidth=2.1,
            markersize=3.2,
            alpha=0.98,
        )
        ax2.plot(
            pancake["gearRatio"],
            pancake["Actuator_width"],
            color=COLOR_WIDTH,
            linestyle="--",
            marker="s",
            linewidth=2.1,
            markersize=3.2,
            alpha=0.98,
        )

        ax.set_title(motor, fontsize=TITLE_FONTSIZE, fontweight="bold")
        ax.tick_params(axis="both", labelsize=TICK_FONTSIZE)
        ax2.tick_params(axis="y", labelsize=TICK_FONTSIZE)
        ax.set_xlim(x_lim)
        ax.set_ylim(mass_lim)
        ax2.set_ylim(width_lim)

        row = i // 3
        col = i % 3

        # Keep ticks compact: show left y labels only on first column,
        # right y labels only on last column, x labels only on bottom row.
        if col != 0:
            ax.tick_params(axis="y", labelleft=False)
        if col != 2:
            ax2.tick_params(axis="y", labelright=False)
        if row == 0:
            ax.tick_params(axis="x", labelbottom=False)

    handles = [
        Line2D([0], [0], color="#333333", lw=2.2, linestyle="-", label="Normal CPG"),
        Line2D([0], [0], color="#333333", lw=2.2, linestyle="--", label="Pancake CPG"),
        Line2D([0], [0], color=COLOR_MASS, lw=2.2, linestyle="-", marker="o", markersize=4, label="Mass"),
        Line2D([0], [0], color=COLOR_WIDTH, lw=2.0, linestyle="--", marker="s", markersize=4, label="Actuator Width"),
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        ncol=4,
        frameon=True,
        fontsize=10.5,
        bbox_to_anchor=(0.5, 0.985),
        borderaxespad=0.2,
        handletextpad=0.4,
        columnspacing=0.8,
    )

    # Single shared axis labels
    fig.supxlabel("Gear Ratio", fontsize=AXIS_LABEL_FONTSIZE, fontweight="bold", y=0.025)
    fig.supylabel("Mass (kg)", fontsize=AXIS_LABEL_FONTSIZE, fontweight="bold", x=0.015)
    fig.text(
        0.992,
        0.5,
        "Width (mm)",
        rotation=270,
        va="center",
        ha="center",
        fontsize=AXIS_LABEL_FONTSIZE,
        fontweight="bold",
    )

    fig.subplots_adjust(
        left=0.065,
        right=0.945,
        bottom=0.10,
        top=0.90,
        wspace=0.12,
        hspace=0.16,
    )
    OUTPUT_PLOT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PLOT, dpi=600, bbox_inches="tight")
    print(f"Plot saved to {OUTPUT_PLOT}")
    plt.show()


if __name__ == "__main__":
    main()
