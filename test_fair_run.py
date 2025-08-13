#!/usr/bin/env python3
"""
Test if FAIR.run() overwrites concentration values
"""

import numpy as np
from fair import FAIR
from fair.interface import initialise

# Initialize FAIR
f = FAIR()
f.define_time(1750, 2023, 1)
f.define_scenarios(['test'])
f.define_configs(['default'])

# Load species properties
from fair.io import read_properties
species, props = read_properties()
f.define_species(species, props)
f.allocate()
f.fill_species_configs()

# Initialize climate configs
initialise(f.climate_configs['ocean_heat_capacity'], [2.92, 11.28, 73.25])
initialise(f.climate_configs['ocean_heat_transfer'], [0.73, 0.70, 0.70])
initialise(f.climate_configs['deep_ocean_efficacy'], 1.28)
initialise(f.climate_configs['forcing_4co2'], 7.32)

# Initialize other arrays
initialise(f.forcing, 0)
initialise(f.temperature, 0)
initialise(f.cumulative_emissions, 0)
initialise(f.airborne_emissions, 0)

# Set all values to zero
f.temperature.values[:] = 0.0
f.forcing.values[:] = 0.0
f.cumulative_emissions.values[:] = 0.0
f.airborne_emissions.values[:] = 0.0

# Initialize concentrations
simple_species = ['CO2', 'CH4', 'N2O', 'Sulfur', 'BC', 'OC']
for species in simple_species:
    if species in f.species_configs['baseline_concentration'].specie.values:
        baseline_value = f.species_configs['baseline_concentration'].sel(specie=species).values
        if not np.isnan(baseline_value):
            f.concentration.sel(specie=species).values[:] = baseline_value

print("Before FAIR.run():")
print("CH4 concentration (first 5):", f.concentration.sel(specie='CH4').values.flatten()[:5])
print("Any NaN in CH4:", np.isnan(f.concentration.sel(specie='CH4').values).any())

print("\nRunning FAIR...")
f.run()

print("\nAfter FAIR.run():")
print("CH4 concentration (first 5):", f.concentration.sel(specie='CH4').values.flatten()[:5])
print("Any NaN in CH4:", np.isnan(f.concentration.sel(specie='CH4').values).any())
