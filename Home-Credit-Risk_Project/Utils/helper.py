import pandas as pd
import numpy as np

# =========================================
# 1. Rate Default Risk
# =========================================

def calculate_default_rate(df):
    if 'TARGET' not in df.columns or df.empty:
        return 0.0
    
    target = pd.to_numeric(df['TARGET'], errors='coerce')
    return target.mean() * 100


# ========================================
# 2. Calculate Average Income
# ========================================

def get_average_income(series):
    return pd.to_numeric(series, errors='coerce').mean()

# ========================================
# 3.Median
# ======================================

def get_median(series):
    return pd.to_numeric(series, errors='coerce').median()

# ========================================
# 4. Age Calculation
# ========================================

def calculate_age(df):
    if "DAYS_BIRTH" not in df.columns or df.empty:
        return pd.Series(
            np.nan, index=df.index
        )
    
    return (
        -pd.to_numeric(
            df["DAYS_BIRTH"],
            errors="coerce"
        ) / 365.25
    )
    
    
# ==========================================
# 5. AGE GROUPS
# ==========================================

def create_age_groups(age):

    bins = [
        0, 25, 30, 35, 40,
        45, 50, 55, 60, 120
    ]

    labels = [
        "Below 25",
        "25-29",
        "30-34",
        "35-39",
        "40-44",
        "45-49",
        "50-54",
        "55-59",
        "60 and above"
    ]

    return pd.cut(
        age,
        bins=bins,
        labels=labels,
        right=False
    )
# ==========================================
# 6. INCOME GROUPS
# ==========================================

def create_income_groups(income):

    bins = [
        0, 75000, 150000,
        300000, 600000,
        np.inf
    ]

    labels = [
        "Below 75K",
        "75K-150K",
        "150K-300K",
        "300K-600K",
        "Above 600K"
    ]

    return pd.cut(
        income,
        bins=bins,
        labels=labels
    )


# ==========================================
# 7. CURRENCY FORMATTING
# ==========================================

def format_currency(value):

    if pd.isna(value):
        return "N/A"

    return f"₹{value:,.2f}"


# ==========================================
# 8. PERCENTAGE FORMATTING
# ==========================================

def format_percentage(value):

    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}%"


# ==========================================
# 9. MISSING VALUE ANALYSIS
# ==========================================

def get_missing_values(df):

    missing = df.isnull().sum()

    missing_df = pd.DataFrame({
        "Column": missing.index,
        "Missing_Count": missing.values
    })

    missing_df["Missing_Percentage"] = (
        missing_df["Missing_Count"]
        / len(df) * 100
    ).round(2) if len(df) else 0

    return missing_df.sort_values(
        by="Missing_Count",
        ascending=False
    )
