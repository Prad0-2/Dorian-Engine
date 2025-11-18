import streamlit as st
import db
import logic
import time

# --- CONFIGURATION ---
USER_ID = "demo_user_123" # A fixed user ID for the demo
# --- END CONFIGURATION ---

def show():
    """
    Displays the main user dashboard.
    """
    st.title("🎭 The Dorian Engine: Your Visual Future")
    st.caption("See your choices shape your future self.")

    # Get/Initialize user data
    user_data = db.get_user_data(USER_ID)
    if not user_data:
        # If the demo user doesn't exist, create it.
        db.create_user(USER_ID, "Demo User", "demo@example.com", "Achieve something great", "2025-12-31")
        user_data = db.get_user_data(USER_ID)


    # Sidebar for User Setup
    with st.sidebar:
        st.header("👤 Your Details")
        
        if user_data.get('basePhotoUrl'):
            st.image(user_data['basePhotoUrl'], caption="Your Base Photo", use_column_width=True)

        uploaded_photo = st.file_uploader("Upload/Change Your Base Photo", type=["png", "jpg", "jpeg"])

        if uploaded_photo is not None:
            if st.button("Upload Photo"):
                with st.spinner("Uploading..."):
                    photo_bytes = uploaded_photo.getvalue()
                    photo_url = logic.upload_base_photo(USER_ID, photo_bytes)
                    db.update_user_data(USER_ID, {'basePhotoUrl': photo_url})
                    st.success("Base photo uploaded!")
                    st.experimental_rerun()

        name = st.text_input("Your Name", user_data.get('name', ''))
        goal = st.text_input("Your Main Goal", user_data.get('mainGoal', ''))
        
        if st.button("Update Details"):
            db.update_user_data(USER_ID, {'name': name, 'mainGoal': goal})
            st.success("Details updated!")
            st.experimental_rerun()

        st.divider()
        
        st.header("🗓️ Daily Check-in")
        status = st.radio("Did you hit your goals today?", ["✅ Yes, I crushed it", "❌ No, I slipped"])
        
        if st.button("Update My Timeline"):
            with st.spinner("Simulating your future... this may take a moment."):
                # Log the habit
                db.log_habit(USER_ID, "Yes" in status)
                
                # Recalculate drift score
                drift_score = logic.calculate_drift_score(USER_ID)
                
                # Generate new image for Universe B (Drifted You)
                st.toast("Generating 'Drift' avatar...")
                prompt = logic.get_avatar_prompt(user_data, drift_score)
                
                logic.generate_avatar(prompt, USER_ID)

                st.success("Timeline updated! Scroll down to see your future.")
                st.experimental_rerun()

    # --- Main Display Area ---
    st.markdown(f"## Hello, {user_data.get('name', 'User')}!")
    st.info(f"Your Goal: **{user_data.get('mainGoal', 'No goal set')}**")

    drift_score = user_data.get('latestDriftScore', 50)
    st.metric("Current Drift Score", drift_score)
    st.progress(drift_score / 100)


    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌟 Universe A: The Ideal You")
        st.image("https://placehold.co/600x600/1a1a1a/FFF?text=Your+Ideal+Self", caption="Projected: Ideal Path", use_column_width=True)
        st.markdown("---")
        st.markdown("**Status:** High Energy, Sharp Focus, Achieving Goals.")

    with col2:
        st.subheader("⚠️ Universe B: The Drifting You")
        display_image_url = user_data.get('currentAvatarUrl', "https://placehold.co/600x600/330000/FFF?text=Your+Drifting+Self")
        st.image(display_image_url, caption=f"Projected: Current Path (Drift Score: {drift_score})", use_column_width=True)
        st.markdown("---")
        st.markdown("**Status:** Fatigue, Brain Fog, Goals Slipping Away.")
