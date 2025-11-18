from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Dict

import pandas as pd

from config import get_config

cfg = get_config()

# Global variable to store current dataset(s)
_current_dataset_id: Optional[str] = None
_current_dataset_ids: List[str] = []  # Support multiple datasets
# Global variable to store cleaned dataset
_cleaned_dataset: Optional[pd.DataFrame] = None


def set_current_dataset(dataset_id: Optional[str] = None):
    """Set the current dataset to use (single dataset, for backward compatibility)"""
    global _current_dataset_id, _current_dataset_ids, _cleaned_dataset
    _current_dataset_id = dataset_id
    _current_dataset_ids = [dataset_id] if dataset_id else []
    _cleaned_dataset = None  # Clear cleaned dataset when dataset changes
    # Clear cache when dataset changes
    load_raw_renewables.cache_clear()


def set_current_datasets(dataset_ids: List[str]):
    """Set multiple datasets to use and merge them"""
    global _current_dataset_id, _current_dataset_ids, _cleaned_dataset
    _current_dataset_ids = dataset_ids if dataset_ids else []
    _current_dataset_id = _current_dataset_ids[0] if _current_dataset_ids else None
    _cleaned_dataset = None  # Clear cleaned dataset when dataset changes
    # Clear cache when dataset changes
    load_raw_renewables.cache_clear()


def get_current_datasets() -> List[str]:
    """Get the list of currently selected dataset IDs"""
    global _current_dataset_ids
    return _current_dataset_ids if _current_dataset_ids else ([_current_dataset_id] if _current_dataset_id else [])


def set_cleaned_dataset(df: pd.DataFrame):
    """Store the cleaned dataset"""
    global _cleaned_dataset
    _cleaned_dataset = df.copy()


def get_cleaned_dataset() -> Optional[pd.DataFrame]:
    """Get the cleaned dataset if available"""
    global _cleaned_dataset
    return _cleaned_dataset.copy() if _cleaned_dataset is not None else None


def get_current_dataset() -> Optional[str]:
    """Get the current dataset ID"""
    return _current_dataset_id


def load_dataset(dataset_id: str) -> pd.DataFrame:
    """
    Load a specific dataset by ID.
    
    Args:
        dataset_id: Dataset ID (filename without extension)
    
    Returns:
        DataFrame with loaded data
    """
    datasets = cfg.get_available_datasets()
    dataset = next((d for d in datasets if d["id"] == dataset_id), None)
    
    if not dataset:
        raise ValueError(f"Dataset {dataset_id} not found")
    
    csv_path = Path(dataset["path"])

    # CSV file uses comma as separator
    # Try comma first, then semicolon as fallback
    try:
        df = pd.read_csv(csv_path, sep=",", encoding='utf-8')
    except Exception:
        try:
            df = pd.read_csv(csv_path, sep=";", encoding='utf-8')
        except Exception:
            # Try with different encoding
            df = pd.read_csv(csv_path, sep=",", encoding='latin-1')

    return df


@lru_cache(maxsize=1)
def load_raw_renewables() -> pd.DataFrame:
    """
    Загружает сырые данные. Требует выбора ровно 2 датасетов для объединения.
    """
    global _current_dataset_ids
    
    # Require exactly 2 datasets
    if not _current_dataset_ids or len(_current_dataset_ids) != 2:
        raise ValueError("Exactly 2 datasets must be selected for analysis")
    
    if len(_current_dataset_ids) == 2:
            # Load datasets
            dfs = []
            for dataset_id in _current_dataset_ids:
                df = load_dataset(dataset_id)
                dfs.append(df)
            
            # Prepare datasets for smart merge
            processed_dfs = []
            
            for i, df in enumerate(dfs):
                dataset_id = _current_dataset_ids[i] if i < len(_current_dataset_ids) else f"dataset{i+1}"
                
                df_processed = df.copy()
                
                # Remove DATAFLOW column
                if 'DATAFLOW' in df_processed.columns:
                    df_processed = df_processed.drop(columns=['DATAFLOW'])
                
                # Rename OBS_VALUE and LAST UPDATE to include dataset identifier
                if 'OBS_VALUE' in df_processed.columns:
                    df_processed = df_processed.rename(columns={'OBS_VALUE': f'OBS_VALUE_{dataset_id}'})
                if 'LAST UPDATE' in df_processed.columns:
                    df_processed = df_processed.rename(columns={'LAST UPDATE': f'LAST UPDATE_{dataset_id}'})
                
                # Handle conflicting column names (like 'nrg_bal' which exists in both but with different meanings)
                # Rename dataset-specific columns to avoid conflicts
                if 'nrg_bal' in df_processed.columns and dataset_id == 'nrg_ind_ren':
                    # In nrg_ind_ren, nrg_bal is always "Renewable energy - overall", so rename it
                    df_processed = df_processed.rename(columns={'nrg_bal': 'nrg_bal_category'})
                
                processed_dfs.append(df_processed)
            
            # Smart merge: merge on common keys (geo + TIME_PERIOD)
            # Primary merge keys: geo and TIME_PERIOD
            merge_keys = []
            for key in ['geo', 'GEO', 'TIME_PERIOD', 'TIME', 'time', 'year', 'Year']:
                if key in processed_dfs[0].columns and key in processed_dfs[1].columns:
                    merge_keys.append(key)
            
            if not merge_keys:
                raise ValueError("Cannot find common merge keys (geo, TIME_PERIOD) between datasets")
            
            print(f"Merging datasets on keys: {merge_keys}")
            print(f"Dataset 1: {len(processed_dfs[0])} rows, columns: {list(processed_dfs[0].columns)}")
            print(f"Dataset 2: {len(processed_dfs[1])} rows, columns: {list(processed_dfs[1].columns)}")
            
            # Before merging, deduplicate datasets on merge keys to prevent cartesian product
            for i, df in enumerate(processed_dfs):
                duplicates_before = len(df)
                # Remove duplicates on merge keys, keeping first occurrence
                df = df.drop_duplicates(subset=merge_keys, keep='first')
                duplicates_removed = duplicates_before - len(df)
                if duplicates_removed > 0:
                    print(f"Removed {duplicates_removed} duplicate rows from dataset {i+1} on merge keys")
                processed_dfs[i] = df
            
            # Determine which dataset is the "main" one
            # Use nrg_ind_ren as main (percentage data) if available, otherwise use the smaller one
            # This ensures we preserve the structure of the percentage dataset
            dataset_0_id = _current_dataset_ids[0] if len(_current_dataset_ids) > 0 else None
            dataset_1_id = _current_dataset_ids[1] if len(_current_dataset_ids) > 1 else None
            
            if dataset_0_id == 'nrg_ind_ren' or dataset_1_id == 'nrg_ind_ren':
                # Use nrg_ind_ren as main dataset (left side)
                if dataset_0_id == 'nrg_ind_ren':
                    main_df = processed_dfs[0]
                    secondary_df = processed_dfs[1]
                else:
                    main_df = processed_dfs[1]
                    secondary_df = processed_dfs[0]
            else:
                # Fallback: use smaller dataset as main to preserve its structure
                if len(processed_dfs[0]) <= len(processed_dfs[1]):
                    main_df = processed_dfs[0]
                    secondary_df = processed_dfs[1]
                else:
                    main_df = processed_dfs[1]
                    secondary_df = processed_dfs[0]
            
            # Ensure merge keys have compatible types
            for key in merge_keys:
                if key in main_df.columns and key in secondary_df.columns:
                    main_df[key] = main_df[key].astype(str)
                    secondary_df[key] = secondary_df[key].astype(str)
            
            # Perform left merge: keep all rows from main_df, add matching data from secondary_df
            # This prevents cartesian product - each row from main_df gets at most one match from secondary_df
            merged_df = pd.merge(
                main_df,
                secondary_df,
                on=merge_keys,
                how='left',
                suffixes=('', '_secondary')
            )
            
            # Handle duplicate columns from merge
            for col in list(merged_df.columns):
                if col.endswith('_secondary'):
                    original_col = col.replace('_secondary', '')
                    if original_col in merged_df.columns:
                        # If original is NaN and duplicate has value, use duplicate
                        mask = merged_df[original_col].isna() & merged_df[col].notna()
                        merged_df.loc[mask, original_col] = merged_df.loc[mask, col]
                    # Drop duplicate column
                    merged_df = merged_df.drop(columns=[col])
            
            # Final deduplication to ensure no duplicate rows
            before_dedup = len(merged_df)
            merged_df = merged_df.drop_duplicates(keep='first')
            after_dedup = len(merged_df)
            if before_dedup != after_dedup:
                print(f"Removed {before_dedup - after_dedup} duplicate rows after merge")
            
            print(f"Merged dataset: {len(merged_df)} rows")
            print(f"Sample: {merged_df[['geo', 'TIME_PERIOD'] + [col for col in merged_df.columns if 'OBS_VALUE' in col]].head() if len(merged_df) > 0 else 'Empty'}")
            
            # Sort columns in specific order - group by dataset
            ordered_cols = []
            
            # First: nuts_code (must be first)
            if 'nuts_code' in merged_df.columns:
                ordered_cols.append('nuts_code')
            
            # Then: common columns (geo, TIME_PERIOD)
            common_cols = ['geo', 'GEO', 'TIME_PERIOD', 'TIME', 'time', 'year', 'Year']
            for col in common_cols:
                if col in merged_df.columns and col not in ordered_cols:
                    ordered_cols.append(col)
            
            # Group columns by dataset: for each dataset, group LAST UPDATE, OBS_VALUE, and related parameters
            # Extract dataset IDs from OBS_VALUE columns
            obs_value_cols = [col for col in merged_df.columns if col.startswith('OBS_VALUE_')]
            dataset_ids = []
            for col in obs_value_cols:
                dataset_id = col.replace('OBS_VALUE_', '')
                if dataset_id not in dataset_ids:
                    dataset_ids.append(dataset_id)
            
            # For each dataset, group its columns together: LAST UPDATE, OBS_VALUE, and parameters
            for dataset_id in sorted(dataset_ids):
                # LAST UPDATE for this dataset
                last_update_col = f'LAST UPDATE_{dataset_id}'
                if last_update_col in merged_df.columns:
                    ordered_cols.append(last_update_col)
                
                # OBS_VALUE for this dataset
                obs_value_col = f'OBS_VALUE_{dataset_id}'
                if obs_value_col in merged_df.columns:
                    ordered_cols.append(obs_value_col)
                
                # Related parameters for this dataset (grouped together)
                # For nrg_ind_ren: nrg_bal_category, freq, unit
                # For nrg_bal: nrg_bal, siec, freq, unit
                if dataset_id == 'nrg_ind_ren':
                    # nrg_bal_category belongs to nrg_ind_ren
                    if 'nrg_bal_category' in merged_df.columns and 'nrg_bal_category' not in ordered_cols:
                        ordered_cols.append('nrg_bal_category')
                    # freq and unit for this dataset
                    for param_col in ['freq', 'unit']:
                        if param_col in merged_df.columns and param_col not in ordered_cols:
                            ordered_cols.append(param_col)
                elif dataset_id == 'nrg_bal':
                    # nrg_bal, siec belong to nrg_bal
                    for param_col in ['nrg_bal', 'siec']:
                        if param_col in merged_df.columns and param_col not in ordered_cols:
                            ordered_cols.append(param_col)
                    # freq and unit for this dataset (if not already added from first dataset)
                    for param_col in ['freq', 'unit']:
                        if param_col in merged_df.columns and param_col not in ordered_cols:
                            ordered_cols.append(param_col)
            
            # Finally: all other columns that weren't grouped
            remaining_cols = [col for col in merged_df.columns if col not in ordered_cols]
            # Remove _source_dataset if it exists
            if '_source_dataset' in remaining_cols:
                remaining_cols.remove('_source_dataset')
            ordered_cols.extend(sorted(remaining_cols))
            
            # Reorder dataframe columns
            merged_df = merged_df[ordered_cols]
            
            # Remove _source_dataset column if it still exists
            if '_source_dataset' in merged_df.columns:
                merged_df = merged_df.drop(columns=['_source_dataset'])
            
            return merged_df
    
    raise ValueError("Exactly 2 datasets must be selected for analysis")


def get_available_countries() -> List[str]:
    df = load_raw_renewables()
    # Find geo/country column - try common names first
    geo_col = None
    for col_name in ["geo", "GEO", "country", "Country", "GEO/TIME"]:
        if col_name in df.columns:
            geo_col = col_name
            break
    if geo_col is None:
        geo_col = df.columns[0]  # fallback to first column
    
    # Extract unique countries, filter out non-country values
    countries = df[geo_col].astype(str).unique().tolist()
    # Filter out very long strings that look like full CSV rows
    countries = [c for c in countries if len(c) < 100 and c != 'nan']
    countries = sorted(countries)
    return countries


def filter_renewables(
    country: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
) -> pd.DataFrame:
    """
    Filter renewable energy data by country and/or year range.
    Used internally for analytics functions.
    """
    df = load_raw_renewables()

    geo_col = "geo" if "geo" in df.columns else df.columns[0]
    year_col = None
    for col_name in ["year", "Year", "TIME", "time", "TIME_PERIOD"]:
        if col_name in df.columns:
            year_col = col_name
            break
    if year_col is None:
        year_col = df.columns[1] if len(df.columns) > 1 else df.columns[-1]

    if country:
        df = df[df[geo_col].astype(str).str.contains(str(country), case=False, na=False)]

    if year_from or year_to:
        df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
        if year_from:
            df = df[df[year_col] >= year_from]
        if year_to:
            df = df[df[year_col] <= year_to]

    return df
