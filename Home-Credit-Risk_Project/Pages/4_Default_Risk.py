
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
    page_title="Default Risk Analysis",
    layout="wide"
)

st.title(" Default Risk Analysis")

st.caption(
    "Analyze loan default patterns and identify "
    "high-risk customer segments."
)

st.divider()


# ==========================================
# LOAD DATASET
# ==========================================

try:
    df = load_dataset(config.DATASET_FILES["application"])

except FileNotFoundError:
    st.error("application_train.csv was not found.")
    st.stop()


# ==========================================
# DATA VALIDATION
# ==========================================

required_columns = [
    "TARGET",
    "NAME_CONTRACT_TYPE",
    "CODE_GENDER",
    "NAME_EDUCATION_TYPE",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "DAYS_BIRTH"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
    st.stop()


# ==========================================
# DATA PREPARATION
# ==========================================

df["TARGET"] = pd.to_numeric(
    df["TARGET"],
    errors="coerce"
)

numeric_columns = [
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "DAYS_BIRTH"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


# Remove invalid target records
df = df[
    df["TARGET"].isin([0, 1])
].copy()


# ------------------------------------------
# Calculate Age
# ------------------------------------------

df["AGE"] = -df["DAYS_BIRTH"] / 365.25


# ------------------------------------------
# Create Age Groups
# ------------------------------------------

age_bins = [0, 25, 35, 45, 55, np.inf]

age_labels = [
    "≤ 25",
    "26 – 35",
    "36 – 45",
    "46 – 55",
    "≥ 56"
]

df["AGE_GROUP"] = pd.cut(
    df["AGE"],
    bins=age_bins,
    labels=age_labels,
    include_lowest=True
)


# ------------------------------------------
# Create Income Bands
# ------------------------------------------

income_bins = [
    -np.inf,
    75000,
    150000,
    300000,
    600000,
    np.inf
]

income_labels = [
    "< 75K",
    "75K – 150K",
    "150K – 300K",
    "300K – 600K",
    "≥ 600K"
]

df["INCOME_BAND"] = pd.cut(
    df["AMT_INCOME_TOTAL"],
    bins=income_bins,
    labels=income_labels,
    right=False
)


# ==========================================
# FILTER SECTION
# ==========================================

st.subheader(" Filters")

# Reset button
if st.button("Reset Filters"):

    filter_keys = [
        "contract_filter",
        "gender_filter",
        "education_filter",
        "income_filter",
        "age_filter"
    ]

    for key in filter_keys:
        st.session_state[key] = "All"

    st.rerun()


# Sidebar-style filter panel
filter_col, dashboard_col = st.columns(
    [1, 4],
    gap="medium"
)


with filter_col:

    st.markdown("### Filters")

    # Contract Type
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


    # Gender
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


    # Education
    education_options = [
        "All"
    ] + sorted(
        df["NAME_EDUCATION_TYPE"].dropna().unique().tolist()
    )

    education_filter = st.selectbox(
        "Education",
        education_options,
        key="education_filter"
    )


    # Income Band
    income_filter = st.selectbox(
        "Income Band",
        ["All"] + income_labels,
        key="income_filter"
    )


    # Age Group
    age_filter = st.selectbox(
        "Age Group",
        ["All"] + age_labels,
        key="age_filter"
    )


# ==========================================
# APPLY FILTERS
# ==========================================

filtered_df = df.copy()


# Contract Type Filter
if contract_filter != "All":

    filtered_df = filtered_df[
        filtered_df["NAME_CONTRACT_TYPE"] == contract_filter
    ]


# Gender Filter
if gender_filter != "All":

    filtered_df = filtered_df[
        filtered_df["CODE_GENDER"] == gender_filter
    ]


# Education Filter
if education_filter != "All":

    filtered_df = filtered_df[
        filtered_df["NAME_EDUCATION_TYPE"] == education_filter
    ]


# Income Band Filter
if income_filter != "All":

    filtered_df = filtered_df[
        filtered_df["INCOME_BAND"].astype(str) == income_filter
    ]


# Age Group Filter
if age_filter != "All":

    filtered_df = filtered_df[
        filtered_df["AGE_GROUP"].astype(str) == age_filter
    ]


# ==========================================
# CHECK FILTERED DATA
# ==========================================

if filtered_df.empty:

    st.warning(
        "No customer records found for the selected filters."
    )
    st.stop()


# ==========================================
# KPI METRICS
# ==========================================

with dashboard_col:

    st.subheader("Default Risk Overview")

    total_customers = len(filtered_df)

    total_defaults = (
        filtered_df["TARGET"] == 1
    ).sum()

    non_default_customers = (
        filtered_df["TARGET"] == 0
    ).sum()

    default_rate = (
        total_defaults / total_customers
    ) * 100

    default_df = filtered_df[
        filtered_df["TARGET"] == 1
    ]

    avg_credit_defaulters = (
        default_df["AMT_CREDIT"].mean()
    )

    avg_income_defaulters = (
        default_df["AMT_INCOME_TOTAL"].mean()
    )


    # High-risk count requires model-predicted probabilities.
    # Expected optional column: PREDICTED_PROBABILITY

    if "PREDICTED_PROBABILITY" in filtered_df.columns:

        predicted_probability = pd.to_numeric(
            filtered_df["PREDICTED_PROBABILITY"],
            errors="coerce"
        )

        high_risk_count = (
            predicted_probability >= 0.20
        ).sum()

        high_risk_value = f"{high_risk_count:,}"

    else:

        high_risk_value = "N/A"


    # Display six KPI cards
    k1, k2, k3, k4, k5, k6 = st.columns(6)


    with k1:
        st.metric(
            "Total Defaults",
            f"{total_defaults:,}"
        )


    with k2:
        st.metric(
            "Default Rate",
            f"{default_rate:.2f}%"
        )


    with k3:
        st.metric(
            "Non-default Customers",
            f"{non_default_customers:,}"
        )


    with k4:
        st.metric(
            "High-risk Applications",
            high_risk_value
        )


    with k5:
        st.metric(
            "Avg. Credit (Defaulters)",
            (
                f"{avg_credit_defaulters:,.0f}"
                if pd.notna(avg_credit_defaulters)
                else "N/A"
            )
        )


    with k6:
        st.metric(
            "Avg. Income (Defaulters)",
            (
                f"{avg_income_defaulters:,.0f}"
                if pd.notna(avg_income_defaulters)
                else "N/A"
            )
        )


    if "PREDICTED_PROBABILITY" not in filtered_df.columns:

        st.caption(
            "High-risk applications require model prediction "
            "probabilities. Connect your ML prediction output "
            "to calculate applications with PD ≥ 20%."
        )


# ==========================================
# CHART 1: DEFAULT VS NON-DEFAULT
# ==========================================

st.divider()

st.subheader("Default Risk Analysis")

chart1, chart2, chart3 = st.columns(3)


with chart1:

    status_df = pd.DataFrame({
        "Status": [
            "Default",
            "Non-default"
        ],
        "Customers": [
            total_defaults,
            non_default_customers
        ]
    })

    fig1 = px.pie(
        status_df,
        names="Status",
        values="Customers",
        hole=0.55,
        title="Default vs Non-default",
        color="Status",
        color_discrete_map={
            "Default": "#DC3545",
            "Non-default": "#14B8A6"
        }
    )

    fig1.update_traces(
        textinfo="percent+label"
    )

    fig1.update_layout(
        template="plotly_white",
        legend_title_text=""
    )

    fig1.add_annotation(
        text=f"{total_customers:,}<br>Applications",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=15)
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )


# ==========================================
# CHART 2: DEFAULT RATE BY GENDER
# ==========================================

with chart2:

    gender_summary = (
        filtered_df.groupby(
            "CODE_GENDER",
            observed=True
        )
        .agg(
            Customers=("TARGET", "count"),
            Default_Rate=("TARGET", "mean")
        )
        .reset_index()
    )

    gender_summary["Default_Rate"] *= 100

    gender_summary["Gender"] = (
        gender_summary["CODE_GENDER"].replace({
            "M": "Male",
            "F": "Female"
        })
    )

    fig2 = px.bar(
        gender_summary,
        x="Gender",
        y="Default_Rate",
        text="Default_Rate",
        title="Default Rate by Gender",
        color="Gender",
        color_discrete_map={
            "Female": "#14B8A6",
            "Male": "#DC3545"
        }
    )

    fig2.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig2.update_layout(
        template="plotly_white",
        showlegend=False,
        yaxis_title="Default Rate (%)"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# ==========================================
# CHART 3: DEFAULT RATE BY EDUCATION
# ==========================================

with chart3:

    education_summary = (
        filtered_df.groupby(
            "NAME_EDUCATION_TYPE",
            observed=True
        )
        .agg(
            Customers=("TARGET", "count"),
            Default_Rate=("TARGET", "mean")
        )
        .reset_index()
        .sort_values("Default_Rate")
    )

    education_summary["Default_Rate"] *= 100

    fig3 = px.bar(
        education_summary,
        x="Default_Rate",
        y="NAME_EDUCATION_TYPE",
        orientation="h",
        text="Default_Rate",
        title="Default Rate by Education",
        color_discrete_sequence=["#DC3545"]
    )

    fig3.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig3.update_layout(
        template="plotly_white",
        showlegend=False,
        xaxis_title="Default Rate (%)",
        yaxis_title=""
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )


# ==========================================
# CHART 4: DEFAULT RATE BY INCOME BAND
# ==========================================

chart4, chart5, chart6 = st.columns(3)


with chart4:

    income_summary = (
        filtered_df.groupby(
            "INCOME_BAND",
            observed=True
        )
        .agg(
            Customers=("TARGET", "count"),
            Default_Rate=("TARGET", "mean")
        )
        .reset_index()
    )

    income_summary["Default_Rate"] *= 100

    income_summary["INCOME_BAND"] = (
        income_summary["INCOME_BAND"].astype(str)
    )

    fig4 = px.bar(
        income_summary,
        x="INCOME_BAND",
        y="Default_Rate",
        text="Default_Rate",
        title="Default Rate by Income Band",
        color="Default_Rate",
        color_continuous_scale=[
            "#14B8A6",
            "#FCA5A5",
            "#DC3545"
        ]
    )

    fig4.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig4.update_layout(
        template="plotly_white",
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Income Band",
        yaxis_title="Default Rate (%)"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )


# ==========================================
# CHART 5: DEFAULT RATE BY AGE GROUP
# ==========================================

with chart5:

    age_summary = (
        filtered_df.groupby(
            "AGE_GROUP",
            observed=True
        )
        .agg(
            Customers=("TARGET", "count"),
            Default_Rate=("TARGET", "mean")
        )
        .reset_index()
    )

    age_summary["Default_Rate"] *= 100

    age_summary["AGE_GROUP"] = (
        age_summary["AGE_GROUP"].astype(str)
    )

    fig5 = px.bar(
        age_summary,
        x="AGE_GROUP",
        y="Default_Rate",
        text="Default_Rate",
        title="Default Rate by Age Group",
        color="Default_Rate",
        color_continuous_scale=[
            "#14B8A6",
            "#FCA5A5",
            "#DC3545"
        ]
    )

    fig5.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig5.update_layout(
        template="plotly_white",
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Age Group",
        yaxis_title="Default Rate (%)"
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )


# ==========================================
# CHART 6: DEFAULT RATE BY CONTRACT TYPE
# ==========================================

with chart6:

    contract_summary = (
        filtered_df.groupby(
            "NAME_CONTRACT_TYPE",
            observed=True
        )
        .agg(
            Customers=("TARGET", "count"),
            Default_Rate=("TARGET", "mean")
        )
        .reset_index()
    )

    contract_summary["Default_Rate"] *= 100

    fig6 = px.bar(
        contract_summary,
        x="NAME_CONTRACT_TYPE",
        y="Default_Rate",
        text="Default_Rate",
        title="Default Rate by Contract Type",
        color="Default_Rate",
        color_continuous_scale=[
            "#14B8A6",
            "#DC3545"
        ]
    )

    fig6.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig6.update_layout(
        template="plotly_white",
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Contract Type",
        yaxis_title="Default Rate (%)"
    )

    st.plotly_chart(
        fig6,
        use_container_width=True
    )


# ==========================================
# HIGH-RISK CUSTOMER SEGMENT TABLE
# ==========================================

st.divider()

st.subheader(" High-Risk Customer Segment (Sample)")

# Display actual defaulted customers
high_risk_df = filtered_df[
    filtered_df["TARGET"] == 1
].copy()


table_columns = [
    "SK_ID_CURR",
    "TARGET",
    "CODE_GENDER",
    "NAME_EDUCATION_TYPE",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "NAME_CONTRACT_TYPE",
    "DAYS_BIRTH"
]

table_columns = [
    col for col in table_columns
    if col in high_risk_df.columns
]


if not high_risk_df.empty:

    display_df = high_risk_df[
        table_columns
    ].head(10)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

#     # Download CSV
#     csv_data = high_risk_df[
#         table_columns
#     ].to_csv(index=False).encode("utf-8")

#     st.download_button(
#         label=" Download Table (CSV)",
#         data=csv_data,
#         file_name="high_risk_customers.csv",
#         mime="text/csv"
#     )

#     st.caption(
#         f"Showing {min(100, len(high_risk_df)):,} "
#         f"of {len(high_risk_df):,} defaulted applications."
#     )

# else:

#     st.info(
#         "No defaulted applications found "
#         "for the selected filters."
#     )
