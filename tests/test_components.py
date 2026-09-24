"""
Automated unit tests for CDC Natality 2025 Dashboard components.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.data_loader import load_and_preprocess_data, MONTH_ORDER, STATE_TO_ABBR
from utils.metrics import calculate_kpis
from utils.charts import (
    create_monthly_trend_chart,
    create_sex_comparison_chart,
    create_state_ranking_chart,
    create_us_choropleth_map,
    create_state_month_heatmap,
    create_top_bottom_comparison,
)


def test_data_loader():
    df, is_valid, audit_log = load_and_preprocess_data()
    assert is_valid, f"Validation failed: {audit_log}"
    assert len(df) == 1224, f"Expected 1224 rows, got {len(df)}"
    assert df["Births"].sum() == 3604640, f"Expected 3604640 births, got {df['Births'].sum()}"
    assert "State Abbr" in df.columns, "State Abbr column missing"
    assert df["State Abbr"].isnull().sum() == 0, "Null state abbreviations found"
    print("[PASS] data_loader tests passed")
    return df


def test_metrics(df):
    kpis = calculate_kpis(df)
    assert kpis["total_births_raw"] == 3604640
    assert kpis["geo_count_raw"] == 51
    assert kpis["top_geo_name"] == "California"
    assert kpis["top_month_name"] == "July"
    assert kpis["top_month_births_formatted"] == "321,538"

    # Test empty handling
    empty_df = df.iloc[0:0]
    empty_kpis = calculate_kpis(empty_df)
    assert empty_kpis["is_empty"] is True
    assert empty_kpis["total_births_raw"] == 0
    print("[PASS] metrics tests passed")


def test_charts(df):
    fig1 = create_monthly_trend_chart(df)
    assert fig1 is not None
    fig2 = create_sex_comparison_chart(df)
    assert fig2 is not None
    fig3 = create_state_ranking_chart(df)
    assert fig3 is not None
    fig4 = create_us_choropleth_map(df)
    assert fig4 is not None
    fig5 = create_state_month_heatmap(df)
    assert fig5 is not None
    fig6 = create_top_bottom_comparison(df)
    assert fig6 is not None
    print("[PASS] charts tests passed")


if __name__ == "__main__":
    data = test_data_loader()
    test_metrics(data)
    test_charts(data)
    print("\nALL AUTOMATED TESTS COMPLETED SUCCESSFULLY!")
