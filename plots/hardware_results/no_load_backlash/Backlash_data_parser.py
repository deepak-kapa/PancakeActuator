#!/usr/bin/env python3
# zero_and_diff.py

import pandas as pd
from pathlib import Path

# ====== CONFIG ======
CSV_FILE = "C:/Users/Quant/Documents/GitHub/Actuator_Optimization_3D_printed/plots/hardware_results/no_load_backlash/cpg_pancake2_sine_vel_2.500tps_2.00s.csv"  # <-- change this to your CSV file path

USE_FIRST_SAMPLE = False   # True = Method 1 (first sample), False = Method 2 (average of first N samples)
N_SAMPLES = 20            # Used only if USE_FIRST_SAMPLE == False

# Encoder orientation & scaling
# If encoders face each other, set OUTPUT_SIGN = -1 (motor sign stays +1 typically).
MOTOR_SIGN  = +1
OUTPUT_SIGN = -1          # <-- encoders facing each other -> flip output sign

# If motor encoder is on motor shaft and output encoder is on output shaft,
# scale motor displacement to the output side by 1/GEAR_RATIO before diff.
USE_GEAR_SCALE = True
GEAR_RATIO = 14          # motor : output
# ====================

def main(csv_path: str):
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {p}")

    df = pd.read_csv(p)

    required = ["time_s", "odrive_pos_rad", "output_pos_rad"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {missing}")

    # ----- Zero offset selection -----
    if USE_FIRST_SAMPLE:
        odrive0 = df.loc[0, "odrive_pos_rad"]
        output0 = df.loc[0, "output_pos_rad"]
        print(f"Using first sample for zeroing: odrive0={odrive0}, output0={output0}")
    else:
        odrive0 = (df["odrive_pos_rad"].max() + df["odrive_pos_rad"].min()) / 2
        output0 = (df["output_pos_rad"].max() + df["output_pos_rad"].min()) / 2
        print(f"Using average of first {N_SAMPLES} samples for zeroing: odrive0={odrive0}, output0={output0}")

    # ----- Relative displacements (zeroed) -----
    odrive_disp = df["odrive_pos_rad"] - odrive0
    output_disp = df["output_pos_rad"] - output0

    # ----- Apply sign for facing/opposite directions -----
    odrive_disp *= MOTOR_SIGN
    output_disp *= OUTPUT_SIGN

    # ----- Scale motor to output side (optional) -----
    if USE_GEAR_SCALE:
        motor_scaled = odrive_disp / GEAR_RATIO   # motor -> output side
    else:
        motor_scaled = odrive_disp

    # Store displacement columns (after sign/scale)
    df["odrive_disp_rad"] = odrive_disp
    df["output_disp_rad"] = output_disp
    df["motor_on_output_side_rad"] = motor_scaled  # for clarity/debug

    # ----- Backlash (on output side) -----
    # backlash = (motor on output side) - (output)
    df["backlash_rad"] = motor_scaled - output_disp

    # Save alongside the original with a suffix
    out_path = p.with_name(p.stem + "_processed.csv")
    df.to_csv(out_path, index=False)
    print(f"Wrote: {out_path}")

if __name__ == "__main__":
    main(CSV_FILE)
