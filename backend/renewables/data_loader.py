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
    csv_path = cfg.DATA_CLEAN_DIR / f"{dataset_id}.csv"
    if not csv_path.exists():
        raise ValueError(f"Dataset {dataset_id} not found at {csv_path}")
    
    df = pd.read_csv(csv_path, sep=",", encoding='utf-8')
    return df


def get_available_countries() -> List[str]:
    df = load_dataset("merged_dataset")
    geo_col = "geo"
    
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

    geo_col = "geo"
    year_col = "TIME_PERIOD"

    if country:
        df = df[df[geo_col].astype(str).str.contains(str(country), case=False, na=False)]

    if year_from or year_to:
            df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
    if year_from:
            df = df[df[year_col] >= year_from]
    if year_to:
            df = df[df[year_col] <= year_to]

    return df
