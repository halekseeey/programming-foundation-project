"""
Data processing module for cleaning, normalizing, merging datasets, and NUTS code mapping.
"""
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

try:
    import pycountry
    PYCOUNTRY_AVAILABLE = True
except ImportError:
    PYCOUNTRY_AVAILABLE = False

from .data_loader import load_raw_renewables, filter_renewables


def _get_iso_code_auto(country: str) -> Optional[str]:
    """
    Automatically get ISO 3166-1 alpha-2 code for a country name using pycountry.
    Returns None if not found.
    """
    if not PYCOUNTRY_AVAILABLE:
        raise ImportError("pycountry is required for automatic NUTS code detection. Install it with: pip install pycountry")
    
    country_clean = country.strip()
    
    # Try fuzzy search (handles variations in country names)
    try:
        country_obj = pycountry.countries.search_fuzzy(country_clean)
        if country_obj:
            return country_obj[0].alpha_2
    except (LookupError, AttributeError):
        pass
    
    return None


def get_nuts_code(country: str) -> Optional[str]:
    """
    Get NUTS code for a country name automatically using pycountry.
    Automatically determines ISO code, then maps to NUTS code.
    Returns None if not found.
    
    Args:
        country: Country name (e.g., "Portugal", "Albania") or ISO code (e.g., "PT", "AL")
    
    Returns:
        NUTS code (e.g., "PT", "AL") or None if not found
    """
    if not PYCOUNTRY_AVAILABLE:
        raise ImportError("pycountry is required for automatic NUTS code detection. Install it with: pip install pycountry")
    
    country_clean = country.strip()
    
    # If input is already an ISO code (2 uppercase letters), use it directly
    if len(country_clean) == 2 and country_clean.isupper():
        iso_code = country_clean
    else:
        # Get ISO code automatically from country name
        iso_code = _get_iso_code_auto(country_clean)
        if not iso_code:
            return None
    
    # Return ISO code directly (NUTS codes typically use ISO 3166-1 alpha-2 codes)
    return iso_code


def build_nuts_mapping_from_data(df: pd.DataFrame, geo_col: str = "geo") -> Dict[str, str]:
    """
    Automatically build NUTS code mapping from data by extracting unique countries
    and determining their NUTS codes.
    
    Args:
        df: DataFrame with geographic data
        geo_col: Column name for geographic region
    
    Returns:
        Dictionary mapping country names to NUTS codes
    """
    if geo_col not in df.columns:
        return {}
    
    mapping = {}
    unique_countries = df[geo_col].dropna().unique()
    
    for country in unique_countries:
        if pd.isna(country):
            continue
        country_str = str(country).strip()
        if country_str and country_str not in mapping:
            nuts_code = get_nuts_code(country_str)
            if nuts_code:
                mapping[country_str] = nuts_code
    
    return mapping


def clean_and_normalize_timeseries(
    df: pd.DataFrame,
    geo_col: str = "geo",
    year_col: str = "TIME_PERIOD",
    value_col: str = "OBS_VALUE",
    missing_strategy: str = "interpolate"
):
    """
    Clean and normalize time-series data.
    
    Args:
        df: Input DataFrame
        geo_col: Column name for geographic region
        year_col: Column name for year/time period
        value_col: Column name for values
        missing_strategy: Strategy for handling missing values
            - "interpolate": Linear interpolation
            - "forward_fill": Forward fill
            - "backward_fill": Backward fill
            - "drop": Drop missing values
            - "zero": Fill with zero
    
    Returns:
        Tuple of (cleaned DataFrame, statistics dict)
    """
    df = df.copy()
    stats = {
        "missing_values_filled": 0,
        "rows_removed": 0,
        "invalid_years_removed": 0,
        "values_converted": 0
    }
    
    initial_rows = len(df)
    
    # Count missing values before processing
    if value_col in df.columns:
        missing_before = df[value_col].isna().sum()
    
    # Convert year to numeric
    if year_col in df.columns:
        invalid_years_before = df[year_col].isna().sum()
        df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
        invalid_years_after = df[year_col].isna().sum()
        stats["values_converted"] += (invalid_years_after - invalid_years_before)
    
    # Convert value to numeric
    if value_col in df.columns:
        invalid_values_before = df[value_col].isna().sum()
        df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
        invalid_values_after = df[value_col].isna().sum()
        stats["values_converted"] += (invalid_values_after - invalid_values_before)
    
    # Sort by geo and year
    if geo_col in df.columns and year_col in df.columns:
        df = df.sort_values([geo_col, year_col])
    
    # Handle missing values
    if value_col in df.columns:
        missing_count = df[value_col].isna().sum()
        
        if missing_strategy == "interpolate":
            # Group by geo and interpolate within each group
            if geo_col in df.columns:
                df[value_col] = df.groupby(geo_col)[value_col].transform(
                    lambda x: x.interpolate(method='linear', limit_direction='both')
                )
            else:
                df[value_col] = df[value_col].interpolate(method='linear', limit_direction='both')
            stats["missing_values_filled"] = missing_count - df[value_col].isna().sum()
        elif missing_strategy == "forward_fill":
            if geo_col in df.columns:
                df[value_col] = df.groupby(geo_col)[value_col].ffill()
            else:
                df[value_col] = df[value_col].ffill()
            stats["missing_values_filled"] = missing_count - df[value_col].isna().sum()
        elif missing_strategy == "backward_fill":
            if geo_col in df.columns:
                df[value_col] = df.groupby(geo_col)[value_col].bfill()
            else:
                df[value_col] = df[value_col].bfill()
            stats["missing_values_filled"] = missing_count - df[value_col].isna().sum()
        elif missing_strategy == "zero":
            df[value_col] = df[value_col].fillna(0)
            stats["missing_values_filled"] = missing_count
        elif missing_strategy == "drop":
            rows_before_drop = len(df)
            df = df.dropna(subset=[value_col])
            stats["rows_removed"] = rows_before_drop - len(df)
    
    # Remove rows with invalid years
    if year_col in df.columns:
        rows_before_year_filter = len(df)
        df = df[(df[year_col] >= 1900) & (df[year_col] <= 2100)]
        stats["invalid_years_removed"] = rows_before_year_filter - len(df)
    
    final_rows = len(df)
    # Calculate total rows removed (excluding invalid years which are counted separately)
    total_removed = initial_rows - final_rows
    if stats["rows_removed"] == 0:  # If no rows were removed by drop strategy
        stats["rows_removed"] = max(0, total_removed - stats["invalid_years_removed"])
    
    return df, stats


def add_nuts_codes(df: pd.DataFrame, geo_col: str = "geo", auto_build: bool = True):
    """
    Add NUTS codes to DataFrame based on geographic column.
    Automatically determines NUTS codes using pycountry if available.
    
    Args:
        df: Input DataFrame
        geo_col: Column name for geographic region
        auto_build: If True, automatically builds mapping from data (default: True)
    
    Returns:
        Tuple of (DataFrame with added 'nuts_code' column, statistics dict)
    """
    df = df.copy()
    stats = {
        "nuts_codes_added": 0,
        "nuts_codes_failed": 0,
        "nuts_codes_failed_values": []
    }
    
    if geo_col not in df.columns:
        return df, stats
    
    # Build mapping automatically if requested
    if auto_build:
        # Cache mapping for performance
        if not hasattr(add_nuts_codes, '_mapping_cache'):
            add_nuts_codes._mapping_cache = {}
        
        # Build mapping for unique countries in this dataframe
        unique_countries = df[geo_col].dropna().unique()
        for country in unique_countries:
            if pd.isna(country):
                continue
            country_str = str(country).strip()
            if country_str and country_str not in add_nuts_codes._mapping_cache:
                nuts_code = get_nuts_code(country_str)
                add_nuts_codes._mapping_cache[country_str] = nuts_code
        
        # Use cached mapping
        def map_to_nuts(geo_value):
            if pd.isna(geo_value):
                return None
            country_str = str(geo_value).strip()
            return add_nuts_codes._mapping_cache.get(country_str)
    else:
        # Use direct lookup (slower but no caching)
        def map_to_nuts(geo_value):
            if pd.isna(geo_value):
                return None
            return get_nuts_code(str(geo_value))
    
    df['nuts_code'] = df[geo_col].apply(map_to_nuts)
    
    # Count statistics and collect failed values
    stats["nuts_codes_added"] = df['nuts_code'].notna().sum()
    stats["nuts_codes_failed"] = df['nuts_code'].isna().sum()
    
    # Collect unique failed values with counts
    failed_mask = df['nuts_code'].isna()
    if failed_mask.any():
        # Get all failed values (including NaN handling)
        failed_df = df.loc[failed_mask, geo_col]
        
        # Count occurrences of each failed value
        try:
            failed_counts = failed_df.value_counts()
            
            # Build list with counts
            failed_list = []
            for value, count in failed_counts.items():
                try:
                    # Convert count to native Python int
                    if hasattr(count, 'item'):
                        count_int = int(count.item())
                    else:
                        count_int = int(count)
                    
                    if pd.isna(value):
                        failed_list.append(f"<empty/null> ({count_int})")
                    else:
                        v_str = str(value).strip()
                        if v_str and v_str.lower() != 'nan':
                            if count_int > 1:
                                failed_list.append(f"{v_str} ({count_int})")
                            else:
                                failed_list.append(v_str)
                except Exception as e:
                    # If conversion fails, just use the value as string
                    print(f"Warning: Failed to process failed value {value}: {e}")
                    failed_list.append(str(value))
        except Exception as e:
            print(f"Error in collecting failed values: {e}")
            # Fallback: just get unique values without counts
            failed_values = failed_df.dropna().unique()
            failed_list = [str(v).strip() for v in failed_values if str(v).strip() and str(v).strip().lower() != 'nan']
        
        stats["nuts_codes_failed_values"] = failed_list
    
    return df, stats




def create_summary_table(
    df: pd.DataFrame,
    group_by: List[str],
    value_col: str = "OBS_VALUE",
    agg_functions: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Create summary table grouped by specified columns.
    
    Args:
        df: Input DataFrame
        group_by: List of column names to group by
        value_col: Column name for values to aggregate
        agg_functions: List of aggregation functions
            - "mean", "median", "sum", "min", "max", "count", "std"
    
    Returns:
        Summary DataFrame
    """
    if agg_functions is None:
        agg_functions = ["mean", "min", "max", "count"]
    
    # Check if columns exist
    missing_cols = [col for col in group_by if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Columns not found: {missing_cols}")
    
    if value_col not in df.columns:
        raise ValueError(f"Value column not found: {value_col}")
    
    # Convert value column to numeric
    df = df.copy()
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    
    # Group and aggregate
    grouped = df.groupby(group_by)[value_col].agg(agg_functions)
    
    # Flatten column names if multi-level
    if isinstance(grouped.columns, pd.MultiIndex):
        grouped.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in grouped.columns]
    else:
        grouped.columns = [f"{value_col}_{col}" for col in grouped.columns]
    
    return grouped.reset_index()


def get_data_quality_report(df: pd.DataFrame) -> Dict:
    """
    Generate data quality report for a DataFrame.
    
    Returns:
        Dictionary with quality metrics
    """
    report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": {},
        "missing_percentage": {},
        "duplicate_rows": int(df.duplicated().sum()),
        "data_types": {}
    }
    
    for col in df.columns:
        missing_count = df[col].isna().sum()
        # Convert to int if it's a scalar, handle Series case
        if hasattr(missing_count, 'item'):
            missing_count_int = int(missing_count.item())
        elif isinstance(missing_count, (pd.Series, pd.core.series.Series)):
            missing_count_int = int(missing_count.iloc[0]) if len(missing_count) > 0 else 0
        else:
            missing_count_int = int(missing_count)
        
        missing_pct = (missing_count_int / len(df)) * 100 if len(df) > 0 else 0
        
        report["missing_values"][col] = missing_count_int
        report["missing_percentage"][col] = round(missing_pct, 2)
        report["data_types"][col] = str(df[col].dtype)
    
    return report


def normalize_timeseries_by_region(
    df: pd.DataFrame,
    geo_col: str = "geo",
    year_col: str = "TIME_PERIOD",
    value_col: str = "OBS_VALUE",
    method: str = "min_max"
) -> pd.DataFrame:
    """
    Normalize time-series values by region.
    
    Args:
        df: Input DataFrame
        geo_col: Column name for geographic region
        year_col: Column name for year
        value_col: Column name for values
        method: Normalization method
            - "min_max": Scale to [0, 1]
            - "z_score": Standardize (mean=0, std=1)
            - "percentile": Rank-based normalization
    
    Returns:
        DataFrame with normalized values in new column 'normalized_value'
    """
    df = df.copy()
    
    if value_col not in df.columns:
        return df
    
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    
    if method == "min_max":
        if geo_col in df.columns:
            def normalize_group(group):
                min_val = group[value_col].min()
                max_val = group[value_col].max()
                if max_val != min_val:
                    return (group[value_col] - min_val) / (max_val - min_val)
                return group[value_col] * 0  # All zeros if constant
            df['normalized_value'] = df.groupby(geo_col)[value_col].transform(normalize_group)
        else:
            min_val = df[value_col].min()
            max_val = df[value_col].max()
            if max_val != min_val:
                df['normalized_value'] = (df[value_col] - min_val) / (max_val - min_val)
            else:
                df['normalized_value'] = 0
    
    elif method == "z_score":
        if geo_col in df.columns:
            def standardize_group(group):
                mean_val = group[value_col].mean()
                std_val = group[value_col].std()
                if std_val != 0:
                    return (group[value_col] - mean_val) / std_val
                return group[value_col] * 0
            df['normalized_value'] = df.groupby(geo_col)[value_col].transform(standardize_group)
        else:
            mean_val = df[value_col].mean()
            std_val = df[value_col].std()
            if std_val != 0:
                df['normalized_value'] = (df[value_col] - mean_val) / std_val
            else:
                df['normalized_value'] = 0
    
    elif method == "percentile":
        if geo_col in df.columns:
            df['normalized_value'] = df.groupby(geo_col)[value_col].transform(
                lambda x: x.rank(pct=True)
            )
        else:
            df['normalized_value'] = df[value_col].rank(pct=True)
    
    return df

