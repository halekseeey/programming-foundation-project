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
    make_animated_regional_map,
    make_animated_regional_bar_chart
)
import plotly.graph_objs as go

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


@analytics_bp.get("/api/filters/regions")
def get_regions():
    """
    Get list of available regions (countries) for filtering.
    """
    from renewables.data_loader import load_dataset
    
    df = load_dataset("merged_dataset")
    geo_col = "geo" if "geo" in df.columns else df.columns[0]
    
    # Filter out aggregated regions
    exclude_patterns = ['union', 'european', 'countries', 'euro area', 'eurozone']
    regions = df[geo_col].astype(str).unique().tolist()
    regions = [
        r for r in regions 
        if not any(pattern in str(r).lower() for pattern in exclude_patterns)
        and r != 'nan' and len(str(r)) < 100
    ]
    regions = sorted(regions)
    
    return jsonify({"regions": regions})


@analytics_bp.get("/api/filters/energy-types")
def get_energy_types():
    """
    Get list of available energy types (sources) for filtering.
    """
    from config import get_config
    
    cfg = get_config()
    energy_file = cfg.DATA_CLEAN_DIR / "clean_nrg_bal.csv"
    
    if not energy_file.exists():
        return jsonify({"energy_types": []})
    
    energy_df = pd.read_csv(energy_file)
    source_col = "siec" if "siec" in energy_df.columns else None
    
    if not source_col:
        return jsonify({"energy_types": []})
    
    # Filter out 'Total' and get unique sources
    energy_types = energy_df[source_col].astype(str).unique().tolist()
    energy_types = [e for e in energy_types if e != 'Total' and e != 'nan']
    energy_types = sorted(energy_types)
    
    return jsonify({"energy_types": energy_types})


@analytics_bp.get("/api/analysis/filtered")
def get_filtered_analysis():
    """
    Get filtered analysis by region and/or energy type.
    /api/analysis/filtered?region=PT&energy_type=Solid fossil fuels
    """
    region = request.args.get("region")
    energy_type = request.args.get("energy_type")
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    
    result = {}
    
    # Get global trends filtered by region
    if region:
        from renewables.analytics import analyze_global_trends
        trends = analyze_global_trends(year_from=year_from, year_to=year_to)
        # Filter regional averages by selected region
        if trends.get("regional_averages"):
            filtered_regional = [
                r for r in trends["regional_averages"] 
                if str(r.get("region", "")).upper() == str(region).upper()
            ]
            trends["regional_averages"] = filtered_regional
        result["global_trends"] = trends
    
    # Get energy sources filtered by region and/or energy type
    if energy_type or region:
        from renewables.analytics import compare_energy_sources
        energy_data = compare_energy_sources(
            year_from=year_from,
            year_to=year_to,
            country=region
        )
        # Filter by energy type if specified
        if energy_type and energy_data.get("sources"):
            filtered_sources = [
                s for s in energy_data["sources"]
                if str(s.get("source", "")).upper() == str(energy_type).upper()
            ]
            energy_data["sources"] = filtered_sources
        result["energy_sources"] = energy_data
    
    # Get regions ranking filtered by region
    if region:
        from renewables.analytics import evaluate_regions_ranking
        ranking = evaluate_regions_ranking(year_from=year_from, year_to=year_to)
        # Filter to show only selected region
        if ranking.get("leading_by_current_value"):
            filtered_leading = [
                r for r in ranking["leading_by_current_value"]
                if str(r.get("region", "")).upper() == str(region).upper()
            ]
            ranking["leading_by_current_value"] = filtered_leading
        result["regions_ranking"] = ranking
    
    return jsonify(result)


@analytics_bp.get("/api/analysis/filtered/visualizations")
def get_filtered_visualizations():
    """
    Get filtered visualizations based on regions (multiple) and/or energy type.
    Works with the large clean_nrg_bal.csv dataset.
    /api/analysis/filtered/visualizations?regions=PT,DE,FR&energy_type=Solid fossil fuels
    """
    from renewables.filtered_analytics import (
        get_yearly_trends_by_regions,
        get_energy_sources_by_regions,
        get_time_series_by_energy_type
    )
    
    # Get regions as comma-separated list
    regions_param = request.args.get("regions", "")
    regions = [r.strip() for r in regions_param.split(",") if r.strip()] if regions_param else []
    
    # Get energy types as comma-separated list
    energy_types_param = request.args.get("energy_types", "")
    energy_types = [e.strip() for e in energy_types_param.split(",") if e.strip()] if energy_types_param else []
    # Backward compatibility: also check for single energy_type
    if not energy_types:
        energy_type_single = request.args.get("energy_type")
        if energy_type_single:
            energy_types = [energy_type_single]
    
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    
    result = {}
    
    # Create yearly trends chart for multiple regions (if regions selected)
    if regions and len(regions) > 0:
        trends_data = get_yearly_trends_by_regions(regions, year_from, year_to)
        
        if "error" not in trends_data:
            # Create multi-line chart for all selected regions
            fig = go.Figure()
            colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#6366f1']
            
            for idx, (region, data) in enumerate(trends_data.items()):
                if data:
                    years = [d['year'] for d in data]
                    values = [d['average_value'] for d in data]
                    fig.add_trace(go.Scatter(
                        x=years,
                        y=values,
                        mode='lines+markers',
                        name=region,
                        line=dict(color=colors[idx % len(colors)], width=2),
                        marker=dict(size=6),
                        hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Value: %{y:.2f} GWh<extra></extra>'
                    ))
            
            if len(fig.data) > 0:
                fig.update_layout(
                    title=f"Yearly Trends Comparison - {', '.join(regions)}",
                    xaxis_title="Year",
                    yaxis_title="Average Energy (GWh)",
                    template="plotly_dark",
                    height=500,
                    hovermode='x unified',
                    legend=dict(
                        x=0.02,
                        y=0.98,
                        bgcolor='rgba(0, 0, 0, 0.5)',
                        bordercolor='rgba(255, 255, 255, 0.2)',
                        borderwidth=1
                    )
                )
                result["yearly_trends_plot"] = clean_plotly_dict_for_json(fig.to_dict())
    
    # Create energy sources distribution chart (if regions selected)
    if regions and len(regions) > 0:
        sources_data = get_energy_sources_by_regions(regions, year_from, year_to)
        
        if "error" not in sources_data:
            # Create grouped bar chart comparing sources across selected regions
            fig = go.Figure()
            colors = ['rgba(56, 189, 248, 0.8)', 'rgba(16, 185, 129, 0.8)', 'rgba(251, 191, 36, 0.8)', 
                      'rgba(239, 68, 68, 0.8)', 'rgba(139, 92, 246, 0.8)', 'rgba(236, 72, 153, 0.8)']
            
            # Get all unique sources across all regions
            all_sources = set()
            for region_data in sources_data.values():
                if "sources" in region_data:
                    all_sources.update([s["source"] for s in region_data["sources"]])
            all_sources = sorted(list(all_sources))
            
            # Add trace for each region
            for idx, region in enumerate(regions):
                if region in sources_data and "sources" in sources_data[region]:
                    region_sources = {s["source"]: s["value"] for s in sources_data[region]["sources"]}
                    values = [region_sources.get(source, 0) for source in all_sources]
                    fig.add_trace(go.Bar(
                        name=region,
                        x=all_sources,
                        y=values,
                        marker=dict(
                            color=colors[idx % len(colors)],
                            line=dict(color='rgba(255, 255, 255, 0.2)', width=1)
                        ),
                        hovertemplate='<b>%{fullData.name}</b><br>Source: %{x}<br>Value: %{y:,.0f} GWh<extra></extra>'
                    ))
            
            if len(fig.data) > 0:
                fig.update_layout(
                    title=f"Energy Sources Distribution - {', '.join(regions)}",
                    xaxis_title="Energy Source",
                    yaxis_title="Energy (GWh)",
                    template="plotly_dark",
                    height=500,
                    xaxis=dict(tickangle=-45),
                    barmode='group',
                    legend=dict(
                        x=1.02,
                        y=1,
                        bgcolor='rgba(0, 0, 0, 0.5)',
                        bordercolor='rgba(255, 255, 255, 0.2)',
                        borderwidth=1
                    )
                )
                result["sources_distribution_plot"] = clean_plotly_dict_for_json(fig.to_dict())
    
    # Create time series by energy types across regions (if energy types selected)
    if energy_types and len(energy_types) > 0:
        # Create combined chart for all selected energy types
        fig = go.Figure()
        colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#6366f1']
        color_idx = 0
        has_data = False
        
        for energy_type in energy_types:
            timeseries_data = get_time_series_by_energy_type(energy_type, regions, year_from, year_to)
            
            if "error" not in timeseries_data:
                # Add trace for each region for this energy type
                for region, data in timeseries_data.items():
                    if data:
                        years = [d['year'] for d in data]
                        values = [d['value'] for d in data]
                        fig.add_trace(go.Scatter(
                            x=years,
                            y=values,
                            mode='lines+markers',
                            name=f"{region} - {energy_type}",
                            line=dict(color=colors[color_idx % len(colors)], width=2),
                            marker=dict(size=6),
                            hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Value: %{y:,.0f} GWh<extra></extra>'
                        ))
                        color_idx += 1
                        has_data = True
        
        if has_data and len(fig.data) > 0:
            fig.update_layout(
                title=f"{', '.join(energy_types)} Trends Across Regions",
                xaxis_title="Year",
                yaxis_title="Energy (GWh)",
                template="plotly_dark",
                height=500,
                hovermode='x unified',
                legend=dict(
                    x=0.02,
                    y=0.98,
                    bgcolor='rgba(0, 0, 0, 0.5)',
                    bordercolor='rgba(255, 255, 255, 0.2)',
                    borderwidth=1
                )
            )
            result["energy_type_timeseries_plot"] = clean_plotly_dict_for_json(fig.to_dict())
    
    if not result:
        return jsonify({"error": "No visualizations available. Please select at least one region or energy type."})
    
    return jsonify(result)

