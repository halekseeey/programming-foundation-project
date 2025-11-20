"""
Analytics routes for Step 3: Data Analysis.
"""
from flask import Blueprint, jsonify, request
import pandas as pd
import math
import numpy as np

from renewables.analytics import (
    analyze_global_trends,
    compare_energy_sources,
    evaluate_regions_ranking,
    correlate_with_indicators
)
from renewables.visualization import (
    make_yearly_averages_plot,
    make_timeseries_by_source_plot,
    make_yearly_comparison_plot,
    make_sources_by_region_bar_chart,
    make_regional_heatmap,
    make_regional_map,
    make_animated_regional_map,
    make_animated_regional_bar_chart
)

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.get("/api/analysis/global-trends")
def global_trends():
    """
    /api/analysis/global-trends?year_from=2010&year_to=2022&value_col=OBS_VALUE_nrg_ind_ren
    Identify overall trends in renewable energy growth over time.
    """
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    value_col = request.args.get("value_col")
    
    data = analyze_global_trends(year_from=year_from, year_to=year_to, value_col=value_col)
    
    # Generate plotly figure for yearly averages
    if 'yearly_averages' in data and data['yearly_averages']:
        fig = make_yearly_averages_plot(data['yearly_averages'], "Global Renewable Energy Trends")
        data['yearly_averages_plot'] = fig.to_dict()
    
    return jsonify(data)


@analytics_bp.get("/api/analysis/energy-sources")
def energy_sources():
    """
    /api/analysis/energy-sources?year_from=2010&year_to=2022&country=PT
    Compare different energy sources (solar, wind, hydro, biomass).
    """
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    country = request.args.get("country")
    
    data = compare_energy_sources(year_from=year_from, year_to=year_to, country=country)
    
    # Generate plotly figure for time series by source
    if 'timeseries_by_source' in data and data['timeseries_by_source']:
        fig = make_timeseries_by_source_plot(data['timeseries_by_source'], "Energy Sources Time Series")
        data['timeseries_plot'] = fig.to_dict()
    
    # Generate bar chart for sources comparison across regions
    # Load energy balance data directly for region-source breakdown
    from renewables.data_loader import load_dataset
    from config import get_config
    
    cfg = get_config()
    energy_file = cfg.DATA_CLEAN_DIR / "clean_nrg_bal.csv"
    
    if energy_file.exists():
        energy_df = pd.read_csv(energy_file)
        
        # Apply same filters as in compare_energy_sources
        energy_geo_col = "geo"
        energy_year_col = "TIME_PERIOD"
        energy_value_col = "OBS_VALUE"
        source_col = "siec" if "siec" in energy_df.columns else None
        
        if source_col:
            energy_df[energy_year_col] = pd.to_numeric(energy_df[energy_year_col], errors='coerce')
            energy_df[energy_value_col] = pd.to_numeric(energy_df[energy_value_col], errors='coerce')
            energy_df = energy_df.dropna(subset=[energy_geo_col, energy_year_col, energy_value_col, source_col])
            
            if year_from:
                energy_df = energy_df[energy_df[energy_year_col] >= year_from]
            if year_to:
                energy_df = energy_df[energy_df[energy_year_col] <= year_to]
            if country:
                energy_df = energy_df[energy_df[energy_geo_col].astype(str).str.contains(str(country), case=False, na=False)]
            
            # Filter out 'Total' source as it's an aggregation
            energy_df = energy_df[energy_df[source_col] != 'Total']
            
            # Filter out aggregated regions (EU, etc.)
            # Exclude regions containing: union, european, countries, euro area, etc.
            exclude_patterns = ['union', 'european', 'countries', 'euro area', 'eurozone']
            energy_df = energy_df[
                ~energy_df[energy_geo_col].astype(str).str.lower().str.contains('|'.join(exclude_patterns), na=False)
            ]
            
            # Aggregate by region and source
            region_source_df = energy_df.groupby([energy_geo_col, source_col])[energy_value_col].sum().reset_index()
            
            if not region_source_df.empty:
                fig_bar = make_sources_by_region_bar_chart(
                    region_source_df,
                    geo_col=energy_geo_col,
                    source_col=source_col,
                    value_col=energy_value_col,
                    title="Energy Sources Comparison Across Regions"
                )
                data['bar_chart_plot'] = fig_bar.to_dict()
    
    return jsonify(data)


@analytics_bp.get("/api/analysis/regions-ranking")
def regions_ranking():
    """
    /api/analysis/regions-ranking?year_from=2010&year_to=2022&value_col=OBS_VALUE_nrg_ind_ren
    Evaluate which regions are leading or lagging in renewable adoption.
    """
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    value_col = request.args.get("value_col")
    
    data = evaluate_regions_ranking(year_from=year_from, year_to=year_to, value_col=value_col)
    return jsonify(data)


@analytics_bp.get("/api/analysis/correlation")
def correlation():
    """
    /api/analysis/correlation?indicator=gdp&year_from=2010&year_to=2022&country=PT&value_col=OBS_VALUE_nrg_ind_ren
    Correlate energy trends with simple indicators such as GDP or population (optional).
    """
    indicator = request.args.get("indicator", "gdp")
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    country = request.args.get("country")
    value_col = request.args.get("value_col")
    
    data = correlate_with_indicators(
        indicator=indicator,
        year_from=year_from,
        year_to=year_to,
        country=country,
        value_col=value_col
    )
    
    # Generate plotly figure for yearly averages comparison
    if 'yearly_averages' in data and data['yearly_averages']:
        fig = make_yearly_comparison_plot(
            data['yearly_averages'],
            data.get('indicator_type', 'indicator'),
            "Renewable Energy vs " + data.get('indicator_type', 'Indicator').upper()
        )
        data['yearly_averages_plot'] = fig.to_dict()
    
    return jsonify(data)


@analytics_bp.get("/api/analysis/visualizations/bar-chart")
def bar_chart_sources():
    """
    /api/analysis/visualizations/bar-chart?year_from=2010&year_to=2022
    Bar chart comparing renewable energy sources across regions.
    """
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    
    data = compare_energy_sources(year_from=year_from, year_to=year_to)
    
    if 'sources' in data and data['sources']:
        fig = make_sources_by_region_bar_chart(
            data['sources'],
            title="Energy Sources Comparison Across Regions"
        )
        return jsonify({"plot": fig.to_dict()})
    
    return jsonify({"error": "No data available"})


def clean_plotly_dict_for_json(obj):
    """
    Recursively clean Plotly figure dict, replacing NaN, Inf, and numpy types with JSON-safe values.
    """
    if isinstance(obj, dict):
        return {key: clean_plotly_dict_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_plotly_dict_for_json(item) for item in obj]
    elif isinstance(obj, (np.floating, np.integer)):
        if pd.isna(obj) or math.isnan(obj):
            return None
        if math.isinf(obj):
            return None
        return float(obj) if isinstance(obj, np.floating) else int(obj)
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif pd.isna(obj):
        return None
    else:
        return obj


@analytics_bp.get("/api/analysis/visualizations/heatmap")
def heatmap_regional():
    """
    /api/analysis/visualizations/heatmap?year_from=2010&year_to=2022
    Heatmap visualizing regional energy intensity over time.
    """
    from renewables.data_loader import load_dataset
    
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    
    df = load_dataset("merged_dataset")
    
    geo_col = "geo"
    year_col = "TIME_PERIOD"
    value_col = None
    
    # Find renewable energy percentage column
    obs_value_cols = [col for col in df.columns if col.startswith('OBS_VALUE_')]
    for col in obs_value_cols:
        if 'nrg_ind_ren' in col or 'ind_ren' in col.lower():
            value_col = col
            break
    
    if not value_col:
        return jsonify({"error": "Renewable energy column not found"})
    
    # Filter data
    df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna(subset=[geo_col, year_col, value_col])
    
    if year_from:
        df = df[df[year_col] >= year_from]
    if year_to:
        df = df[df[year_col] <= year_to]
    
    if df.empty:
        return jsonify({"error": "No data available"})
    
    fig = make_regional_heatmap(
        df,
        geo_col,
        year_col,
        value_col,
        "Regional Renewable Energy Intensity Heatmap"
    )
    
    # Convert figure to dict and clean NaN values
    # Use to_json() to ensure frames are included, then parse back to dict
    import json
    fig_json = fig.to_json()
    fig_dict = json.loads(fig_json)
    fig_dict = clean_plotly_dict_for_json(fig_dict)
    
    return jsonify({"plot": fig_dict})


@analytics_bp.get("/api/analysis/visualizations/map")
def map_regional():
    """
    /api/analysis/visualizations/map?year=2023
    Interactive map displaying renewable energy adoption by region.
    """
    from renewables.data_loader import load_dataset
    
    year = request.args.get("year", type=int)
    
    df = load_dataset("merged_dataset")
    
    geo_col = "geo"
    year_col = "TIME_PERIOD"
    value_col = None
    
    # Find renewable energy percentage column
    obs_value_cols = [col for col in df.columns if col.startswith('OBS_VALUE_')]
    for col in obs_value_cols:
        if 'nrg_ind_ren' in col or 'ind_ren' in col.lower():
            value_col = col
            break
    
    if not value_col:
        return jsonify({"error": "Renewable energy column not found"})
    
    # Filter to latest year or specified year
    df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna(subset=[geo_col, year_col, value_col])
    
    if year:
        df = df[df[year_col] == year]
    else:
        # Use latest year
        latest_year = df[year_col].max()
        df = df[df[year_col] == latest_year]
    
    # Get latest value per region
    df_map = df.groupby(geo_col)[value_col].mean().reset_index()
    
    if df_map.empty:
        return jsonify({"error": "No data available"})
    
    fig = make_regional_map(
        df_map,
        geo_col,
        value_col,
        f"Renewable Energy Adoption by Region ({df[year_col].max() if not year else year})"
    )
    
    # Convert figure to dict and clean NaN values
    # Use to_json() to ensure frames are included, then parse back to dict
    import json
    fig_json = fig.to_json()
    fig_dict = json.loads(fig_json)
    fig_dict = clean_plotly_dict_for_json(fig_dict)
    
    return jsonify({"plot": fig_dict})


@analytics_bp.get("/api/analysis/visualizations/animated-map")
def animated_map_regional():
    """
    /api/analysis/visualizations/animated-map?year_from=2010&year_to=2022
    Animated map showing how renewable energy adoption evolves year by year.
    """
    from renewables.data_loader import load_dataset
    
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    
    df = load_dataset("merged_dataset")
    
    geo_col = "geo"
    year_col = "TIME_PERIOD"
    value_col = None
    
    # Find renewable energy percentage column
    obs_value_cols = [col for col in df.columns if col.startswith('OBS_VALUE_')]
    for col in obs_value_cols:
        if 'nrg_ind_ren' in col or 'ind_ren' in col.lower():
            value_col = col
            break
    
    if not value_col:
        return jsonify({"error": "Renewable energy column not found"})
    
    # Filter data
    df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna(subset=[geo_col, year_col, value_col])
    
    if year_from:
        df = df[df[year_col] >= year_from]
    if year_to:
        df = df[df[year_col] <= year_to]
    
    if df.empty:
        return jsonify({"error": "No data available"})
    
    fig = make_animated_regional_map(
        df,
        geo_col,
        year_col,
        value_col,
        "Renewable Energy Adoption Evolution by Region"
    )
    
    # Convert figure to dict and clean NaN values
    # Use to_json() to ensure frames are included, then parse back to dict
    import json
    fig_json = fig.to_json()
    fig_dict = json.loads(fig_json)
    fig_dict = clean_plotly_dict_for_json(fig_dict)
    
    return jsonify({"plot": fig_dict})


@analytics_bp.get("/api/analysis/visualizations/animated-bar")
def animated_bar_regional():
    """
    /api/analysis/visualizations/animated-bar?year_from=2010&year_to=2022
    Animated bar chart showing how renewable energy share changes year by year across regions.
    """
    from renewables.data_loader import load_dataset
    
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    
    df = load_dataset("merged_dataset")
    
    geo_col = "geo"
    year_col = "TIME_PERIOD"
    value_col = None
    
    # Find renewable energy percentage column
    obs_value_cols = [col for col in df.columns if col.startswith('OBS_VALUE_')]
    for col in obs_value_cols:
        if 'nrg_ind_ren' in col or 'ind_ren' in col.lower():
            value_col = col
            break
    
    if not value_col:
        return jsonify({"error": "Renewable energy column not found"})
    
    # Filter data
    df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna(subset=[geo_col, year_col, value_col])
    
    if year_from:
        df = df[df[year_col] >= year_from]
    if year_to:
        df = df[df[year_col] <= year_to]
    
    if df.empty:
        return jsonify({"error": "No data available"})
    
    fig = make_animated_regional_bar_chart(
        df,
        geo_col,
        year_col,
        value_col,
        "Renewable Energy Share Evolution by Region"
    )
    
    # Convert figure to dict and clean NaN values
    # Use to_json() to ensure frames are included, then parse back to dict
    import json
    fig_json = fig.to_json()
    fig_dict = json.loads(fig_json)
    fig_dict = clean_plotly_dict_for_json(fig_dict)
    
    return jsonify({"plot": fig_dict})

