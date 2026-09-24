"""
data_loader.py
==============
Data loading, validation, and preprocessing module for the CDC 2025 Natality Dashboard.

Designed for undergraduate business analytics students to understand data auditing,
categorical ordering, and defensive programming in analytics pipelines.
"""

from pathlib import Path
from typing import Dict, Tuple
import pandas as pd
import streamlit as st

# Comprehensive mapping of all 50 states + District of Columbia to standard 2-letter postal codes.
# This mapping is required by Plotly's choropleth maps (locationmode='USA-states').
STATE_TO_ABBR: Dict[str, str] = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}

# Chronological order of calendar months to avoid alphabetical sorting (April before January)
MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

EXPECTED_ROWS = 1224
EXPECTED_TOTAL_BIRTHS = 3604640
EXPECTED_GEOGRAPHIES = 51
EXPECTED_MONTHS = 12
EXPECTED_SEX_CATEGORIES = 2


def validate_data(df: pd.DataFrame) -> Tuple[bool, list]:
    """
    Performs data quality audit assertions on the ingested dataset.
    
    Returns a tuple of (is_valid: bool, audit_messages: list).
    If any critical assertion fails, the dashboard can notify the user immediately.
    """
    audit_messages = []
    is_valid = True

    # Check 1: Row count
    if len(df) != EXPECTED_ROWS:
        is_valid = False
        audit_messages.append(f"Row count mismatch: expected {EXPECTED_ROWS:,}, found {len(df):,}")
    else:
        audit_messages.append(f"Row count check passed ({EXPECTED_ROWS:,} observations)")

    # Check 2: Missing values
    missing_count = df.isnull().sum().sum()
    if missing_count > 0:
        is_valid = False
        audit_messages.append(f"Missing values detected: {missing_count} null cells found")
    else:
        audit_messages.append("Missing values check passed (0 null values)")

    # Check 3: Total birth count sum check
    total_births = df["Births"].sum()
    if total_births != EXPECTED_TOTAL_BIRTHS:
        is_valid = False
        audit_messages.append(f"Total births mismatch: expected {EXPECTED_TOTAL_BIRTHS:,}, found {total_births:,}")
    else:
        audit_messages.append(f"Total sum integrity passed ({EXPECTED_TOTAL_BIRTHS:,} live births)")

    # Check 4: Geographies count
    geo_count = df["State of Residence"].nunique()
    if geo_count != EXPECTED_GEOGRAPHIES:
        is_valid = False
        audit_messages.append(f"Geography count mismatch: expected {EXPECTED_GEOGRAPHIES}, found {geo_count}")
    else:
        audit_messages.append(f"Geography coverage check passed ({EXPECTED_GEOGRAPHIES} states & DC)")

    # Check 5: Month count and consistency
    month_count = df["Month"].nunique()
    if month_count != EXPECTED_MONTHS:
        is_valid = False
        audit_messages.append(f"Month count mismatch: expected {EXPECTED_MONTHS}, found {month_count}")
    else:
        audit_messages.append(f"Monthly coverage check passed ({EXPECTED_MONTHS} months)")

    # Check 6: Infant sex categories
    sex_count = df["Sex of Infant"].nunique()
    if sex_count != EXPECTED_SEX_CATEGORIES:
        is_valid = False
        audit_messages.append(f"Sex category mismatch: expected {EXPECTED_SEX_CATEGORIES}, found {sex_count}")
    else:
        audit_messages.append(f"Sex categories check passed ({EXPECTED_SEX_CATEGORIES} categories)")

    return is_valid, audit_messages


@st.cache_data(show_spinner="Loading and verifying CDC natality dataset...")
def load_and_preprocess_data() -> Tuple[pd.DataFrame, bool, list]:
    """
    Loads the CDC Excel workbook using a cross-platform relative path,
    runs automated quality checks, and applies clean categorical typing.
    
    Cached using st.cache_data for instant repeat performance.
    """
    # Cross-platform path resolution: works both locally and in Streamlit Community Cloud
    base_dir = Path(__file__).resolve().parent.parent
    data_path = base_dir / "data" / "Provisional_Natality_2025_CDC.xlsx"

    if not data_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at expected location: {data_path}. "
            "Please ensure 'data/Provisional_Natality_2025_CDC.xlsx' exists."
        )

    # Read the first worksheet (index 0) to avoid failures if sheet name formatting differs
    df = pd.read_excel(data_path, sheet_name=0)

    # Clean whitespace in column names if any
    df.columns = df.columns.str.strip()

    # Run audit assertions
    is_valid, audit_log = validate_data(df)

    # Add standard two-letter state postal abbreviations for choropleth mapping
    df["State Abbr"] = df["State of Residence"].map(STATE_TO_ABBR)

    # Ensure chronological categorical sorting for months so charts preserve calendar order
    df["Month"] = pd.Categorical(df["Month"], categories=MONTH_ORDER, ordered=True)

    return df, is_valid, audit_log
