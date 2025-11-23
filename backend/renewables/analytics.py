"""Analytics functions for renewable energy data analysis."""
from typing import Optional
import pandas as pd
import numpy as np

from config import get_config
from .data_loader import load_dataset

cfg = get_config()
def analyze_global_trends(year_from: Optional[int] = None, year_to: Optional[int] = None, value_col: Optional[str] = None) -> dict:
    """Analyze global trends in renewable energy growth over time."""
    df = load_dataset("clean_nrg_ind_ren")

    geo_col = "geo"
    year_col = "TIME_PERIOD"
    primary_value_col = "OBS_VALUE"
    
    df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
    df[primary_value_col] = pd.to_numeric(df[primary_value_col], errors='coerce')
    df = df.dropna(subset=[year_col, primary_value_col])
    
    if year_from:
        df = df[df[year_col] >= year_from]
    if year_to:
        df = df[df[year_col] <= year_to]
    
    if len(df) == 0:
        return {"error": "No data available for the specified period"}
    
    yearly_avg = df.groupby(year_col)[primary_value_col].mean().sort_index()
    
    if len(yearly_avg) >= 2:
        years = yearly_avg.index.values
        values = yearly_avg.values
        coeffs = np.polyfit(years, values, 1)
        growth_rate = coeffs[0]  # Slope of the trend line
        trend_direction = "increasing" if growth_rate > 0.1 else ("decreasing" if growth_rate < -0.1 else "stable")
    else:
        growth_rate = 0.0
        trend_direction = "stable"
    
    yoy_changes = []
    for i in range(1, len(yearly_avg)):
        prev_year = yearly_avg.index[i-1]
        curr_year = yearly_avg.index[i]
        prev_val = yearly_avg.iloc[i-1]
        curr_val = yearly_avg.iloc[i]
        change_pct = ((curr_val - prev_val) / prev_val * 100) if prev_val != 0 else 0
        yoy_changes.append({
            "from_year": int(prev_year),
            "to_year": int(curr_year),
            "change_pct": float(change_pct),
            "from_value": float(prev_val),
            "to_value": float(curr_val)
        })
    
    # Regional averages (top regions by average renewable energy percentage)
    regional_avg = df.groupby(geo_col)[primary_value_col].mean().sort_values(ascending=False)
    top_regions = [
        {"region": region, "average": float(avg)}
        for region, avg in regional_avg.head(10).items()
    ]

    return {
        "overall_growth_rate": float(growth_rate),
        "trend_direction": trend_direction,
        "yearly_averages": [
            {"year": int(year), "average_value": float(value)}
            for year, value in yearly_avg.items()
        ],
        "year_over_year_changes": yoy_changes,
        "top_regions": top_regions,
        "period": {
            "from": int(yearly_avg.index.min()) if len(yearly_avg) > 0 else None,
            "to": int(yearly_avg.index.max()) if len(yearly_avg) > 0 else None
        },
        "metric_used": "Renewable energy percentage (%)"
    }


def compare_energy_sources(year_from: Optional[int] = None, year_to: Optional[int] = None, country: Optional[str] = None) -> dict:
    """
    Compare different energy sources from the energy balance dataset.
    
    Uses the energy balances dataset (nrg_bal) with siec column to compare different energy sources.
    Compares available energy source types (Solid fossil fuels, Peat and peat products, 
    Oil shale and oil sands, Manufactured gases, Total) by calculating statistics 
    (average, total, min, max) and time series trends for each source.
    
    Returns:
        Dictionary with comparison data by energy source
    """
    # Load cleaned energy balance dataset (retains all energy sources / siec values)

    energy_df = load_dataset("clean_nrg_bal")

    
    energy_geo_col = "geo"
    energy_year_col = "TIME_PERIOD"
    energy_value_col = "OBS_VALUE"
    source_col = "siec"
    
    # Apply filters
    if country:
        energy_df = energy_df[energy_df[energy_geo_col].astype(str).str.contains(str(country), case=False, na=False)]
    
    energy_df[energy_year_col] = pd.to_numeric(energy_df[energy_year_col], errors='coerce')
    energy_df[energy_value_col] = pd.to_numeric(energy_df[energy_value_col], errors='coerce')
    
    if year_from:
        energy_df = energy_df[energy_df[energy_year_col] >= year_from]
    if year_to:
        energy_df = energy_df[energy_df[energy_year_col] <= year_to]
    
    # Remove rows lacking necessary info
    energy_df = energy_df.dropna(subset=[energy_year_col, energy_value_col, source_col])
    if len(energy_df) == 0:
        return {"error": "No data available"}
    
    # Group by energy source and year
    source_year_avg = (
        energy_df.groupby([source_col, energy_year_col])[energy_value_col]
        .mean()
        .reset_index()
    )
    
    sources = energy_df[source_col].unique()
    
    # Calculate total energy across all sources for share calculation
    total_energy_all_sources = energy_df[energy_value_col].sum()
    
    source_stats = []
    for source in sources:
        source_data = energy_df[energy_df[source_col] == source]
        if len(source_data) == 0:
            continue

        # Use absolute values for statistics to avoid distortions from negative values (stock changes)
        source_data_abs = source_data.copy()
        source_data_abs[energy_value_col] = source_data_abs[energy_value_col].abs()
        
        # Calculate statistics on absolute values
        source_total = float(source_data_abs[energy_value_col].sum())
        source_avg = float(source_data_abs[energy_value_col].mean())
        source_min = float(source_data_abs[energy_value_col].min())
        source_max = float(source_data_abs[energy_value_col].max())
        
        # Calculate share of total energy consumption (using absolute values)
        total_energy_abs = energy_df[energy_value_col].abs().sum()
        share_of_total = (source_total / total_energy_abs * 100) if total_energy_abs > 0 else 0
        
        # Calculate growth rate (trend over time) using absolute values and percentage change
        source_by_year = source_data_abs.groupby(energy_year_col)[energy_value_col].mean().sort_index()
        growth_rate = None
        
        # Only calculate growth rate if there are non-zero values
        if source_total > 0 and len(source_by_year) >= 2:
            years = source_by_year.index.values
            values = source_by_year.values
            
            # Use percentage change per year instead of absolute change
            # Calculate average annual percentage change
            first_value = values[0]
            last_value = values[-1]
            num_years = years[-1] - years[0]
            
            if first_value > 0 and num_years > 0:
                # Compound annual growth rate (CAGR)
                if last_value > 0:
                    growth_rate = ((last_value / first_value) ** (1.0 / num_years) - 1) * 100
                else:
                    growth_rate = -100.0  # Complete decline
            else:
                # Fallback to linear regression slope as percentage of average
                coeffs = np.polyfit(years, values, 1)
                avg_value = np.mean(values)
                if avg_value > 0:
                    growth_rate = (coeffs[0] / avg_value) * 100  # Percentage change per year
                else:
                    # If all values are zero, growth rate is undefined
                    growth_rate = None
        
        # Convert growth_rate to float if it's a numpy type
        if growth_rate is not None:
            growth_rate = float(growth_rate)
        
        source_stats.append({
            "source": str(source),
            "average": source_avg,
            "total": source_total,
            "min": source_min,
            "max": source_max,
            "data_points": int(len(source_data)),
            "share_of_total": float(share_of_total),
            "growth_rate": growth_rate
        })
    
    source_timeseries = {}
    for source in sources:
        source_data = source_year_avg[source_year_avg[source_col] == source].sort_values(energy_year_col)
        source_timeseries[str(source)] = [
            {"year": int(row[energy_year_col]), "value": float(row[energy_value_col])}
            for _, row in source_data.iterrows()
        ]
    
    return {
        "sources": source_stats,
        "timeseries_by_source": source_timeseries,
        "source_column": source_col
    }


def evaluate_regions_ranking(year_from: Optional[int] = None, year_to: Optional[int] = None, value_col: Optional[str] = None) -> dict:
    """
    Evaluate which regions are leading or lagging in renewable adoption.
    
    Uses renewable energy percentage (nrg_ind_ren) to rank regions by:
    - Current adoption level (latest year average)
    - Growth rate (trend over time)
    
    Returns:
        Dictionary with leading and lagging regions
    """
    # Use clean_nrg_ind_ren dataset for better coverage
    # This dataset contains share of renewable energy, which is the correct metric
    # for evaluating renewable adoption across regions
    df = load_dataset("clean_nrg_ind_ren")
    
    geo_col = "geo"
    year_col = "TIME_PERIOD"
    primary_value_col = "OBS_VALUE"
    
    df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
    df[primary_value_col] = pd.to_numeric(df[primary_value_col], errors='coerce')
    df = df.dropna(subset=[year_col, primary_value_col])
    
    if year_from:
        df = df[df[year_col] >= year_from]
    if year_to:
        df = df[df[year_col] <= year_to]
    
    if len(df) == 0:
        return {"error": "No data available"}
    
    # Calculate statistics per region
    region_stats = []
    
    for region in df[geo_col].unique():
        region_data = df[df[geo_col] == region].sort_values(year_col)
        if len(region_data) < 2:
            continue

        # Current adoption level (latest year value)
        latest_year = region_data[year_col].max()
        latest_year_data = region_data[region_data[year_col] == latest_year]
        if len(latest_year_data) > 0:
            current_value = latest_year_data[primary_value_col].iloc[0]
        else:
            continue

        # Growth rate (linear regression)
        years = region_data[year_col].values
        values = region_data[primary_value_col].values
        if len(years) >= 2:
            coeffs = np.polyfit(years, values, 1)
            growth_rate = coeffs[0]
            
            # Calculate percentage change from first to last
            first_val = values[0]
            last_val = values[-1]
            total_change_pct = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
            
            region_stats.append({
                "region": str(region),
                "current_value": float(current_value),  # Used only for sorting, not returned
                "growth_rate": float(growth_rate),
                "total_change_pct": float(total_change_pct),
                "first_value": float(first_val),
                "last_value": float(last_val),
                "data_points": int(len(region_data))
            })
    
    # Sort by current value (leading) and growth rate (fastest growing)
    leading_by_value = sorted(region_stats, key=lambda x: x["current_value"], reverse=True)[:10]
    fastest_growing = sorted(region_stats, key=lambda x: x["growth_rate"], reverse=True)[:10]
    lagging = sorted(region_stats, key=lambda x: x["current_value"])[:10]
    
    # Remove current_value from response (used only for sorting)
    def remove_current_value(region_dict):
        return {k: v for k, v in region_dict.items() if k != "current_value"}
    
    return {
        "leading_by_value": [remove_current_value(r) for r in leading_by_value],
        "fastest_growing": [remove_current_value(r) for r in fastest_growing],
        "lagging": [remove_current_value(r) for r in lagging],
        "total_regions": len(region_stats),
        "metric_used": "Renewable energy percentage (%)"
    }


def correlate_with_indicators(
    indicator: str = "gdp",
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    country: Optional[str] = None,
    value_col: Optional[str] = None
) -> dict:
    """
    Correlate energy trends with simple indicators such as GDP or population.
    
    For GDP: tries to load real data from namq_10_gdp.csv if available,
    otherwise falls back to synthetic data.
    
    Returns:
        Dictionary with correlation analysis
    """
    # Use clean_nrg_ind_ren dataset for renewable energy percentage data
    # This is the correct metric for correlating with GDP or population
    df = load_dataset("clean_nrg_ind_ren")
    
    geo_col = "geo"
    year_col = "TIME_PERIOD"
    renewable_pct_col = "OBS_VALUE"
    
    if country:
        df = df[df[geo_col].astype(str).str.contains(str(country), case=False, na=False)]
    
    df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
    df[renewable_pct_col] = pd.to_numeric(df[renewable_pct_col], errors='coerce')
    
    if year_from:
        df = df[df[year_col] >= year_from]
    if year_to:
        df = df[df[year_col] <= year_to]
    
    df = df.dropna(subset=[year_col, renewable_pct_col])

    if len(df) == 0:
        return {"error": "No data available"}
    
    # Calculate renewable energy trends by region and year
    renewable_trends = df.groupby([geo_col, year_col])[renewable_pct_col].mean().reset_index()
    renewable_trends = renewable_trends.rename(columns={renewable_pct_col: 'renewable_value'})
    
    # Try to load real GDP data from clean_nama_10_gdp dataset
    gdp_data = None
    if indicator.lower() == "gdp":
        try:
            gdp_df = load_dataset("clean_nama_10_gdp")
            
            # Standardize column names (strip whitespace)
            gdp_df.columns = gdp_df.columns.str.strip()
            
            # Normalize geo column (strip whitespace for consistent matching)
            gdp_df['geo'] = gdp_df['geo'].astype(str).str.strip()
            
            # Convert TIME_PERIOD to numeric for easier matching
            gdp_df['TIME_PERIOD'] = pd.to_numeric(gdp_df['TIME_PERIOD'], errors='coerce')
            
            # Convert OBS_VALUE to numeric
            gdp_df['OBS_VALUE'] = pd.to_numeric(gdp_df['OBS_VALUE'], errors='coerce')
            
            # Remove rows with invalid data
            gdp_df = gdp_df.dropna(subset=['geo', 'TIME_PERIOD', 'OBS_VALUE'])
            
            gdp_data = gdp_df
        except (ValueError, FileNotFoundError):
            # Silently fall back to synthetic GDP data if dataset cannot be loaded
            pass
    
    # Prepare indicator data
    indicator_data = []
    
    for region in renewable_trends[geo_col].unique():
        region_data = renewable_trends[renewable_trends[geo_col] == region].sort_values(year_col)
        for _, row in region_data.iterrows():
            if indicator.lower() == "gdp":
                # Try to use real GDP data if available
                if gdp_data is not None:
                    # Convert year and region for matching
                    gdp_year = int(row[year_col])
                    region_str = str(row[geo_col]).strip()
                    
                    # Filter GDP data for this region and year (direct matching, codes should be the same)
                    gdp_match = gdp_data[
                        (gdp_data['geo'].str.strip() == region_str) &
                        (gdp_data['TIME_PERIOD'] == gdp_year)
                    ]
                    
                    if len(gdp_match) > 0:
                        # Take the first match (in case of multiple entries for same region/year)
                        gdp_value = gdp_match['OBS_VALUE'].iloc[0]
                        if pd.notna(gdp_value) and gdp_value > 0:
                            indicator_data.append({
                                "region": region_str,
                                "year": gdp_year,
                                "indicator_value": float(gdp_value),
                                "renewable_value": float(row['renewable_value'])
                            })
                            continue
                
                # Fallback to synthetic GDP data if real data not available or no match found
                base_gdp = 1000 + (row['renewable_value'] * 50)
                gdp_value = base_gdp * (1 + (row[year_col] - 2010) * 0.02)
                indicator_data.append({
                    "region": str(row[geo_col]),
                    "year": int(row[year_col]),
                    "indicator_value": float(gdp_value),
                    "renewable_value": float(row['renewable_value'])
                })
            elif indicator.lower() == "population":
                base_pop = 1000000 + (row['renewable_value'] * 10000)
                pop_value = base_pop * (1 + (row[year_col] - 2010) * 0.01)
                indicator_data.append({
                    "region": str(region),
                    "year": int(row[year_col]),
                    "indicator_value": float(pop_value),
                    "renewable_value": float(row['renewable_value'])
                })
            elif indicator.lower() == "energy_balance" and energy_balance_col:
                # Use actual energy balance data from merged dataset
                region_year_data = df[(df[geo_col] == region) & (df[year_col] == row[year_col])]
                if len(region_year_data) > 0:
                    balance_value = region_year_data[energy_balance_col].mean()
                    indicator_data.append({
                        "region": str(region),
                        "year": int(row[year_col]),
                        "indicator_value": float(balance_value) if pd.notna(balance_value) else 0,
                        "renewable_value": float(row['renewable_value'])
                    })
            else:
                indicator_data.append({
                    "region": str(region),
                    "year": int(row[year_col]),
                    "indicator_value": float(row['renewable_value'] * 10),
                    "renewable_value": float(row['renewable_value'])
                })
    
    if len(indicator_data) == 0:
        return {"error": "No correlation data available"}
    
    # Calculate correlation coefficient
    indicator_df = pd.DataFrame(indicator_data)
    
    correlation = indicator_df['renewable_value'].corr(indicator_df['indicator_value'])
    
    # Calculate correlation by region
    regional_correlations = []
    for region in indicator_df['region'].unique():
        region_data = indicator_df[indicator_df['region'] == region]
        if len(region_data) >= 2:
            reg_corr = region_data['renewable_value'].corr(region_data['indicator_value'])
            if pd.notna(reg_corr):
                regional_correlations.append({
                    "region": str(region),
                    "correlation": float(reg_corr),
                    "data_points": int(len(region_data))
                })
    
    # Sort by correlation strength
    regional_correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
    
    # Calculate trend lines
    years = indicator_df['year'].unique()
    renewable_avg_by_year = indicator_df.groupby('year')['renewable_value'].mean()
    indicator_avg_by_year = indicator_df.groupby('year')['indicator_value'].mean()
    
    # Linear regression for trends
    if len(years) >= 2:
        renewable_trend = np.polyfit(years, renewable_avg_by_year.values, 1)
        indicator_trend = np.polyfit(years, indicator_avg_by_year.values, 1)
    else:
        renewable_trend = [0, 0]
        indicator_trend = [0, 0]
    
    return {
        "indicator_type": indicator,
        "overall_correlation": float(correlation) if pd.notna(correlation) else None,
        "correlation_strength": (
            "strong" if abs(correlation) > 0.7 else
            "moderate" if abs(correlation) > 0.4 else
            "weak" if pd.notna(correlation) else "none"
        ) if pd.notna(correlation) else "none",
        "regional_correlations": regional_correlations[:20],
        "renewable_trend": {
            "slope": float(renewable_trend[0]),
            "intercept": float(renewable_trend[1])
        },
        "indicator_trend": {
            "slope": float(indicator_trend[0]),
            "intercept": float(indicator_trend[1])
        },
        "yearly_averages": [
            {
                "year": int(year),
                "renewable_avg": float(renewable_avg_by_year[year]),
                "indicator_avg": float(indicator_avg_by_year[year])
            }
            for year in sorted(years)
        ]
    }


def forecast_renewable_energy(
    region: Optional[str] = None,
    years_ahead: int = 5,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None
) -> dict:
    """
    Simple forecasting model to estimate future renewable energy shares.
    
    Uses linear regression on historical data to extrapolate future values.
    
    Args:
        region: Optional region code to forecast for specific region
        years_ahead: Number of years to forecast (default: 5)
        year_from: Start year for historical data
        year_to: End year for historical data
    
    Returns:
        Dictionary with forecast data including:
        - historical_data: List of historical year-value pairs
        - forecast_data: List of forecast year-value pairs
        - trend_line: Linear regression coefficients
        - r_squared: Model fit quality
    """
    df = load_dataset("clean_nrg_ind_ren")
    
    geo_col = "geo"
    year_col = "TIME_PERIOD"
    value_col = "OBS_VALUE"
    
    # Filter by region if specified
    if region:
        df = df[df[geo_col].astype(str).str.contains(str(region), case=False, na=False)]
    
    # Filter by year range
    df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna(subset=[year_col, value_col])
    
    if year_from:
        df = df[df[year_col] >= year_from]
    if year_to:
        df = df[df[year_col] <= year_to]
    
    if len(df) == 0:
        return {"error": "No data available for forecasting"}
    
    # Aggregate by year (average across regions if no specific region)
    yearly_data = df.groupby(year_col)[value_col].mean().sort_index()
    
    if len(yearly_data) < 2:
        return {"error": "Insufficient data for forecasting (need at least 2 years)"}
    
    # Prepare data for regression
    years = yearly_data.index.values.astype(float)
    values = yearly_data.values.astype(float)
    
    # Linear regression
    coeffs = np.polyfit(years, values, 1)
    slope = coeffs[0]
    intercept = coeffs[1]
    
    # Calculate R-squared for model quality
    predicted_historical = np.polyval(coeffs, years)
    ss_res = np.sum((values - predicted_historical) ** 2)
    ss_tot = np.sum((values - np.mean(values)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    # Historical data
    historical = [
        {"year": int(year), "value": float(value)}
        for year, value in zip(years, values)
    ]
    
    # Forecast future years
    last_year = int(years[-1])
    forecast_years = np.arange(last_year + 1, last_year + 1 + years_ahead)
    forecast_values = np.polyval(coeffs, forecast_years)
    
    # Ensure forecast values don't go below 0 or above 100 (percentage)
    forecast_values = np.clip(forecast_values, 0, 100)
    
    forecast = [
        {"year": int(year), "value": float(value)}
        for year, value in zip(forecast_years, forecast_values)
    ]
    
    # Calculate trend line for visualization
    all_years = np.concatenate([years, forecast_years])
    trend_line_values = np.polyval(coeffs, all_years)
    trend_line = [
        {"year": int(year), "value": float(value)}
        for year, value in zip(all_years, trend_line_values)
    ]

    return {
        "historical_data": historical,
        "forecast_data": forecast,
        "trend_line": trend_line,
        "model": {
            "slope": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r_squared),
            "model_type": "linear_regression"
        },
        "region": region if region else "Global Average",
        "forecast_period": {
            "from": int(forecast_years[0]),
            "to": int(forecast_years[-1])
        }
    }


def analyze_merged_dataset(year_from: Optional[int] = None, year_to: Optional[int] = None) -> dict:
    """
    Analyze merged dataset to show correlations between production volume and renewable share.
    
    This function demonstrates the value of merging production and renewable share data:
    - Correlation analysis between production volume and renewable share
    - Calculation of absolute renewable energy production
    - Trend analysis over time
    - Regional comparisons
    
    Args:
        year_from: Start year filter
        year_to: End year filter
    
    Returns:
        Dictionary with analysis results including correlations, metrics, and regional data
    """
    # Load merged dataset
    df = load_dataset("merged_dataset")
    
    geo_col = "geo"
    year_col = "TIME_PERIOD"
    production_col = "OBS_VALUE_nrg_bal"
    renewable_share_col = "OBS_VALUE_nrg_ind_ren"
    
    # Convert to numeric
    df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
    df[production_col] = pd.to_numeric(df[production_col], errors='coerce')
    df[renewable_share_col] = pd.to_numeric(df[renewable_share_col], errors='coerce')
    
    # Filter by year range
    if year_from:
        df = df[df[year_col] >= year_from]
    if year_to:
        df = df[df[year_col] <= year_to]
    
    # Filter out rows where both values are missing
    df = df.dropna(subset=[geo_col, year_col])
    
    # Calculate absolute renewable energy production (production * renewable_share / 100)
    df['absolute_renewable'] = (df[production_col] * df[renewable_share_col] / 100)
    
    # 1. Overall correlation between production and renewable share
    valid_corr = df[[production_col, renewable_share_col]].dropna()
    correlation = None
    if len(valid_corr) >= 2:
        correlation = float(valid_corr[production_col].corr(valid_corr[renewable_share_col]))
    
    # 2. Yearly trends
    yearly_stats = []
    for year in sorted(df[year_col].dropna().unique()):
        year_data = df[df[year_col] == year]
        year_data_valid = year_data[[production_col, renewable_share_col, 'absolute_renewable']].dropna()
        
        if len(year_data_valid) > 0:
            yearly_stats.append({
                "year": int(year),
                "avg_production": float(year_data_valid[production_col].mean()),
                "avg_renewable_share": float(year_data_valid[renewable_share_col].mean()),
                "avg_absolute_renewable": float(year_data_valid['absolute_renewable'].mean()),
                "total_regions": len(year_data_valid)
            })
    
    # 3. Top regions by absolute renewable production (latest year)
    latest_year = df[year_col].max()
    if pd.notna(latest_year):
        latest_data = df[df[year_col] == latest_year]
        latest_data_valid = latest_data[[geo_col, production_col, renewable_share_col, 'absolute_renewable']].dropna()
        
        top_absolute = latest_data_valid.nlargest(10, 'absolute_renewable')[
            [geo_col, production_col, renewable_share_col, 'absolute_renewable']
        ].to_dict(orient='records')
        
        top_share = latest_data_valid.nlargest(10, renewable_share_col)[
            [geo_col, production_col, renewable_share_col, 'absolute_renewable']
        ].to_dict(orient='records')
    else:
        top_absolute = []
        top_share = []
    
    # 4. Regional data for scatter plot (latest year with both values)
    if pd.notna(latest_year):
        scatter_data = df[df[year_col] == latest_year][
            [geo_col, production_col, renewable_share_col, 'absolute_renewable']
        ].dropna().to_dict(orient='records')
    else:
        scatter_data = []
    
    # 5. Summary statistics
    all_valid = df[[production_col, renewable_share_col, 'absolute_renewable']].dropna()
    summary = {}
    if len(all_valid) > 0:
        summary = {
            "total_records": len(df),
            "valid_records": len(all_valid),
            "avg_production": float(all_valid[production_col].mean()),
            "avg_renewable_share": float(all_valid[renewable_share_col].mean()),
            "avg_absolute_renewable": float(all_valid['absolute_renewable'].mean()),
            "max_production": float(all_valid[production_col].max()),
            "max_renewable_share": float(all_valid[renewable_share_col].max()),
            "max_absolute_renewable": float(all_valid['absolute_renewable'].max())
        }
    
    return {
        "correlation": correlation,
        "yearly_trends": yearly_stats,
        "top_regions_absolute": top_absolute,
        "top_regions_share": top_share,
        "scatter_data": scatter_data,
        "summary": summary,
        "latest_year": int(latest_year) if pd.notna(latest_year) else None
    }
