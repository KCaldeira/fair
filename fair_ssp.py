# env: python -m venv .venv && source .venv/bin/activate && pip install fair
from fair import FAIR
from fair.io import read_properties
from fair.interface import fill, initialise

# 1) Model & horizon
f = FAIR(ch4_method='thornhill2021')  # common option in examples
f.define_time(1750, 2100, 1)
f.define_scenarios(['ssp245'])

# 2) Species & properties (defaults OK for an emissions-driven run)
species, props = read_properties()          # default “kitchen sink”
f.define_species(species, props)
f.allocate()

# 3) Default species configs
f.fill_species_configs()

# 4) Pull emissions (and solar/volcanic) directly from RCMIP
#    This stitches historical + SSP automatically for 'ssp245'
f.fill_from_rcmip()  # <- key step

# 5) Initialise state & run
initialise(f.concentration, f.species_configs['baseline_concentration'])
initialise(f.forcing, 0); initialise(f.temperature, 0)
initialise(f.cumulative_emissions, 0); initialise(f.airborne_emissions, 0)
f.run()

# e.g., access emissions or temps:
em_CO2 = f.emissions.sel(scenario='ssp245', specie='CO2 FFI')  # example
