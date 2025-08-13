# env: python -m venv .venv && source .venv/bin/activate
# pip install pandas requests fair

import io, requests, pandas as pd
from pathlib import Path

# 1) Download RCMIP emissions (v5.1.0)
url = "https://rcmip-protocols-au.s3-ap-southeast-2.amazonaws.com/v5.1.0/rcmip-emissions-annual-means-v5-1-0.csv"
csv = requests.get(url, timeout=60).text
df = pd.read_csv(io.StringIO(csv))

# 2) Keep World totals, species-level aggregates, and the bits we need
keep_vars = [
    # Add/trim as desired; these are common drivers
    "Emissions|CO2", "Emissions|CH4", "Emissions|N2O",
    "Emissions|Sulfur", "Emissions|BC", "Emissions|OC",
    # many more exist in RCMIP; you can extend this list
]

df = df[
    (df["Region"] == "World") &
    (df["Variable"].isin(keep_vars)) &
    (df["Scenario"].isin(["historical", "ssp245"]))
].copy()

# 3) Melt to long, split historical vs SSP years, then combine
value_year_cols = [c for c in df.columns if c.isdigit()]  # "1750"..."2100"
long = df.melt(id_vars=["Scenario", "Variable", "Unit"], value_vars=value_year_cols,
               var_name="Year", value_name="Value").dropna()

# RCMIP uses 'historical' through 2014 (some species to 2015); keep <=2014 from historical, >=2015 from ssp245
long["Year"] = long["Year"].astype(int)
hist = long[(long["Scenario"] == "historical") & (long["Year"] <= 2014)]
ssp  = long[(long["Scenario"] == "ssp245")     & (long["Year"] >= 2015)]

combo = pd.concat([hist, ssp], ignore_index=True)
combo["Scenario"] = "ssp245"  # one stitched scenario name

# 4) Pivot back to FAIR's required wide format: Scenario, Variable, Unit, 1750, …, 2100
wide = combo.pivot_table(index=["Scenario","Variable","Unit"],
                         columns="Year", values="Value").reset_index()

# Fix: Sort columns properly by separating year columns from metadata columns
# Get metadata columns (non-year columns)
metadata_cols = ["Scenario", "Variable", "Unit"]
# Get year columns and sort them numerically
year_cols = [col for col in wide.columns if col not in metadata_cols]
year_cols_sorted = sorted(year_cols, key=int)
# Reorder columns: metadata first, then sorted years
wide = wide[metadata_cols + year_cols_sorted]

# 5) Save it
out = Path("inputs"); out.mkdir(exist_ok=True, parents=True)
out_csv = out / "emissions_ssp245.csv"
wide.to_csv(out_csv, index=False)
print("Wrote", out_csv)
