# Project Continuation Guide

This document is intended for LLMs and collaborators to understand the project's current state and the preferred working approach.

## Project Status

**Current Phase**: FAIR model analysis and scenario comparison (facing log warnings)
**Last Updated**: 2025-01-13

### Current Challenge
The project is currently blocked by "invalid value encountered in log" warnings from FAIR's CH4 lifetime calculation. The warnings occur in `/home/kcaldeira/github/fair/.venv/lib/python3.12/site-packages/fair/gas_cycle/ch4_lifetime.py:73` during the model run.

**Root Cause**: Temperature values passed to the CH4 lifetime function contain invalid values that cause problems in the logarithm calculation: `np.log(1 + temperature * ch4_lifetime_temperature_sensitivity)`

**Additional Issue**: Time slice mismatch - we should have 274 time slices but some variables only have 273, which could be causing initialization problems.

## Progress Made

- ✅ **MAJOR SUCCESS**: FAIR model comparison completed successfully!
- ✅ **Unit Conversion Fixed**: Correctly implemented MtCO2/yr to GtCO2/yr conversion (divide by 1000)
- ✅ **Temperature Initialization Fixed**: Properly initialized temperature arrays to zero, eliminating NaN values
- ✅ **Concentration Initialization Fixed**: Added proper baseline concentration initialization for all species
- ✅ **Species Mapping Fixed**: Corrected CSV variable names to FAIR species mapping
- ✅ **Scenario Name Handling**: Fixed scenario name changes in all FAIR arrays
- ✅ **Shape Mismatch Debugging**: Added comprehensive shape debugging and reshaping logic
- 🔄 **CURRENT ISSUE**: Array shape compatibility still causing broadcast errors despite reshaping attempts
- 💡 **REALIZATION**: This approach is becoming unnecessarily complex for a simple task

## Current Challenges

### Primary Issue: Over-Engineering
- **Goal**: Run SSP245 scenario with modified CO2 emissions for some years
- **Current Approach**: Complex custom initialization, species mapping, shape fixing
- **Problem**: Making a simple task unnecessarily difficult
- **Solution Needed**: Return to vanilla SSP245 approach and make minimal changes

### Technical Issues (if continuing current approach)
- Array shape compatibility between our data and FAIR's expected format
- Need to ensure all species (BC, CH4, CO2, N2O, Sulfur, OC) load correctly
- Comprehensive CSV export for early period diagnostic (1750-1910)

## Recommended Next Steps

### Option 1: Simplify Approach (RECOMMENDED)
1. **Start with vanilla SSP245**: Use `fair_ssp.py` as base
2. **Minimal modifications**: Only change CO2 emissions for specific years
3. **Keep everything else identical**: Use FAIR's default initialization
4. **Avoid custom complexity**: Let FAIR handle species, shapes, etc.

**Specific Implementation Plan:**
- **Base file**: `fair_ssp.py` (already works with SSP245)
- **Modification**: Create a new script that copies `fair_ssp.py` and only changes CO2 emissions
- **Approach**: 
  - Load the working SSP245 scenario
  - Modify only the CO2 emissions array for specific years
  - Keep all other species, initialization, and processing identical
  - Run both baseline (original SSP245) and modified scenarios
  - Compare results
- **Benefits**: 
  - Leverages proven working code
  - Minimal changes = fewer bugs
  - FAIR handles all complexity (species, shapes, initialization)
  - Much more likely to work correctly

### Option 2: Continue Current Approach
1. Fix remaining shape compatibility issues
2. Complete comprehensive CSV export
3. Diagnose early period problems (1750-1910)
4. Address CH4/N2O concentration issues

## Key Insight
The user's observation is correct: "This should not be so difficult. All I am trying to do is run something identical to the SSP245 case except change the CO2 emissions for some of the years."

**Recommendation**: Go back to the vanilla SSP245 approach and make only the minimal changes needed for the CO2 emissions modification.

## Environment Setup

**IMPORTANT**: Before working on this project, always activate the virtual environment:
```bash
source .venv/bin/activate
```

The virtual environment contains all required dependencies including FAIR v2.2.2.

## Working Style Preferences

- **Root Cause Analysis**: Focus on identifying and fixing underlying causes rather than applying band-aid solutions
- **Systematic Problem-Solving**: When encountering an issue with one variable or component, check if the same problem exists for other similar variables/components
- **Comprehensive Fixes**: Address all instances of a problem pattern, not just the first occurrence
- **Three-Solution Approach**: For any problem, develop at least three possible solutions, recommend one, and ask for approval before implementing
- **Debugging Permission**: Assistant can add debugging code (print statements, logging) without permission
- **Functional Changes**: Require explicit approval before adding or modifying code that changes processing or functionality
- **Clean Code**: Avoid band-aid fixes; produce clean final code with imports at the top of files

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
