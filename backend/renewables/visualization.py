# backend/renewables/visualization.py
from io import BytesIO
from typing import Tuple, Optional
from pathlib import Path

import numpy as np              # <= явно используем numpy
import pandas as pd             # <= и pandas
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid GUI warnings
import matplotlib.pyplot as plt
import seaborn as sns           # <= seaborn сверху над matplotlib
import plotly.graph_objs as go  # <= plotly

from config import get_config
from .data_loader import filter_renewables

cfg = get_config()


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
        value_col = None
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
    Create a line chart showing changes in renewable energy share over time.
    
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
        go.Scatter(
            x=years,
            y=values,
            mode='lines+markers',
            name="Renewable Energy Share (%)",
            line=dict(color='rgba(56, 189, 248, 1.0)', width=3),
            marker=dict(color='rgba(56, 189, 248, 1.0)', size=8),
            hovertemplate='<b>Year: %{x}</b><br>Renewable Energy Share: %{y:.2f}%<extra></extra>'
        )
    )
    
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title="Renewable Energy Share (%)",
        template="plotly_dark",
        height=400,
        showlegend=False,
        hovermode='x unified'
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
    
    # Filter out sources with all zero values (they won't be visible on log scale anyway)
    filtered_sources = {}
    for source, points in timeseries_by_source.items():
        if not points:
            continue
        values = [p['value'] for p in points]
        # Skip sources where all values are zero or very close to zero
        if max(values) > 0.01:  # Threshold to filter out effectively zero sources
            filtered_sources[source] = points
    
    if not filtered_sources:
        fig.add_annotation(text="No data available (all sources have zero values)", showarrow=False)
        return fig
    
    for idx, (source, points) in enumerate(filtered_sources.items()):
        years = [p['year'] for p in points]
        values = [p['value'] for p in points]
        
        # Normalize to first year (index = 100) to compare relative changes across sources
        # This makes the chart more relevant for comparing trends of sources with different scales
        first_value = values[0] if values[0] > 0 else 1.0
        normalized_values = [(v / first_value * 100) if first_value > 0 else 100 for v in values]
        
        fig.add_trace(
            go.Scatter(
                x=years,
                y=normalized_values,
                mode='lines+markers',
                name=source,
                line=dict(color=colors[idx % len(colors)], width=2),
                marker=dict(size=6),
                hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Index: %{y:.1f} (Base year = 100)<br>Actual Value: %{customdata:.2f} GWh<extra></extra>',
                customdata=values  # Show original values in hover
            )
        )
    
    fig.update_layout(
        title=title + " (Normalized to first year = 100)",
        xaxis_title="Year",
        yaxis_title="Index (First year = 100)",
        yaxis=dict(
            title="Index (First year = 100)",
            # Use linear scale for normalized values (they're already comparable)
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

def make_sources_by_region_bar_chart(
    region_source_data: pd.DataFrame,
    geo_col: str = "geo",
    source_col: str = "siec",
    value_col: str = "OBS_VALUE",
    title: str = "Energy Sources Comparison Across Regions"
) -> go.Figure:
    """
    Create a grouped bar chart comparing renewable energy sources across regions.
    
    Args:
        region_source_data: DataFrame with columns: geo (region), siec (source), OBS_VALUE (value)
        geo_col: Column name for regions
        source_col: Column name for energy sources
        value_col: Column name for energy values
        title: Chart title
    
    Returns:
        Plotly Figure
    """
    if region_source_data.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    # Filter out aggregated regions (EU, etc.) - only show individual countries
    exclude_patterns = ['union', 'european', 'countries', 'euro area', 'eurozone']
    region_source_data = region_source_data[
        ~region_source_data[geo_col].astype(str).str.lower().str.contains('|'.join(exclude_patterns), na=False)
    ]
    
    if region_source_data.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    # Pivot data: regions as rows, sources as columns
    pivot_df = region_source_data.pivot_table(
        index=geo_col,
        columns=source_col,
        values=value_col,
        aggfunc='sum',
        fill_value=0
    )
    
    # Get top regions by total energy (to avoid too many bars)
    pivot_df['total'] = pivot_df.sum(axis=1)
    pivot_df = pivot_df.sort_values('total', ascending=False).head(15)  # Top 15 regions
    pivot_df = pivot_df.drop(columns=['total'])
    
    # Filter out sources with all zeros
    pivot_df = pivot_df.loc[:, (pivot_df != 0).any(axis=0)]
    
    if pivot_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    fig = go.Figure()
    
    # Add a trace for each energy source
    colors = ['rgba(56, 189, 248, 0.8)', 'rgba(16, 185, 129, 0.8)', 'rgba(251, 191, 36, 0.8)', 
              'rgba(239, 68, 68, 0.8)', 'rgba(139, 92, 246, 0.8)', 'rgba(236, 72, 153, 0.8)']
    
    for idx, source in enumerate(pivot_df.columns):
        fig.add_trace(
            go.Bar(
                name=str(source),
                x=pivot_df.index.tolist(),
                y=pivot_df[source].tolist(),
                marker=dict(
                    color=colors[idx % len(colors)],
                    line=dict(color='rgba(255, 255, 255, 0.2)', width=1)
                ),
                hovertemplate='<b>%{fullData.name}</b><br>Region: %{x}<br>Value: %{y:,.0f} GWh<extra></extra>'
            )
        )
    
    fig.update_layout(
        title=title,
        xaxis_title="Region",
        yaxis_title="Energy (GWh)",
        template="plotly_dark",
        height=600,
        xaxis=dict(tickangle=-45),
        barmode='group',  # Grouped bars
        legend=dict(
            x=1.02,
            y=1,
            bgcolor='rgba(0, 0, 0, 0.5)',
            bordercolor='rgba(255, 255, 255, 0.2)',
            borderwidth=1
        )
    )
    
    return fig


def make_regional_heatmap(
    df: pd.DataFrame,
    geo_col: str,
    year_col: str,
    value_col: str,
    title: str = "Regional Energy Intensity Heatmap"
) -> go.Figure:
    """
    Create a heatmap visualizing regional energy intensity over time.
    
    Args:
        df: DataFrame with regional data
        geo_col: Column name for regions
        year_col: Column name for years
        value_col: Column name for values
        title: Chart title
    
    Returns:
        Plotly Figure
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    # Filter out aggregated regions (EU, etc.) - only show individual countries
    exclude_patterns = ['union', 'european', 'countries', 'euro area', 'eurozone']
    df = df[
        ~df[geo_col].astype(str).str.lower().str.contains('|'.join(exclude_patterns), na=False)
    ]
    
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    # Pivot data for heatmap
    pivot_df = df.pivot_table(
        index=geo_col,
        columns=year_col,
        values=value_col,
        aggfunc='mean'
    )
    
    # Sort regions by average value
    pivot_df['avg'] = pivot_df.mean(axis=1)
    pivot_df = pivot_df.sort_values('avg', ascending=False).drop(columns=['avg'])
    
    # Convert numpy arrays to lists for JSON serialization
    # Replace NaN with None for JSON compatibility
    z_values = pivot_df.values
    z_values = np.where(np.isnan(z_values), None, z_values)
    z_values = z_values.tolist()
    x_values = [str(col) for col in pivot_df.columns]
    y_values = pivot_df.index.tolist()
    
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_values,
        y=y_values,
        colorscale='Viridis',
        colorbar=dict(title="Renewable Energy %"),
        hovertemplate='Region: %{y}<br>Year: %{x}<br>Value: %{z:.2f}%<extra></extra>',
        showscale=True
    ))
    
    # Limit height to reasonable maximum, add scroll if needed
    num_regions = len(pivot_df)
    calculated_height = max(400, min(800, num_regions * 20))
    
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title="Region",
        template="plotly_dark",
        height=calculated_height,
        autosize=True,
        margin=dict(l=150, r=50, t=50, b=50)
    )
    
    # Improve y-axis display for many regions
    if num_regions > 20:
        fig.update_yaxes(tickfont=dict(size=9))
    
    return fig


def make_regional_map(
    df: pd.DataFrame,
    geo_col: str,
    value_col: str,
    title: str = "Renewable Energy Adoption by Region"
) -> go.Figure:
    """
    Create an interactive map displaying renewable energy adoption by region.
    Uses Plotly's built-in country/region mapping.
    
    Args:
        df: DataFrame with regional data (latest year)
        geo_col: Column name for regions
        value_col: Column name for values
        title: Chart title
    
    Returns:
        Plotly Figure
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    # Filter out aggregated regions (EU, etc.) - only show individual countries
    exclude_patterns = ['union', 'european', 'countries', 'euro area', 'eurozone']
    df = df[
        ~df[geo_col].astype(str).str.lower().str.contains('|'.join(exclude_patterns), na=False)
    ]
    
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    # Prepare data for choropleth
    # Use ISO country codes if available, otherwise use region names
    fig = go.Figure(data=go.Choropleth(
        locations=df[geo_col].tolist(),
        z=df[value_col].tolist(),
        text=df[geo_col].tolist(),
        colorscale='Viridis',
        colorbar=dict(title="Renewable Energy %"),
        hovertemplate='<b>%{text}</b><br>Value: %{z:.2f}%<extra></extra>',
        locationmode='country names'  # Plotly will try to match country names
    ))
    
    fig.update_geos(
        projection_type='natural earth',
        showframe=False,
        showcoastlines=True,
        projection_scale=1.2
    )
    
    fig.update_layout(
        title=title,
        template="plotly_dark",
        height=600
    )
    
    return fig


def save_chart(fig: go.Figure, chart_name: str, format: str = 'png') -> Optional[str]:
    """
    Save a Plotly figure to file as PNG (overwrites existing file).
    Runs in background thread to avoid blocking API response.
    
    Args:
        fig: Plotly Figure object
        chart_name: Name for the chart file (without extension)
        format: File format ('png' or 'html', default: 'png')
    
    Returns:
        Path to saved file or None if error (returns immediately, actual save happens in background)
    """
    import threading
    
    def _save_in_background():
        try:
            # Ensure charts directory exists
            charts_dir = cfg.CHARTS_DIR
            charts_dir.mkdir(parents=True, exist_ok=True)
            
            # Sanitize chart name for filename
            safe_name = "".join(c for c in chart_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            
            # Use fixed filename (overwrites on each save)
            filename = f"{safe_name}.{format}"
            filepath = charts_dir / filename
            
            if format == 'html':
                fig.write_html(str(filepath))
            elif format == 'png':
                try:
                    fig.write_image(str(filepath), width=1200, height=800, scale=2)
                except Exception as img_error:
                    # If PNG save fails (e.g., kaleido not installed), fallback to HTML
                    print(f"Warning: Failed to save PNG for {chart_name}: {img_error}")
                    print(f"Falling back to HTML format")
                    html_filename = f"{safe_name}.html"
                    html_filepath = charts_dir / html_filename
                    fig.write_html(str(html_filepath))
        except Exception as e:
            print(f"Error saving chart {chart_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Start saving in background thread (non-blocking)
    thread = threading.Thread(target=_save_in_background, daemon=True)
    thread.start()
    
    # Return immediately (don't wait for save to complete)
    charts_dir = cfg.CHARTS_DIR
    safe_name = "".join(c for c in chart_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_')
    filename = f"{safe_name}.{format}"
    filepath = charts_dir / filename
    return str(filepath)
