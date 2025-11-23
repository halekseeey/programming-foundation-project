"""
Filtered analytics functions for region and energy type filtering.
Works with the large clean_nrg_bal.csv dataset.
"""
from typing import Optional, List
import pandas as pd
import numpy as np

from config import get_config
from .data_loader import load_dataset

cfg = get_config()


def get_filtered_energy_data(
    regions: Optional[List[str]] = None,
    energy_type: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None
) -> pd.DataFrame:
    """
    Load and filter energy balance data based on selected criteria.
    
    Args:
        regions: List of region codes to filter by
        energy_type: Energy source type to filter by
        year_from: Start year filter
        year_to: End year filter
    
    Returns:
        Filtered DataFrame
    """

    energy_df = load_dataset("clean_nrg_bal")

    
    # Column names
    geo_col = "geo"
    year_col = "TIME_PERIOD"
    value_col = "OBS_VALUE"
    source_col = "siec"
    
    # Convert to numeric
    energy_df[year_col] = pd.to_numeric(energy_df[year_col], errors='coerce')
    energy_df[value_col] = pd.to_numeric(energy_df[value_col], errors='coerce')
    energy_df = energy_df.dropna(subset=[geo_col, year_col, value_col, source_col])
    
    # Apply filters
    if year_from:
        energy_df = energy_df[energy_df[year_col] >= year_from]
    if year_to:
        energy_df = energy_df[energy_df[year_col] <= year_to]
    
    if regions and len(regions) > 0:
        # Filter by multiple regions
        energy_df = energy_df[energy_df[geo_col].astype(str).isin([str(r) for r in regions])]
    
    if energy_type:
        energy_df = energy_df[energy_df[source_col].astype(str).str.contains(str(energy_type), case=False, na=False)]
    
    # Filter out 'Total' source
    energy_df = energy_df[energy_df[source_col] != 'Total']
    
    return energy_df


def get_yearly_trends_by_regions(
    regions: List[str],
    year_from: Optional[int] = None,
    year_to: Optional[int] = None
) -> dict:
    """
    Get yearly trends for multiple selected regions.
    
    Args:
        regions: List of region codes
        year_from: Start year
        year_to: End year
    
    Returns:
        Dictionary with yearly averages per region
    """
    energy_df = get_filtered_energy_data(regions=regions, year_from=year_from, year_to=year_to)
    
    if energy_df.empty:
        return {"error": "No data available for selected regions"}
    
    year_col = "TIME_PERIOD"
    value_col = "OBS_VALUE"
    geo_col = "geo"
    
    # Group by region and year, calculate average
    yearly_by_region = energy_df.groupby([geo_col, year_col])[value_col].mean().reset_index()
    
    result = {}
    for region in regions:
        region_data = yearly_by_region[yearly_by_region[geo_col].astype(str) == str(region)]
        if not region_data.empty:
            result[str(region)] = [
                {"year": int(row[year_col]), "average_value": float(row[value_col])}
                for _, row in region_data.iterrows()
            ]
    
    # If no data found for any selected region, return error
    if not result:
        return {"error": f"No data available for selected regions: {', '.join(regions)}"}
    
    return result


def get_energy_sources_by_regions(
    regions: List[str],
    year_from: Optional[int] = None,
    year_to: Optional[int] = None
) -> dict:
    """
    Get energy sources distribution for multiple selected regions.
    
    Args:
        regions: List of region codes
        year_from: Start year
        year_to: End year
    
    Returns:
        Dictionary with energy sources data per region
    """
    energy_df = get_filtered_energy_data(regions=regions, year_from=year_from, year_to=year_to)
    
    if energy_df.empty:
        return {"error": "No data available for selected regions"}
    
    geo_col = "geo"
    source_col = "siec"
    value_col = "OBS_VALUE"
    
    # Group by region and source
    region_source_df = energy_df.groupby([geo_col, source_col])[value_col].sum().reset_index()
    
    result = {}
    for region in regions:
        region_data = region_source_df[region_source_df[geo_col].astype(str) == str(region)]
        if not region_data.empty:
            result[str(region)] = {
                "sources": [
                    {
                        "source": str(row[source_col]),
                        "value": float(row[value_col])
                    }
                    for _, row in region_data.iterrows()
                ]
            }
    
    # If no data found for any selected region, return error
    if not result:
        return {"error": f"No data available for selected regions: {', '.join(regions)}"}
    
    return result


def get_time_series_by_energy_type(
    energy_type: str,
    regions: Optional[List[str]] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None
) -> dict:
    """
    Get time series data for a specific energy type across regions.
    
    Args:
        energy_type: Energy source type
        regions: Optional list of regions to filter by
        year_from: Start year
        year_to: End year
    
    Returns:
        Dictionary with time series data per region
    """
    energy_df = get_filtered_energy_data(
        regions=regions,
        energy_type=energy_type,
        year_from=year_from,
        year_to=year_to
    )
    
    if energy_df.empty:
        return {"error": "No data available"}
    
    geo_col = "geo"
    year_col = "TIME_PERIOD"
    value_col = "OBS_VALUE"
    
    # Group by region and year
    region_yearly = energy_df.groupby([geo_col, year_col])[value_col].sum().reset_index()
    
    result = {}
    for region in region_yearly[geo_col].unique():
        region_data = region_yearly[region_yearly[geo_col] == region]
        result[str(region)] = [
            {"year": int(row[year_col]), "value": float(row[value_col])}
            for _, row in region_data.iterrows()
        ]
    
    # If no data found, return error
    if not result:
        filter_info = []
        if regions:
            filter_info.append(f"regions: {', '.join(regions)}")
        filter_info.append(f"energy type: {energy_type}")
        return {"error": f"No data available for selected filters ({', '.join(filter_info)})"}
    
    return result

