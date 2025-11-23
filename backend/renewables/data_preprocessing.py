"""
Data preprocessing module for cleaning, merging datasets, and adding NUTS codes.
This module processes raw datasets and creates cleaned, merged datasets at server startup.
"""
from pathlib import Path
from typing import Dict, Optional
import pandas as pd

from config import get_config
from .data_processing import add_nuts_codes, get_data_quality_report, clean_and_normalize_timeseries

cfg = get_config()


def clean_nrg_ind_ren() -> pd.DataFrame:
    """
    Clean nrg_ind_ren (share of renewable energy) dataset.
    Steps:
      - Step 1: Load raw data and generate quality report
      - keep relevant columns
      - convert TIME_PERIOD and OBS_VALUE to numeric
      - drop rows with missing TIME_PERIOD or OBS_VALUE
    
    Returns:
        Cleaned DataFrame
    """
    raw_file = cfg.DATA_RAW_DIR / "nrg_ind_ren.csv"
    
    if not raw_file.exists():
        raise FileNotFoundError(f"Raw dataset not found: {raw_file}")
    
    # Step 1: Load raw data and check quality
    df_raw = pd.read_csv(raw_file)
    
    # Generate quality report for raw data (stored in stats, not printed)
    quality_report = get_data_quality_report(df_raw)

    # Keep only useful columns
    df = df_raw[["freq", "nrg_bal", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "LAST UPDATE"]].copy()

    # Normalize geo column (strip whitespace)
    df["geo"] = df["geo"].astype(str).str.strip()
    
    # Convert to numeric types
    df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce")
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")

    # Drop rows without TIME_PERIOD or OBS_VALUE
    df = df.dropna(subset=["TIME_PERIOD", "OBS_VALUE"])

    # Filter out aggregated regions (EU, Euro area, etc.) - only keep individual countries
    rows_before_agg_filter = len(df)
    exclude_patterns = ['union', 'european', 'countries', 'euro area', 'eurozone']
    # Get list of regions that will be removed
    mask = df["geo"].astype(str).str.lower().str.contains('|'.join(exclude_patterns), na=False)
    removed_regions = sorted(df[mask]["geo"].unique().tolist())
    df = df[~mask]
    rows_removed_aggregated = rows_before_agg_filter - len(df)

    # Remove duplicate rows (same geo, TIME_PERIOD, and other key columns)
    # Keep first occurrence
    dedup_cols = ["geo", "TIME_PERIOD", "nrg_bal", "unit"]
    available_dedup_cols = [col for col in dedup_cols if col in df.columns]
    if len(available_dedup_cols) >= 2:  # Need at least geo and TIME_PERIOD
        df = df.drop_duplicates(subset=available_dedup_cols, keep='first')

    # Store metadata about removed aggregated regions
    df.attrs['rows_removed_aggregated'] = rows_removed_aggregated
    df.attrs['removed_aggregated_regions'] = removed_regions
    return df


def clean_energy_balance() -> pd.DataFrame:
    """
    Clean nrg_bal (energy balance) dataset.
    Steps:
      - Step 1: Load raw data and generate quality report
      - keep relevant columns
      - convert TIME_PERIOD and OBS_VALUE to numeric
      - drop rows with missing TIME_PERIOD or OBS_VALUE
    
    Returns:
        Cleaned DataFrame
    """
    raw_file = cfg.DATA_RAW_DIR / "nrg_bal.csv"
    
    if not raw_file.exists():
        raise FileNotFoundError(f"Raw dataset not found: {raw_file}")
    
    # Step 1: Load raw data and check quality
    df_raw = pd.read_csv(raw_file)
    
    # Generate quality report for raw data (stored in stats, not printed)
    quality_report = get_data_quality_report(df_raw)

    df = df_raw[["freq", "nrg_bal", "siec", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "LAST UPDATE"]].copy()

    # Normalize geo column (strip whitespace)
    df["geo"] = df["geo"].astype(str).str.strip()
    
    # Convert to numeric types
    df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce")
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")

    # Drop rows without TIME_PERIOD or OBS_VALUE
    df = df.dropna(subset=["TIME_PERIOD", "OBS_VALUE"])

    # Filter out aggregated regions (EU, Euro area, etc.) - only keep individual countries
    rows_before_agg_filter = len(df)
    exclude_patterns = ['union', 'european', 'countries', 'euro area', 'eurozone']
    # Get list of regions that will be removed
    mask = df["geo"].astype(str).str.lower().str.contains('|'.join(exclude_patterns), na=False)
    removed_regions = sorted(df[mask]["geo"].unique().tolist())
    df = df[~mask]
    rows_removed_aggregated = rows_before_agg_filter - len(df)

    # Remove duplicate rows (same geo, TIME_PERIOD, siec, unit)
    # Keep first occurrence
    dedup_cols = ["geo", "TIME_PERIOD", "nrg_bal", "siec", "unit"]
    available_dedup_cols = [col for col in dedup_cols if col in df.columns]
    if len(available_dedup_cols) >= 2:  # Need at least geo and TIME_PERIOD
        df = df.drop_duplicates(subset=available_dedup_cols, keep='first')

    # Store metadata about removed aggregated regions
    df.attrs['rows_removed_aggregated'] = rows_removed_aggregated
    df.attrs['removed_aggregated_regions'] = removed_regions
    return df


def clean_gdp_dataset() -> pd.DataFrame:
    """
    Clean nama_10_gdp (GDP) dataset used for correlation analysis.
    Keeps relevant columns and converts values to numeric types.
    """
    raw_file = cfg.DATA_RAW_DIR / "nama_10_gdp.csv"
    if not raw_file.exists():
        raise FileNotFoundError(f"Raw GDP dataset not found: {raw_file}")

    df_raw = pd.read_csv(raw_file)

    # Keep relevant columns (if present)
    keep_columns = ["geo", "TIME_PERIOD", "OBS_VALUE", "LAST UPDATE", "unit"]
    available_columns = [col for col in keep_columns if col in df_raw.columns]
    if len(available_columns) < 3:  # Need at least geo, TIME_PERIOD, OBS_VALUE
        raise ValueError(f"GDP dataset missing required columns. Expected subset of {keep_columns}")

    df = df_raw[available_columns].copy()

    if "TIME_PERIOD" in df.columns:
        df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce")
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    df["geo"] = df["geo"].astype(str).str.strip()

    df = df.dropna(subset=["geo", "TIME_PERIOD", "OBS_VALUE"])

    # Filter out aggregated regions (EU, Euro area, etc.) - only keep individual countries
    rows_before_agg_filter = len(df)
    exclude_patterns = ['union', 'european', 'countries', 'euro area', 'eurozone']
    # Get list of regions that will be removed
    mask = df["geo"].astype(str).str.lower().str.contains('|'.join(exclude_patterns), na=False)
    removed_regions = sorted(df[mask]["geo"].unique().tolist())
    df = df[~mask]
    rows_removed_aggregated = rows_before_agg_filter - len(df)

    # Remove duplicate rows (same geo, TIME_PERIOD, unit)
    # Keep first occurrence
    dedup_cols = ["geo", "TIME_PERIOD"]
    if "unit" in df.columns:
        dedup_cols.append("unit")
    available_dedup_cols = [col for col in dedup_cols if col in df.columns]
    if len(available_dedup_cols) >= 2:  # Need at least geo and TIME_PERIOD
        df = df.drop_duplicates(subset=available_dedup_cols, keep='first')

    # Store metadata about removed aggregated regions
    df.attrs['rows_removed_aggregated'] = rows_removed_aggregated
    df.attrs['removed_aggregated_regions'] = removed_regions
    return df


def merge_datasets(ren_df: pd.DataFrame, bal_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge cleaned renewable share and energy balance datasets.
    
    PROCESS:
    1. Start with nrg_bal (larger dataset) as base
    2. Filter to only "Primary production" category (nrg_bal='Primary production')
       → This represents primary energy production, most relevant for comparison
    3. Filter to only "Total" rows (siec='Total')
       → These are already aggregated across all energy sources
    4. Deduplicate rows with same (geo, TIME_PERIOD) - handles different units
       → Prefers Terajoule if available, otherwise keeps first
    5. Add data from nrg_ind_ren (smaller dataset) by matching (geo, TIME_PERIOD)
       → Adds renewable energy percentage to each row
    
    Example for Albania 2014:
    - nrg_bal has rows with nrg_bal='Primary production' and siec='Total'
    - After deduplication: 1 row with OBS_VALUE_nrg_bal (primary production in Terajoule)
    - nrg_ind_ren has 1 row for Albania 2014
    - Result: 1 merged row with both OBS_VALUE_nrg_bal (primary production) and OBS_VALUE_nrg_ind_ren (renewable %)
    
    Args:
        ren_df: Cleaned renewable share dataset (smaller, ~375 rows)
        bal_df: Cleaned energy balance dataset (larger, ~27k rows, main dataset)
    
    Returns:
        Merged DataFrame with one row per (geo, TIME_PERIOD) combination
    """
    # STEP 1: Start with bal_df as base (larger dataset)
    merged_df = bal_df.copy()
    
    # STEP 2: Normalize geo column (strip whitespace) before any operations
    merged_df["geo"] = merged_df["geo"].astype(str).str.strip()
    merged_df["TIME_PERIOD"] = pd.to_numeric(merged_df["TIME_PERIOD"], errors='coerce')
    
    # STEP 3: Use only "Primary production" category from nrg_bal
    # This represents the primary energy production, which is the most relevant metric
    # for comparing with renewable energy percentage
    if 'nrg_bal' in merged_df.columns:
        merged_df = merged_df[merged_df['nrg_bal'] == 'Primary production']
    
    # STEP 4: Use only "Total" rows (aggregated across all energy sources)
    # These rows already contain the sum of all energy sources for primary production
    if 'siec' in merged_df.columns:
        merged_df = merged_df[merged_df['siec'] == 'Total']
    
    # STEP 5: Deduplicate: for same (geo, TIME_PERIOD), keep only one row
    # This handles cases where same data appears in different units (e.g., Terajoule, GWh, etc.)
    # Prefer Terajoule if available, otherwise keep first
    dedup_cols = ["geo", "TIME_PERIOD"]
    if all(col in merged_df.columns for col in dedup_cols):
        # Sort by unit to prefer Terajoule, then take first
        if 'unit' in merged_df.columns:
            merged_df['unit_priority'] = merged_df['unit'].apply(
                lambda x: 0 if 'Terajoule' in str(x) else 1
            )
            merged_df = merged_df.sort_values('unit_priority').drop_duplicates(subset=dedup_cols, keep='first')
            merged_df = merged_df.drop(columns=['unit_priority'])
        else:
            merged_df = merged_df.drop_duplicates(subset=dedup_cols, keep='first')
    
    # STEP 6: Rename columns - no aggregation needed, we already have one row per (geo, TIME_PERIOD)
    bal_aggregated = merged_df.copy()
    bal_aggregated = bal_aggregated.rename(columns={
        "OBS_VALUE": "OBS_VALUE_nrg_bal",
        "LAST UPDATE": "LAST UPDATE_nrg_bal",
        "unit": "unit_nrg_bal"
    })
    
    # Rename aggregated columns
    bal_aggregated = bal_aggregated.rename(columns={
        "OBS_VALUE": "OBS_VALUE_nrg_bal",
        "LAST UPDATE": "LAST UPDATE_nrg_bal",
        "unit": "unit_nrg_bal"
    })
    
    # STEP 6: Prepare ren_df: normalize and rename columns
    ren_prepared = ren_df.copy()
    ren_prepared["geo"] = ren_prepared["geo"].astype(str).str.strip()
    ren_prepared["TIME_PERIOD"] = pd.to_numeric(ren_prepared["TIME_PERIOD"], errors='coerce')
    
    ren_prepared = ren_prepared.rename(columns={
        "OBS_VALUE": "OBS_VALUE_nrg_ind_ren",
        "LAST UPDATE": "LAST UPDATE_nrg_ind_ren",
        "unit": "unit_nrg_ind_ren"
    })
    
    # Rename nrg_bal column in ren_df to avoid confusion
    if 'nrg_bal' in ren_prepared.columns:
        ren_prepared = ren_prepared.rename(columns={"nrg_bal": "nrg_bal_category"})
    
    # STEP 7: Perform left merge: add ren data to aggregated bal data
    # Left merge ensures all rows from bal_aggregated are kept, with ren data added where available
    # Matching is done by (geo, TIME_PERIOD)
    # If ren data doesn't exist for a (geo, TIME_PERIOD) pair, those columns will be NaN
    merged_df = pd.merge(
        bal_aggregated,  # Left side: aggregated nrg_bal (one row per country/year)
        ren_prepared[["geo", "TIME_PERIOD", "OBS_VALUE_nrg_ind_ren", "LAST UPDATE_nrg_ind_ren", "unit_nrg_ind_ren", "freq", "nrg_bal_category"]],  # Right side: nrg_ind_ren data
        on=["geo", "TIME_PERIOD"],  # Match by country and year
        how='left',  # Keep all rows from bal_aggregated, add ren data where it exists
        suffixes=('', '_ren')  # Add suffix only to ren columns if there are conflicts
    )
    
    # STEP 8: Clean up duplicate columns
    if 'freq_ren' in merged_df.columns:
        merged_df = merged_df.drop(columns=['freq_ren'])
    
    # Remove siec and nrg_bal columns as they're not meaningful after aggregation
    # (they represent individual energy sources, but we've aggregated them)
    if 'siec' in merged_df.columns:
        merged_df = merged_df.drop(columns=['siec'])
    if 'nrg_bal' in merged_df.columns:
        merged_df = merged_df.drop(columns=['nrg_bal'])
    
    return merged_df


def preprocess_all_datasets() -> Dict[str, any]:
    """
    Main function to preprocess all datasets at server startup.
    Steps:
      1. Clean nrg_ind_ren dataset
      2. Clean nrg_bal dataset
      3. Merge datasets
      4. Add NUTS codes
      5. Save cleaned and merged datasets to data_clean/
    
    Returns:
        Dictionary with preprocessing statistics
    """
    stats = {
        "ren_rows_before": 0,
        "ren_rows_after": 0,
        "ren_quality_report": {},
        "bal_rows_before": 0,
        "bal_rows_after": 0,
        "bal_quality_report": {},
        "gdp_rows_before": 0,
        "gdp_rows_after": 0,
        "gdp_quality_report": {},
        "merged_rows": 0,
        "normalization_stats": {},
        "nuts_codes_added": 0,
        "nuts_codes_failed": 0,
        "errors": []
    }
    
    try:
        # Ensure clean directory exists
        cfg.DATA_CLEAN_DIR.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Clean renewable share dataset
        ren_df = clean_nrg_ind_ren()
        stats["ren_rows_after"] = len(ren_df)
        stats["ren_rows_removed_aggregated"] = ren_df.attrs.get('rows_removed_aggregated', 0)
        stats["ren_removed_aggregated_regions"] = ren_df.attrs.get('removed_aggregated_regions', [])
        
        # Store quality report
        ren_raw = pd.read_csv(cfg.DATA_RAW_DIR / "nrg_ind_ren.csv")
        stats["ren_quality_report"] = get_data_quality_report(ren_raw)
        stats["ren_rows_before"] = stats["ren_quality_report"]["total_rows"]
        
        # Save cleaned renewable dataset
        clean_ren_file = cfg.DATA_CLEAN_DIR / "clean_nrg_ind_ren.csv"
        ren_df.to_csv(clean_ren_file, index=False)
        
        # Step 2: Clean energy balance dataset
        bal_df = clean_energy_balance()
        stats["bal_rows_after"] = len(bal_df)
        stats["bal_rows_removed_aggregated"] = bal_df.attrs.get('rows_removed_aggregated', 0)
        stats["bal_removed_aggregated_regions"] = bal_df.attrs.get('removed_aggregated_regions', [])
        
        # Store quality report
        bal_raw = pd.read_csv(cfg.DATA_RAW_DIR / "nrg_bal.csv")
        stats["bal_quality_report"] = get_data_quality_report(bal_raw)
        stats["bal_rows_before"] = stats["bal_quality_report"]["total_rows"]
        
        # Save cleaned energy balance dataset
        clean_bal_file = cfg.DATA_CLEAN_DIR / "clean_nrg_bal.csv"
        bal_df.to_csv(clean_bal_file, index=False)

        # Step 3: Clean GDP dataset for analytics
        gdp_df = clean_gdp_dataset()
        stats["gdp_rows_after"] = len(gdp_df)
        stats["gdp_rows_removed_aggregated"] = gdp_df.attrs.get('rows_removed_aggregated', 0)
        stats["gdp_removed_aggregated_regions"] = gdp_df.attrs.get('removed_aggregated_regions', [])

        gdp_raw = pd.read_csv(cfg.DATA_RAW_DIR / "nama_10_gdp.csv")
        stats["gdp_quality_report"] = get_data_quality_report(gdp_raw)
        stats["gdp_rows_before"] = stats["gdp_quality_report"]["total_rows"]

        clean_gdp_file = cfg.DATA_CLEAN_DIR / "clean_nama_10_gdp.csv"
        gdp_df.to_csv(clean_gdp_file, index=False)
        
        # Step 2: Data Preparation - Merge datasets
        merged_df = merge_datasets(ren_df, bal_df)
        stats["merged_rows"] = len(merged_df)
        
        # Handle missing values / normalize time-series per dataset column
        obs_value_cols = [col for col in merged_df.columns if col.startswith("OBS_VALUE_")]
        normalization_stats = {}
        for value_col in obs_value_cols:
            merged_df, norm_stats = clean_and_normalize_timeseries(
                merged_df,
                geo_col="geo",
                year_col="TIME_PERIOD",
                value_col=value_col,
                missing_strategy="interpolate"
            )
            normalization_stats[value_col] = norm_stats
        stats["normalization_stats"] = normalization_stats
        
        # Step 4: Add NUTS codes
        merged_df, nuts_stats = add_nuts_codes(merged_df, geo_col="geo", auto_build=True)
        stats["nuts_codes_added"] = int(nuts_stats.get("nuts_codes_added", 0))
        stats["nuts_codes_failed"] = int(nuts_stats.get("nuts_codes_failed", 0))
        
        # Step 5: Filter to keep only rows with NUTS codes
        rows_before_filter = len(merged_df)
        merged_df = merged_df[merged_df['nuts_code'].notna()]
        rows_after_filter = len(merged_df)
        stats["merged_rows_after_nuts_filter"] = rows_after_filter
        stats["merged_rows_removed_no_nuts"] = rows_before_filter - rows_after_filter
        
        # Step 6: Save merged dataset
        merged_file = cfg.DATA_CLEAN_DIR / "merged_dataset.csv"
        merged_df.to_csv(merged_file, index=False)
        
        print("✅ Data preprocessing completed successfully!")
        
    except Exception as e:
        error_msg = f"Error during preprocessing: {str(e)}"
        stats["errors"].append(error_msg)
        print(f"❌ {error_msg}")
        raise
    
    return stats


def format_preprocessing_stats(stats: Dict[str, any]) -> None:
    """
    Pretty-print preprocessing statistics.
    """
    print("Data Preprocessing Statistics")
    print("=" * 60)

    # Renewable energy dataset
    print("\n📊 Renewable Energy Dataset (nrg_ind_ren):")
    print(f"   Rows: {stats['ren_rows_before']} → {stats['ren_rows_after']} (after cleaning)")
    ren_agg_removed = stats.get("ren_rows_removed_aggregated", 0)
    ren_agg_regions = stats.get("ren_removed_aggregated_regions", [])
    if ren_agg_removed > 0:
        print(f"   Removed aggregated regions: {ren_agg_removed} rows")
        if ren_agg_regions:
            print(f"   Removed regions: {', '.join(ren_agg_regions)}")
    ren_qual = stats.get("ren_quality_report", {})
    if ren_qual:
        missing = ren_qual.get("missing_values", {})
        missing_obs = missing.get("OBS_VALUE", 0)
        if missing_obs > 0:
            pct = ren_qual.get("missing_percentage", {}).get("OBS_VALUE", 0)
            print(f"   Missing OBS_VALUE: {missing_obs} ({pct}%)")
        print(f"   Duplicate rows: {ren_qual.get('duplicate_rows', 0)}")

    # Energy balance dataset
    print("\n📊 Energy Balance Dataset (nrg_bal):")
    print(f"   Rows: {stats['bal_rows_before']} → {stats['bal_rows_after']} (after cleaning)")
    bal_agg_removed = stats.get("bal_rows_removed_aggregated", 0)
    bal_agg_regions = stats.get("bal_removed_aggregated_regions", [])
    if bal_agg_removed > 0:
        print(f"   Removed aggregated regions: {bal_agg_removed} rows")
        if bal_agg_regions:
            print(f"   Removed regions: {', '.join(bal_agg_regions)}")
    removed_bal = stats["bal_rows_before"] - stats["bal_rows_after"]
    if removed_bal > 0:
        pct = (removed_bal / stats["bal_rows_before"]) * 100
        print(f"   Total removed: {removed_bal} rows ({pct:.2f}%)")
    bal_qual = stats.get("bal_quality_report", {})
    if bal_qual:
        missing = bal_qual.get("missing_values", {})
        missing_obs = missing.get("OBS_VALUE", 0)
        if missing_obs > 0:
            pct = bal_qual.get("missing_percentage", {}).get("OBS_VALUE", 0)
            print(f"   Missing OBS_VALUE: {missing_obs} ({pct}%)")
        print(f"   Duplicate rows: {bal_qual.get('duplicate_rows', 0)}")

    # GDP dataset
    if stats.get("gdp_rows_before"):
        print("\n📊 GDP Dataset (nama_10_gdp):")
        print(f"   Rows: {stats['gdp_rows_before']} → {stats['gdp_rows_after']} (after cleaning)")
        gdp_agg_removed = stats.get("gdp_rows_removed_aggregated", 0)
        gdp_agg_regions = stats.get("gdp_removed_aggregated_regions", [])
        if gdp_agg_removed > 0:
            print(f"   Removed aggregated regions: {gdp_agg_removed} rows")
            if gdp_agg_regions:
                print(f"   Removed regions: {', '.join(gdp_agg_regions)}")
        gdp_qual = stats.get("gdp_quality_report", {})
        if gdp_qual:
            missing = gdp_qual.get("missing_values", {})
            missing_obs = missing.get("OBS_VALUE", 0)
            if missing_obs > 0:
                pct = gdp_qual.get("missing_percentage", {}).get("OBS_VALUE", 0)
                print(f"   Missing OBS_VALUE: {missing_obs} ({pct}%)")
            print(f"   Duplicate rows: {gdp_qual.get('duplicate_rows', 0)}")

    # Merged dataset
    print("\n🔗 Merged Dataset:")
    print(f"   Total rows: {stats['merged_rows']}")

    # Normalization stats
    norm_stats = stats.get("normalization_stats", {})
    if norm_stats:
        print("\n📈 Data Normalization:")
        for col, col_stats in norm_stats.items():
            parts = []
            filled = col_stats.get("missing_values_filled", 0)
            removed = col_stats.get("rows_removed", 0)
            invalid_years = col_stats.get("invalid_years_removed", 0)
            if filled > 0:
                parts.append(f"filled {filled} missing values")
            if removed > 0:
                parts.append(f"removed {removed} rows")
            if invalid_years > 0:
                parts.append(f"removed {invalid_years} invalid years")
            if parts:
                print(f"   {col}: {', '.join(parts)}")

    # NUTS codes
    print("\n🌍 NUTS Codes:")
    print(f"   Added: {stats['nuts_codes_added']}")
    if stats["nuts_codes_failed"] > 0:
        print(f"   Failed: {stats['nuts_codes_failed']}")

    # Errors
    if stats.get("errors"):
        print("\n⚠️  Errors:")
        for error in stats["errors"]:
            print(f"   - {error}")

    print("\n" + "=" * 60)

