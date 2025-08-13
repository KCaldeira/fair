# FAIR Climate Model Analysis: Historical Carbon Intensity Scenario

## Project Overview

This project uses the FAIR (Finite Amplitude Impulse Response) climate model to analyze the potential climate effects of a counterfactual scenario where carbon intensity of GDP remained at 1975 levels while maintaining historical GDP growth rates.

## Research Question

What would be the climate impact if global carbon intensity of GDP had not improved since 1975, but GDP growth had continued at historical rates?

## Methodology

- **Model**: FAIR (Finite Amplitude Impulse Response) climate model
- **Baseline**: Historical carbon intensity improvements since 1975
- **Scenario**: Carbon intensity frozen at 1975 levels with historical GDP growth
- **Analysis**: Comparison of temperature and climate outcomes between baseline and scenario

## Key Components

- **FAIR Model Implementation**: Climate model setup and configuration using MAGICC-derived parameters
- **Data Processing Pipeline**: RCMIP data download, interpolation, and counterfactual scenario generation
- **Carbon Intensity Analysis**: Historical GDP and emissions data integration
- **Scenario Comparison**: Baseline SSP245 vs. 1975 carbon intensity counterfactual
- **Visualization Tools**: Temperature and CO2 concentration comparison plots
- **Results Analysis**: Quantitative comparison of climate impacts

## Climate Model Parameters

The FAIR model uses climate parameters derived from the MAGICC model, which has been extensively used in IPCC assessments:

- **Ocean Heat Capacity**: [2.92, 11.28, 73.25] W/m²/K for three-layer ocean model
- **Ocean Heat Transfer**: [0.73, 0.70, 0.70] W/m²/K for three-layer ocean model
- **Deep Ocean Efficacy**: [1.28, 1.28, 1.28] dimensionless parameter
- **Radiative Forcing 4xCO2**: 7.32 W/m² (standard climate sensitivity parameter)

*Source: Meinshausen et al. (2011) "The RCP greenhouse gas concentrations and their extensions from 1765 to 2300"*

## Getting Started

### Prerequisites
- Python 3.x
- Virtual environment (`.venv/` directory)

### Setup
1. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Data Processing Workflow

1. **Download RCMIP Data**: Run `python fair_ssp_csv.py` to download and process RCMIP emissions data
2. **Interpolate Emissions**: Run `python interpolate_emissions.py` to create interpolated emissions for all years (1750-2023)
3. **Create Counterfactual**: Run `python create_counterfactual_interpolated.py` to create the 1975 carbon intensity scenario
4. **Run FAIR Comparison**: Run `python run_fair_comparison.py` to compare baseline vs. counterfactual scenarios

### Running FAIR Model Examples

The project includes several scripts for data processing and analysis:

- **`fair_ssp.py`**: Basic FAIR model setup using SSP245 scenario with RCMIP data
- **`fair_ssp_csv.py`**: Downloads and processes RCMIP emissions data to CSV format
- **`interpolate_emissions.py`**: Interpolates emissions data to fill all years from 1750-2023
- **`create_counterfactual_emissions.py`**: Creates counterfactual emissions based on 1975 carbon intensity scenario
- **`create_counterfactual_interpolated.py`**: Creates counterfactual emissions from interpolated data
- **`run_fair_comparison.py`**: Runs FAIR model comparison between baseline and counterfactual scenarios

## Current Status

The project is currently in development with the following components implemented:

- ✅ Data processing pipeline for emissions data
- ✅ FAIR model integration and initialization
- 🔄 Counterfactual scenario analysis (in progress - facing log warnings)
- ⏳ Visualization and results analysis (pending)

### Current Issues

The main remaining challenge is resolving the "invalid value encountered in log" warnings from FAIR's CH4 lifetime calculation. These warnings indicate that the temperature values being passed to the CH4 lifetime function contain invalid values (likely NaN or negative values that cause problems in the logarithm calculation).

**Root Cause Analysis:**
The warnings are coming from `/home/kcaldeira/github/fair/.venv/lib/python3.12/site-packages/fair/gas_cycle/ch4_lifetime.py:73` where the code calculates:
```python
+ np.log(1 + temperature * ch4_lifetime_temperature_sensitivity)
```

This suggests that either:
1. The temperature values contain NaN values
2. The temperature values are negative enough to make `(1 + temperature * ch4_lifetime_temperature_sensitivity)` negative or zero
3. The initialization of temperature arrays is not properly handling all timepoints

**Next Steps:**
1. Investigate the temperature initialization in FAIR
2. Ensure all temperature values are properly initialized before the model run
3. Check if the issue is related to the manual species definition vs. using FAIR's built-in species
4. Consider using FAIR's `fill_from_rcmip()` method for proper data loading

## Dependencies

Key dependencies include:
- `fair==2.2.2`: FAIR climate model
- `pandas`: Data manipulation
- `xarray`: Multi-dimensional arrays
- `requests`: HTTP requests for data download
- `openpyxl`: Excel file reading
- `matplotlib`: Data visualization
- `numpy`: Numerical computations

## License

[To be specified]

## Contributing

This is a research project. Please refer to CONTINUATION.md for development guidelines and workflow preferences.
