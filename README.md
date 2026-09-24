# CDC Provisional Natality 2025 Dashboard

An interactive, educational Streamlit dashboard designed for undergraduate business analytics students to explore geographic, seasonal, and biological sex dynamics in provisional 2025 US live birth counts from the Centers for Disease Control and Prevention (CDC).

---

## Key Features

1. **Strict Data Integrity:**
   - Adheres strictly to CDC vital statistics principles: all figures are **counts**, not birth rates.
   - Built-in automated audit assertions verifying 1,224 observations, 51 geographies, 12 months, and 3,604,640 total births.
   - Preserves chronological month ordering (`January` to `December`).

2. **Interactive Analytics:**
   - **Sidebar Filtering:** Multiselect states, months, and infant sexes, with quick "Select All" and "Reset Filters" toggles.
   - **5 Dynamic KPI Cards:** Tracks total births, geography coverage, average monthly volume, top state, and peak month.
   - **5 Educational Dashboard Tabs:**
     - `📊 Overview`: High-level monthly trajectory, aggregate sex breakdown, and core analytics takeaways.
     - `🗺️ Geographic Analysis`: Interactive US state choropleth map, ranked bar chart, and Top 5 vs. Bottom 5 volume comparison.
     - `📈 Monthly and Sex Analysis`: Grouped monthly comparison by sex, and a state-by-month seasonal heatmap.
     - `📋 Data Table and Download`: Filtered interactive table with search and 1-click CSV download.
     - `📖 About the Data`: Background on vital statistics, the "Denominator Problem", and audit logs.

3. **Accessible & Defensive Visualization Design:**
   - Non-zero baselines are prohibited for magnitude comparisons (`rangemode='tozero'`).
   - Clean, colorblind-friendly color palettes (deep teal, indigo, and ocean blue).
   - Clear empty-state messaging when filters yield zero records.

---

## Directory Structure

```text
cdc-births-2025/
├── app.py                     # Main dashboard application
├── requirements.txt           # Python dependency specifications
├── README.md                  # Project overview and student instructions
├── utils/
│   ├── __init__.py
│   ├── data_loader.py         # Cached loader, validation assertions, state abbreviation map
│   ├── metrics.py             # KPI calculation engine
│   └── charts.py              # Plotly chart builders with zero-baseline axes
└── data/
    └── Provisional_Natality_2025_CDC.xlsx  # Original untouched CDC source data
```

---

## Quickstart Guide

### 1. Install Dependencies
Ensure you have Python 3.9+ installed, then install the required packages:

```bash
pip install -r requirements.txt
```

### 2. Launch the Streamlit Dashboard

```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.
