import streamlit as st
import ui_dashboard
import ui_weekly_report

def main():
    """
    Main function to run the Streamlit app.
    This version bypasses authentication and goes directly to the dashboard.
    """
    st.set_page_config(layout="wide", page_title="The Dorian Engine")

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Weekly Report"])

    if page == "Dashboard":
        ui_dashboard.show()
    elif page == "Weekly Report":
        ui_weekly_report.show()

if __name__ == "__main__":
    main()
