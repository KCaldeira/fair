#!/usr/bin/env python3
"""
Check which species need concentration initialization
"""

from fair import FAIR
from fair.io import read_properties

# Initialize FAIR
f = FAIR()
f.define_time(1750, 2023, 1)
f.define_scenarios(['test'])
f.define_configs(['default'])

# Load species properties
species, props = read_properties()
f.define_species(species, props)
f.allocate()
f.fill_species_configs()

print("All species in FAIR:")
all_species = list(f.species_configs['baseline_concentration'].specie.values)
for s in all_species:
    print(f"  {s}")

print("\nSpecies that might need concentration initialization:")
ghg_species = ['CO2', 'CH4', 'N2O', 'CO2 FFI', 'CO2 AFOLU']
for s in ghg_species:
    if s in f.species_configs['baseline_concentration'].specie.values:
        baseline_val = f.species_configs['baseline_concentration'].sel(specie=s).values
        print(f"  {s}: {baseline_val}")

print("\nChecking concentration arrays for these species:")
for s in ghg_species:
    if s in f.species_configs['baseline_concentration'].specie.values:
        import numpy as np
        conc_vals = f.concentration.sel(specie=s).values
        nan_count = np.isnan(conc_vals).sum()
        print(f"  {s}: {nan_count} NaN values out of {conc_vals.size} total")
        if nan_count > 0:
            print(f"    First 5 values: {conc_vals.flatten()[:5]}")
