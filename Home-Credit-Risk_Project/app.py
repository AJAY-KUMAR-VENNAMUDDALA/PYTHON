import streamlit as st
import config

st.set_page_config(
    page_title=config.APP_TITLE,
    layout=config.LAYOUT,
    initial_sidebar_state=config.INITIAL_SIDEBAR_STATE,
    page_icon=config.APP_ICON,
)

st.title("Home Credit Risk Analytics")
st.write("Welcome to the Home Credit Risk Analytics dashboard!")
st.divider()

pages = [
    st.Page("Pages/1_Executive_Overview.py", title="Executive Overview", icon=":bar_chart:"),
    st.Page("Pages/2_Customer_Demographics.py", title="Customer Demographics", icon=":busts_in_silhouette:"),
    st.Page("Pages/3_Loan_Application.py", title="Loan Application Analysis", icon=":money_with_wings:"),
    st.Page("Pages/4_Default_Risk.py", title="Default Risk Analysis", icon=":warning:"),
    st.Page("Pages/5_Income_Employment.py", title="Income and Employment Analysis", icon=":briefcase:"),
    st.Page("Pages/6_Credit_Bureau.py", title="Credit Bureau Analysis", icon=":credit_card:")
]

navigation = st.navigation(pages)
navigation.run()