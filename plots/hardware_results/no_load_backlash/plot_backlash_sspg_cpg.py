import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# File paths
SSPG_File1 = r"C:/Users/jvira/Documents/Actuator_Optimization_3D_printed/Actuator_Optimization_3D_printed/plots/hardware_results/no_load_backlash/cpg_backlash_sine_vel_2.500tps_2.00s.csv"
CPG_File2  = r"C:/Users/jvira/Documents/Actuator_Optimization_3D_printed/Actuator_Optimization_3D_printed/plots/hardware_results/no_load_backlash/cpg_pancake_sine_vel_2.500tps_2.00s.csv"

# Column names
x_col = "time_s"
y_col = "backlash_rad"

# Read CSV files


df_sspg = pd.read_csv(SSPG_File1)
df_cpg = pd.read_csv(CPG_File2)

# Compute averages
avg_sspg = df_sspg[y_col].mean()
avg_cpg = df_cpg[y_col].mean()

max_sspg = df_sspg[y_col].max()
max_cpg = df_cpg[y_col].max()

min_sspg = df_sspg[y_col].min()
min_cpg = df_cpg[y_col].min()

print(f"Average CPG backlash_rad: {avg_sspg:.6f} rad")
print(f"Average Pancake CPG backlash_rad:  {avg_cpg:.6f} rad")

print(f"Maximum CPG backlash_rad: {max_sspg:.6f} rad")
print(f"Maximum Pancake CPG backlash_rad:  {max_cpg:.6f} rad")

print(f"Minimum CPG backlash_rad: {min_sspg:.6f} rad")
print(f"Minimum Pancake CPG backlash_rad:  {min_cpg:.6f} rad")

print(f"CPG backlash_rad: {max_sspg-min_sspg:.6f} rad, {(max_sspg-min_sspg)*(180/np.pi):.6f} deg")
print(f"Pancake CPG backlash_rad:  {max_cpg-min_cpg:.6f} rad, {(max_cpg-min_cpg)*(180/np.pi):.6f} deg")

# Font sizes (modifiable)
axis_fontsize = 20
legend_fontsize = 18
tick_size = 18

# Plot
# Sort by time (important!)
df_sspg = df_sspg.sort_values(by=x_col)
df_cpg  = df_cpg.sort_values(by=x_col)

# Plot as continuous lines
plt.figure(figsize=(10, 6))

plt.plot(df_sspg[x_col], df_sspg[y_col],
         label="CPG (14:1)",
         linewidth=2)

plt.plot(df_cpg[x_col], df_cpg[y_col],
         label="Pancake CPG (14:1)",
         linewidth=2)

# Labels and title
plt.xlabel("Time (s)", fontsize=axis_fontsize)
plt.ylabel("Backlash (rad)", fontsize=axis_fontsize)
plt.title("No-load backlash: CPG and Pancake CPG", fontsize=axis_fontsize)

plt.legend(fontsize=legend_fontsize)
plt.grid(True, linestyle="-", alpha=0.6)
plt.tick_params(axis='both', which='major', labelsize=tick_size)

plt.tight_layout()
plt.show()

