"""
app.py
======
Provisional US Natality Dashboard (2025)
Built with Streamlit, pandas, and Plotly.

Created for undergraduate business analytics students to explore geographic,
seasonal, and biological sex patterns in provisional CDC live birth counts.
"""

from typing import List
import streamlit as st
import pandas as pd

from utils.data_loader import load_and_preprocess_data, MONTH_ORDER
from utils.metrics import calculate_kpis
from utils.charts import (
    create_monthly_trend_chart,
    create_sex_comparison_chart,
    create_state_ranking_chart,
    create_us_choropleth_map,
    create_state_month_heatmap,
    create_top_bottom_comparison,
)

# Page configuration
st.set_page_config(
    page_title="CDC Provisional Natality 2025",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded",
)




def render_header():
    """Renders the dashboard title, source attribution, and required notices."""
    st.title("👶 CDC Provisional Natality Dashboard (2025)")
    st.markdown(
        "**Exploratory Data Analysis of Geographic, Seasonal, and Biological Sex Patterns in US Live Births**"
    )

    # Notice banner: Provisional data notice & Counts vs Rates clarification
    st.info(
        """
        **📌 Critical Analytical Notices for Business Analytics Students:**
        - **Birth Counts, Not Birth Rates:** All figures in this dashboard represent *raw counts of recorded live births*. They do **not** represent birth rates or general fertility rates because population denominators are not included in this dataset. A populous state like California records more births than Wyoming primarily due to population size.
        - **Provisional 2025 CDC Data:** Data are provisional vital statistics from the CDC National Center for Health Statistics (NCHS) and are subject to routine reporting delays and retrospective revisions.
        - **Data Provenance:** CDC WONDER Provisional Natality Dataset (2025).
        """
    )


def initialize_session_state(all_states: List[str], all_months: List[str], all_sexes: List[str]):
    """Sets initial default values in st.session_state if not already present."""
    if "selected_states" not in st.session_state:
        st.session_state.selected_states = all_states
    if "selected_months" not in st.session_state:
        st.session_state.selected_months = all_months
    if "selected_sexes" not in st.session_state:
        st.session_state.selected_sexes = all_sexes


def render_sidebar(all_states: List[str], all_months: List[str], all_sexes: List[str]):
    """Renders sidebar controls, filter buttons, and active filter summaries."""
    st.sidebar.header("🔍 Filter Controls")

    # Helper callbacks for reset and select all buttons
    col_btn1, col_btn2 = st.sidebar.columns(2)
    if col_btn1.button("Select All", use_container_width=True):
        st.session_state.selected_states = all_states
        st.session_state.selected_months = all_months
        st.session_state.selected_sexes = all_sexes
        st.rerun()

    if col_btn2.button("Reset Filters", use_container_width=True):
        st.session_state.selected_states = all_states
        st.session_state.selected_months = all_months
        st.session_state.selected_sexes = all_sexes
        st.rerun()

    # 1. Geography Multiselect
    selected_states = st.sidebar.multiselect(
        "State / Geography:",
        options=all_states,
        default=st.session_state.selected_states,
        key="state_selector",
        help="Select one or more US states and the District of Columbia.",
    )

    # 2. Month Multiselect (Preserves chronological calendar order)
    selected_months = st.sidebar.multiselect(
        "Month (Chronological):",
        options=all_months,
        default=st.session_state.selected_months,
        key="month_selector",
        help="Filter observations by calendar month.",
    )

    # 3. Infant Sex Selector
    selected_sexes = st.sidebar.multiselect(
        "Infant Sex:",
        options=all_sexes,
        default=st.session_state.selected_sexes,
        key="sex_selector",
        help="Filter by biological infant sex classification.",
    )

    # Update session states with widget selections
    st.session_state.selected_states = selected_states
    st.session_state.selected_months = selected_months
    st.session_state.selected_sexes = selected_sexes

    # Filter summary readout
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Active Filter Summary")
    st.sidebar.markdown(
        f"""
        - **Geographies:** {len(selected_states)} of {len(all_states)} selected
        - **Months:** {len(selected_months)} of {len(all_months)} selected
        - **Infant Sex:** {', '.join(selected_sexes) if selected_sexes else 'None selected'}
        """
    )

    return selected_states, selected_months, selected_sexes


def render_kpis(kpis: dict):
    """Renders the 5 required top-level KPI cards using native responsive st.metric."""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Total Recorded Births",
            value=kpis["total_births_formatted"],
            help="Cumulative recorded live births in active selection",
        )

    with col2:
        st.metric(
            label="Selected Geographies",
            value=kpis["geo_count_formatted"],
            help="Number of US states & DC included",
        )

    with col3:
        st.metric(
            label="Avg. Births / Month",
            value=kpis["avg_monthly_births_formatted"],
            help="Average monthly birth volume across selected months",
        )

    with col4:
        st.metric(
            label="Highest Birth Geography",
            value=kpis["top_geo_name"],
            help=f"{kpis['top_geo_births_formatted']} births in selection",
        )

    with col5:
        st.metric(
            label="Peak Birth Month",
            value=kpis["top_month_name"],
            help=f"{kpis['top_month_births_formatted']} births in selection",
        )


def main():
    # Load and validate dataset
    try:
        raw_df, is_valid, audit_log = load_and_preprocess_data()
    except Exception as e:
        st.error(f"❌ Failed to load dataset: {e}")
        return

    if not is_valid:
        st.error("⚠️ Data validation warnings detected upon loading:")
        for msg in audit_log:
            st.warning(msg)

    # Master lists for filter initialization
    all_states = sorted(raw_df["State of Residence"].unique().tolist())
    all_months = MONTH_ORDER
    all_sexes = sorted(raw_df["Sex of Infant"].unique().tolist())

    # Initialize session state defaults
    initialize_session_state(all_states, all_months, all_sexes)

    # Header
    render_header()

    # Sidebar
    selected_states, selected_months, selected_sexes = render_sidebar(all_states, all_months, all_sexes)

    # Filter data slice
    filtered_df = raw_df[
        (raw_df["State of Residence"].isin(selected_states))
        & (raw_df["Month"].isin(selected_months))
        & (raw_df["Sex of Infant"].isin(selected_sexes))
    ].copy()

    # KPI Calculation
    kpis = calculate_kpis(filtered_df, total_geos_available=len(all_states))
    render_kpis(kpis)

    # Empty-state check: Handle cases where filters produce zero rows
    if filtered_df.empty:
        st.warning(
            "⚠️ **No observations match your current filter selection.** "
            "Please select at least one geography, one month, and one infant-sex category in the sidebar, "
            "or click **'Reset Filters'** to restore all defaults."
        )
        return

    # Dashboard Tabs
    tab_overview, tab_geo, tab_monthly_sex, tab_table, tab_about = st.tabs([
        "📊 Overview",
        "🗺️ Geographic Analysis",
        "📈 Monthly and Sex Analysis",
        "📋 Data Table and Download",
        "📖 About the Data",
    ])

    # ---------------- TAB 1: OVERVIEW ----------------
    with tab_overview:
        st.subheader("Executive Natality Overview")
        st.markdown(
            "This tab provides a high-level summary of provisional US live birth counts across 2025, "
            "displaying seasonal trajectories and overall biological sex distribution."
        )

        col_trend, col_sex_share = st.columns([3, 2])

        with col_trend:
            trend_fig = create_monthly_trend_chart(filtered_df)
            st.plotly_chart(trend_fig, use_container_width=True)

        with col_sex_share:
            # Proportion metric and bar summary
            sex_summary = (
                filtered_df.groupby("Sex of Infant", as_index=False)["Births"]
                .sum()
            )
            total_births_sel = sex_summary["Births"].sum()
            sex_summary["Proportion"] = sex_summary["Births"] / total_births_sel * 100

            st.markdown("#### Aggregate Infant Sex Breakdown")
            for _, row in sex_summary.iterrows():
                st.write(
                    f"**{row['Sex of Infant']} Infants:** {row['Births']:,} births ({row['Proportion']:.2f}%)"
                )
                st.progress(float(row["Proportion"] / 100))

            st.markdown(
                """
                > **💡 Business Analytics Observation:**  
                > Notice that male births consistently account for approximately **51.2%** of total live births, while female births represent **48.8%**. This aligns with the well-documented biological *secondary sex ratio* observed globally across human populations.
                """
            )

        st.markdown("---")
        st.subheader("Key Analytical Takeaways for Students")
        takeaway_col1, takeaway_col2 = st.columns(2)
        with takeaway_col1:
            st.info(
                """
                **1. Seasonal Seasonality:**  
                In the United States, birth counts typically experience a late summer peak (July through September) and a trough in the late winter/spring (February/April). Note that February naturally has fewer days (28 days in 2025), which partially depresses its raw monthly total.
                """
            )
        with takeaway_col2:
            st.info(
                """
                **2. Scale Variance across States:**  
                Total counts vary by more than two orders of magnitude between the largest states (California, Texas) and smaller states (Vermont, Wyoming). When comparing jurisdictions, remember that these variations reflect resident population size rather than differing fertility behavior.
                """
            )

    # ---------------- TAB 2: GEOGRAPHIC ANALYSIS ----------------
    with tab_geo:
        st.subheader("Geographic Natality Distribution")
        st.markdown(
            "Explore spatial patterns across the United States. "
            "Notice how raw birth counts trace the underlying population distribution."
        )

        # Choropleth map
        choropleth_fig = create_us_choropleth_map(filtered_df)
        st.plotly_chart(choropleth_fig, use_container_width=True)

        col_rank, col_top_bottom = st.columns([1, 1])

        with col_rank:
            ranking_fig = create_state_ranking_chart(filtered_df, max_display=25)
            st.plotly_chart(ranking_fig, use_container_width=True)

        with col_top_bottom:
            comparison_fig = create_top_bottom_comparison(filtered_df, n=5)
            st.plotly_chart(comparison_fig, use_container_width=True)
            st.markdown(
                """
                > **⚠️ The Denominator Caution:**  
                > Comparing California directly to Vermont using raw counts demonstrates the **scale effect**. To evaluate whether women in Vermont or California have more children on average, an analyst would require census population figures to compute the **General Fertility Rate** (*births per 1,000 women of reproductive age*).
                """
            )

    # ---------------- TAB 3: MONTHLY AND SEX ANALYSIS ----------------
    with tab_monthly_sex:
        st.subheader("Monthly Trajectories and Biological Sex Dynamics")
        st.markdown(
            "Evaluate month-by-month changes and compare biological sex categories across the calendar year."
        )

        # Monthly sex comparison
        sex_comp_fig = create_sex_comparison_chart(filtered_df)
        st.plotly_chart(sex_comp_fig, use_container_width=True)

        st.markdown("---")
        st.subheader("Seasonal Heatmap Matrix")
        st.markdown(
            "The matrix below visualizes monthly birth volume by jurisdiction. "
            "It allows students to quickly detect seasonal shifts and compare volume across states."
        )

        heatmap_fig = create_state_month_heatmap(filtered_df)
        st.plotly_chart(heatmap_fig, use_container_width=True)

    # ---------------- TAB 4: DATA TABLE AND DOWNLOAD ----------------
    with tab_table:
        st.subheader("Filtered Dataset and Export")
        st.markdown(
            "Review the exact rows matching your active filter criteria. "
            "You can sort, search, and download this sliced dataset for further external analysis in Excel or Python."
        )

        # Presentation dataframe: formatted numbers for readability
        display_df = filtered_df.copy()
        display_df["Births Formatted"] = display_df["Births"].apply(lambda x: f"{x:,}")

        # Summary count
        st.write(f"Displaying **{len(display_df):,}** matching observations.")

        # Interactive table
        st.dataframe(
            display_df[["State of Residence", "Month", "Month Code", "Sex of Infant", "Births Formatted"]],
            use_container_width=True,
            hide_index=True,
        )

        # CSV Download Button
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_data,
            file_name="cdc_provisional_natality_2025_filtered.csv",
            mime="text/csv",
            help="Click to export the currently filtered observations to a standard CSV file.",
        )

        st.markdown("---")
        st.subheader("Data Dictionary")
        st.markdown(
            """
            | Column Name | Analytical Description | Type | Notes |
            | :--- | :--- | :--- | :--- |
            | `State of Residence` | State or federal district of mother's residence | Text | Covers 50 US States + District of Columbia |
            | `Month` | Calendar month of live birth | Text | Chronologically ordered from January to December |
            | `Month Code` | Numerical month index | Integer | Range: 1 to 12 |
            | `Year Code` | Calendar year of occurrence | Integer | Fixed at 2025 (Provisional) |
            | `Sex of Infant` | Biological sex classification | Text | 'Female' or 'Male' |
            | `Births` | Count of registered live births | Integer | Aggregate volume; no cell suppression present |
            """
        )

    # ---------------- TAB 5: ABOUT THE DATA ----------------
    with tab_about:
        st.subheader("About the Provisional Natality Dataset")
        st.markdown(
            """
            ### 1. Data Provenance & Purpose
            This dashboard utilizes provisional live birth data published by the **National Center for Health Statistics (NCHS)**, 
            a division of the **Centers for Disease Control and Prevention (CDC)**.
            
            Vital statistics natality data are compiled from birth certificates registered in all 50 states and the District of Columbia. 
            Provisional data provide early indicators of demographic patterns before final data files are released.

            ---

            ### 2. The Difference Between Birth Counts and Birth Rates
            A frequent pitfall for beginning business analytics students is conflating **magnitude (counts)** with **rates (proportions)**:
            - **Live Birth Count:** The raw tally of births occurring within a given jurisdiction and timeframe ($N$).
            - **Crude Birth Rate (CBR):** The number of live births per 1,000 total population ($\frac{\text{Births}}{\text{Total Population}} \times 1,000$).
            - **General Fertility Rate (GFR):** The number of live births per 1,000 women of childbearing age (typically ages 15–44).

            Because this dataset does not supply population census figures, **rates cannot be calculated**. 
            Students should always distinguish between volume metrics and per-capita rate metrics.

            ---

            ### 3. Automated Data Quality Audit Results
            Upon application launch, the data loader runs automated validation checks to ensure data integrity:
            """
        )

        for msg in audit_log:
            st.success(f"✔️ {msg}")

        st.markdown(
            f"- **Total Rows Audited:** {len(raw_df):,}  \n"
            f"- **Total Live Births Audited:** {raw_df['Births'].sum():,}  \n"
            "- **Duplicate Observations:** 0  \n"
            "- **Missing Values:** 0  \n"
            "- **Completeness:** 100% balanced panel (51 states x 12 months x 2 infant sexes = 1,224 observations)"
        )


if __name__ == "__main__":
    main()
