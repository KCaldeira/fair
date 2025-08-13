#!/usr/bin/env python3
"""
Script to interpolate emissions data to fill in all years from 1750-2023.

This script:
1. Reads the baseline emissions_ssp245.csv file
2. Linearly interpolates between available years to fill in missing years
3. Saves the interpolated emissions file
"""

import pandas as pd
import numpy as np
from pathlib import Path

def interpolate_emissions():
    """
    Interpolate emissions data to fill in all years from 1750-2023.
    """
    
    print("Reading baseline emissions file...")
    baseline_file = "inputs/emissions_ssp245.csv"
    df_baseline = pd.read_csv(baseline_file)
    
    print(f"Original file has {len(df_baseline)} rows")
    
    # Get the metadata columns (Scenario, Variable, Unit)
    metadata_cols = ['Scenario', 'Variable', 'Unit']
    
    # Get the year columns (all columns that are numeric)
    year_cols = [col for col in df_baseline.columns if col not in metadata_cols]
    year_cols = sorted([int(col) for col in year_cols if col.isdigit()])
    
    print(f"Available years: {min(year_cols)} to {max(year_cols)}")
    print(f"Number of available years: {len(year_cols)}")
    
    # Create the full range of years we want (1750-2023)
    full_year_range = list(range(1750, 2024))  # 2024 to include 2023
    print(f"Target years: {min(full_year_range)} to {max(full_year_range)}")
    print(f"Number of target years: {len(full_year_range)}")
    
    # Create a more efficient approach to avoid DataFrame fragmentation
    print("Interpolating emissions data...")
    
    # Pre-allocate the interpolated data as a list of dictionaries
    interpolated_data = []
    
    for idx, row in df_baseline.iterrows():
        # Get the available values for this emission type
        available_values = []
        available_years = []
        
        for year in year_cols:
            value = row[str(year)]
            if pd.notna(value):  # Only include non-NaN values
                available_values.append(value)
                available_years.append(year)
        
        # Create the row data dictionary
        row_data = {
            'Scenario': row['Scenario'],
            'Variable': row['Variable'],
            'Unit': row['Unit']
        }
        
        if len(available_values) < 2:
            print(f"Warning: Row {idx} ({row['Variable']}) has insufficient data for interpolation")
            # Fill with zeros or the single available value
            default_value = available_values[0] if available_values else 0
            for year in full_year_range:
                row_data[str(year)] = default_value
        else:
            # Perform linear interpolation
            interpolated_values = np.interp(full_year_range, available_years, available_values)
            for year, value in zip(full_year_range, interpolated_values):
                row_data[str(year)] = value
        
        interpolated_data.append(row_data)
    
    # Create the DataFrame from the list of dictionaries (much more efficient)
    df_interpolated = pd.DataFrame(interpolated_data)
    
    # Save the interpolated emissions file
    output_file = "inputs/emissions_ssp245_interpolated.csv"
    df_interpolated.to_csv(output_file, index=False)
    print(f"\nSaved interpolated emissions file: {output_file}")
    
    # Print some statistics
    print(f"\nInterpolation summary:")
    print(f"Original years: {len(year_cols)}")
    print(f"Interpolated years: {len(full_year_range)}")
    print(f"Added {len(full_year_range) - len(year_cols)} years through interpolation")
    
    return output_file

if __name__ == "__main__":
    interpolate_emissions()
