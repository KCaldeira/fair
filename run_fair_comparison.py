#!/usr/bin/env python3
"""
Script to run FAIR model comparison between baseline and counterfactual scenarios.

This script:
1. Runs FAIR with the interpolated baseline emissions (emissions_ssp245_interpolated.csv)
2. Runs FAIR with the counterfactual emissions (emissions_ssp245_interpolated_counterfactual_1975.csv)
3. Compares temperature and concentration results between the two scenarios
4. Saves results and creates visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fair import FAIR
from fair.io import read_properties
from fair.interface import fill, initialise
from pathlib import Path

def run_fair_scenario(emissions_file, scenario_name):
    """
    Run FAIR model for a given emissions file and scenario name.
    
    Parameters:
    -----------
    emissions_file : str
        Path to the emissions CSV file
    scenario_name : str
        Name for the scenario (for labeling results)
    
    Returns:
    --------
    dict
        Dictionary containing FAIR model results
    """
    
    print(f"\n{'='*60}")
    print(f"Running FAIR model for: {scenario_name}")
    print(f"Emissions file: {emissions_file}")
    print(f"{'='*60}")
    
    # 1) Model & horizon
    f = FAIR(ch4_method='thornhill2021')  # Use default GHG method
    f.define_time(1750, 2023, 1)  # Updated to match our data range
    f.define_scenarios([scenario_name])
    f.define_configs(['default'])  # Add default config
    
    # 2) Species & properties - use only the species we have data for
    # Define a simpler set of species that matches our CSV data
    simple_species = ['CO2', 'CH4', 'N2O', 'Sulfur', 'BC', 'OC']
    simple_props = {
        'CO2': {
            'type': 'co2',
            'input_mode': 'emissions',
            'greenhouse_gas': True,
            'aerosol_chemistry_from_emissions': False,
            'aerosol_chemistry_from_concentration': False,
        },
        'CH4': {
            'type': 'ch4',
            'input_mode': 'emissions',
            'greenhouse_gas': True,
            'aerosol_chemistry_from_emissions': False,
            'aerosol_chemistry_from_concentration': False,
        },
        'N2O': {
            'type': 'n2o',
            'input_mode': 'emissions',
            'greenhouse_gas': True,
            'aerosol_chemistry_from_emissions': False,
            'aerosol_chemistry_from_concentration': False,
        },
        'Sulfur': {
            'type': 'sulfur',
            'input_mode': 'emissions',
            'greenhouse_gas': False,
            'aerosol_chemistry_from_emissions': True,
            'aerosol_chemistry_from_concentration': False,
        },
        'BC': {
            'type': 'black carbon',
            'input_mode': 'emissions',
            'greenhouse_gas': False,
            'aerosol_chemistry_from_emissions': True,
            'aerosol_chemistry_from_concentration': False,
        },
        'OC': {
            'type': 'organic carbon',
            'input_mode': 'emissions',
            'greenhouse_gas': False,
            'aerosol_chemistry_from_emissions': True,
            'aerosol_chemistry_from_concentration': False,
        }
    }
    
    f.define_species(simple_species, simple_props)
    f.allocate()
    
    # 3) Default species configs and climate configs
    f.fill_species_configs()
    
    # Initialize climate configs with default values
    # These values are from the MAGICC model parameter set used in IPCC assessments
    # Source: Meinshausen et al. (2011) "The RCP greenhouse gas concentrations and their extensions from 1765 to 2300"
    from fair.interface import initialise
    
    # Ocean heat capacity values (W/m²/K) for three-layer ocean model
    initialise(f.climate_configs['ocean_heat_capacity'], [2.92, 11.28, 73.25])
    # Ocean heat transfer coefficients (W/m²/K) for three-layer ocean model  
    initialise(f.climate_configs['ocean_heat_transfer'], [0.73, 0.70, 0.70])
    # Deep ocean efficacy parameter (dimensionless) - single value, not array
    initialise(f.climate_configs['deep_ocean_efficacy'], 1.28)
    # Radiative forcing for 4xCO2 (W/m²) - standard climate sensitivity parameter - single value
    initialise(f.climate_configs['forcing_4co2'], 7.32)
    
    # 4) Load emissions from our custom CSV file
    print("Loading emissions data from CSV...")
    df_emissions = pd.read_csv(emissions_file)
    
    # Map CSV variables to FAIR species names
    variable_mapping = {
        'Emissions|CO2': 'CO2',  # Use 'CO2' instead of 'CO2 FFI' for GHG method compatibility
        'Emissions|CH4': 'CH4',
        'Emissions|N2O': 'N2O',
        'Emissions|Sulfur': 'Sulfur',
        'Emissions|BC': 'BC',
        'Emissions|OC': 'OC'
    }
    
    # Fill emissions data into FAIR for all species
    print("Filling emissions data into FAIR...")
    for csv_var, fair_species in variable_mapping.items():
        # Get the emissions row for this species
        species_row = df_emissions[df_emissions['Variable'] == csv_var]
        if len(species_row) == 0:
            print(f"Warning: Could not find '{csv_var}' in {emissions_file}")
            continue
            
        print(f"Processing {csv_var} -> {fair_species}")
        
        # Get the emissions values for all years
        species_values = species_row.iloc[0, 3:].values  # Skip Scenario, Variable, Unit columns
        years = species_row.columns[3:].astype(int).values  # Get year columns
        
        # Fill NaN values with zeros for early years (before emissions data starts)
        species_values = np.nan_to_num(species_values, nan=0.0)
        
        # Find the species index in FAIR
        species_idx = simple_species.index(fair_species)
        
        # Fill the emissions array directly
        filled_count = 0
        for i, year in enumerate(years):
            # Find the index in the FAIR timepoints (FAIR uses half-year timepoints)
            target_timepoint = year + 0.5  # Convert integer year to half-year timepoint
            time_idx = np.where(f.emissions.timepoints.values == target_timepoint)[0]
            if len(time_idx) > 0:
                f.emissions[time_idx[0], 0, 0, species_idx] = species_values[i]  # [time, scenario, config, specie]
                filled_count += 1
                if species_values[i] > 0 and fair_species == 'CO2':
                    print(f"  Year {year}: {species_values[i]:.1f} MtCO2/yr")
        
        print(f"  Filled {filled_count} timepoints for {fair_species}")
    
    # Debug: Check for NaN values in the emissions array
    print(f"\nDebug: Checking for NaN values in emissions array...")
    print(f"FAIR timepoints range: {f.emissions.timepoints.min().values} to {f.emissions.timepoints.max().values}")
    print(f"Number of FAIR timepoints: {len(f.emissions.timepoints)}")
    print(f"First 10 FAIR timepoints: {f.emissions.timepoints[:10].values}")
    
    for i, species in enumerate(simple_species):
        nan_count = np.isnan(f.emissions[:, 0, 0, i]).sum()
        print(f"  {species}: {nan_count} NaN values out of {len(f.emissions.timepoints)} total")
        if nan_count > 0:
            print(f"    First few values: {f.emissions[:5, 0, 0, i].values}")
    
    # 5) Initialise state & run
    print("Initializing model state...")
    # Don't use initialise for concentration - it only sets first timepoint
    initialise(f.forcing, 0)
    initialise(f.temperature, 0)
    initialise(f.cumulative_emissions, 0)
    initialise(f.airborne_emissions, 0)
    
    # Additional initialization to prevent NaN values in gas cycle calculations
    # Ensure all arrays are properly initialized to prevent log(0) or log(NaN) issues
    f.temperature.values[:] = 0.0  # Ensure all temperature values are exactly 0
    f.forcing.values[:] = 0.0      # Ensure all forcing values are exactly 0
    f.cumulative_emissions.values[:] = 0.0  # Ensure all cumulative emissions are exactly 0
    f.airborne_emissions.values[:] = 0.0    # Ensure all airborne emissions are exactly 0
    
    # Properly initialize concentration arrays to prevent NaN values
    # The baseline_concentration only has one value per species, but we need to fill all timepoints
    # Initialize all species that have baseline concentrations, not just simple_species
    for species in f.species_configs['baseline_concentration'].specie.values:
        baseline_value = f.species_configs['baseline_concentration'].sel(specie=species).values
        if not np.isnan(baseline_value):
            # Fill all timepoints with the baseline concentration value
            f.concentration.sel(specie=species).values[:] = baseline_value
        else:
            # If baseline value is NaN, use a reasonable default
            if species == 'CH4':
                f.concentration.sel(specie=species).values[:] = 729.2  # Pre-industrial CH4
            elif species == 'CO2':
                f.concentration.sel(specie=species).values[:] = 278.0  # Pre-industrial CO2
            elif species == 'N2O':
                f.concentration.sel(specie=species).values[:] = 270.0  # Pre-industrial N2O
            elif species == 'CO2 FFI':
                f.concentration.sel(specie=species).values[:] = 278.0  # Same as CO2
            elif species == 'CO2 AFOLU':
                f.concentration.sel(specie=species).values[:] = 278.0  # Same as CO2
            else:
                f.concentration.sel(specie=species).values[:] = 0.0  # Default for other species
    

    
    print("Running FAIR model...")
    f.run()
    
    # 6) Extract results
    print("Extracting results...")
    results = {
        'scenario_name': scenario_name,
        'temperature': f.temperature.sel(scenario=scenario_name, layer=0).values,  # Surface temperature
        'co2_concentration': f.concentration.sel(scenario=scenario_name, specie='CO2').values,
        'years': np.arange(1750, 2023),  # Match FAIR's 273 timepoints (1750-2022)
        'emissions': f.emissions.sel(scenario=scenario_name, specie='CO2').values  # Use 'CO2' not 'CO2 FFI'
    }
    
    print(f"Completed FAIR run for {scenario_name}")
    return results

def compare_scenarios(baseline_results, counterfactual_results):
    """
    Compare results between baseline and counterfactual scenarios.
    
    Parameters:
    -----------
    baseline_results : dict
        Results from baseline scenario
    counterfactual_results : dict
        Results from counterfactual scenario
    
    Returns:
    --------
    dict
        Comparison metrics
    """
    
    print(f"\n{'='*60}")
    print("COMPARISON RESULTS")
    print(f"{'='*60}")
    
    # Calculate differences
    temp_diff = counterfactual_results['temperature'] - baseline_results['temperature']
    co2_diff = counterfactual_results['co2_concentration'] - baseline_results['co2_concentration']
    emissions_diff = counterfactual_results['emissions'] - baseline_results['emissions']
    
    # Key metrics
    comparison = {
        'temp_diff_2023': temp_diff[-1],  # Temperature difference in 2023
        'co2_diff_2023': co2_diff[-1],    # CO2 concentration difference in 2023
        'max_temp_diff': np.max(temp_diff),
        'max_co2_diff': np.max(co2_diff),
        'cumulative_emissions_diff': np.sum(emissions_diff),
        'temp_diff_series': temp_diff,
        'co2_diff_series': co2_diff,
        'emissions_diff_series': emissions_diff,  # Add missing emissions difference series
        'years': baseline_results['years']
    }
    
    # Print summary
    print(f"Temperature difference in 2023: {float(comparison['temp_diff_2023']):.3f}°C")
    print(f"CO2 concentration difference in 2023: {float(comparison['co2_diff_2023']):.1f} ppm")
    print(f"Maximum temperature difference: {float(comparison['max_temp_diff']):.3f}°C")
    print(f"Maximum CO2 concentration difference: {float(comparison['max_co2_diff']):.1f} ppm")
    print(f"Cumulative emissions difference: {float(comparison['cumulative_emissions_diff']):.0f} MtCO2")
    
    return comparison

def create_visualizations(baseline_results, counterfactual_results, comparison):
    """
    Create visualizations comparing the two scenarios.
    
    Parameters:
    -----------
    baseline_results : dict
        Results from baseline scenario
    counterfactual_results : dict
        Results from counterfactual scenario
    comparison : dict
        Comparison metrics
    """
    
    print("\nCreating visualizations...")
    
    # Create output directory
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    # Set up the plot
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('FAIR Model Comparison: Baseline vs 1975 Carbon Intensity Counterfactual', fontsize=16)
    
    years = baseline_results['years']
    
    # 1. Temperature comparison
    axes[0, 0].plot(years, baseline_results['temperature'], 'b-', label='Baseline SSP245', linewidth=2)
    axes[0, 0].plot(years, counterfactual_results['temperature'], 'r-', label='1975 Carbon Intensity', linewidth=2)
    axes[0, 0].set_xlabel('Year')
    axes[0, 0].set_ylabel('Temperature Anomaly (°C)')
    axes[0, 0].set_title('Global Mean Temperature')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. CO2 concentration comparison
    axes[0, 1].plot(years, baseline_results['co2_concentration'], 'b-', label='Baseline SSP245', linewidth=2)
    axes[0, 1].plot(years, counterfactual_results['co2_concentration'], 'r-', label='1975 Carbon Intensity', linewidth=2)
    axes[0, 1].set_xlabel('Year')
    axes[0, 1].set_ylabel('CO2 Concentration (ppm)')
    axes[0, 1].set_title('Atmospheric CO2 Concentration')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Temperature difference
    axes[1, 0].plot(years, comparison['temp_diff_series'], 'g-', linewidth=2)
    axes[1, 0].set_xlabel('Year')
    axes[1, 0].set_ylabel('Temperature Difference (°C)')
    axes[1, 0].set_title('Temperature Difference (Counterfactual - Baseline)')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].axhline(y=0, color='k', linestyle='--', alpha=0.5)
    
    # 4. CO2 concentration difference
    axes[1, 1].plot(years, comparison['co2_diff_series'], 'g-', linewidth=2)
    axes[1, 1].set_xlabel('Year')
    axes[1, 1].set_ylabel('CO2 Concentration Difference (ppm)')
    axes[1, 1].set_title('CO2 Concentration Difference (Counterfactual - Baseline)')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].axhline(y=0, color='k', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    
    # Save the plot
    plot_file = output_dir / "fair_comparison_results.png"
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"Saved comparison plot: {plot_file}")
    
    # Save results to CSV
    # Ensure all arrays are 1D for pandas DataFrame
    results_df = pd.DataFrame({
        'Year': years,
        'Baseline_Temperature_C': baseline_results['temperature'].flatten(),
        'Counterfactual_Temperature_C': counterfactual_results['temperature'].flatten(),
        'Temperature_Difference_C': comparison['temp_diff_series'].flatten(),
        'Baseline_CO2_ppm': baseline_results['co2_concentration'].flatten(),
        'Counterfactual_CO2_ppm': counterfactual_results['co2_concentration'].flatten(),
        'CO2_Difference_ppm': comparison['co2_diff_series'].flatten(),
        'Baseline_Emissions_MtCO2': baseline_results['emissions'].flatten(),
        'Counterfactual_Emissions_MtCO2': counterfactual_results['emissions'].flatten(),
        'Emissions_Difference_MtCO2': comparison['emissions_diff_series'].flatten()  # Fixed: use emissions difference
    })
    
    csv_file = output_dir / "fair_comparison_results.csv"
    results_df.to_csv(csv_file, index=False)
    print(f"Saved results to CSV: {csv_file}")
    
    plt.show()

def main():
    """
    Main function to run the FAIR comparison.
    """
    
    print("FAIR Model Comparison: Baseline vs 1975 Carbon Intensity Counterfactual")
    print("="*80)
    
    # File paths
    baseline_file = "inputs/emissions_ssp245_interpolated.csv"
    counterfactual_file = "inputs/emissions_ssp245_interpolated_counterfactual_1975.csv"
    
    # Check if files exist
    if not Path(baseline_file).exists():
        raise FileNotFoundError(f"Baseline emissions file not found: {baseline_file}")
    if not Path(counterfactual_file).exists():
        raise FileNotFoundError(f"Counterfactual emissions file not found: {counterfactual_file}")
    
    # Run FAIR for baseline scenario
    baseline_results = run_fair_scenario(baseline_file, "baseline_ssp245")
    
    # Run FAIR for counterfactual scenario
    counterfactual_results = run_fair_scenario(counterfactual_file, "counterfactual_1975")
    
    # Compare results
    comparison = compare_scenarios(baseline_results, counterfactual_results)
    
    # Create visualizations
    create_visualizations(baseline_results, counterfactual_results, comparison)
    
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print("The counterfactual scenario shows the climate impact of maintaining")
    print("1975 carbon intensity levels while allowing GDP to grow historically.")
    print("This represents the 'cost' of not improving energy efficiency and")
    print("decarbonization technologies since 1975.")

if __name__ == "__main__":
    main()
