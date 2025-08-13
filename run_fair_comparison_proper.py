#!/usr/bin/env python3
"""
Script to run FAIR model comparison between baseline and counterfactual scenarios.

This script uses the proper FAIR initialization approach based on fair_ssp.py example.
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
    f.define_configs(['default'])
    
    # 2) Species & properties - use only species we have data for
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
    
    # 3) Default species configs
    f.fill_species_configs()
    
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
        species_idx = list(f.emissions.specie.values).index(fair_species)
        
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
    
    # 5) Initialise state & run
    print("Initializing model state...")
    # Initialize climate configs with default values
    initialise(f.climate_configs['ocean_heat_capacity'], [2.92, 11.28, 73.25])
    initialise(f.climate_configs['ocean_heat_transfer'], [0.73, 0.70, 0.70])
    initialise(f.climate_configs['deep_ocean_efficacy'], 1.28)
    initialise(f.climate_configs['forcing_4co2'], 7.32)
    
    # Use proper FAIR initialization method
    initialise(f.concentration, f.species_configs['baseline_concentration'])
    initialise(f.forcing, 0)
    initialise(f.temperature, 0)
    initialise(f.cumulative_emissions, 0)
    initialise(f.airborne_emissions, 0)
    
    print("Running FAIR model...")
    f.run()
    
    # 6) Extract results
    print("Extracting results...")
    results = {
        'scenario_name': scenario_name,
        'temperature': f.temperature.sel(scenario=scenario_name, layer=0).values.flatten(),  # Surface temperature
        'co2_concentration': f.concentration.sel(scenario=scenario_name, specie='CO2').values.flatten(),
        'years': np.arange(1750, 2023),  # Match FAIR's 273 timepoints (1750-2022)
        'emissions': f.emissions.sel(scenario=scenario_name, specie='CO2').values.flatten()  # Use 'CO2' not 'CO2 FFI'
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
        'emissions_diff_series': emissions_diff,
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
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    years = baseline_results['years']
    
    # Plot 1: Temperature comparison
    ax1.plot(years, baseline_results['temperature'], 'b-', label='Baseline SSP245', linewidth=2)
    ax1.plot(years, counterfactual_results['temperature'], 'r-', label='1975 Carbon Intensity', linewidth=2)
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Temperature Change (°C)')
    ax1.set_title('Temperature Comparison')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: CO2 concentration comparison
    ax2.plot(years, baseline_results['co2_concentration'], 'b-', label='Baseline SSP245', linewidth=2)
    ax2.plot(years, counterfactual_results['co2_concentration'], 'r-', label='1975 Carbon Intensity', linewidth=2)
    ax2.set_xlabel('Year')
    ax2.set_ylabel('CO2 Concentration (ppm)')
    ax2.set_title('CO2 Concentration Comparison')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Temperature difference
    ax3.plot(years, comparison['temp_diff_series'], 'g-', linewidth=2)
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Temperature Difference (°C)')
    ax3.set_title('Temperature Difference (Counterfactual - Baseline)')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: CO2 concentration difference
    ax4.plot(years, comparison['co2_diff_series'], 'g-', linewidth=2)
    ax4.set_xlabel('Year')
    ax4.set_ylabel('CO2 Concentration Difference (ppm)')
    ax4.set_title('CO2 Concentration Difference (Counterfactual - Baseline)')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    plot_file = output_dir / "fair_comparison_results.png"
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"Saved comparison plot: {plot_file}")
    
    # Save results to CSV
    # Arrays are already flattened from the results extraction
    results_df = pd.DataFrame({
        'Year': years,
        'Baseline_Temperature_C': baseline_results['temperature'],
        'Counterfactual_Temperature_C': counterfactual_results['temperature'],
        'Temperature_Difference_C': comparison['temp_diff_series'],
        'Baseline_CO2_ppm': baseline_results['co2_concentration'],
        'Counterfactual_CO2_ppm': counterfactual_results['co2_concentration'],
        'CO2_Difference_ppm': comparison['co2_diff_series'],
        'Baseline_Emissions_MtCO2': baseline_results['emissions'],
        'Counterfactual_Emissions_MtCO2': counterfactual_results['emissions'],
        'Emissions_Difference_MtCO2': comparison['emissions_diff_series']
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

if __name__ == "__main__":
    main()
