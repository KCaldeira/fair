# Project Continuation Guide

This document is intended for LLMs and collaborators to understand the project's current state and the preferred working approach.

## Project Status

**Current Phase**: FAIR model setup and data preparation
**Last Updated**: 2025-01-13

### Current Implementation
- **FAIR Model Setup**: Basic FAIR model configuration with SSP245 scenario
- **Data Sources**: RCMIP (Representative Concentration Model Intercomparison Project) emissions data
- **Data Processing**: Scripts to download and process RCMIP data to CSV format
- **Available Scripts**:
  - `fair_ssp.py`: Demonstrates FAIR model setup and RCMIP data integration
  - `fair_ssp_csv.py`: Downloads and processes RCMIP emissions data

## Environment Setup

**IMPORTANT**: Before working on this project, always activate the virtual environment:
```bash
source .venv/bin/activate
```

The virtual environment contains all required dependencies including FAIR v2.2.2.

## Working Style Preferences

### 1. Problem-Solving Approach
- **Root Cause Analysis**: Always investigate underlying causes rather than applying band-aid fixes
- **Multiple Solutions**: Present at least 3 possible approaches to any problem
- **Approval Process**: Get explicit approval before implementing code changes that affect functionality

### 2. Code Quality Standards
- **Heavy Commenting**: All code should be extensively commented with explanations for:
  - Why specific approaches were chosen
  - What each function/block does
  - Assumptions and limitations
  - Mathematical formulations (for climate modeling)
- **Clean Code**: Avoid temporary fixes; aim for clean, maintainable final code
- **Import Organization**: Keep imports at the top of files unless absolutely necessary

### 3. Development Workflow
- **Debugging**: Adding debugging code (print statements, logging) is allowed without permission
- **Functional Changes**: Require explicit approval before modifying processing or functionality
- **Documentation**: Update this file as the project evolves

## Technical Preferences

### Climate Modeling Specific
- **FAIR Model**: Finite Amplitude Impulse Response model for climate calculations
- **Data Sources**: Historical GDP, emissions, and carbon intensity data
- **Validation**: Compare results with known climate science benchmarks
- **Reproducibility**: Ensure all calculations are reproducible and well-documented

### Code Structure
- **Modular Design**: Separate data processing, model calculations, and visualization
- **Configuration**: Use configuration files for model parameters
- **Testing**: Include validation tests for climate model outputs

## Current Project Goals

1. ✅ **FAIR Model Setup**: Basic FAIR model implementation with SSP245 scenario
2. ✅ **Data Sources**: RCMIP emissions data integration
3. 🔄 **Data Collection**: Process historical GDP and carbon intensity data from Excel file
4. 🔄 **Scenario Generation**: Create baseline and 1975 carbon intensity counterfactual scenarios
5. ⏳ **Analysis**: Compare climate outcomes between scenarios
6. ⏳ **Visualization**: Create clear visualizations of results

## Next Steps

1. **Examine Excel Data**: Analyze `combined_global_data_v2.xlsx` to understand available GDP and emissions data
2. **Create Custom Scenarios**: Develop scenarios for 1975 carbon intensity counterfactual analysis
3. **Integrate Historical Data**: Combine RCMIP data with historical GDP/carbon intensity data
4. **Run Comparative Analysis**: Execute FAIR model runs for baseline vs. counterfactual scenarios

## Important Notes

- This is a research project focused on understanding climate impacts
- All assumptions and methodologies should be clearly documented
- Results should be validated against established climate science
- Code should be educational and well-explained for future researchers

## Contact

For questions about this project or development approach, refer to the project owner's preferences documented above.
