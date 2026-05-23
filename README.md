# Pancake Actuators: A Novel Design Architecture for Compound Planetary Gearboxes

This repo is a lightweight actuator optimization framework for:
- `cpg` (Compound Planetary Gearbox)
- `pancake-cpg` (Pancake variant of CPG)

## Quick Start

1. Clone and enter the repo

2. Install dependencies:
```bash
pip install numpy pandas matplotlib
```

3. Run optimization:
```bash
python actOpt.py <motor> cpg <ratio>
```

Example:
```bash
python actOpt.py U8 cpg 6.5
```

## Inputs

- `motor`: `U8`, `U10`, `U12`, `MN8014`, `VT8020`, `MAD_M6C12`
- `gearbox`: use `cpg`
- `ratio`: gear ratio (recommended `> 6`)

## CPG vs Pancake-CPG Mode

- Current default run path uses the pancake CPG style.
- To switch to normal CPG style, edit the default in
  `Opt_compoundPlanetaryGBOptimization.py`:
  `run(..., actuator_style="pancake", ...)` -> `run(..., actuator_style="normal", ...)`

## Output

- Console prints optimization time and optimal gear parameters.
- Result CSVs are written under:
  - `results/results_BruteForce_<MOTOR>/`

## Hardware Test Data Logs

- Primary hardware test logs are under:
  - `plots/Data Logs/`
  - `plots/hardware_results/`
- `plots/Data Logs/` contains:
  - `Backlash/`, `Efficiency/`, `Endurance/`, `peak torque/`, `stiffness/`
- `plots/hardware_results/` contains:
  - `no_load_backlash/`, `pancake/`, `power_efficiency/`, `transmission_stiffness/`
