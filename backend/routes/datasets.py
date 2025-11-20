"""
Dataset management routes.
"""
from flask import Blueprint, jsonify, request
import pandas as pd
import math

from config import get_config
from renewables.data_loader import load_dataset

datasets_bp = Blueprint('datasets', __name__)


@datasets_bp.get("/api/datasets")
def list_datasets():
    """Get list of available datasets."""
    cfg = get_config()
    datasets = cfg.get_available_datasets()
    return jsonify(datasets=datasets)


def _get_dataset_preview(dataset_id, limit=10):
    """Helper function to get dataset preview."""
    cfg = get_config()
    available_datasets = cfg.get_available_datasets()
    available_ids = {d["id"] for d in available_datasets}
    
    if not dataset_id:
        dataset_id = next(iter(available_ids), None)
    
    if not dataset_id or dataset_id not in available_ids:
        return None, "Dataset not found"
    
    try:
        df = load_dataset(dataset_id)
        
        # Get preview
        preview_df = df.head(limit)
        
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
        
        return {
            "dataset_id": dataset_id,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "preview": preview_records,
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }, None
    except Exception as e:
        return None, str(e)


@datasets_bp.get("/api/datasets/preview")
def preview_dataset():
    """Get preview of a dataset (first N rows)."""
    dataset_id = request.args.get("dataset_id")
    rows = request.args.get("rows", type=int, default=10)
    
    data, error = _get_dataset_preview(dataset_id, rows)
    
    if error:
        return jsonify(error=error), 404 if error == "Dataset not found" else 400
    
    return jsonify(data)


@datasets_bp.get("/api/datasets/<dataset_id>/preview")
def preview_dataset_by_id(dataset_id):
    """Get preview of a dataset by ID in URL path."""
    limit = request.args.get("limit", type=int, default=10)
    
    data, error = _get_dataset_preview(dataset_id, limit)
    
    if error:
        return jsonify(error=error), 404 if error == "Dataset not found" else 400
    
    return jsonify(data)

