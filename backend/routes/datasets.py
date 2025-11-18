"""
Dataset management routes.
"""
from flask import Blueprint, jsonify, request
import pandas as pd
import math

from config import get_config
from renewables.data_loader import (
    get_current_dataset,
    get_current_datasets,
    load_dataset,
    set_current_dataset,
    set_current_datasets,
    set_cleaned_dataset,
    get_cleaned_dataset
)

datasets_bp = Blueprint('datasets', __name__)


@datasets_bp.get("/api/datasets")
def list_datasets():
    """Get list of available datasets."""
    cfg = get_config()
    datasets = cfg.get_available_datasets()
    return jsonify(datasets=datasets)


@datasets_bp.post("/api/datasets/select")
def select_dataset():
    """
    Select dataset(s) to use for analysis.
    POST body: {"dataset_id": "nrg_ind_ren"} or {"dataset_ids": ["nrg_ind_ren", "nrg_bal"]}
    """
    data = request.get_json() or {}
    
    # Support both single and multiple dataset selection
    dataset_id = data.get("dataset_id")
    dataset_ids = data.get("dataset_ids", [])
    
    # If single dataset_id provided, convert to list
    if dataset_id and not dataset_ids:
        dataset_ids = [dataset_id]
    
    if not dataset_ids:
        return jsonify(error="dataset_id or dataset_ids is required"), 400
    
    # Verify all datasets exist
    cfg = get_config()
    available_datasets = cfg.get_available_datasets()
    available_ids = {d["id"] for d in available_datasets}
    
    invalid_ids = [did for did in dataset_ids if did not in available_ids]
    if invalid_ids:
        return jsonify(error=f"Datasets not found: {invalid_ids}"), 404
    
    # Set current dataset(s)
    if len(dataset_ids) == 1:
        set_current_dataset(dataset_ids[0])
    else:
        set_current_datasets(dataset_ids)
    
    return jsonify({
        "dataset_ids": dataset_ids,
        "current_datasets": get_current_datasets(),
        "message": f"{len(dataset_ids)} dataset(s) selected successfully"
    })


@datasets_bp.get("/api/datasets/preview")
def preview_dataset():
    """Get preview of a dataset (first N rows)."""
    dataset_id = request.args.get("dataset_id")
    rows = request.args.get("rows", type=int, default=10)
    
    if not dataset_id:
        # Use current dataset if no ID provided
        dataset_id = get_current_dataset()
        if not dataset_id:
            return jsonify(error="No dataset selected and dataset_id not provided"), 400
    
    try:
        # Check if cleaned dataset is available
        cleaned_df = get_cleaned_dataset()
        if cleaned_df is not None:
            df = cleaned_df
            print(f"Using cleaned dataset for preview: {len(df)} rows")
        else:
            df = load_dataset(dataset_id)
            print(f"Using original dataset for preview: {len(df)} rows")
        
        # Get preview
        preview_df = df.head(rows)
        
        # Convert to dict first
        preview_records = preview_df.to_dict(orient="records")
        
        # Replace all NaN/NaT/Inf values with None for JSON serialization
        for record in preview_records:
            for key, value in list(record.items()):
                # Check for NaN/NaT using pandas
                if pd.isna(value):
                    record[key] = None
                # Check for float NaN/Inf
                elif isinstance(value, float):
                    if math.isnan(value) or math.isinf(value):
                        record[key] = None
        
        return jsonify({
            "dataset_id": dataset_id,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "preview": preview_records,
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        })
    except Exception as e:
        return jsonify(error=str(e)), 400

