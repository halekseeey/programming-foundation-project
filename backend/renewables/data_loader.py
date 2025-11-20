from pathlib import Path
from typing import List, Optional, Dict

import pandas as pd

from config import get_config

cfg = get_config()

def load_dataset(dataset_id: str) -> pd.DataFrame:
    """
    Load a specific dataset by ID from clean directory.
    
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
    df = pd.read_csv(csv_path, sep=",", encoding='utf-8')
    return df


def get_available_countries() -> List[str]:
    df = load_dataset("merged_dataset")
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
    df = load_dataset("merged_dataset")

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
