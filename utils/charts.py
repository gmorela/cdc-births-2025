"""
charts.py
=========
Plotly visualization builders for the CDC Natality Dashboard.

Adheres strictly to core business analytics visualization standards:
1. Accessible, high-contrast, colorblind-friendly palettes.
2. Non-zero baselines are prohibited for magnitude comparisons (rangemode='tozero').
3. Strict thousands separator formatting (:,) on all hover tooltips and axes.
4. Descriptive titles, axis labels, and subtitles.
"""

from typing import List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Color tokens for accessible, high-contrast visual design
COLOR_PRIMARY = "#0284c7"      # Ocean Blue
COLOR_FEMALE = "#0d9488"       # Deep Teal
COLOR_MALE = "#6366f1"         # Slate Indigo
COLOR_ACCENT = "#f59e0b"       # Warm Amber
COLOR_TOP = "#10b981"          # Emerald
COLOR_BOTTOM = "#f43f5e"       # Rose
CHART_BG = "rgba(0,0,0,0)"
GRID_COLOR = "#f1f5f9"


def create_monthly_trend_chart(df: pd.DataFrame) -> go.Figure:
    """
    Renders an aggregate monthly birth count line and bar overlay chart.
    Preserves calendar chronological ordering with zero-baseline y-axis.
    """
    monthly = (
        df.groupby("Month", observed=True, as_index=False)["Births"]
        .sum()
        .sort_values("Month")
    )

    fig = go.Figure()

    # Subtle bar baseline
    fig.add_trace(
        go.Bar(
            x=monthly["Month"],
            y=monthly["Births"],
            name="Monthly Volume",
            marker_color="#e0f2fe",
            hovertemplate="<b>%{x}</b><br>Provisional Births: %{y:,}<extra></extra>",
        )
    )

    # Connected trend line with markers
    fig.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["Births"],
            mode="lines+markers+text",
            name="Trend Line",
            line=dict(color=COLOR_PRIMARY, width=3),
            marker=dict(size=8, color=COLOR_PRIMARY),
            text=monthly["Births"].apply(lambda v: f"{v:,.0f}"),
            textposition="top center",
            hovertemplate="<b>%{x}</b><br>Provisional Births: %{y:,}<extra></extra>",
        )
    )

    fig.update_layout(
        title="<b>Monthly Total Live Birth Count (2025 Provisional)</b><br><sup>Aggregate live births recorded per calendar month</sup>",
        xaxis_title="Calendar Month",
        yaxis_title="Recorded Live Births (Count)",
        yaxis=dict(rangemode="tozero", tickformat=","),
        showlegend=False,
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        hovermode="x unified",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def create_sex_comparison_chart(df: pd.DataFrame) -> go.Figure:
    """
    Renders a grouped bar chart comparing Female and Male births across months,
    using accessible, non-stereotypical colors (Deep Teal vs. Slate Indigo).
    """
    sex_monthly = (
        df.groupby(["Month", "Sex of Infant"], observed=True, as_index=False)["Births"]
        .sum()
        .sort_values(["Month", "Sex of Infant"])
    )

    fig = px.bar(
        sex_monthly,
        x="Month",
        y="Births",
        color="Sex of Infant",
        barmode="group",
        color_discrete_map={"Female": COLOR_FEMALE, "Male": COLOR_MALE},
        labels={"Births": "Recorded Live Births", "Month": "Month", "Sex of Infant": "Infant Sex"},
        title="<b>Provisional Births by Infant Sex & Month</b><br><sup>Comparing recorded counts for female and male infants across 2025</sup>",
    )

    fig.update_layout(
        yaxis=dict(rangemode="tozero", tickformat=","),
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b> (%{data.name})<br>Recorded Births: %{y:,}<extra></extra>"
    )
    return fig


def create_state_ranking_chart(df: pd.DataFrame, max_display: int = 25) -> go.Figure:
    """
    Renders a horizontal sorted bar chart ranking states by cumulative birth count.
    Zero-baseline enforced, with thousands separators on hover and axis.
    """
    state_totals = (
        df.groupby("State of Residence", as_index=False)["Births"]
        .sum()
        .sort_values("Births", ascending=True)
    )

    total_states = len(state_totals)
    if total_states > max_display:
        state_totals = state_totals.tail(max_display)
        subtitle = f"Showing Top {max_display} of {total_states} selected geographies"
    else:
        subtitle = f"Showing all {total_states} selected geographies"

    fig = px.bar(
        state_totals,
        x="Births",
        y="State of Residence",
        orientation="h",
        color="Births",
        color_continuous_scale="Tealgrn",
        labels={"Births": "Recorded Live Births", "State of Residence": "Geography"},
        title=f"<b>State Ranking by Cumulative Birth Count</b><br><sup>{subtitle}</sup>",
    )

    fig.update_layout(
        xaxis=dict(rangemode="tozero", tickformat=","),
        coloraxis_showscale=False,
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        height=max(450, len(state_totals) * 22),
        margin=dict(l=40, r=40, t=60, b=40),
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Total Recorded Births: %{x:,}<extra></extra>"
    )
    return fig


def create_us_choropleth_map(df: pd.DataFrame) -> go.Figure:
    """
    Renders an interactive US State Choropleth map using 2-letter postal abbreviations.
    Highlights geographic distribution of aggregate birth counts.
    """
    state_map_data = (
        df.groupby(["State of Residence", "State Abbr"], as_index=False)["Births"]
        .sum()
    )

    fig = px.choropleth(
        state_map_data,
        locations="State Abbr",
        locationmode="USA-states",
        color="Births",
        scope="usa",
        color_continuous_scale="Viridis",
        labels={"Births": "Live Births", "State Abbr": "State"},
        hover_name="State of Residence",
        title="<b>Geographic Distribution of Live Birth Counts (2025)</b><br><sup>Darker/warmer shades indicate higher raw birth counts (strongly influenced by state population size)</sup>",
    )

    fig.update_layout(
        geo=dict(
            lakecolor="rgb(255, 255, 255)",
            showlakes=True,
            projection_type="albers usa",
            bgcolor=CHART_BG,
        ),
        paper_bgcolor=CHART_BG,
        coloraxis_colorbar=dict(title="Live Births", tickformat=","),
        margin=dict(l=0, r=0, t=50, b=0),
    )
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b> (%{location})<br>Total Births: %{z:,}<extra></extra>"
    )
    return fig


def create_state_month_heatmap(df: pd.DataFrame, selected_states: List[str] = None) -> go.Figure:
    """
    Renders a 2D Heatmap matrix of State (rows) vs. Month (columns).
    Demonstrates seasonal birth fluctuations across geographies.
    """
    pivot = (
        df.groupby(["State of Residence", "Month"], observed=True)["Births"]
        .sum()
        .unstack(fill_value=0)
    )

    # Sort states by total annual births descending so largest states appear at top
    state_totals = pivot.sum(axis=1).sort_values(ascending=True)
    pivot = pivot.loc[state_totals.index]

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale="Tealrose",
            colorbar=dict(title="Births", tickformat=","),
            hovertemplate="<b>%{y}</b><br>Month: %{x}<br>Births: %{z:,}<extra></extra>",
        )
    )

    fig.update_layout(
        title="<b>State-by-Month Natality Heatmap Matrix</b><br><sup>Visualizing seasonal volume variations across jurisdictions</sup>",
        xaxis_title="Month (Chronological)",
        yaxis_title="State / Geography",
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        height=max(450, len(pivot) * 20),
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def create_top_bottom_comparison(df: pd.DataFrame, n: int = 5) -> go.Figure:
    """
    Renders a comparative horizontal chart highlighting the Top N and Bottom N
    geographies by total birth count to illustrate the scale disparities between large
    and small population states.
    """
    state_totals = (
        df.groupby("State of Residence", as_index=False)["Births"]
        .sum()
        .sort_values("Births", ascending=False)
    )

    if len(state_totals) < (2 * n):
        # If selection is small, show all states sorted
        top_df = state_totals.copy()
        top_df["Tier"] = "Selected Geographies"
    else:
        top_slice = state_totals.head(n).copy()
        top_slice["Tier"] = f"Top {n} Geographies"

        bottom_slice = state_totals.tail(n).copy()
        bottom_slice["Tier"] = f"Bottom {n} Geographies"

        top_df = pd.concat([top_slice, bottom_slice]).sort_values("Births", ascending=True)

    fig = px.bar(
        top_df,
        x="Births",
        y="State of Residence",
        color="Tier",
        orientation="h",
        color_discrete_map={
            f"Top {n} Geographies": COLOR_TOP,
            f"Bottom {n} Geographies": COLOR_BOTTOM,
            "Selected Geographies": COLOR_PRIMARY,
        },
        labels={"Births": "Recorded Live Births", "State of Residence": "Geography"},
        title=f"<b>Population Scale Contrast: Top {n} vs. Bottom {n} Geographies</b><br><sup>Underlining why raw counts must not be interpreted as birth rates</sup>",
    )

    fig.update_layout(
        xaxis=dict(rangemode="tozero", tickformat=","),
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b> (%{data.name})<br>Live Births: %{x:,}<extra></extra>"
    )
    return fig
