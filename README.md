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

- FAIR model implementation
- Historical data processing (GDP, emissions, carbon intensity)
- Scenario generation and comparison
- Visualization and analysis tools

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

### Running FAIR Model Examples

The project includes two example scripts:

- **`fair_ssp.py`**: Basic FAIR model setup using SSP245 scenario with RCMIP data
- **`fair_ssp_csv.py`**: Downloads and processes RCMIP emissions data to CSV format

## Dependencies

Key dependencies include:
- `fair==2.2.2`: FAIR climate model
- `pandas`: Data manipulation
- `xarray`: Multi-dimensional arrays
- `requests`: HTTP requests for data download

## License

[To be specified]

## Contributing

This is a research project. Please refer to CONTINUATION.md for development guidelines and workflow preferences.
