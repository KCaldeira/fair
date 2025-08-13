# Project Continuation Guide

This document is intended for LLMs and collaborators to understand the project's current state and the preferred working approach.

## Project Status

**Current Phase**: FAIR model analysis and scenario comparison (facing log warnings)
**Last Updated**: 2025-01-13

### Current Challenge
The project is currently blocked by "invalid value encountered in log" warnings from FAIR's CH4 lifetime calculation. The warnings occur in `/home/kcaldeira/github/fair/.venv/lib/python3.12/site-packages/fair/gas_cycle/ch4_lifetime.py:73` during the model run.

**Root Cause**: Temperature values passed to the CH4 lifetime function contain invalid values that cause problems in the logarithm calculation: `np.log(1 + temperature * ch4_lifetime_temperature_sensitivity)`

**Investigation Needed**: 
- Check temperature initialization in FAIR
- Verify all temperature arrays are properly initialized
- Consider if manual species definition vs. FAIR's built-in species is causing the issue
- Explore using FAIR's `fill_from_rcmip()` method for proper data loading

### Current Implementation
- **FAIR Model Setup**: Complete FAIR model configuration with SSP245 scenario
- **Data Sources**: RCMIP (Representative Concentration Model Intercomparison Project) emissions data + Excel GDP/carbon intensity data
- **Data Processing Pipeline**: Complete workflow from RCMIP download to counterfactual scenario generation
- **Available Scripts**:
  - `fair_ssp.py`: Demonstrates FAIR model setup and RCMIP data integration
  - `fair_ssp_csv.py`: Downloads and processes RCMIP emissions data
  - `interpolate_emissions.py`: Interpolates emissions data to fill all years (1750-2023)
  - `create_counterfactual_emissions.py`: Creates counterfactual emissions from original data
  - `create_counterfactual_interpolated.py`: Creates counterfactual emissions from interpolated data
  - `run_fair_comparison.py`: Runs FAIR model comparison between baseline and counterfactual scenarios

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

1. ✅ **FAIR Model Setup**: Complete FAIR model implementation with SSP245 scenario
2. ✅ **Data Sources**: RCMIP emissions data integration
3. ✅ **Data Collection**: Processed historical GDP and carbon intensity data from Excel file
4. ✅ **Scenario Generation**: Created baseline and 1975 carbon intensity counterfactual scenarios
5. ✅ **Data Processing Pipeline**: Complete workflow from RCMIP download to counterfactual generation
6. 🔄 **Analysis**: FAIR model comparison script created but facing log warnings
7. ⏳ **Visualization**: Visualization tools implemented but not yet executed due to warnings

## Next Steps

### Immediate Priority: Fix Log Warnings
1. **Investigate Temperature Initialization**: Check how FAIR initializes temperature arrays and ensure proper initialization
2. **Debug Temperature Values**: Add debugging to identify which temperature values are causing the log warnings
3. **Compare with Working Example**: Test the `fair_ssp.py` example to see if it has the same warnings
4. **Consider Alternative Approaches**: 
   - Use FAIR's built-in species instead of manual definition
   - Use `fill_from_rcmip()` method for data loading
   - Check if the issue is related to the custom emissions data format

### After Fixing Warnings
1. **Execute FAIR Comparison**: Run `run_fair_comparison_proper.py` to compare baseline vs. counterfactual scenarios
2. **Analyze Results**: Review temperature and CO2 concentration differences
3. **Validate Findings**: Compare results with climate science expectations
4. **Document Insights**: Update documentation with key findings and implications

## Important Notes

- This is a research project focused on understanding climate impacts
- All assumptions and methodologies should be clearly documented
- Results should be validated against established climate science
- Code should be educational and well-explained for future researchers
- **Documentation Maintenance**: The user prefers to keep README.md and CONTINUATION.md files updated as the project progresses

## Contact

For questions about this project or development approach, refer to the project owner's preferences documented above.
