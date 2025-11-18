"""
Data processing routes (cleaning, NUTS codes, summaries, normalization).
"""
from flask import Blueprint, jsonify, request

from renewables.data_loader import filter_renewables
from renewables.data_processing import (
    clean_and_normalize_timeseries,
    add_nuts_codes,
    create_summary_table,
    get_data_quality_report,
    normalize_timeseries_by_region,
    get_nuts_code,
    build_nuts_mapping_from_data
)

data_processing_bp = Blueprint('data_processing', __name__)


def _find_columns(df):
    """Helper to find geo, year, and value columns."""
    geo_col = "geo" if "geo" in df.columns else df.columns[0]
    year_col = None
    value_col = None
    
    for col_name in ["year", "Year", "TIME", "time", "TIME_PERIOD"]:
        if col_name in df.columns:
            year_col = col_name
            break
    
    # Check for merged datasets first (OBS_VALUE_* columns)
    obs_value_cols = [col for col in df.columns if col.startswith('OBS_VALUE_')]
    if obs_value_cols:
        # If multiple OBS_VALUE columns exist (merged datasets), use the first one
        value_col = obs_value_cols[0]
    else:
        # Single dataset - look for standard OBS_VALUE column
        for col_name in ["value", "Value", "VALUE", "OBS_VALUE"]:
            if col_name in df.columns:
                value_col = col_name
                break
    
    return geo_col, year_col, value_col


@data_processing_bp.get("/api/data/clean")
def clean_data():
    """Clean and normalize time-series data."""
    country = request.args.get("country")
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    strategy = request.args.get("strategy", "interpolate")
    
    df = filter_renewables(country=country, year_from=year_from, year_to=year_to)
    geo_col, year_col, value_col = _find_columns(df)
    
    if year_col and value_col:
        df, _ = clean_and_normalize_timeseries(
            df, geo_col=geo_col, year_col=year_col, value_col=value_col,
            missing_strategy=strategy
        )
    
    return jsonify({
        "data": df.to_dict(orient="records"),
        "columns": list(df.columns),
        "rows": len(df)
    })


@data_processing_bp.get("/api/data/nuts")
def get_nuts_mapping():
    """Get NUTS code for a country."""
    country = request.args.get("country")
    if not country:
        return jsonify(error="country is required"), 400
    
    nuts_code = get_nuts_code(country)
    return jsonify({
        "country": country,
        "nuts_code": nuts_code
    })


@data_processing_bp.get("/api/data/add-nuts")
def add_nuts_to_data():
    """Add NUTS codes to filtered data."""
    country = request.args.get("country")
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    
    df = filter_renewables(country=country, year_from=year_from, year_to=year_to)
    geo_col = "geo" if "geo" in df.columns else df.columns[0]
    df, _ = add_nuts_codes(df, geo_col=geo_col, auto_build=True)
    
    return jsonify({
        "data": df.to_dict(orient="records"),
        "columns": list(df.columns),
        "rows": len(df)
    })


@data_processing_bp.get("/api/data/nuts-mapping")
def get_nuts_mapping_from_data():
    """Automatically build NUTS code mapping from data."""
    country = request.args.get("country")
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    
    df = filter_renewables(country=country, year_from=year_from, year_to=year_to)
    geo_col = "geo" if "geo" in df.columns else df.columns[0]
    mapping = build_nuts_mapping_from_data(df, geo_col=geo_col)
    
    return jsonify({
        "mapping": mapping,
        "countries_count": len(mapping)
    })


@data_processing_bp.get("/api/data/summary")
def get_summary_table():
    """Create summary table grouped by specified columns."""
    group_by_param = request.args.get("group_by", "geo")
    agg_param = request.args.get("agg", "mean,min,max,count")
    country = request.args.get("country")
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    
    df = filter_renewables(country=country, year_from=year_from, year_to=year_to)
    geo_col, year_col, value_col = _find_columns(df)
    
    if not value_col:
        return jsonify(error="Value column not found"), 400
    
    # Parse group_by
    group_by = [g.strip() for g in group_by_param.split(",")]
    group_by_mapped = []
    for gb in group_by:
        if gb.lower() in ["geo", "country", "region"]:
            group_by_mapped.append(geo_col)
        elif gb.lower() in ["year", "time", "time_period"]:
            if year_col:
                group_by_mapped.append(year_col)
        else:
            if gb in df.columns:
                group_by_mapped.append(gb)
    
    # Parse aggregation functions
    agg_functions = [a.strip() for a in agg_param.split(",")]
    
    try:
        summary_df = create_summary_table(
            df, group_by=group_by_mapped, value_col=value_col,
            agg_functions=agg_functions
        )
        return jsonify({
            "data": summary_df.to_dict(orient="records"),
            "columns": list(summary_df.columns),
            "rows": len(summary_df)
        })
    except Exception as e:
        return jsonify(error=str(e)), 400


@data_processing_bp.get("/api/data/quality")
def get_quality_report():
    """Get data quality report."""
    country = request.args.get("country")
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    
    df = filter_renewables(country=country, year_from=year_from, year_to=year_to)
    report = get_data_quality_report(df)
    
    return jsonify(report)


@data_processing_bp.get("/api/data/normalize")
def normalize_data():
    """Normalize time-series data by region."""
    country = request.args.get("country")
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    method = request.args.get("method", "min_max")
    
    df = filter_renewables(country=country, year_from=year_from, year_to=year_to)
    geo_col, year_col, value_col = _find_columns(df)
    
    if not value_col:
        return jsonify(error="Value column not found"), 400
    
    df = normalize_timeseries_by_region(
        df, geo_col=geo_col, year_col=year_col, value_col=value_col,
        method=method
    )
    
    return jsonify({
        "data": df.to_dict(orient="records"),
        "columns": list(df.columns),
        "rows": len(df)
    })

