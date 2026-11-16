import plotly.express as px 
import streamlit as st 
import pandas as pd 
import config
import numpy as np 
from Utils.data_loader import load_dataset


st.title(" Loan Application Analysis")
st.caption("Analyze loan amounts, contract types, ""income ratios and key application metrics"
)

# ============================
# Load Dataset
# ============================

try:
    df = load_dataset(config.DATASET_FILES["application"])
    
except FileNotFoundError:
    st.error("application_train.csv not found")
    st.stop()
    

# ===================================
# Data Validation
# ======================================

required_columns = [
    "NAME_CONTRACT_TYPE",
    "CODE_GENDER",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",
    "TARGET"
]

missing_columns=[
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
    st.stop()
    

# =================================================
# Data Preparation
# ===================================================

numeric_columns = [
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",
    "TARGET"
]

for col in numeric_columns:
    df[col]= pd.to_numeric(df[col], errors="coerce")
    
    
# Loan to income ratio
df["LOAN_TO_INCOME"] = (
    df["AMT_CREDIT"]/
    df["AMT_INCOME_TOTAL"].replace(0,np.nan)
)

# Annuity-to-income ratio
df["ANNUITY_TO_INCOME"] = (
    df["AMT_ANNUITY"] /
    df["AMT_INCOME_TOTAL"].replace(0, np.nan)
)

# Create income groups
df["INCOME_RANGE"] = pd.cut(
    df["AMT_INCOME_TOTAL"],
    bins=[-np.inf, 100000, 200000, 500000, np.inf],
    labels=[
        "Below 100K",
        "100K - 200K",
        "200K - 500K",
        "Above 500K"
    ],
    include_lowest=True
)

# Create credit amount groups
df["CREDIT_RANGE"] = pd.cut(
    df["AMT_CREDIT"],
    bins=[-np.inf, 250000, 500000, 1000000, np.inf],
    labels=[
        "Below 250K",
        "250K - 500K",
        "500K - 1M",
        "Above 1M"
    ],
    include_lowest=True
)

# ==========================================
# FILTER SECTION
# ==========================================

st.subheader(" Filters")

# Reset filter values
if st.button("Reset Filters"):
    for key in [
        "contract_filter",
        "gender_filter",
        "income_filter",
        "credit_filter",
        "target_filter"
    ]:
        st.session_state[key] = "All"

    st.rerun()


col1, col2, col3, col4, col5 = st.columns(5)


# Contract Type Filter
with col1:

    contract_options = ["All"] + sorted(
        df["NAME_CONTRACT_TYPE"].dropna().unique().tolist()
    )

    contract_filter = st.selectbox(
        "Contract Type",
        contract_options,
        key="contract_filter"
    )


# Gender Filter
with col2:

    gender_options = ["All"] + sorted(
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


# Income Range Filter
with col3:

    income_options = [
        "All",
        "Below 100K",
        "100K - 200K",
        "200K - 500K",
        "Above 500K"
    ]

    income_filter = st.selectbox(
        "Income Range",
        income_options,
        key="income_filter"
    )


# Credit Amount Filter
with col4:

    credit_options = [
        "All",
        "Below 250K",
        "250K - 500K",
        "500K - 1M",
        "Above 1M"
    ]

    credit_filter = st.selectbox(
        "Credit Amount Range",
        credit_options,
        key="credit_filter"
    )


# Target Filter
with col5:

    target_filter = st.selectbox(
        "Target (Default)",
        [
            "All",
            "Non-default",
            "Default"
        ],
        key="target_filter"
    )


# ==========================================
# APPLY FILTERS
# ==========================================

filtered_df = df.copy()


# Contract filter
if contract_filter != "All":

    filtered_df = filtered_df[
        filtered_df["NAME_CONTRACT_TYPE"] == contract_filter
    ]


# Gender filter
if gender_filter != "All":

    filtered_df = filtered_df[
        filtered_df["CODE_GENDER"] == gender_filter
    ]


# Income filter
if income_filter != "All":

    filtered_df = filtered_df[
        filtered_df["INCOME_RANGE"].astype(str) == income_filter
    ]


# Credit amount filter
if credit_filter != "All":

    filtered_df = filtered_df[
        filtered_df["CREDIT_RANGE"].astype(str) == credit_filter
    ]


# Target filter
if target_filter == "Non-default":

    filtered_df = filtered_df[
        filtered_df["TARGET"] == 0
    ]

elif target_filter == "Default":

    filtered_df = filtered_df[
        filtered_df["TARGET"] == 1
    ]


st.divider()


# ==========================================
# KPI METRICS
# ==========================================

st.subheader(" Loan Application Overview")

if filtered_df.empty:

    st.warning("No applications found for the selected filters.")
    st.stop()


total_loan_amount = filtered_df["AMT_CREDIT"].sum()

average_loan_amount = filtered_df["AMT_CREDIT"].mean()

median_loan_amount = filtered_df["AMT_CREDIT"].median()

average_loan_income = filtered_df["LOAN_TO_INCOME"].mean()

average_annuity_income = filtered_df["ANNUITY_TO_INCOME"].mean()

cash_loan_count = (
    filtered_df["NAME_CONTRACT_TYPE"] == "Cash loans"
).sum()

cash_loan_share = (
    cash_loan_count / len(filtered_df)
) * 100

average_goods_price = filtered_df["AMT_GOODS_PRICE"].mean()


# Display seven KPI cards
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6, kpi7 = st.columns(7)


with kpi1:
    st.metric(
        "Total Loan Amount",
        f"{total_loan_amount:,.0f}"
    )

with kpi2:
    st.metric(
        "Average Loan Amount",
        f"{average_loan_amount:,.2f}"
    )

with kpi3:
    st.metric(
        "Median Loan Amount",
        f"{median_loan_amount:,.2f}"
    )

with kpi4:
    st.metric(
        "Avg. Loan-to-Income",
        f"{average_loan_income:.2f}"
    )

with kpi5:
    st.metric(
        "Avg. Annuity-to-Income",
        f"{average_annuity_income:.2f}"
    )

with kpi6:
    st.metric(
        "Cash Loan Share",
        f"{cash_loan_share:.2f}%"
    )

with kpi7:
    st.metric(
        "Avg. Goods Price",
        f"{average_goods_price:,.2f}"
    )


st.caption(
    f"Total Applications: {len(filtered_df):,}"
)

st.divider()
# ====================================
# Chart 1: Loan Amount Distribution
# =========================================

st.subheader("Loan Amount Distribution")

col1, col2 = st.columns(2)

with col1:
    fig_loan = px.histogram(
        filtered_df,
        x = "AMT_CREDIT",
        nbins= 40,
        title="Distribution of loan amount",
        labels ={
            "AMT_CREDIT":"Loan Amount",
            "count": "Number of Applications"
        },
        color_discrete_sequence=[config.CHART_COLORS[0]]
    )
    
    fig_loan.update_layout(template ="plotly_white", bargap =0.05 )

    st.plotly_chart(fig_loan, use_container_width=True)
    

# =============================================
# Chart 2 : CREDIT AMOUNT BY CONTRACT TYPE
# ==============================================


with col2:

    contract_summary = (
        filtered_df.groupby(
            "NAME_CONTRACT_TYPE"
        )["AMT_CREDIT"]
        .sum()
        .reset_index()
    )

    fig2 = px.bar(
        contract_summary,
        x="NAME_CONTRACT_TYPE",
        y="AMT_CREDIT",
        text="AMT_CREDIT",
        title="Credit Amount by Contract Type",
        labels={
            "NAME_CONTRACT_TYPE": "Contract Type",
            "AMT_CREDIT": "Total Credit Amount"
        },
        color="NAME_CONTRACT_TYPE",
        color_discrete_sequence=[
            "#0D9488",
            "#F97316"
        ]
    )

    fig2.update_traces(
        texttemplate="%{text:.3s}",
        textposition="outside"
    )

    fig2.update_layout(
        template="plotly_white",
        showlegend=False
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


st.divider()


# ==========================================
# CHART 3: LOAN-TO-INCOME DISTRIBUTION
# ==========================================

st.subheader("Loan-to-Income Distribution")

col1, col2, col3 = st.columns([1, 1, 1])


with col1:

    ratio_data = filtered_df[
        "LOAN_TO_INCOME"
    ].dropna()

    ratio_data = ratio_data[
        (ratio_data >= 0) &
        (ratio_data <= 10)
    ]

    if not ratio_data.empty:

        fig3 = px.histogram(
            ratio_data,
            x="LOAN_TO_INCOME",
            nbins=40,
            histnorm="probability density",
            title="Loan-to-Income Ratio",
            labels={
                "LOAN_TO_INCOME": "AMT_CREDIT / AMT_INCOME_TOTAL",
                "density": "Density"
            },
            color_discrete_sequence=[
                "#14B8A6"
            ]
        )

        fig3.update_layout(
            template="plotly_white"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    else:
        st.info("Loan-to-income data unavailable.")


# ==========================================
# CHART 4: ANNUITY-TO-INCOME BY DEFAULT
# ==========================================

with col2:

    annuity_summary = (
        filtered_df.dropna(
            subset=["TARGET", "ANNUITY_TO_INCOME"]
        )
        .groupby("TARGET")
        ["ANNUITY_TO_INCOME"]
        .mean()
        .reset_index()
    )

    annuity_summary["Default Status"] = (
        annuity_summary["TARGET"].map({
            0: "Non-default",
            1: "Default"
        })
    )

    fig4 = px.bar(
        annuity_summary,
        x="Default Status",
        y="ANNUITY_TO_INCOME",
        text="ANNUITY_TO_INCOME",
        color="Default Status",
        title="Annuity-to-Income Comparison",
        labels={
            "ANNUITY_TO_INCOME": "Average Annuity-to-Income"
        },
        color_discrete_map={
            "Non-default": "#0D9488",
            "Default": "#F97316"
        }
    )

    fig4.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig4.update_layout(
        template="plotly_white",
        showlegend=False
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )


# ==========================================
# CHART 5: CONTRACT TYPE SHARE
# ==========================================

with col3:

    contract_count = (
        filtered_df["NAME_CONTRACT_TYPE"]
        .value_counts()
        .reset_index()
    )

    contract_count.columns = [
        "Contract Type",
        "Applications"
    ]

    fig5 = px.pie(
        contract_count,
        names="Contract Type",
        values="Applications",
        hole=0.55,
        title="Contract Type Share",
        color_discrete_sequence=[
            "#0D9488",
            "#F97316"
        ]
    )

    fig5.update_traces(
        textinfo="percent+label"
    )

    fig5.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )


st.divider()


# ==========================================
# LOAN APPLICATION DETAILS TABLE
# ==========================================

st.subheader(" Loan Application Details")

table_columns = [
    "SK_ID_CURR",
    "NAME_CONTRACT_TYPE",
    "AMT_CREDIT",
    "AMT_INCOME_TOTAL",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",
    "TARGET"
]

# Select only existing columns
table_columns = [
    col for col in table_columns
    if col in filtered_df.columns
]

st.dataframe(
    filtered_df[table_columns].head(5),
    use_container_width=True,
    hide_index=True
)

st.caption(
    f"Showing {min(20, len(filtered_df)):,} "
    f"of {len(filtered_df):,} applications."
)

