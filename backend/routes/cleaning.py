"""
Dataset cleaning routes.
"""
from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np

from renewables.data_loader import (
    get_current_dataset,
    load_raw_renewables,
    set_cleaned_dataset
)
from renewables.data_processing import (
    clean_and_normalize_timeseries,
    add_nuts_codes,
    get_data_quality_report
)

cleaning_bp = Blueprint('cleaning', __name__)


def convert_to_native(obj):
    """Recursively convert numpy/pandas types to native Python types"""
    if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    elif isinstance(obj, dict):
        return {k: convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_native(item) for item in obj]
    else:
        return obj


@cleaning_bp.post("/api/datasets/clean")
def clean_dataset():
    """Clean and organize the selected dataset."""
    data = request.get_json() or {}
    strategy = data.get("strategy", "interpolate")
    
    current_dataset = get_current_dataset()
    if not current_dataset:
        return jsonify(error="No dataset selected. Please select a dataset first."), 400
    
    try:
        df = load_raw_renewables()
        print(f"Loaded dataset: {len(df)} rows, columns: {list(df.columns)}")
        
        # Handle empty values from merge: convert None/NaN to empty string for display
        # This is expected behavior when merging datasets - some columns will be empty for rows from other datasets
        # We'll keep them as NaN for now, but can optionally convert to empty string or 0 for display
        obs_value_cols = [col for col in df.columns if col.startswith('OBS_VALUE_')]
        last_update_cols = [col for col in df.columns if col.startswith('LAST UPDATE_')]
        
        # For merged datasets, empty values in OBS_VALUE_* and LAST UPDATE_* columns are expected
        # We can optionally fill them with 0 or leave as NaN (which will show as empty in preview)
        # For now, we'll leave them as NaN to preserve information about which dataset the row came from
        
        # Find columns automatically
        geo_col = "geo" if "geo" in df.columns else df.columns[0]
        print(f"Unique geo values: {df[geo_col].unique()[:10] if geo_col in df.columns else 'N/A'}")
        year_col = None
        value_col = None
        
        for col_name in ["year", "Year", "TIME", "time", "TIME_PERIOD"]:
            if col_name in df.columns:
                year_col = col_name
                break
        
        for col_name in ["value", "Value", "VALUE", "OBS_VALUE"]:
            if col_name in df.columns:
                value_col = col_name
                break
        
        # If value column not found, check for merged columns (with dataset suffix)
        if not value_col:
            for col in df.columns:
                if col.startswith("OBS_VALUE") or col.startswith("value") or col.startswith("Value"):
                    value_col = col
                    break
        
        print(f"Detected columns: geo_col={geo_col}, year_col={year_col}, value_col={value_col}")
        print(f"Found {len(obs_value_cols)} OBS_VALUE columns and {len(last_update_cols)} LAST UPDATE columns from merge")
        
        if not year_col or not value_col:
            return jsonify(error=f"Could not identify year and value columns. Available columns: {list(df.columns)}"), 400
        
        # Clean and normalize - process each OBS_VALUE column separately if multiple exist
        print("Starting clean_and_normalize_timeseries...")
        
        # If we have multiple OBS_VALUE columns (merged datasets), process each one
        if len(obs_value_cols) > 1:
            # For merged datasets, we need to preserve NaN values that came from merge
            # Only fill NaN values that existed in the original data (within the same dataset)
            # Since we don't have _source_dataset anymore, we'll process all NaN values
            # but only for rows where the column should have data (non-NaN in related columns)
            
            # Process each OBS_VALUE column separately
            for obs_col in obs_value_cols:
                if obs_col in df.columns:
                    # Convert to numeric
                    df[obs_col] = pd.to_numeric(df[obs_col], errors='coerce')
                    
                    # Apply missing strategy to all NaN values in this column
                    # (the merge already preserved NaN where data doesn't exist)
                    mask_to_fill = df[obs_col].isna()
                    
                    if mask_to_fill.any():
                        # Apply missing strategy
                        if strategy == "interpolate" and geo_col in df.columns:
                            # Group by geo and interpolate
                            for geo_val in df[geo_col].unique():
                                geo_mask = df[geo_col] == geo_val
                                if geo_mask.sum() > 1:
                                    df.loc[geo_mask, obs_col] = df.loc[geo_mask, obs_col].interpolate(
                                        method='linear', limit_direction='both'
                                    )
                        elif strategy == "forward_fill" and geo_col in df.columns:
                            for geo_val in df[geo_col].unique():
                                geo_mask = df[geo_col] == geo_val
                                df.loc[geo_mask, obs_col] = df.loc[geo_mask, obs_col].ffill()
                        elif strategy == "backward_fill" and geo_col in df.columns:
                            for geo_val in df[geo_col].unique():
                                geo_mask = df[geo_col] == geo_val
                                df.loc[geo_mask, obs_col] = df.loc[geo_mask, obs_col].bfill()
                        elif strategy == "zero":
                            df.loc[mask_to_fill, obs_col] = 0
                        # For "drop" strategy, we don't drop rows based on secondary columns
            
            # Now process the first OBS_VALUE column as primary for statistics
            result = clean_and_normalize_timeseries(
                df, geo_col=geo_col, year_col=year_col, value_col=obs_value_cols[0],
                missing_strategy=strategy
            )
            if isinstance(result, tuple):
                df_cleaned, clean_stats = result
            else:
                df_cleaned = result
                clean_stats = {}
        else:
            # Single dataset or single OBS_VALUE column
            result = clean_and_normalize_timeseries(
                df, geo_col=geo_col, year_col=year_col, value_col=value_col,
                missing_strategy=strategy
            )
            if isinstance(result, tuple):
                df_cleaned, clean_stats = result
            else:
                df_cleaned = result
                clean_stats = {}
        
        print(f"Cleaned dataset: {len(df_cleaned)} rows")
        
        # Add NUTS codes
        print("Starting add_nuts_codes...")
        result = add_nuts_codes(df_cleaned, geo_col=geo_col, auto_build=True)
        if isinstance(result, tuple):
            df_cleaned, nuts_stats = result
        else:
            df_cleaned = result
            nuts_stats = {}
        print(f"Added NUTS codes: {len(df_cleaned)} rows")
        print(f"NUTS stats: added={nuts_stats.get('nuts_codes_added', 0)}, failed={nuts_stats.get('nuts_codes_failed', 0)}")
        if nuts_stats.get('nuts_codes_failed_values'):
            print(f"Failed NUTS values: {nuts_stats['nuts_codes_failed_values']}")
        
        # Reorder columns: group by dataset (same logic as in data_loader.py)
        ordered_cols = []
        
        # First: nuts_code (must be first)
        if 'nuts_code' in df_cleaned.columns:
            ordered_cols.append('nuts_code')
        
        # Then: common columns (geo, TIME_PERIOD)
        common_cols = ['geo', 'GEO', 'TIME_PERIOD', 'TIME', 'time', 'year', 'Year']
        for col in common_cols:
            if col in df_cleaned.columns and col not in ordered_cols:
                ordered_cols.append(col)
        
        # Group columns by dataset: for each dataset, group LAST UPDATE, OBS_VALUE, and related parameters
        # Extract dataset IDs from OBS_VALUE columns
        obs_value_cols_clean = [col for col in df_cleaned.columns if col.startswith('OBS_VALUE_')]
        dataset_ids = []
        for col in obs_value_cols_clean:
            dataset_id = col.replace('OBS_VALUE_', '')
            if dataset_id not in dataset_ids:
                dataset_ids.append(dataset_id)
        
        # For each dataset, group its columns together: LAST UPDATE, OBS_VALUE, and parameters
        for dataset_id in sorted(dataset_ids):
            # LAST UPDATE for this dataset
            last_update_col = f'LAST UPDATE_{dataset_id}'
            if last_update_col in df_cleaned.columns:
                ordered_cols.append(last_update_col)
            
            # OBS_VALUE for this dataset
            obs_value_col = f'OBS_VALUE_{dataset_id}'
            if obs_value_col in df_cleaned.columns:
                ordered_cols.append(obs_value_col)
            
            # Related parameters for this dataset (grouped together)
            # For nrg_ind_ren: nrg_bal_category, freq, unit
            # For nrg_bal: nrg_bal, siec, freq, unit
            if dataset_id == 'nrg_ind_ren':
                # nrg_bal_category belongs to nrg_ind_ren
                if 'nrg_bal_category' in df_cleaned.columns and 'nrg_bal_category' not in ordered_cols:
                    ordered_cols.append('nrg_bal_category')
                # freq and unit for this dataset
                for param_col in ['freq', 'unit']:
                    if param_col in df_cleaned.columns and param_col not in ordered_cols:
                        ordered_cols.append(param_col)
            elif dataset_id == 'nrg_bal':
                # nrg_bal, siec belong to nrg_bal
                for param_col in ['nrg_bal', 'siec']:
                    if param_col in df_cleaned.columns and param_col not in ordered_cols:
                        ordered_cols.append(param_col)
                # freq and unit for this dataset (if not already added from first dataset)
                for param_col in ['freq', 'unit']:
                    if param_col in df_cleaned.columns and param_col not in ordered_cols:
                        ordered_cols.append(param_col)
        
        # Finally: all other columns that weren't grouped
        remaining_cols = [col for col in df_cleaned.columns if col not in ordered_cols]
        # Remove _source_dataset if it exists
        if '_source_dataset' in remaining_cols:
            remaining_cols.remove('_source_dataset')
        ordered_cols.extend(sorted(remaining_cols))
        
        # Reorder dataframe columns
        df_cleaned = df_cleaned[ordered_cols]
        
        # Remove _source_dataset column if it still exists
        if '_source_dataset' in df_cleaned.columns:
            df_cleaned = df_cleaned.drop(columns=['_source_dataset'])
        print(f"Reordered columns: {list(df_cleaned.columns)[:5]}... (total: {len(df_cleaned.columns)})")
        
        # Store cleaned dataset for preview
        set_cleaned_dataset(df_cleaned)
        print(f"Stored cleaned dataset for preview")
        
        # Get quality report
        quality_report = get_data_quality_report(df_cleaned)
        quality_report = convert_to_native(quality_report)
        
        # Combine statistics and convert numpy/pandas types to native Python types
        statistics = {}
        for key, value in {**clean_stats, **nuts_stats}.items():
            # Special handling for failed_values list (already strings, but ensure it's a list)
            if key == "nuts_codes_failed_values" and isinstance(value, list):
                statistics[key] = [str(v) for v in value]  # Ensure all are strings
            else:
                statistics[key] = convert_to_native(value)
        
        return jsonify({
            "dataset_id": current_dataset,
            "status": "cleaned",
            "rows_before": int(len(df)),
            "rows_after": int(len(df_cleaned)),
            "columns": list(df_cleaned.columns),
            "quality_report": quality_report,
            "statistics": statistics,
            "message": "Dataset cleaned and organized successfully"
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in clean_dataset: {error_details}")
        return jsonify(error=str(e), details=error_details), 500

