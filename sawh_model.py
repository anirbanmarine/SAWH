#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Sorbent SAWH Modelling for Marine Survival Crafts
Author: Anirban Das (2026)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def dubinin_astakhov_uptake(RH, T, q0, E, n):
    """Dubinin-Astakhov isotherm for water uptake (kg/kg)"""
    R = 8.314
    if RH <= 0:
        return 0.0
    A = -R * T * np.log(RH)
    if E <= 0:
        return 0.0
    arg = (A / E) ** n
    arg = np.minimum(arg, 700)
    return q0 * np.exp(-arg)

# ============================================================================
# Sorbent Parameters (from open literature)
# ============================================================================
sorbents = {
    'Silica Gel': {'q0': 0.42, 'E': 9500, 'n': 2.5, 'eff': 0.75},
    'LiCl-Composite': {'q0': 2.15, 'E': 8500, 'n': 2.0, 'eff': 0.70},
    'Biomass Aerogel': {'q0': 2.80, 'E': 7000, 'n': 2.2, 'eff': 0.75},
    'MOF-303': {'q0': 0.43, 'E': 10000, 'n': 2.8, 'eff': 0.80}
}

sorbent_mass = 1.0      # kg
cycles_per_day = 1

# Maritime test point (tropical ocean: 25°C, 80% RH)
T_test_K = 25 + 273.15
RH_test = 0.80

print("=== Daily Water Yield Comparison (1 kg sorbent, 25°C, 80% RH) ===\n")
print(f"{'Sorbent':<18} {'Uptake (kg/kg)':<15} {'Yield (L/day)':<15}")
print("-" * 50)

results = {}
for name, params in sorbents.items():
    q_eq = dubinin_astakhov_uptake(RH_test, T_test_K, params['q0'], params['E'], params['n'])
    daily_yield = sorbent_mass * q_eq * params['eff'] * cycles_per_day
    results[name] = daily_yield
    print(f"{name:<18} {q_eq:<15.3f} {daily_yield:<15.2f}")

# ============================================================================
# Plot 1: Comparative Bar Chart
# ============================================================================
plt.figure(figsize=(8,5))
names = list(results.keys())
yields = list(results.values())
bars = plt.bar(names, yields, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
plt.ylabel('Daily Water Yield (L/day per kg sorbent)')
plt.title('SAWH Performance Comparison at 25°C, 80% RH')
plt.ylim(0, max(yields) * 1.2)
for bar, yield_val in zip(bars, yields):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
             f'{yield_val:.2f}', ha='center', va='bottom')
plt.tight_layout()
plt.savefig('sorbent_comparison.png', dpi=300)
plt.close()
print("\n✓ Saved: sorbent_comparison.png")

# ============================================================================
# Plot 2: Isotherm Comparison (Uptake vs RH at 25°C)
# ============================================================================
RH_range = np.linspace(0.10, 0.99, 200)
T_fixed = 25 + 273.15

plt.figure(figsize=(9,6))
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
linestyles = ['-', '--', '-.', ':']

for (name, params), color, ls in zip(sorbents.items(), colors, linestyles):
    uptake = [dubinin_astakhov_uptake(rh, T_fixed, params['q0'], params['E'], params['n']) for rh in RH_range]
    plt.plot(RH_range*100, uptake, color=color, linestyle=ls, linewidth=2, label=name)

plt.xlabel('Relative Humidity (%)')
plt.ylabel('Equilibrium Water Uptake (kg/kg)')
plt.title('SAWH Sorbent Isotherms at 25°C')
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.savefig('isotherm_comparison_all.png', dpi=300)
plt.close()
print("✓ Saved: isotherm_comparison_all.png")

print("\n=== All plots generated successfully ===")
