import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ============ CONFIG ============
# Set CSV_FILE_2 = None to plot only one file.
CSV_FILE_1 = "/home/surya/odrive_testing/actuator-testbench/Actuator_Data/CPG_NEW_2SEP/Backdrivability_Test_Saketh/backdrive_0to0.9Nm_25s_t5_opp.csv"
CSV_FILE_2 = None  # "/path/to/second_file.csv"

LABEL_1 = "Actuator 1"
LABEL_2 = "Actuator 2"
COLOR_1 = "blue"
COLOR_2 = "red"

GEAR_RATIO = 1      # divide position by this (1 = no scaling)
TO_RADIANS = False  # True -> convert degrees to radians before plotting

OUT_PNG = "load_pos_vs_torque_cell.png"
# =================================

X_COL = "static_torque_cell_nm"
Y_COL = "load_pos_integrated_deg"


def load_and_plot(ax, csv_path, label, color):
    df = pd.read_csv(csv_path)

    for col in [X_COL, Y_COL]:
        if col not in df.columns:
            raise ValueError(f"{csv_path} is missing column '{col}'. Found: {list(df.columns)}")

    # Coerce to numeric and drop rows where either value is NaN
    df[X_COL] = pd.to_numeric(df[X_COL], errors="coerce")
    df[Y_COL] = pd.to_numeric(df[Y_COL], errors="coerce")
    df = df.dropna(subset=[X_COL, Y_COL])

    if df.empty:
        raise ValueError(f"{csv_path}: no valid rows after dropping NaNs in {X_COL}/{Y_COL}")

    x = df[X_COL].values
    y = df[Y_COL].values / GEAR_RATIO
    if TO_RADIANS:
        y = np.deg2rad(y)

    ax.plot(x, y, color=color, linewidth=1.5, alpha=0.7, label=label)

    for mask, suffix in [(x > 0, "pos fit"), (x < 0, "neg fit")]:
        xm, ym = x[mask], y[mask]
        # need at least 2 distinct x values for a valid linear fit
        if len(np.unique(xm)) > 1:
            m, b = np.polyfit(xm, ym, 1)
            xf = np.linspace(xm.min(), xm.max(), 100)
            ax.plot(xf, m * xf + b, color=color, linestyle=":", linewidth=2,
                    label=f"{label} {suffix} (slope={m:.4g})")
            print(f"{label} {suffix}: slope = {m:.6g} {'rad' if TO_RADIANS else 'deg'}/Nm, "
                  f"intercept = {b:.6g}")


def main():
    fig, ax = plt.subplots(figsize=(8, 6))

    load_and_plot(ax, CSV_FILE_1, LABEL_1, COLOR_1)
    if CSV_FILE_2:
        load_and_plot(ax, CSV_FILE_2, LABEL_2, COLOR_2)

    unit = "rad" if TO_RADIANS else "deg"
    ax.set_xlabel("Static Torque Cell [Nm]")
    ax.set_ylabel(f"Load Position (integrated) [{unit}]")
    ax.set_title("Load Position vs Static Torque Cell")
    ax.grid(True)
    ax.legend()
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    print(f"Saved: {OUT_PNG}")
    plt.show()


if __name__ == "__main__":
    main()