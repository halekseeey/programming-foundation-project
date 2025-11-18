"""
Analytics routes for Step 3: Data Analysis.
"""
from flask import Blueprint, jsonify, request

from renewables.analytics import (
    analyze_global_trends,
    compare_energy_sources,
    evaluate_regions_ranking,
    correlate_with_indicators
)
from renewables.visualization import (
    make_yearly_averages_plot,
    make_timeseries_by_source_plot,
    make_yearly_comparison_plot
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

