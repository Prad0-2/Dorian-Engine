import streamlit as st
from fb_streamlit_auth import fb_streamlit_auth
import os

def show():
    """
    Displays the onboarding page, including login and signup forms,
    using the fb-streamlit-auth component.
    """
    st.title("Welcome to The Dorian Engine")
    st.write("Please log in or sign up to continue.")

    # The Firebase config needs to be available to the client-side.
    # In a real-world scenario, these would be loaded from environment variables
    # or a configuration file, populated by Secret Manager during the build/deploy process.
    # For now, we will use placeholders and expect them to be set as environment variables.
    firebase_config = {
        "apiKey": os.environ.get("FIREBASE_API_KEY"),
        "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
        "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.environ.get("FIREBASE_APP_ID"),
        "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID"),
        "databaseURL": "", # Not needed for Firestore
    }

    # Perform authentication
    user = fb_streamlit_auth(firebase_config)

    if user:
        # If the user is authenticated, store their info in the session state
        st.session_state['authenticated'] = True
        st.session_state['user_info'] = user
        
        # Trigger a rerun to navigate to the dashboard
        st.experimental_rerun()
