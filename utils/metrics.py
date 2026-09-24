"""
metrics.py
==========
KPI and metric calculation functions for the CDC Natality Dashboard.

Provides formatted values, clean handles for empty datasets, and business
analytics summaries suitable for undergraduate coursework.
"""

from typing import Dict, Any
import pandas as pd


def calculate_kpis(filtered_df: pd.DataFrame, total_geos_available: int = 51) -> Dict[str, Any]:
    """
    Computes summary KPI metrics for the user-selected data slice.
    
    Returns a dictionary of formatted values, raw figures, and contextual descriptors.
    """
    if filtered_df.empty:
        return {
            "total_births_formatted": "0",
            "total_births_raw": 0,
            "geo_count_formatted": f"0 of {total_geos_available}",
            "geo_count_raw": 0,
            "avg_monthly_births_formatted": "0",
            "avg_monthly_births_raw": 0,
            "top_geo_name": "N/A",
            "top_geo_births_formatted": "0",
            "top_month_name": "N/A",
            "top_month_births_formatted": "0",
            "is_empty": True,
        }

    # 1. Total Births
    total_births = int(filtered_df["Births"].sum())

    # 2. Number of selected geographies
    selected_geos = int(filtered_df["State of Residence"].nunique())

    # 3. Average births per selected month
    # In business analytics, this represents the average aggregate monthly volume across the selected months
    num_selected_months = filtered_df["Month"].nunique()
    avg_per_month = total_births / num_selected_months if num_selected_months > 0 else 0

    # 4. Geography with highest birth count
    geo_totals = filtered_df.groupby("State of Residence", as_index=False)["Births"].sum()
    top_geo_row = geo_totals.loc[geo_totals["Births"].idxmax()]
    top_geo_name = str(top_geo_row["State of Residence"])
    top_geo_births = int(top_geo_row["Births"])

    # 5. Month with highest birth count
    month_totals = filtered_df.groupby("Month", observed=True, as_index=False)["Births"].sum()
    top_month_row = month_totals.loc[month_totals["Births"].idxmax()]
    top_month_name = str(top_month_row["Month"])
    top_month_births = int(top_month_row["Births"])

    return {
        "total_births_formatted": f"{total_births:,}",
        "total_births_raw": total_births,
        "geo_count_formatted": f"{selected_geos} of {total_geos_available}",
        "geo_count_raw": selected_geos,
        "avg_monthly_births_formatted": f"{avg_per_month:,.0f}",
        "avg_monthly_births_raw": avg_per_month,
        "top_geo_name": top_geo_name,
        "top_geo_births_formatted": f"{top_geo_births:,}",
        "top_month_name": top_month_name,
        "top_month_births_formatted": f"{top_month_births:,}",
        "is_empty": False,
    }
