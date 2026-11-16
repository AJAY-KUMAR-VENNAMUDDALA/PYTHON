
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

import config
from Utils.data_loader import load_dataset


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Credit Bureau Analysis",
    layout="wide"
)

st.title("Credit Bureau Analysis")

st.caption(
    "Analysis of customers' external credit history "
    "from the bureau dataset."
)


# ==========================================
# LOAD DATASETS
# ==========================================

try:
    bureau = load_dataset(
        config.DATASET_FILES["bureau"]
    )

    application = load_dataset(
        config.DATASET_FILES["application"]
    )

except FileNotFoundError:
    st.error(
        "Required dataset not found. "
        "Please check application_train.csv and bureau.csv."
    )
    st.stop()


# ==========================================
# DATA VALIDATION
# ==========================================

bureau_required = [
    "SK_ID_CURR",
    "SK_ID_BUREAU",
    "CREDIT_ACTIVE",
    "DAYS_CREDIT",
    "AMT_CREDIT_SUM",
    "AMT_CREDIT_SUM_DEBT",
    "AMT_CREDIT_SUM_OVERDUE",
    "CREDIT_DAY_OVERDUE"
]

application_required = [
    "SK_ID_CURR",
    "NAME_CONTRACT_TYPE",
    "CODE_GENDER",
    "TARGET",
    "NAME_EDUCATION_TYPE"
]

missing_bureau = [
    col for col in bureau_required
    if col not in bureau.columns
]

missing_application = [
    col for col in application_required
    if col not in application.columns
]

if missing_bureau or missing_application:

    st.error(
        f"Missing bureau columns: {missing_bureau}\n\n"
        f"Missing application columns: {missing_application}"
    )
    st.stop()


# ==========================================
# DATA PREPARATION
# ==========================================

bureau_numeric = [
    "DAYS_CREDIT",
    "AMT_CREDIT_SUM",
    "AMT_CREDIT_SUM_DEBT",
    "AMT_CREDIT_SUM_OVERDUE",
    "CREDIT_DAY_OVERDUE"
]

for col in bureau_numeric:
    bureau[col] = pd.to_numeric(
        bureau[col],
        errors="coerce"
    )


application["TARGET"] = pd.to_numeric(
    application["TARGET"],
    errors="coerce"
)


# Remove duplicate customer records in application
application_info = (
    application[
        [
            "SK_ID_CURR",
            "NAME_CONTRACT_TYPE",
            "CODE_GENDER",
            "TARGET",
            "NAME_EDUCATION_TYPE"
        ]
    ]
    .drop_duplicates(subset=["SK_ID_CURR"])
)


# ==========================================
# MERGE BUREAU AND APPLICATION
# ==========================================

df = bureau.merge(
    application_info,
    on="SK_ID_CURR",
    how="left",
    validate="many_to_one"
)


# Replace missing categorical values
categorical_columns = [
    "CREDIT_ACTIVE",
    "NAME_CONTRACT_TYPE",
    "CODE_GENDER",
    "NAME_EDUCATION_TYPE"
]

for col in categorical_columns:
    df[col] = df[col].fillna("Unknown")


# ==========================================
# CREDIT DURATION PREPARATION
# ==========================================

# DAYS_CREDIT is negative for previous credit history.
# Use absolute value for duration analysis.

df["CREDIT_DURATION"] = (
    df["DAYS_CREDIT"].abs()
)


# ==========================================
# FILTER SECTION
# ==========================================

st.subheader("Filters")


# Get DAYS_CREDIT range
valid_days = df["DAYS_CREDIT"].dropna()

if valid_days.empty:
    st.error("DAYS_CREDIT contains no valid values.")
    st.stop()

min_days = int(np.floor(valid_days.min()))
max_days = int(np.ceil(valid_days.max()))


# Reset Filters
if st.button("Reset Filters"):

    st.session_state["contract_filter"] = "All"
    st.session_state["gender_filter"] = "All"
    st.session_state["credit_status_filter"] = "All"
    st.session_state["days_credit_range"] = (
        min_days,
        max_days
    )

    st.rerun()


filter1, filter2, filter3, filter4 = st.columns(4)


# ------------------------------------------
# Contract Type Filter
# ------------------------------------------

with filter1:

    contract_options = [
        "All"
    ] + sorted(
        df["NAME_CONTRACT_TYPE"].dropna().unique().tolist()
    )

    contract_filter = st.selectbox(
        "Contract Type",
        contract_options,
        key="contract_filter"
    )


# ------------------------------------------
# Gender Filter
# ------------------------------------------

with filter2:

    gender_options = [
        "All"
    ] + sorted(
        df["CODE_GENDER"].dropna().unique().tolist()
    )

    gender_filter = st.selectbox(
        "Gender",
        gender_options,
        format_func=lambda x: {
            "M": "Male",
            "F": "Female"
        }.get(x, x),
        key="gender_filter"
    )


# ------------------------------------------
# Credit Active Status Filter
# ------------------------------------------

with filter3:

    credit_status_options = [
        "All"
    ] + sorted(
        df["CREDIT_ACTIVE"].dropna().unique().tolist()
    )

    credit_status_filter = st.selectbox(
        "Credit Active Status",
        credit_status_options,
        key="credit_status_filter"
    )


# ------------------------------------------
# Days Credit Filter
# ------------------------------------------

with filter4:

    days_credit_range = st.slider(
        "Date Range (Days Credit)",
        min_value=min_days,
        max_value=max_days,
        value=(min_days, max_days),
        key="days_credit_range"
    )


# ==========================================
# APPLY FILTERS
# ==========================================

filtered_df = df.copy()


# Contract Type
if contract_filter != "All":

    filtered_df = filtered_df[
        filtered_df["NAME_CONTRACT_TYPE"]
        == contract_filter
    ]


# Gender
if gender_filter != "All":

    filtered_df = filtered_df[
        filtered_df["CODE_GENDER"]
        == gender_filter
    ]


# Credit Active Status
if credit_status_filter != "All":

    filtered_df = filtered_df[
        filtered_df["CREDIT_ACTIVE"]
        == credit_status_filter
    ]


# DAYS_CREDIT range
filtered_df = filtered_df[
    filtered_df["DAYS_CREDIT"].between(
        days_credit_range[0],
        days_credit_range[1]
    )
]


# ==========================================
# CHECK FILTERED DATA
# ==========================================

if filtered_df.empty:

    st.warning(
        "No credit bureau records found for the selected filters."
    )
    st.stop()


st.divider()


# ==========================================
# KPI METRICS
# ==========================================

st.subheader("Credit Bureau Overview")


# Total customers with bureau history
customers_with_history = (
    filtered_df["SK_ID_CURR"].nunique()
)


# Average bureau credit amount per record
average_bureau_credit = (
    filtered_df["AMT_CREDIT_SUM"].mean()
)

median_bureau_credit = (
    filtered_df["AMT_CREDIT_SUM"].median()
)


# Active bureau loans
active_loans = (
    filtered_df["CREDIT_ACTIVE"] == "Active"
).sum()


total_bureau_records = len(filtered_df)

active_loan_percentage = (
    active_loans / total_bureau_records
) * 100


# Total overdue amount
total_overdue_amount = (
    filtered_df["AMT_CREDIT_SUM_OVERDUE"].sum()
)


# Average credit duration
average_credit_duration = (
    filtered_df["CREDIT_DURATION"].mean()
)


# Bureau-linked default rate:
# Use unique customers to avoid counting customers
# multiple times when they have multiple bureau records.

customer_target = (
    filtered_df[
        ["SK_ID_CURR", "TARGET"]
    ]
    .drop_duplicates(subset=["SK_ID_CURR"])
)

bureau_default_rate = (
    customer_target["TARGET"].mean() * 100
)


# ==========================================
# DISPLAY SIX KPI CARDS
# ==========================================

k1, k2, k3, k4, k5, k6 = st.columns(6)


with k1:

    st.metric(
        "Customers with Bureau History",
        f"{customers_with_history:,}"
    )


with k2:

    st.metric(
        "Average Bureau Credit",
        (
            f"{average_bureau_credit:,.0f}"
            if pd.notna(average_bureau_credit)
            else "N/A"
        )
    )

    st.caption(
        f"Median: {median_bureau_credit:,.0f}"
        if pd.notna(median_bureau_credit)
        else "Median: N/A"
    )


with k3:

    st.metric(
        "Active Bureau Loans",
        f"{active_loans:,}"
    )

    st.caption(
        f"{active_loan_percentage:.2f}% of bureau records"
    )


with k4:

    st.metric(
        "Overdue Bureau Amount",
        f"{total_overdue_amount:,.0f}"
    )


with k5:

    st.metric(
        "Average Credit Duration",
        (
            f"{average_credit_duration:,.0f} Days"
            if pd.notna(average_credit_duration)
            else "N/A"
        )
    )

    if pd.notna(average_credit_duration):
        st.caption(
            f"≈ {average_credit_duration / 365.25:.2f} years"
        )


with k6:

    st.metric(
        "Bureau-Linked Default Rate",
        (
            f"{bureau_default_rate:.2f}%"
            if pd.notna(bureau_default_rate)
            else "N/A"
        )
    )


st.caption(
    f"Total Bureau Records: {len(filtered_df):,}"
)

st.divider()


# ==========================================
# CHART 1: ACTIVE VS CLOSED BUREAU CREDITS
# ==========================================

st.subheader("Credit History Analysis")

chart1, chart2, chart3 = st.columns(3)


with chart1:

    active_closed = (
        filtered_df["CREDIT_ACTIVE"]
        .value_counts()
        .reset_index()
    )

    active_closed.columns = [
        "Credit Status",
        "Credits"
    ]

    fig1 = px.pie(
        active_closed,
        names="Credit Status",
        values="Credits",
        hole=0.55,
        title="Active vs Closed Bureau Credits",
        color="Credit Status",
        color_discrete_map={
            "Active": "#0563D6",
            "Closed": "#82B9F5",
            "Sold": "#F59E0B",
            "Bad debt": "#DC3545",
            "Unknown": "#94A3B8"
        }
    )

    fig1.update_traces(
        textinfo="percent+label"
    )

    fig1.update_layout(
        template="plotly_white"
    )

    fig1.add_annotation(
        text=f"{total_bureau_records:,}<br>Bureau Credits",
        x=0.5,
        y=0.5,
        showarrow=False
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )


# ==========================================
# CHART 2: CREDIT STATUS DISTRIBUTION
# ==========================================

with chart2:

    status_summary = (
        filtered_df["CREDIT_ACTIVE"]
        .value_counts(normalize=True)
        .mul(100)
        .reset_index()
    )

    status_summary.columns = [
        "Credit Status",
        "Percentage"
    ]

    fig2 = px.bar(
        status_summary,
        x="Credit Status",
        y="Percentage",
        text="Percentage",
        title="Credit Status Distribution",
        color="Credit Status",
        color_discrete_map={
            "Active": "#0563D6",
            "Closed": "#82B9F5",
            "Sold": "#A78BFA",
            "Bad debt": "#DC3545",
            "Unknown": "#94A3B8"
        }
    )

    fig2.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig2.update_layout(
        template="plotly_white",
        showlegend=False,
        yaxis_title="Share of Credits (%)"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# ==========================================
# CHART 3: OVERDUE AMOUNT DISTRIBUTION
# ==========================================

with chart3:

    overdue_data = filtered_df[
        "AMT_CREDIT_SUM_OVERDUE"
    ].dropna()

    overdue_bins = [
        -np.inf,
        0,
        1000,
        5000,
        10000,
        50000,
        np.inf
    ]

    overdue_labels = [
        "0",
        "(0–1K]",
        "(1K–5K]",
        "(5K–10K]",
        "(10K–50K]",
        "> 50K"
    ]

    overdue_groups = pd.cut(
        overdue_data,
        bins=overdue_bins,
        labels=overdue_labels,
        right=True
    )

    overdue_summary = (
        overdue_groups
        .value_counts(sort=False)
        .reset_index()
    )

    overdue_summary.columns = [
        "Overdue Range",
        "Number of Credits"
    ]

    fig3 = px.bar(
        overdue_summary,
        x="Overdue Range",
        y="Number of Credits",
        text="Number of Credits",
        title="Overdue Amount Distribution",
        color_discrete_sequence=[
            "#DC3545"
        ]
    )

    fig3.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig3.update_layout(
        template="plotly_white",
        yaxis_title="Number of Credits"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )


st.divider()


# ==========================================
# CHART 4: BUREAU CREDIT AMOUNT BY EDUCATION
# ==========================================

chart4, chart5 = st.columns(2)


with chart4:

    education_summary = (
        filtered_df[
            filtered_df["NAME_EDUCATION_TYPE"] != "Unknown"
        ]
        .groupby("NAME_EDUCATION_TYPE")
        .agg(
            Average_Credit=("AMT_CREDIT_SUM", "mean"),
            Customers=("SK_ID_CURR", "nunique")
        )
        .reset_index()
        .sort_values(
            "Average_Credit",
            ascending=False
        )
    )

    fig4 = px.bar(
        education_summary,
        x="Average_Credit",
        y="NAME_EDUCATION_TYPE",
        orientation="h",
        text="Average_Credit",
        title="Bureau Credit Amount by Customer Segment",
        labels={
            "Average_Credit": "Average Bureau Credit Amount",
            "NAME_EDUCATION_TYPE": "Education"
        },
        color_discrete_sequence=[
            "#0563D6"
        ]
    )

    fig4.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig4.update_layout(
        template="plotly_white",
        yaxis={
            "categoryorder": "total ascending"
        }
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )


# ==========================================
# CHART 5: CREDIT DURATION DISTRIBUTION
# ==========================================

with chart5:

    duration_bins = [
        0,
        180,
        365,
        730,
        1095,
        1825,
        2555,
        np.inf
    ]

    duration_labels = [
        "0–180",
        "181–365",
        "366–730",
        "731–1,095",
        "1,096–1,825",
        "1,826–2,555",
        "> 2,555"
    ]

    duration_groups = pd.cut(
        filtered_df["CREDIT_DURATION"],
        bins=duration_bins,
        labels=duration_labels,
        include_lowest=True
    )

    duration_summary = (
        duration_groups
        .value_counts(sort=False)
        .reset_index()
    )

    duration_summary.columns = [
        "Credit Duration",
        "Number of Credits"
    ]

    fig5 = px.bar(
        duration_summary,
        x="Credit Duration",
        y="Number of Credits",
        text="Number of Credits",
        title="Credit Duration Distribution",
        color_discrete_sequence=[
            "#A78BFA"
        ]
    )

    fig5.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig5.update_layout(
        template="plotly_white",
        xaxis_title="Credit Duration (Days)",
        yaxis_title="Number of Credits"
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )


st.divider()


# ==========================================
# BUREAU CREDIT RECORDS TABLE
# ==========================================

st.subheader("Bureau Credit Records (Sample)")


table_columns = [
    "SK_ID_CURR",
    "SK_ID_BUREAU",
    "CREDIT_ACTIVE",
    "CREDIT_CURRENCY",
    "DAYS_CREDIT",
    "AMT_CREDIT_SUM",
    "AMT_CREDIT_SUM_DEBT",
    "AMT_CREDIT_SUM_OVERDUE",
    "CREDIT_DAY_OVERDUE"
]


table_columns = [
    col for col in table_columns
    if col in filtered_df.columns
]


st.dataframe(
    filtered_df[
        table_columns
    ].head(10),
    use_container_width=True,
    hide_index=True
)


# # ==========================================
# # DOWNLOAD CSV
# # ==========================================

# csv_data = filtered_df[
#     table_columns
# ].to_csv(index=False).encode("utf-8")


# st.download_button(
#     label="⬇️ Download Bureau Data (CSV)",
#     data=csv_data,
#     file_name="credit_bureau_analysis.csv",
#     mime="text/csv"
# )


# st.caption(
#     f"Showing {min(20, len(filtered_df)):,} "
#     f"of {len(filtered_df):,} bureau records."
# )
