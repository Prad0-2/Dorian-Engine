import streamlit as st
import ui_onboarding
import ui_dashboard
import ui_weekly_report

def main():
    """
    Main function to run the Streamlit app.
    This function will act as a router to display the correct page based on the user's authentication status.
    """
    st.set_page_config(layout="wide", page_title="The Dorian Engine")

    # Initialize session state variables if they don't exist
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'page' not in st.session_state:
        st.session_state['page'] = 'onboarding'

    # --- Main Router ---
    if not st.session_state['authenticated']:
        # If the user is not authenticated, show the onboarding/login page.
        ui_onboarding.show()
    else:
        # If the user is authenticated, show the main app navigation.
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Dashboard", "Weekly Report"])

        if page == "Dashboard":
            ui_dashboard.show()
        elif page == "Weekly Report":
            ui_weekly_report.show()

if __name__ == "__main__":
    main()
