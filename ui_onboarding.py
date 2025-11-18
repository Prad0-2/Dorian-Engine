import streamlit as st
from fb_streamlit_auth import fb_streamlit_auth
import os

def show():
    """
    Displays the onboarding page, including login and signup forms,
    and validates the presence of Firebase configuration.
    """
    st.title("Welcome to The Dorian Engine")

    required_env_vars = [
        "FIREBASE_API_KEY",
        "FIREBASE_AUTH_DOMAIN",
        "FIREBASE_PROJECT_ID",
        "FIREBASE_STORAGE_BUCKET",
        "FIREBASE_MESSAGING_SENDER_ID",
        "FIREBASE_APP_ID",
        "FIREBASE_MEASUREMENT_ID",
    ]

    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

    if missing_vars:
        st.error(f"The following required environment variables are missing: {', '.join(missing_vars)}")
        st.error("Please ensure that the secrets are correctly configured and mounted in the Cloud Run service.")
    else:
        st.write("Please log in or sign up to continue.")
        firebase_config = {
            "apiKey": os.environ.get("FIREBASE_API_KEY"),
            "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
            "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
            "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.environ.get("FIREBASE_APP_ID"),
            "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID"),
            "databaseURL": "",
        }

        user = fb_streamlit_auth(firebase_config)

        if user:
            st.session_state['authenticated'] = True
            st.session_state['user_info'] = user
            st.experimental_rerun()
