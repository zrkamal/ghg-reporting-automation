import pandas as pd
import numpy as np
from datetime import datetime
import os

# STEP 1: LOAD THE MESSY DATA
def load_raw_data(filepath):
    """Load messy activity data from CSV"""
    # Use error_bad_lines=False to skip problematic rows (or on_bad_lines='skip' in newer pandas)
    try:
        df = pd.read_csv(filepath)
    except pd.errors.ParserError:
        # If parsing fails, try with more lenient settings
        df = pd.read_csv(filepath, on_bad_lines='skip', engine='python')
        print("  Warning: Some rows were skipped due to formatting issues")
    
    print(f"X Loaded {len(df)} records")
    return df

# STEP 2: CLEAN & STANDARDIZE
def clean_data(df):
    """Automated data cleaning and standardization"""
    df_clean = df.copy()

    # Standardize dates to YYYY-MM-DD
    df_clean['Date'] = pd.to_datetime(df_clean['Date'], errors='coerce')

    # Standardize source names (title case, remove extra spaces)
    df_clean['Source'] = df_clean['Source'].str.strip().str.title()

    # Remove commas from amounts and convert to numeric
    df_clean['Amount'] = df_clean['Amount'].astype(str).str.replace(',','')
    df_clean['Amount'] = pd.to_numeric(df_clean['Amount'], errors='coerce')

    # Standardize units (lowercase for matching)
    df_clean['Unit'] = df_clean['Unit'].str.lower().str.strip()

    # Flag missing values
    df_clean['Has_Missing'] = df_clean.isnull().any(axis=1)

    print(f"X Cleaned {len(df_clean)} records")
    print(f" - {df_clean['Has_Missing'].sum()} records flagged with missing data")

    return df_clean

# STEP 3: UNIT CONVERSION
def convert_units(df):
    """Convert all units to standard SI units"""
    df_converted = df.copy()
    
    # Convert km to miles (for travel)
    mask = (df_converted['Unit'] == 'km')
    df_converted.loc[mask, 'Amount'] = df_converted.loc[mask, 'Amount'] * 0.621371
    df_converted.loc[mask, 'Unit'] = 'miles'

    # Convert kg to tons (for waste)
    mask = (df_converted['Unit'] == 'kg') & (df_converted['Source'].str.contains('Waste', na=False))
    df_converted.loc[mask, 'Amount'] = df_converted.loc[mask, 'Amount'] / 1000
    df_converted.loc[mask, 'Unit'] = 'tons'

    # Convert liter to gallons (for fuel)
    mask = (df_converted['Unit'] == 'liters')
    df_converted.loc[mask, 'Amount'] = df_converted.loc[mask, 'Amount'] * 0.264172
    df_converted.loc[mask, 'Unit'] = 'gallons'

    # Standardize currency
    df_converted['Unit'] = df_converted['Unit'].replace({'$': 'usd'})

    print("X Units standardized")
    return df_converted



# ============================================================
# DEBUG: Test individual steps
# ============================================================
if __name__ == "__main__":
    import os
    
    # Define file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    input_file = os.path.join(project_root, "data", "raw", "messy_ghg_activity_data_Q1_2024.csv")
    
    print("="*60)
    print("DEBUG MODE: Testing Steps 1, 2, and 3")
    print("="*60)
    
    # STEP 1: Load data
    print("\n--- STEP 1: Loading Data ---")
    df_raw = load_raw_data(input_file)
    print("\nFirst 5 rows of RAW data:")
    print(df_raw.head())
    
    # STEP 2: Clean data
    print("\n--- STEP 2: Cleaning Data ---")
    df_clean = clean_data(df_raw)
    print("\nFirst 5 rows of CLEANED data:")
    print(df_clean[['Source', 'Amount', 'Unit']].head())
    
    # STEP 3: Convert units
    print("\n--- STEP 3: Converting Units ---")
    df_converted = convert_units(df_clean)
    print("\nFirst 10 rows showing unit conversions:")
    print(df_converted[['Source', 'Amount', 'Unit']].head(10))
    
    # Detailed comparison of before/after conversions
    print("\n--- UNIT CONVERSION COMPARISON ---")
    
    # Show km to miles conversion
    print("\n1. Kilometers to Miles (Air Travel):")
    km_rows = df_clean[df_clean['Unit'] == 'km']
    if len(km_rows) > 0:
        print("BEFORE conversion:")
        print(km_rows[['Source', 'Amount', 'Unit']])
        km_indices = km_rows.index
        print("\nAFTER conversion:")
        print(df_converted.loc[km_indices, ['Source', 'Amount', 'Unit']])
    
    # Show kg to tons conversion
    print("\n2. Kilograms to Tons (Waste):")
    kg_rows = df_clean[(df_clean['Unit'] == 'kg') & (df_clean['Source'].str.contains('Waste', na=False))]
    if len(kg_rows) > 0:
        print("BEFORE conversion:")
        print(kg_rows[['Source', 'Amount', 'Unit']])
        kg_indices = kg_rows.index
        print("\nAFTER conversion:")
        print(df_converted.loc[kg_indices, ['Source', 'Amount', 'Unit']])
    
    # Show liters to gallons conversion
    print("\n3. Liters to Gallons (Fuel):")
    liter_rows = df_clean[df_clean['Unit'] == 'liters']
    if len(liter_rows) > 0:
        print("BEFORE conversion:")
        print(liter_rows[['Source', 'Amount', 'Unit']])
        liter_indices = liter_rows.index
        print("\nAFTER conversion:")
        print(df_converted.loc[liter_indices, ['Source', 'Amount', 'Unit']])
    
    # Show currency standardization
    print("\n4. Currency Standardization:")
    dollar_rows = df_clean[df_clean['Unit'] == '$']
    if len(dollar_rows) > 0:
        print("BEFORE standardization:")
        print(dollar_rows[['Source', 'Amount', 'Unit']])
        dollar_indices = dollar_rows.index
        print("\nAFTER standardization:")
        print(df_converted.loc[dollar_indices, ['Source', 'Amount', 'Unit']])
    
    # Summary of all unique units
    print("\n--- UNIT SUMMARY ---")
    print("\nUnique units BEFORE conversion:")
    print(df_clean['Unit'].value_counts())
    print("\nUnique units AFTER conversion:")
    print(df_converted['Unit'].value_counts())
    
    print("\n✓ Steps 1-3 completed successfully!")