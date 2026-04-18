#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
High-Yield SAWH Modelling for Marine Survival Crafts
Author: Anirban Das (2026)
Sorbent: LiCl-composite (based on LiCl@UiO-66, q₀ = 2.15 kg/kg)
"""

import numpy as np
import matplotlib.pyplot as plt

# Use Agg backend for headless environments (GitHub Actions)
import matplotlib
matplotlib.use('Agg')

def dubinin_astakhov_uptake(RH, T, q0, E, n):
    """Dubinin-Astakhov isotherm for water uptake (kg/kg)"""
    R = 8.314  # J/(mol·K)
    if RH <= 0:
        return 0.0
    A = -R * T * np.log(RH)
    if E <= 0:
        return 0.0
    arg = (A / E) ** n
    arg = np.minimum(arg, 700)  # prevent overflow
    return q0 * np.exp(-arg)

# ============================================================================
# Parameters for High-Yield LiCl-Composite Sorbent
# ============================================================================
da_q0 = 2.15      # kg/kg (from LiCl@UiO-66 at p/p₀=0.9)
da_E  = 8500.0    # J/mol (estimated for LiCl-salt composite)
da_n  = 2.0       # dimensionless (Dubinin-Radushkevich approximation)

# Baseline silica gel for comparison
si_q0 = 0.42
si_E  = 9500.0
si_n  = 2.5

# Survival craft constraints
sorbent_mass = 1.0      # kg
cycles_per_day = 1
cycle_efficiency = 0.70  # 70% for composite (conservative)

# Maritime conditions (tropical ocean)
RH_vals = np.array([0.60, 0.70, 0.80, 0.90])
T_vals_C = np.array([15, 20, 25, 30, 35])
T_vals_K = T_vals_C + 273.15

print("=== Daily Water Yield for 1 kg High-Yield LiCl Composite Sorbent ===\n")
print("RH% | T°C  | Uptake (kg/kg) | Daily Yield (L/day)")
print("-" * 55)

for RH in RH_vals:
    for T_C, T_K in zip(T_vals_C, T_vals_K):
        q_eq = dubinin_astakhov_uptake(RH, T_K, da_q0, da_E, da_n)
        q_cycle = q_eq * cycle_efficiency
        daily_yield = sorbent_mass * q_cycle * cycles_per_day
        print(f"{int(RH*100):3}% | {T_C:3}°C | {q_eq:6.3f}       | {daily_yield:5.2f}")

# Comparison with silica gel at typical maritime point (25°C, 80% RH)
RH_typical = 0.80
T_typical_K = 25 + 273.15

q_licl = dubinin_astakhov_uptake(RH_typical, T_typical_K, da_q0, da_E, da_n)
q_si   = dubinin_astakhov_uptake(RH_typical, T_typical_K, si_q0, si_E, si_n)

print("\n=== Comparison at 80% RH, 25°C ===")
print(f"LiCl-composite uptake    : {q_licl:.3f} kg/kg")
print(f"Silica gel uptake        : {q_si:.3f} kg/kg")
print(f"Yield (LiCl, 1 kg, 70% eff): {1.0 * q_licl * 0.70:.2f} L/day")
print(f"Yield (silica gel, 1 kg, 75% eff): {1.0 * q_si * 0.75:.2f} L/day")

# ============================================================================
# PLOT 1: Isotherm comparison (uptake vs RH at fixed temperature)
# ============================================================================
RH_range = np.linspace(0.10, 0.99, 200)
T_fixed = 25 + 273.15

licl_uptake = [dubinin_astakhov_uptake(rh, T_fixed, da_q0, da_E, da_n) for rh in RH_range]
silica_uptake = [dubinin_astakhov_uptake(rh, T_fixed, si_q0, si_E, si_n) for rh in RH_range]

plt.figure(figsize=(8,5))
plt.plot(RH_range*100, licl_uptake, 'g-', linewidth=2, label='LiCl-Composite (q₀=2.15)')
plt.plot(RH_range*100, silica_uptake, 'b--', linewidth=2, label='Silica Gel (q₀=0.42)')
plt.xlabel('Relative Humidity (%)')
plt.ylabel('Equilibrium Water Uptake (kg/kg)')
plt.title('SAWH Sorbent Isotherms at 25°C')
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.savefig('isotherm_comparison.png', dpi=300)
plt.close()
print("\n✓ Saved: isotherm_comparison.png")

# ============================================================================
# PLOT 2: Yield sensitivity heatmap (for LiCl-composite)
# ============================================================================
RH_fine = np.linspace(0.50, 0.95, 50)
T_fine_C = np.linspace(10, 35, 50)
T_fine_K = T_fine_C + 273.15
RH_grid, T_grid = np.meshgrid(RH_fine, T_fine_K)
yield_grid = np.zeros_like(RH_grid)

for i in range(len(T_fine_K)):
    for j in range(len(RH_fine)):
        q_eq = dubinin_astakhov_uptake(RH_fine[j], T_fine_K[i], da_q0, da_E, da_n)
        yield_grid[i, j] = sorbent_mass * q_eq * cycle_efficiency * cycles_per_day

plt.figure(figsize=(8,6))
contour = plt.contourf(RH_fine*100, T_fine_C, yield_grid, levels=20, cmap='viridis')
plt.colorbar(contour, label='Daily Water Yield (L/day per kg sorbent)')
plt.xlabel('Relative Humidity (%)')
plt.ylabel('Temperature (°C)')
plt.title('SAWH Yield Sensitivity (LiCl-Composite Sorbent)')
plt.grid(True, linestyle=':', alpha=0.3)
plt.tight_layout()
plt.savefig('yield_sensitivity.png', dpi=300)
plt.close()
print("✓ Saved: yield_sensitivity.png")

print("\n=== All plots generated successfully ===")
