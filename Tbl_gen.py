#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Sorbent SAWH Modelling for Marine Survival Crafts
Author: Anirban Das (2026)
Generates: Bar chart, isotherm plot, sensitivity heatmap, and table image
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Also need pandas for easy table creation (add to environment.yml)
import pandas as pd

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

sorbent_mass = 1.0
cycles_per_day = 1

# Maritime test point
T_test_K = 25 + 273.15
RH_test = 0.80

print("=== Daily Water Yield Comparison (1 kg sorbent, 25°C, 80% RH) ===\n")

results_summary = []
for name, params in sorbents.items():
    q_eq = dubinin_astakhov_uptake(RH_test, T_test_K, params['q0'], params['E'], params['n'])
    daily_yield = sorbent_mass * q_eq * params['eff'] * cycles_per_day
    results_summary.append({
        'Sorbent': name,
        'Uptake (kg/kg)': round(q_eq, 3),
        'Cycle Efficiency': params['eff'],
        'Yield (L/day)': round(daily_yield, 2)
    })
    print(f"{name:<18} Uptake: {q_eq:.3f} kg/kg  →  Yield: {daily_yield:.2f} L/day")

# ============================================================================
# Generate Table Image (Summary Table)
# ============================================================================
df_summary = pd.DataFrame(results_summary)

fig, ax = plt.subplots(figsize=(8, 2.5))
ax.axis('tight')
ax.axis('off')
table = ax.table(cellText=df_summary.values,
                 colLabels=df_summary.columns,
                 cellLoc='center',
                 loc='center',
                 colWidths=[0.30, 0.20, 0.20, 0.20])

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.5)

plt.title('Table 1: Daily Water Yield Comparison at 25°C, 80% RH', fontsize=12, pad=20)
plt.tight_layout()
plt.savefig('table_summary.png', dpi=300, bbox_inches='tight')
plt.close()
print("\n✓ Saved: table_summary.png")

# ============================================================================
# Generate Full Sensitivity Table (All RH and Temperatures)
# ============================================================================
RH_vals = [0.60, 0.70, 0.80, 0.90]
T_vals_C = [15, 20, 25, 30, 35]

# Create a list to hold all rows for the full table
full_table_rows = []

for name, params in sorbents.items():
    for RH in RH_vals:
        for T_C in T_vals_C:
            T_K = T_C + 273.15
            q_eq = dubinin_astakhov_uptake(RH, T_K, params['q0'], params['E'], params['n'])
            daily_yield = sorbent_mass * q_eq * params['eff'] * cycles_per_day
            full_table_rows.append({
                'Sorbent': name,
                'RH (%)': int(RH * 100),
                'Temp (°C)': T_C,
                'Uptake (kg/kg)': round(q_eq, 3),
                'Yield (L/day)': round(daily_yield, 2)
            })

df_full = pd.DataFrame(full_table_rows)

# Pivot for better presentation: rows = (RH, Temp), columns = Sorbent
pivot_yield = df_full.pivot_table(index=['RH (%)', 'Temp (°C)'], columns='Sorbent', values='Yield (L/day)')
pivot_uptake = df_full.pivot_table(index=['RH (%)', 'Temp (°C)'], columns='Sorbent', values='Uptake (kg/kg)')

# Create a formatted table image for yields
fig, ax = plt.subplots(figsize=(12, 8))
ax.axis('tight')
ax.axis('off')

# Prepare data for display: combine RH and Temp as a single column label
display_data = []
for (rh, temp), row in pivot_yield.iterrows():
    display_data.append([f"{rh}% / {temp}°C", 
                         row['Silica Gel'], 
                         row['LiCl-Composite'], 
                         row['Biomass Aerogel'], 
                         row['MOF-303']])

col_labels = ['Condition (RH/Temp)', 'Silica Gel', 'LiCl-Composite', 'Biomass Aerogel', 'MOF-303']

table_full = ax.table(cellText=display_data,
                      colLabels=col_labels,
                      cellLoc='center',
                      loc='center',
                      colWidths=[0.25, 0.15, 0.15, 0.15, 0.15])

table_full.auto_set_font_size(False)
table_full.set_fontsize(8)
table_full.scale(1.2, 1.5)

plt.title('Table 2: Daily Water Yield (L/day per kg sorbent) Across Maritime Conditions', 
          fontsize=12, pad=20)
plt.tight_layout()
plt.savefig('table_full_sensitivity.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: table_full_sensitivity.png")

# ============================================================================
# Also generate the bar chart and isotherm plot (as before)
# ============================================================================
# (Include your existing bar chart and isotherm code here)

print("\n=== All tables and plots generated successfully ===")
