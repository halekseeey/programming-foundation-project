# backend/renewables/visualization.py
from io import BytesIO
from typing import Tuple, Optional

import numpy as np              # <= явно используем numpy
import pandas as pd             # <= и pandas
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid GUI warnings
import matplotlib.pyplot as plt
import seaborn as sns           # <= seaborn сверху над matplotlib
import plotly.graph_objs as go  # <= plotly

from .data_loader import filter_renewables


def _prepare_timeseries(country: str, year_from: Optional[int], year_to: Optional[int], value_col: Optional[str] = None) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Вытаскиваем данные по стране и считаем трендовую линию через numpy.
    """
    df = filter_renewables(country=country, year_from=year_from, year_to=year_to)

    # Find year column
    year_col = None
    for col_name in ["year", "Year", "TIME", "time", "TIME_PERIOD"]:
        if col_name in df.columns:
            year_col = col_name
            break
    if year_col is None:
        # Try to find numeric column that looks like years
        for col in df.columns:
            try:
                sample = df[col].dropna().iloc[0] if len(df) > 0 else None
                if sample is not None:
                    year_val = int(float(str(sample)))
                    if 1900 <= year_val <= 2100:
                        year_col = col
                        break
            except (ValueError, TypeError):
                continue
        if year_col is None:
            year_col = df.columns[1] if len(df.columns) > 1 else df.columns[-1]

    # Find value column - use provided value_col if specified, otherwise auto-detect
    if value_col and value_col in df.columns:
        # Use the specified column
        pass
    else:
        # Auto-detect: check for merged datasets first (OBS_VALUE_* columns)
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
    if value_col is None:
        value_col = [c for c in df.columns if c != year_col][-1] if len(df.columns) > 1 else df.columns[-1]

    if year_col not in df.columns or value_col not in df.columns:
        # Return empty series if columns not found
        empty_series = pd.Series(dtype=float)
        return empty_series, empty_series, empty_series

    df = df[[year_col, value_col]].dropna()
    if len(df) == 0:
        empty_series = pd.Series(dtype=float)
        return empty_series, empty_series, empty_series
    
    # Convert to numeric
    df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna().sort_values(year_col)

    years = df[year_col].astype(int)
    values = df[value_col].astype(float)

    # numpy: простая линейная регрессия для тренда
    if len(df) >= 2:
        coeffs = np.polyfit(years, values, 1)
        trend = np.poly1d(coeffs)(years)
    else:
        trend = np.full_like(values, fill_value=np.nan)

    return years, values, pd.Series(trend, index=years.index)


def make_matplotlib_png(country: str, year_from: Optional[int], year_to: Optional[int], value_col: Optional[str] = None) -> bytes:
    """
    Строим PNG-график через matplotlib + seaborn и возвращаем байты.
    """
    years, values, trend = _prepare_timeseries(country, year_from, year_to, value_col=value_col)

    sns.set_theme(style="whitegrid")  # seaborn

    fig, ax = plt.subplots(figsize=(8, 4))

    # основная линия
    ax.plot(years, values, marker="o", label="Renewable share")

    # трендовая линия
    ax.plot(years, trend, linestyle="--", label="Trend (numpy fit)")

    ax.set_title(f"Share of renewable energy – {country}")
    ax.set_xlabel("Year")
    ax.set_ylabel("Percentage")
    ax.legend()

    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def make_plotly_figure(country: str, year_from: Optional[int], year_to: Optional[int], value_col: Optional[str] = None) -> go.Figure:
    """
    Строим интерактивный график через plotly и отдаём Figure.
    """
    years, values, trend = _prepare_timeseries(country, year_from, year_to, value_col=value_col)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=years,
            y=values,
            mode="lines+markers",
            name="Renewable share",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=years,
            y=trend,
            mode="lines",
            name="Trend",
            line=dict(dash="dash"),
        )
    )

    fig.update_layout(
        title=f"Share of renewable energy – {country}",
        xaxis_title="Year",
        yaxis_title="Percentage",
        template="plotly_white",
    )

    return fig


def make_yearly_averages_plot(yearly_averages: list, title: str = "Yearly Averages") -> go.Figure:
    """
    Create a bar chart for yearly averages.
    
    Args:
        yearly_averages: List of dicts with 'year' and 'average_value' keys
        title: Chart title
    
    Returns:
        Plotly Figure
    """
    if not yearly_averages:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    years = [point['year'] for point in yearly_averages]
    values = [point['average_value'] for point in yearly_averages]
    
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=years,
            y=values,
            marker=dict(color='rgba(56, 189, 248, 0.8)', line=dict(color='rgba(56, 189, 248, 1.0)', width=1)),
            name="Average Value"
        )
    )
    
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title="Average Value",
        template="plotly_dark",
        height=400,
        showlegend=False
    )
    
    return fig


def make_timeseries_by_source_plot(timeseries_by_source: dict, title: str = "Time Series by Source") -> go.Figure:
    """
    Create a line chart for time series data by source.
    
    Args:
        timeseries_by_source: Dict with source names as keys and lists of {year, value} as values
        title: Chart title
    
    Returns:
        Plotly Figure
    """
    if not timeseries_by_source:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    fig = go.Figure()
    
    colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
    
    for idx, (source, points) in enumerate(timeseries_by_source.items()):
        if not points:
            continue
        
        years = [p['year'] for p in points]
        values = [p['value'] for p in points]
        
        fig.add_trace(
            go.Scatter(
                x=years,
                y=values,
                mode='lines+markers',
                name=source,
                line=dict(color=colors[idx % len(colors)], width=2),
                marker=dict(size=6)
            )
        )
    
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title="Value",
        template="plotly_dark",
        height=400,
        hovermode='x unified'
    )
    
    return fig


def make_yearly_comparison_plot(
    yearly_averages: list,
    indicator_type: str,
    title: str = "Yearly Averages Comparison"
) -> go.Figure:
    """
    Create a line chart comparing renewable energy and indicator values with dual y-axes.
    Uses two separate y-axes to handle different scales (e.g., percentage vs large numbers).
    
    Args:
        yearly_averages: List of dicts with 'year', 'renewable_avg', 'indicator_avg' keys
        indicator_type: Type of indicator (e.g., 'gdp', 'population')
        title: Chart title
    
    Returns:
        Plotly Figure
    """
    if not yearly_averages:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    years = [point['year'] for point in yearly_averages]
    renewable_values = [point['renewable_avg'] for point in yearly_averages]
    indicator_values = [point['indicator_avg'] for point in yearly_averages]
    
    fig = go.Figure()
    
    # Add renewable energy trace (left y-axis)
    fig.add_trace(
        go.Scatter(
            x=years,
            y=renewable_values,
            name="Renewable Energy (%)",
            line=dict(color='rgba(56, 189, 248, 1.0)', width=3),
            marker=dict(color='rgba(56, 189, 248, 1.0)', size=8),
            yaxis='y'
        )
    )
    
    # Add indicator trace (right y-axis)
    fig.add_trace(
        go.Scatter(
            x=years,
            y=indicator_values,
            name=indicator_type.upper(),
            line=dict(color='rgba(16, 185, 129, 1.0)', width=3),
            marker=dict(color='rgba(16, 185, 129, 1.0)', size=8),
            yaxis='y2'
        )
    )
    
    # Update layout with dual y-axes
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis=dict(
            title=dict(text="Renewable Energy (%)", font=dict(color='rgba(56, 189, 248, 1.0)')),
            tickfont=dict(color='rgba(56, 189, 248, 1.0)'),
            side='left'
        ),
        yaxis2=dict(
            title=dict(text=indicator_type.upper(), font=dict(color='rgba(16, 185, 129, 1.0)')),
            tickfont=dict(color='rgba(16, 185, 129, 1.0)'),
            overlaying='y',
            side='right'
        ),
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

    return fig
