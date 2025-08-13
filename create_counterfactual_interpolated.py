#!/usr/bin/env python3
"""
Script to create counterfactual emissions file from interpolated emissions data.

This script:
1. Reads the interpolated emissions file (emissions_ssp245_interpolated.csv)
2. Reads the Excel file to get CO2 emissions adjustment data
3. Adjusts CO2 emissions for years 1976-2023 based on the difference between
   actual emissions and emissions without improvements in carbon intensity after 1975
4. Saves the modified emissions file
"""

import pandas as pd
import numpy as np
from pathlib import Path

def create_counterfactual_interpolated():
    """
    Create counterfactual emissions file from interpolated emissions data.
    """
    
    # Read the Excel file to get the adjustment data
    print("Reading Excel file...")
    excel_file = "combined_global_data_v2.xlsx"
    
    # Read the Excel file - we need columns Z (Year), AA (Actual CO2), AC (Counterfactual CO2)
    # Note: Excel columns Z=26, AA=27, AC=29 (0-indexed: 25, 26, 28)
    df_excel = pd.read_excel(excel_file, header=None)
    
    # Extract the relevant columns
    # Column Z (26th column, 0-indexed: 25) = Year
    # Column AA (27th column, 0-indexed: 26) = Actual CO2 emissions (GtCO2/yr)
    # Column AC (29th column, 0-indexed: 28) = Counterfactual CO2 emissions (GtCO2/yr)
    years = df_excel.iloc[:, 25]  # Column Z
    actual_co2 = df_excel.iloc[:, 26]  # Column AA
    counterfactual_co2 = df_excel.iloc[:, 28]  # Column AC
    
    # Convert to numeric values, handling any non-numeric data
    years = pd.to_numeric(years, errors='coerce')
    actual_co2 = pd.to_numeric(actual_co2, errors='coerce')
    counterfactual_co2 = pd.to_numeric(counterfactual_co2, errors='coerce')
    
    # Create a DataFrame with the adjustment data
    adjustment_data = pd.DataFrame({
        'Year': years,
        'Actual_CO2_Gt': actual_co2,
        'Counterfactual_CO2_Gt': counterfactual_co2
    })
    
    # Calculate the adjustment needed (in GtCO2/yr)
    adjustment_data['Adjustment_Gt'] = adjustment_data['Counterfactual_CO2_Gt'] - adjustment_data['Actual_CO2_Gt']
    
    # Convert to MtCO2/yr (multiply by 1000)
    adjustment_data['Adjustment_Mt'] = adjustment_data['Adjustment_Gt'] * 1000
    
    # Filter for years 1976-2023 and remove any NaN values
    adjustment_data = adjustment_data[
        (adjustment_data['Year'] >= 1976) & 
        (adjustment_data['Year'] <= 2023) &
        adjustment_data['Adjustment_Mt'].notna()
    ].copy()
    
    print(f"Found adjustment data for {len(adjustment_data)} years (1976-2023)")
    
    # Read the interpolated emissions file
    print("Reading interpolated emissions file...")
    interpolated_file = "inputs/emissions_ssp245_interpolated.csv"
    df_interpolated = pd.read_csv(interpolated_file)
    
    # Find the CO2 emissions row (should be "Emissions|CO2")
    co2_row = df_interpolated[df_interpolated['Variable'] == 'Emissions|CO2'].copy()
    
    if len(co2_row) == 0:
        raise ValueError("Could not find 'Emissions|CO2' in the interpolated emissions file")
    
    print("Found CO2 emissions data in interpolated file")
    
    # Create a copy of the interpolated file for modification
    df_counterfactual = df_interpolated.copy()
    
    # Apply adjustments to CO2 emissions for years 1976-2023
    print("Applying CO2 emissions adjustments...")
    for _, row in adjustment_data.iterrows():
        year = int(row['Year'])
        adjustment = row['Adjustment_Mt']
        
        # Find the CO2 row and apply the adjustment
        mask = df_counterfactual['Variable'] == 'Emissions|CO2'
        if str(year) in df_counterfactual.columns:
            df_counterfactual.loc[mask, str(year)] += adjustment
            print(f"  Year {year}: Added {adjustment:.1f} MtCO2/yr")
        else:
            print(f"  Warning: Year {year} not found in interpolated emissions file")
    
    # Save the modified emissions file
    output_file = "inputs/emissions_ssp245_interpolated_counterfactual_1975.csv"
    df_counterfactual.to_csv(output_file, index=False)
    print(f"\nSaved counterfactual interpolated emissions file: {output_file}")
    
    # Print summary statistics
    print("\nSummary of adjustments:")
    print(f"Total years adjusted: {len(adjustment_data)}")
    print(f"Average annual adjustment: {adjustment_data['Adjustment_Mt'].mean():.1f} MtCO2/yr")
    print(f"Total cumulative adjustment: {adjustment_data['Adjustment_Mt'].sum():.1f} MtCO2")
    
    return output_file

if __name__ == "__main__":
    create_counterfactual_interpolated()
