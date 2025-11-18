import streamlit as st
import db
import logic
import time # For simulating delays and toasts

# --- CONFIGURATION ---
USER_ID = "demo_user_123" # A fixed user ID for the demo
# --- END CONFIGURATION ---

st.set_page_config(layout="wide", page_title="The Dorian Engine MVP")

# --- UI SETUP ---
st.title("🎭 The Dorian Engine: Your Visual Future (MVP)")
st.caption("See your choices shape your future self.")

# Get/Initialize user data
user_data = db.get_user_data(USER_ID)

# Sidebar for User Setup
with st.sidebar:
    st.header("👤 Your Details")
    user_data['name'] = st.text_input("Your Name", user_data['name'])
    user_data['goal'] = st.text_input("Your Main Goal", user_data['goal'])
    user_data['base_desc'] = st.text_area("Describe Yourself (for AI reference)", user_data['base_desc'])
    
    st.divider()
    
    st.header("🗓️ Daily Check-in")
    status = st.radio("Did you hit your goals today?", ["✅ Yes, I crushed it", "❌ No, I slipped"])
    
    if st.button("Update My Timeline"):
        with st.spinner("Simulating your future... this may take a moment."):
            # Update user data in Firestore
            db.update_user_data(USER_ID, user_data)
            
            # Add habit log and update drift score
            updated_user_data = db.add_habit_log(USER_ID, status)
            st.session_state['user_data'] = updated_user_data # Update session state

            # Generate new image for Universe B (Drifted You)
            st.toast("Generating 'Drift' avatar...")
            drift_prompt = logic.get_drift_prompt(
                updated_user_data['drift_score'], 
                updated_user_data['base_desc']
            )
            
            drift_image_url = logic.generate_image(
                drift_prompt, 
                USER_ID
            )
            db.update_image_url(USER_ID, drift_image_url)
            st.session_state['last_image_url'] = drift_image_url # Update session state

            st.success("Timeline updated! Scroll down to see your future.")
            st.experimental_rerun() # Rerun to update main display

# --- Main Display Area ---
st.markdown(f"## Hello, {user_data['name']}!")
st.info(f"Your Goal: **{user_data['goal']}**")

st.metric("Current Drift Score", user_data['drift_score'])
st.progress(max(0, min(100, 50 + user_data['drift_score'] * 5)), text="Progress towards ideal self")


col1, col2 = st.columns(2)

with col1:
    st.subheader("🌟 Universe A: The Consistent You")
    # This image is a placeholder for the ideal state
    st.image("[https://placehold.co/600x600/1a1a1a/FFF?text=Your+Ideal+Self](https://placehold.co/600x600/1a1a1a/FFF?text=Your+Ideal+Self)", caption="Projected: Ideal Path", use_column_width=True)
    st.markdown("---")
    st.markdown("**Status:** High Energy, Sharp Focus, Achieving Goals.")

with col2:
    st.subheader("⚠️ Universe B: The Drifting You")
    display_image_url = user_data.get('last_image_url', "[https://placehold.co/600x600/330000/FFF?text=Your+Drifting+Self](https://placehold.co/600x600/330000/FFF?text=Your+Drifting+Self)")
    st.image(display_image_url, caption=f"Projected: Current Path (Drift Score: {user_data['drift_score']})", use_column_width=True)
    st.markdown("---")
    st.markdown("**Status:** Fatigue, Brain Fog, Goals Slipping Away.")

st.markdown("---")
st.markdown("This MVP showcases Google Cloud Run, Firestore, Vertex AI (Gemini & Imagen), Cloud Storage, and Cloud Build for CI/CD.")

# Triggering initial build - Third trigger (retrying)
