#!/usr/bin/env python3
"""
Test proper FAIR initialization following the example in fair_ssp.py
"""

from fair import FAIR
from fair.io import read_properties
from fair.interface import fill, initialise

print("Testing proper FAIR initialization...")

# 1) Model & horizon
f = FAIR(ch4_method='thornhill2021')  # common option in examples
f.define_time(1750, 2023, 1)
f.define_scenarios(['ssp245'])
f.define_configs(['default'])  # Add config definition

# 2) Species & properties (defaults OK for an emissions-driven run)
species, props = read_properties()          # default "kitchen sink"
f.define_species(species, props)
f.allocate()

# 3) Default species configs
f.fill_species_configs()

# 4) Pull emissions (and solar/volcanic) directly from RCMIP
#    This stitches historical + SSP automatically for 'ssp245'
print("Filling from RCMIP...")
f.fill_from_rcmip()  # <- key step

# 5) Initialise state & run
print("Initializing state...")
# Initialize climate configs with default values
initialise(f.climate_configs['ocean_heat_capacity'], [2.92, 11.28, 73.25])
initialise(f.climate_configs['ocean_heat_transfer'], [0.73, 0.70, 0.70])
initialise(f.climate_configs['deep_ocean_efficacy'], 1.28)
initialise(f.climate_configs['forcing_4co2'], 7.32)

initialise(f.concentration, f.species_configs['baseline_concentration'])
initialise(f.forcing, 0); initialise(f.temperature, 0)
initialise(f.cumulative_emissions, 0); initialise(f.airborne_emissions, 0)

print("Running FAIR...")
f.run()

print("FAIR run completed successfully!")
print("Available scenarios:", list(f.emissions.scenario.values))
print("Available species:", list(f.emissions.specie.values)[:10], "...")  # First 10 species

# Check for any NaN values
import numpy as np
print("\nChecking for NaN values:")
print("Emissions NaN count:", np.isnan(f.emissions.values).sum())
print("Concentration NaN count:", np.isnan(f.concentration.values).sum())
print("Temperature NaN count:", np.isnan(f.temperature.values).sum())
