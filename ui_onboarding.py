import streamlit as st
from fb_streamlit_auth import fb_streamlit_auth
import os

def show():
    """
    Displays the onboarding page, including login and signup forms,
    and validates the presence of Firebase configuration.
    """
    st.title("Welcome to The Dorian Engine")

    # --- TEMPORARY DEBUGGING STEP ---
    # Hardcoding Firebase config to isolate the problem.
    # If this works, the issue is with how secrets are being passed as environment variables.
    firebase_config = {
        "apiKey": "AIzaSyAaG7ynv1k3PgVvjc8SB2ieWwvcrZ6CwWI",
        "authDomain": "dorian-engine-478520.firebaseapp.com",
        "projectId": "dorian-engine-478520",
        "storageBucket": "dorian-engine-478520.firebasestorage.app",
        "messagingSenderId": "483770294230",
        "appId": "1:483770294230:web:54a81c557606a0ede38e77",
        "measurementId": "G-9046TJQ5WQ",
        "databaseURL": "",
    }

    st.write("Please log in or sign up to continue.")
    
    user = fb_streamlit_auth(firebase_config)

    if user:
        st.session_state['authenticated'] = True
        st.session_state['user_info'] = user
        st.experimental_rerun()
