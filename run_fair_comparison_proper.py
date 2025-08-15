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
    Run FAIR model for a given emissions scenario.
    
    Parameters:
    -----------
    emissions_file : str
        Path to emissions CSV file
    scenario_name : str
        Name of the scenario
    
    Returns:
    --------
    dict
        Dictionary containing processed results and raw FAIR model data
    """
    print(f"\n{'='*60}")
    print(f"Running FAIR model for: {scenario_name}")
    print(f"Emissions file: {emissions_file}")
    print(f"{'='*60}")
    
    # Initialize FAIR model
    f = FAIR()
    
    # Proper initialization sequence
    print("Initializing FAIR model...")
    f.define_time(1750, 2023, 1)
    f.define_scenarios(['ssp245'])
    f.define_configs(['default'])
    
    # Define species and properties
    print("Defining species and properties...")
    from fair.io import read_properties
    species, props = read_properties()  # Use default "kitchen sink"
    f.define_species(species, props)
    f.allocate()
    
    # Use fill_from_rcmip() for proper initialization
    print("Using fill_from_rcmip() for proper initialization with scenario 'ssp245'...")
    f.fill_from_rcmip()
    
    # Change scenario name for our custom data
    print("Changing scenario name from 'ssp245' to '{}'...".format(scenario_name))
    f.scenarios = [scenario_name]
    
    # Update scenario names in all FAIR arrays
    f.emissions['scenario'] = [scenario_name]
    f.concentration['scenario'] = [scenario_name]
    f.forcing['scenario'] = [scenario_name]
    f.temperature['scenario'] = [scenario_name]
    f.cumulative_emissions['scenario'] = [scenario_name]
    f.airborne_emissions['scenario'] = [scenario_name]
    
    # Load and apply custom emissions data
    print("Loading and applying custom emissions data...")
    emissions_data = pd.read_csv(emissions_file)
    print("Overriding emissions with custom data...")
    
    # Process each species
    for _, row in emissions_data.iterrows():
        species = row['Variable']
        unit_info = row.get('Unit', 'Unknown')
        
        # Map CSV variable names to FAIR species names
        fair_species_map = {
            'Emissions|CO2': 'CO2 FFI',
            'Emissions|CH4': 'CH4',
            'Emissions|N2O': 'N2O',
            'Emissions|Sulfur': 'Sulfur',
            'Emissions|BC': 'BC',
            'Emissions|OC': 'OC'
        }
        
        fair_species = fair_species_map.get(species, species)
        
        # Check if the species exists in FAIR's baseline emissions config
        if fair_species in f.species_configs['baseline_emissions'].specie.values:
            print(f"Processing {species} -> {fair_species}")
            
            # Extract emissions values
            species_values = []
            for year in range(1750, 2024):
                if str(year) in row:
                    species_values.append(row[str(year)])
                else:
                    species_values.append(0.0)
            
            species_values = np.array(species_values)
            
            # Print emissions info
            print(f"  Unit from CSV: {unit_info}")
            print(f"  First 5 emissions values: {species_values[:5]}")
            print(f"  Last 5 emissions values: {species_values[-5:]}")
            print(f"  Min emissions: {species_values.min():.1f}")
            print(f"  Max emissions: {species_values.max():.1f}")
            
            # Handle unit conversion for CO2
            if fair_species == 'CO2 FFI':
                if 'MtCO2' in str(unit_info):
                    print(f"  Emissions are in MtCO2/yr, but FAIR expects GtCO2/yr")
                    print(f"  Converting from MtCO2/yr to GtCO2/yr (dividing by 1000)")
                    print(f"  Max emissions: {species_values.max():.1f} MtCO2/yr = {species_values.max()/1000:.3f} GtCO2/yr")
                    species_values = species_values / 1000.0
                    print(f"  After conversion - First 5 values: {species_values[:5]}")
                    print(f"  After conversion - Max value: {species_values.max():.3f} GtCO2/yr")
                elif 'GtCO2' in str(unit_info):
                    print(f"  Emissions are in GtCO2/yr - this should be correct for FAIR")
                    print(f"  Max emissions: {species_values.max():.3f} GtCO2/yr")
                else:
                    print(f"  WARNING: Unknown unit '{unit_info}' for CO2 emissions")
                    print(f"  Values: {species_values.max():.1f} - assuming MtCO2/yr and converting to GtCO2/yr")
                    species_values = species_values / 1000.0
                    print(f"  After conversion - Max value: {species_values.max():.3f} GtCO2/yr")
            
            # Print year-by-year emissions for CO2
            if fair_species == 'CO2 FFI':
                print("  Year-by-year CO2 emissions (first 20 and last 20 years):")
                for i, year in enumerate(range(1750, 1770)):
                    print(f"  Year {year}: {species_values[i]:.3f} GtCO2/yr")
                print("  ...")
                for i, year in enumerate(range(2004, 2024)):
                    actual_index = year - 1750
                    if actual_index < len(species_values):
                        print(f"  Year {year}: {species_values[actual_index]:.3f} GtCO2/yr")
            
            # Ensure emissions data length matches FAIR timepoints
            fair_years = f.temperature.timebounds.values
            if len(species_values) != len(fair_years):
                print(f"  Warning: Emissions data length ({len(species_values)}) doesn't match FAIR timepoints ({len(fair_years)})")
                if len(species_values) < len(fair_years):
                    # Pad with zeros
                    padding = np.zeros(len(fair_years) - len(species_values))
                    species_values = np.concatenate([species_values, padding])
                    print(f"  Padded emissions data to {len(species_values)} timepoints")
                else:
                    # Truncate
                    species_values = species_values[:len(fair_years)]
                    print(f"  Truncated emissions data to {len(species_values)} timepoints")
            
            # Debug: Check FAIR emissions array shape
            print(f"  FAIR emissions array shape for {fair_species}: {f.emissions.sel(scenario=scenario_name, specie=fair_species).shape}")
            print(f"  Our species_values shape: {species_values.shape}")
            
            # Reshape species_values to match FAIR's expected format
            # FAIR expects (timepoints, scenarios, configs, species) format
            # We need to ensure our data matches the timepoints dimension
            if len(species_values) != f.emissions.sel(scenario=scenario_name, specie=fair_species).shape[0]:
                print(f"  WARNING: Shape mismatch! Reshaping data...")
                # Get the expected shape from FAIR
                expected_shape = f.emissions.sel(scenario=scenario_name, specie=fair_species).shape
                print(f"  Expected shape: {expected_shape}")
                
                # Reshape to match the timepoints dimension
                if len(species_values) > expected_shape[0]:
                    species_values = species_values[:expected_shape[0]]
                    print(f"  Truncated to {len(species_values)} timepoints")
                elif len(species_values) < expected_shape[0]:
                    padding = np.zeros(expected_shape[0] - len(species_values))
                    species_values = np.concatenate([species_values, padding])
                    print(f"  Padded to {len(species_values)} timepoints")
            
            # Ensure the array has the correct 2D shape that FAIR expects
            # FAIR expects (timepoints, 1) format, not just (timepoints,)
            if len(species_values.shape) == 1:
                species_values = species_values.reshape(-1, 1)
                print(f"  Reshaped from 1D to 2D: {species_values.shape}")
            
            print(f"  Final species_values shape: {species_values.shape}")
            
            # Additional debug: Check if shapes are compatible
            fair_shape = f.emissions.sel(scenario=scenario_name, specie=fair_species).shape
            print(f"  FAIR target shape: {fair_shape}")
            print(f"  Our data shape: {species_values.shape}")
            print(f"  Shapes compatible: {species_values.shape == fair_shape}")
            
            # Set emissions in FAIR
            f.emissions.loc[dict(scenario=scenario_name, specie=fair_species)] = species_values
            print(f"  Filled {len(species_values)} timepoints for {fair_species}")
        else:
            print(f"  Skipping {species} -> {fair_species} (not in FAIR species config)")
            # Debug: Show available species in FAIR
            if species == 'Emissions|CO2':  # Only show this once to avoid spam
                print(f"    Available species in FAIR baseline_emissions: {list(f.species_configs['baseline_emissions'].specie.values)}")
    
    print("=== DEBUGGING EMISSIONS DATA IN FAIR ===")
    co2_emissions_in_fair = f.emissions.sel(scenario=scenario_name, specie='CO2 FFI').values
    print(f"CO2 emissions in FAIR array:")
    print(f"  Shape: {co2_emissions_in_fair.shape}")
    print(f"  First 10 values: {co2_emissions_in_fair[:10]}")
    print(f"  Last 10 values: {co2_emissions_in_fair[-10:]}")
    print(f"  Min: {co2_emissions_in_fair.min():.6f}")
    print(f"  Max: {co2_emissions_in_fair.max():.6f}")
    print(f"  Non-zero count: {(co2_emissions_in_fair > 0).sum()}")
    
    print(f"\nBaseline concentrations in FAIR:")
    for species in ['CO2', 'CH4', 'N2O']:
        if species in f.species_configs['baseline_concentration'].specie.values:
            baseline_val = f.species_configs['baseline_concentration'].sel(specie=species).values
            print(f"  {species}: {baseline_val}")
    
    print(f"\nConcentration values after initialization:")
    for species in ['CO2', 'CH4', 'N2O']:
        if species in f.concentration.specie.values:
            conc_vals = f.concentration.sel(specie=species).values
            print(f"  {species}: min={conc_vals.min():.1f}, max={conc_vals.max():.1f}, mean={conc_vals.mean():.1f}")
    print("=== END EMISSIONS DEBUGGING ===\n")
    
    # 7) Initialize climate configs with our preferred values
    # These values are from the MAGICC model parameter set used in IPCC assessments
    # Source: Meinshausen et al. (2011) "The RCP greenhouse gas concentrations and their extensions from 1765 to 2300"
    print("Setting climate model parameters...")
    initialise(f.climate_configs['ocean_heat_capacity'], [2.92, 11.28, 73.25])
    initialise(f.climate_configs['ocean_heat_transfer'], [0.73, 0.70, 0.70])
    initialise(f.climate_configs['deep_ocean_efficacy'], 1.28)
    initialise(f.climate_configs['forcing_4co2'], 7.32)
    
    # CRITICAL FIX: Initialize temperature and other arrays BEFORE debugging
    print("Initializing temperature and other arrays...")
    initialise(f.temperature, 0)
    initialise(f.forcing, 0)
    initialise(f.cumulative_emissions, 0)
    initialise(f.airborne_emissions, 0)
    
    # CRITICAL FIX: Initialize concentrations properly
    print("Initializing concentrations with baseline values...")
    for species in f.concentration.specie.values:
        if species in f.species_configs['baseline_concentration'].specie.values:
            baseline_val = f.species_configs['baseline_concentration'].sel(specie=species).values
            print(f"  Setting {species} concentration to baseline: {baseline_val}")
            f.concentration.loc[dict(specie=species)] = baseline_val
        else:
            # Fallback values for species not in baseline config
            fallback_values = {
                'CO2': 278.3,  # Pre-industrial CO2
                'CH4': 729.2,  # Pre-industrial CH4
                'N2O': 270.1,  # Pre-industrial N2O
            }
            if species in fallback_values:
                print(f"  Setting {species} concentration to fallback: {fallback_values[species]}")
                f.concentration.loc[dict(specie=species)] = fallback_values[species]
            else:
                print(f"  WARNING: No baseline value found for {species}")
    
    # DEBUG: Check CH4 emissions and concentrations
    print("\n=== DEBUGGING CH4 DATA ===")
    ch4_emissions = f.emissions.sel(scenario=scenario_name, specie='CH4').values
    ch4_concentrations = f.concentration.sel(scenario=scenario_name, specie='CH4').values
    print(f"CH4 emissions (1750-2023):")
    print(f"  Min: {ch4_emissions.min():.3f}")
    print(f"  Max: {ch4_emissions.max():.3f}")
    print(f"  Mean: {ch4_emissions.mean():.3f}")
    print(f"  First 10 values: {ch4_emissions[:10]}")
    print(f"  Values around 1900: {ch4_emissions[140:151]}")
    print(f"\nCH4 concentrations (1750-2023):")
    print(f"  Min: {ch4_concentrations.min()}")
    print(f"  Max: {ch4_concentrations.max()}")
    print(f"  Mean: {ch4_concentrations.mean()}")
    print(f"  First 10 values: {ch4_concentrations[:10]}")
    print(f"  Values around 1900: {ch4_concentrations[140:151]}")
    ch4_nan_count = np.isnan(ch4_concentrations).sum()
    print(f"  NaN values in CH4 concentrations: {ch4_nan_count}")
    early_ch4_emissions = ch4_emissions[:161]  # 1750-1910
    print(f"\nEarly CH4 emissions (1750-1910):")
    print(f"  Min: {early_ch4_emissions.min():.3f}")
    print(f"  Max: {early_ch4_emissions.max():.3f}")
    print(f"  First 10 values: {early_ch4_emissions[:10]}")
    early_ch4_negative = (early_ch4_emissions < 0).sum()
    early_ch4_zero = (early_ch4_emissions == 0).sum()
    print(f"  Negative values: {early_ch4_negative}")
    print(f"  Zero values: {early_ch4_zero}")
    print("=== END CH4 DEBUGGING ===\n")
    
    # 8) Run the model
    print("Running FAIR model...")
    
    # Debug temperature array before model run
    print("Debug: Temperature array shape:", f.temperature.shape)
    print("Debug: Temperature array dimensions:", f.temperature.dims)
    print("Debug: Temperature timebounds dimension:", f.temperature.timebounds)
    print("Debug: First 10 temperature values:", f.temperature.values.flatten()[:10])
    print("Debug: Any NaN in temperature:", np.isnan(f.temperature.values).any())
    print("Debug: Any negative in temperature:", (f.temperature.values < 0).any())
    
    # Debug CH4 lifetime temperature sensitivity
    print("Debug: Available species config parameters:", list(f.species_configs.keys()))
    possible_names = ['ch4_lifetime_temperature_sensitivity', 'lifetime_temperature_sensitivity', 'temperature_sensitivity']
    ch4_sensitivity = None
    for name in possible_names:
        if name in f.species_configs:
            ch4_sensitivity = f.species_configs[name]
            print(f"Debug: Found CH4 lifetime temperature sensitivity parameter: {name}")
            break
    
    if ch4_sensitivity is None:
        print("Debug: Could not find CH4 lifetime temperature sensitivity parameter")
        ch4_sensitivity = 0.1  # Default value for debugging
        print("Debug: CH4 lifetime temperature sensitivity is NaN:", np.isnan(ch4_sensitivity))
        print("Debug: CH4 lifetime temperature sensitivity value:", ch4_sensitivity)
    
    # Debug what values would be passed to np.log()
    print("Debug: Values that would be passed to np.log() for first 10 timepoints:")
    for i in range(min(10, len(f.temperature.values.flatten()))):
        temp = f.temperature.values.flatten()[i]
        log_arg = 1 + temp * ch4_sensitivity
        print(f"  Timepoint {i}: temp={temp:.6f}, log_arg={log_arg:.6f}")
        if np.isnan(log_arg):
            print(f"    WARNING: log_arg is NaN! This will cause log warning!")
    
    if np.isnan(f.temperature.values).any():
        print("\nROOT CAUSE IDENTIFIED: Temperature array contains NaN values!")
        print("This causes np.log(1 + NaN * sensitivity) = NaN, triggering the warnings.")
        print("Fixing temperature initialization...")
        f.temperature.values[:] = 0.0
        print("Debug: After fix - First 10 temperature values:", f.temperature.values.flatten()[:10])
        print("Debug: After fix - Any NaN in temperature:", np.isnan(f.temperature.values).any())
        print("Ensuring other arrays are properly initialized...")
        f.forcing.values[:] = 0.0
        f.cumulative_emissions.values[:] = 0.0
        f.airborne_emissions.values[:] = 0.0
        print("Temperature and other arrays properly initialized. Running model...")
    
    # Monitor temperature during model run
    print("\n=== MONITORING TEMPERATURE DURING MODEL RUN ===")
    temp_before = f.temperature.sel(scenario=scenario_name, layer=0).values.copy()
    print("Before model run - Temperature stats:")
    print(f"  Min: {temp_before.min():.6f}")
    print(f"  Max: {temp_before.max():.6f}")
    print(f"  Mean: {temp_before.mean():.6f}")
    print(f"  NaN count: {np.isnan(temp_before).sum()}")
    print(f"  Negative count: {(temp_before < 0).sum()}")
    
    # Check specific timepoints
    timepoints_to_check = [0, 10, 50, 100]
    print("Temperature at timepoints 0, 10, 50, 100:")
    for tp in timepoints_to_check:
        if tp < len(temp_before):
            temp = temp_before[tp]
            log_arg = 1 + temp * ch4_sensitivity
            print(f"  Timepoint {tp}: temp={temp:.6f}, log_arg={log_arg:.6f}")
    
    # Run the model
    f.run()
    
    # Check temperature after model run
    temp_after = f.temperature.sel(scenario=scenario_name, layer=0).values
    print("\nAfter model run - Temperature stats:")
    print(f"  Min: {temp_after.min():.6f}")
    print(f"  Max: {temp_after.max():.6f}")
    print(f"  Mean: {temp_after.mean():.6f}")
    print(f"  NaN count: {np.isnan(temp_after).sum()}")
    print(f"  Negative count: {(temp_after < 0).sum()}")
    
    # Check specific timepoints after run
    print("Temperature at timepoints 0, 10, 50, 100 (after run):")
    for tp in timepoints_to_check:
        if tp < len(temp_after):
            temp = temp_after[tp]
            log_arg = 1 + temp * ch4_sensitivity
            print(f"  Timepoint {tp}: temp={temp:.6f}, log_arg={log_arg:.6f}")
    
    print("=== END TEMPERATURE MONITORING ===\n")
    
    # Debug concentration values after model run
    print("\n=== DEBUGGING CONCENTRATION VALUES AFTER MODEL RUN ===")
    for species in ['CO2', 'CH4', 'N2O']:
        if species in f.concentration.specie.values:
            conc_vals = f.concentration.sel(scenario=scenario_name, specie=species).values
            print(f"{species} concentrations:")
            print(f"  Min: {conc_vals.min():.1f}")
            print(f"  Max: {conc_vals.max():.1f}")
            print(f"  Mean: {conc_vals.mean():.1f}")
            print(f"  First 5 values: {conc_vals[:5]}")
            print(f"  Last 5 values: {conc_vals[-5:]}")
            if species == 'CO2' and conc_vals.max() > 1000:
                print(f"  WARNING: CO2 concentrations > 1000 ppm - this is unrealistic!")
                print(f"  Historical CO2 should be ~280-420 ppm")
            elif species == 'CH4' and conc_vals.max() > 2000:
                print(f"  WARNING: CH4 concentrations > 2000 ppb - this is unrealistic!")
                print(f"  Historical CH4 should be ~700-1900 ppb")
    
    print(f"\nCumulative emissions:")
    cumul_emissions = f.cumulative_emissions.sel(scenario=scenario_name, specie='CO2 FFI').values
    print(f"  Min: {cumul_emissions.min():.1f}")
    print(f"  Max: {cumul_emissions.max():.1f}")
    print("=== END CONCENTRATION DEBUGGING ===\n")
    
    # Extract results
    print("Extracting results...")
    years = f.temperature.timebounds.values - 0.5  # Convert to year centers
    print(f"Debug: FAIR has {len(years)} timepoints")
    print(f"Debug: FAIR years range: {years.min():.1f} to {years.max():.1f}")
    
    # Extract emissions data
    emissions_raw = f.emissions.sel(scenario=scenario_name, specie='CO2 FFI').values
    print(f"Debug: Raw emissions data length: {len(emissions_raw)}")
    if len(emissions_raw) != len(years):
        print(f"Warning: Emissions data length ({len(emissions_raw)}) doesn't match years length ({len(years)})")
        if len(emissions_raw) < len(years):
            # Pad with last value
            padding = np.full(len(years) - len(emissions_raw), emissions_raw[-1])
            emissions_raw = np.concatenate([emissions_raw, padding])
        else:
            # Truncate
            emissions_raw = emissions_raw[:len(years)]
        print(f"Debug: Adjusted emissions data length: {len(emissions_raw)}")
    
    # Extract temperature and CO2 concentration
    temperature = f.temperature.sel(scenario=scenario_name, layer=0).values
    co2_concentration = f.concentration.sel(scenario=scenario_name, specie='CO2').values
    
    print(f"Debug: Results temperature shape: {temperature.shape}")
    print(f"Debug: Results years shape: {years.shape}")
    print(f"Debug: Results CO2 shape: {co2_concentration.shape}")
    print(f"Debug: Results emissions shape: {emissions_raw.shape}")
    
    print(f"Completed FAIR run for {scenario_name}")
    
    # Return both processed results and raw FAIR model data
    return {
        'years': years,
        'temperature': temperature,
        'co2_concentration': co2_concentration,
        'emissions': emissions_raw,
        'fair_model': f  # Include the complete FAIR model object
    }

def create_comparison(baseline_results, counterfactual_results):
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

def create_visualizations(baseline_results, counterfactual_results, comparison, all_results):
    """Create comprehensive visualizations and save results to CSV."""
    
    # Create output directory
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    # Create comparison plot
    print("Creating visualizations...")
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    years = baseline_results['years']
    
    # Temperature comparison
    axes[0].plot(years, baseline_results['temperature'], label='Baseline (SSP245)', linewidth=2)
    axes[0].plot(years, counterfactual_results['temperature'], label='Counterfactual (1975 Carbon Intensity)', linewidth=2)
    axes[0].set_ylabel('Temperature Change (°C)')
    axes[0].set_title('Temperature Comparison: Baseline vs Counterfactual')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # CO2 concentration comparison
    axes[1].plot(years, baseline_results['co2_concentration'], label='Baseline (SSP245)', linewidth=2)
    axes[1].plot(years, counterfactual_results['co2_concentration'], label='Counterfactual (1975 Carbon Intensity)', linewidth=2)
    axes[1].set_ylabel('CO2 Concentration (ppm)')
    axes[1].set_title('CO2 Concentration Comparison: Baseline vs Counterfactual')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Emissions comparison
    axes[2].plot(years, baseline_results['emissions'], label='Baseline (SSP245)', linewidth=2)
    axes[2].plot(years, counterfactual_results['emissions'], label='Counterfactual (1975 Carbon Intensity)', linewidth=2)
    axes[2].set_xlabel('Year')
    axes[2].set_ylabel('CO2 Emissions (MtCO2/yr)')
    axes[2].set_title('CO2 Emissions Comparison: Baseline vs Counterfactual')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_file = output_dir / "fair_comparison_results.png"
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"Saved comparison plot: {plot_file}")
    
    # Save detailed results to CSV for analysis
    print("Saving detailed results to CSV for analysis...")
    
    # Create comprehensive results DataFrame with all available data
    results_data = {
        'Year': years,
        'Temperature_Baseline': baseline_results['temperature'],
        'Temperature_Counterfactual': counterfactual_results['temperature'],
        'Temperature_Difference': counterfactual_results['temperature'] - baseline_results['temperature'],
        'CO2_Concentration_Baseline': baseline_results['co2_concentration'],
        'CO2_Concentration_Counterfactual': counterfactual_results['co2_concentration'],
        'CO2_Concentration_Difference': counterfactual_results['co2_concentration'] - baseline_results['co2_concentration'],
        'Emissions_Baseline': baseline_results['emissions'],
        'Emissions_Counterfactual': counterfactual_results['emissions'],
        'Emissions_Difference': counterfactual_results['emissions'] - baseline_results['emissions']
    }
    
    # Add all available concentration fields from both scenarios
    print("Adding all concentration fields to CSV...")
    
    # Get all species from FAIR results
    all_species = []
    for scenario_name in ['baseline_ssp245', 'counterfactual_1975']:
        if scenario_name in all_results:
            scenario_species = all_results[scenario_name]['concentration'].specie.values
            all_species.extend(scenario_species)
    
    all_species = list(set(all_species))  # Remove duplicates
    print(f"Found species: {all_species}")
    
    # Add concentration data for each species
    for species in all_species:
        try:
            # Baseline concentration
            if 'baseline_ssp245' in all_results and species in all_results['baseline_ssp245']['concentration'].specie.values:
                baseline_conc = all_results['baseline_ssp245']['concentration'].sel(specie=species).values.flatten()
                results_data[f'{species}_Concentration_Baseline'] = baseline_conc
            else:
                results_data[f'{species}_Concentration_Baseline'] = [np.nan] * len(years)
            
            # Counterfactual concentration
            if 'counterfactual_1975' in all_results and species in all_results['counterfactual_1975']['concentration'].specie.values:
                counterfactual_conc = all_results['counterfactual_1975']['concentration'].sel(specie=species).values.flatten()
                results_data[f'{species}_Concentration_Counterfactual'] = counterfactual_conc
            else:
                results_data[f'{species}_Concentration_Counterfactual'] = [np.nan] * len(years)
            
            # Calculate difference if both exist
            if (f'{species}_Concentration_Baseline' in results_data and 
                f'{species}_Concentration_Counterfactual' in results_data):
                baseline_vals = results_data[f'{species}_Concentration_Baseline']
                counterfactual_vals = results_data[f'{species}_Concentration_Counterfactual']
                if not (all(np.isnan(baseline_vals)) or all(np.isnan(counterfactual_vals))):
                    results_data[f'{species}_Concentration_Difference'] = [
                        counterfactual_vals[i] - baseline_vals[i] if not (np.isnan(baseline_vals[i]) or np.isnan(counterfactual_vals[i])) else np.nan
                        for i in range(len(years))
                    ]
                else:
                    results_data[f'{species}_Concentration_Difference'] = [np.nan] * len(years)
            
            print(f"  Added {species} concentration data")
            
        except Exception as e:
            print(f"  Warning: Could not add {species} concentration data: {e}")
            results_data[f'{species}_Concentration_Baseline'] = [np.nan] * len(years)
            results_data[f'{species}_Concentration_Counterfactual'] = [np.nan] * len(years)
            results_data[f'{species}_Concentration_Difference'] = [np.nan] * len(years)
    
    # Add emissions data for all species
    print("Adding all emissions fields to CSV...")
    for species in all_species:
        try:
            # Baseline emissions
            if 'baseline_ssp245' in all_results and species in all_results['baseline_ssp245']['emissions'].specie.values:
                baseline_emissions = all_results['baseline_ssp245']['emissions'].sel(specie=species).values.flatten()
                results_data[f'{species}_Emissions_Baseline'] = baseline_emissions
            else:
                results_data[f'{species}_Emissions_Baseline'] = [np.nan] * len(years)
            
            # Counterfactual emissions
            if 'counterfactual_1975' in all_results and species in all_results['counterfactual_1975']['emissions'].specie.values:
                counterfactual_emissions = all_results['counterfactual_1975']['emissions'].sel(specie=species).values.flatten()
                results_data[f'{species}_Emissions_Counterfactual'] = counterfactual_emissions
            else:
                results_data[f'{species}_Emissions_Counterfactual'] = [np.nan] * len(years)
            
            # Calculate difference if both exist
            if (f'{species}_Emissions_Baseline' in results_data and 
                f'{species}_Emissions_Counterfactual' in results_data):
                baseline_vals = results_data[f'{species}_Emissions_Baseline']
                counterfactual_vals = results_data[f'{species}_Emissions_Counterfactual']
                if not (all(np.isnan(baseline_vals)) or all(np.isnan(counterfactual_vals))):
                    results_data[f'{species}_Emissions_Difference'] = [
                        counterfactual_vals[i] - baseline_vals[i] if not (np.isnan(baseline_vals[i]) or np.isnan(counterfactual_vals[i])) else np.nan
                        for i in range(len(years))
                    ]
                else:
                    results_data[f'{species}_Emissions_Difference'] = [np.nan] * len(years)
            
            print(f"  Added {species} emissions data")
            
        except Exception as e:
            print(f"  Warning: Could not add {species} emissions data: {e}")
            results_data[f'{species}_Emissions_Baseline'] = [np.nan] * len(years)
            results_data[f'{species}_Emissions_Counterfactual'] = [np.nan] * len(years)
            results_data[f'{species}_Emissions_Difference'] = [np.nan] * len(years)
    
    # Create DataFrame and save to CSV
    results_df = pd.DataFrame(results_data)
    csv_filename = 'results/fair_comparison_results.csv'
    results_df.to_csv(csv_filename, index=False)
    print(f"Saved detailed results to CSV: {csv_filename}")
    
    # Print summary of what was saved
    print(f"\nCSV contains {len(results_df.columns)} columns:")
    for col in results_df.columns:
        print(f"  - {col}")
    
    print(f"\nCSV contains {len(results_df)} rows (years {results_df['Year'].min():.0f}-{results_df['Year'].max():.0f})")
    
    # Quick diagnostic for early period issues
    print(f"\n=== EARLY PERIOD DIAGNOSTIC (1750-1910) ===")
    early_data = results_df[results_df['Year'] <= 1910]
    if len(early_data) > 0:
        print(f"Early period has {len(early_data)} years")
        
        # Check for NaN values in key fields
        key_fields = ['Temperature_Baseline', 'CO2_Concentration_Baseline', 'CH4_Concentration_Baseline', 'N2O_Concentration_Baseline']
        for field in key_fields:
            if field in early_data.columns:
                nan_count = early_data[field].isna().sum()
                print(f"  {field}: {nan_count}/{len(early_data)} NaN values")
                
                if nan_count == 0:
                    # Show range of values
                    min_val = early_data[field].min()
                    max_val = early_data[field].max()
                    print(f"    Range: {min_val:.3f} to {max_val:.3f}")
                else:
                    # Show first few non-NaN values
                    non_nan_vals = early_data[field].dropna()
                    if len(non_nan_vals) > 0:
                        print(f"    First few non-NaN values: {non_nan_vals.head(5).tolist()}")
    else:
        print("No early period data found!")
    
    print("=== END EARLY PERIOD DIAGNOSTIC ===\n")
    
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
    
    # Run FAIR model for both scenarios
    print("Running FAIR model for baseline scenario...")
    baseline_results = run_fair_scenario(baseline_file, "baseline_ssp245")
    
    print("Running FAIR model for counterfactual scenario...")
    counterfactual_results = run_fair_scenario(counterfactual_file, "counterfactual_1975")
    
    # Store complete FAIR model results for CSV export
    all_results = {
        'baseline_ssp245': baseline_results['fair_model'],
        'counterfactual_1975': counterfactual_results['fair_model']
    }
    
    # Create comparison
    comparison = create_comparison(baseline_results, counterfactual_results)
    
    # Create visualizations
    create_visualizations(baseline_results, counterfactual_results, comparison, all_results)
    
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
