import os

APP_TITLE = "Home Credit Risk Analytics"

APP_ICON = ":house:"

LAYOUT = "wide"

INITIAL_SIDEBAR_STATE = "expanded"

# ==========================================
# DASHBOARD COLORS
# ==========================================

PRIMARY_COLOR = "#142B52"

SECONDARY_COLOR = "#087F8C"

SUCCESS_COLOR = "#16A36A"

DANGER_COLOR = "#DC3545"

WARNING_COLOR = "#F4B942"

BACKGROUND_COLOR = "#F5F7FB"

CARD_COLOR = "#FFFFFF"

TEXT_COLOR = "#172B4D"


# ==========================================
# CHART COLORS
# ==========================================

CHART_COLORS = [
    "#087F8C",
    "#318CE7",
    "#8B5CF6",
    "#F4B942",
    "#DC3545",
    "#16A36A",
    "#64748B"
]



# ==========================================
# DATASET INFORMATION
# ==========================================

DATASET_NAME = "Home Credit Default Risk"

MAIN_DATASET = "application_train.csv"

TOTAL_EXPECTED_COLUMNS = 122



# ==========================================
# DASHBOARD NAVIGATION
# ==========================================

DASHBOARD_PAGES = [
    "Executive Overview",
    "Customer Demographics",
    "Loan Application Analysis",
    "Default Risk Analysis",
    "Income & Employment",
    "Credit Bureau Analysis",
    "Previous Loan Applications",
    "Repayment & Installments",
    "ML Default Prediction",
    "Reports & Data Download"
]



# ==========================================
# DATASET CONFIGURATION
# ==========================================

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "Data")

DATASET_FILES = {
    "application": "application_train.csv",
    "bureau": "bureau.csv",
    "previous": "previous_application.csv",
    "installments": "installments_payments.csv",
    "pos_cash": "POS_CASH_balance.csv",
    "credit_card": "credit_card_balance.csv"
}
