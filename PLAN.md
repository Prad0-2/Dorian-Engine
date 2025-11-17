# Project Plan: The Dorian Engine - Core MVP

## Project ID: `dorian-engine-478520`

## Context & Vision

This plan focuses on establishing the core MVP of "The Dorian Engine": an AI-powered habit tracker that provides visual feedback based on habit consistency. The primary goal for this phase is to get the Streamlit frontend, AI (Gemini + Imagen), Firestore, Cloud Storage, and Cloud Run deployment pipeline fully operational. Advanced features and mentor feedback will be integrated in a subsequent phase.

## Final Golden Stack (Core MVP)

| Component / Layer   | Technology                       | Google Cloud Integration             | Marathon Points Addressed      |
| :------------------ | :------------------------------- | :----------------------------------- | :----------------------------- |
| **Frontend (UI)** | **Streamlit (Python)** | Deployed on Cloud Run                | **+5 (Functional Demo)** |
| **Backend / Compute** | **Google Cloud Run** | Hosts Streamlit app & Python logic.  | **+5 (Cloud Run Usage)** |
| **Database** | **Google Cloud Firestore** | Stores user data, habits, drift score, image URLs. | **+2 (GCP Database Usage)** |
| **AI Logic / Text** | **Gemini 1.5 Pro (Vertex AI)** | Generates descriptive prompts for image generation. | **+2.5 (Google's AI Usage)** |
| **AI Image Gen.** | **Imagen 3 (Vertex AI)** | Renders photorealistic "Future Self" avatars. | **+2.5 (Google's AI Usage)** |
| **Artifact Storage**| **Google Cloud Storage (GCS)** | Stores generated images, reducing regeneration costs. | *Implicit in AI/Data* |
| **CI/CD ("MCP Toolbox")** | **Google Cloud Build** | Automates Docker build and Cloud Run deployment from GitHub. | *Implied "MCP Toolbox"* |
| **Development IDE** | **Cloud Shell Editor (or Cursor AI)** | Your development environment.          | *N/A (Tooling for speed)* |

---

## Marathon Game Plan: Step-by-Step Execution (Core MVP)

**Goal:** Get a basic, working, AI-powered "Universe A vs. B" Streamlit app deployed on Cloud Run via Cloud Build.

---

### **Phase 0: Prerequisites (Web UI)**

**ACTION:** Ensure these are done in your **Google Cloud Web Console** *before* opening Cloud Shell.

1.  **Project Creation:** Confirmed as `dorian-engine-478520`.
2.  **Billing Account:** Ensure an active billing account is linked to project `dorian-engine-478520`.

---

### **Phase 1: The Foundation (GCP Environment Setup)**

* **Purpose:** Initialize GCP project, enable necessary APIs, and set up core data storage services.
* **Action:**
    1.  **Open Google Cloud Shell.**
    2.  **Copy and paste the entire block below into your Cloud Shell and press Enter.** This will set your project, enable all APIs, create your Firestore database, and create your unique Cloud Storage bucket.
    3.  **IMPORTANT:** Note down the `BUCKET_NAME` that the script outputs. You will need it in `logic.py`.

    ```bash
    # Set Project ID
    gcloud config set project dorian-engine-478520

    # Enable all necessary APIs
    gcloud services enable \
      run.googleapis.com \
      firestore.googleapis.com \
      aiplatform.googleapis.com \
      cloudbuild.googleapis.com \
      storage.googleapis.com \
      artifactregistry.googleapis.com

    # Create a globally unique Cloud Storage Bucket for avatars
    export BUCKET_NAME="dorian-engine-avatars-$(date +%s)"
    gcloud storage buckets create gs://$BUCKET_NAME --location=us-central1

    # Create the Firestore Database in Native Mode
    gcloud firestore databases create --location=us-central1 --type=firestore-native

    # Output crucial variables for your code
    echo "------------------------------------"
    echo "✅ GCP ENVIRONMENT SETUP COMPLETE."
    echo "⚠️ YOU MUST SAVE THIS BUCKET NAME FOR YOUR CODE:"
    echo "BUCKET_NAME: $BUCKET_NAME"
    echo "PROJECT_ID: dorian-engine-478520"
    echo "LOCATION: us-central1"
    echo "------------------------------------"
    ```
* **Expected Outcome:** All GCP services enabled, Firestore and GCS bucket created. You have your unique `BUCKET_NAME`.

---

### **Phase 2: Code Creation (Files & Logic - MVP)**

* **Purpose:** Create all application files (`requirements.txt`, `db.py`, `logic.py`, `app.py`, `Dockerfile`, `cloudbuild.yaml`) with minimal content to get the core AI loop working.
* **Action:**
    1.  In your Cloud Shell, use the built-in editor (type `code .` and press Enter) or create the files manually.
    2.  For each file below, **copy the entire content and paste it into the respective file.**
    3.  **CRITICAL:** In `logic.py`, you **MUST replace the placeholder `YOUR_GENERATED_BUCKET_NAME`** with the exact `BUCKET_NAME` you received from Phase 1.

---

#### **File: `requirements.txt`**

```text
streamlit
google-cloud-aiplatform
google-cloud-firestore
google-cloud-storage
pandas
watchdog
```

---

#### **File: `Dockerfile`**

```dockerfile
# Use a Python base image suitable for Google Cloud Run
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port that Streamlit will run on
EXPOSE 8080

# Command to run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
```

---

#### **File: `db.py` (MVP Version)**

```python
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase Admin SDK (Cloud Run's default service account handles authentication)
if not firebase_admin._apps:
    firebase_admin.initialize_app(credentials.ApplicationDefault(), {
        'projectId': 'dorian-engine-478520', # Pre-filled with your Project ID
    })

db = firestore.client()

def get_user_data(user_id):
    """Retrieves user profile, goals, drift_score, and history."""
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        data.setdefault('drift_score', 0)
        data.setdefault('history', [])
        return data
    return {
        'user_id': user_id,
        'name': 'New User',
        'goal': 'Achieve something great',
        'base_desc': 'A person with average build',
        'drift_score': 0,
        'history': [],
        'last_image_url': None,
    }

def update_user_data(user_id, data):
    """Updates user profile and general data."""
    doc_ref = db.collection('users').document(user_id)
    doc_ref.set(data, merge=True)

def add_habit_log(user_id, status):
    """Logs daily habit status and updates drift score."""
    user_data = get_user_data(user_id)
    
    log_entry = {
        'date': datetime.now().isoformat(),
        'status': status, # 'Yes' or 'No'
    }
    user_data['history'].append(log_entry)

    # Simple drift calculation: -1 for yes, +1 for no. Capped between -10 and 10.
    drift_change = 0
    if status == "✅ Yes, I crushed it":
        drift_change = -1
    elif status == "❌ No, I slipped":
        drift_change = 1
        
    user_data['drift_score'] += drift_change
    user_data['drift_score'] = max(-10, min(10, user_data['drift_score']))

    update_user_data(user_id, user_data)
    return user_data

def update_image_url(user_id, url):
    """Updates the last generated image URL for a user."""
    doc_ref = db.collection('users').document(user_id)
    doc_ref.set({'last_image_url': url}, merge=True)
```

---

#### **File: `logic.py` (MVP Version)**

**IMPORTANT:** Replace `YOUR_GENERATED_BUCKET_NAME` below with the actual `BUCKET_NAME` you received from the Phase 1 setup.

```python
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from vertexai.generative_models import GenerativeModel
from google.cloud import storage
import uuid
from io import BytesIO

# --- CONFIGURATION (UPDATE THIS) ---
PROJECT_ID = "dorian-engine-478520" # Pre-filled with your Project ID
LOCATION = "us-central1"
GCS_BUCKET_NAME = "YOUR_GENERATED_BUCKET_NAME" # <<< --- !!! REPLACE THIS !!! --- <<<
# --- END CONFIGURATION ---

# Initialize Vertex AI SDK
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize Storage Client (for GCS operations)
storage_client = storage.Client(project=PROJECT_ID)

def upload_image_to_gcs(image_bytes, user_id, filename_prefix="avatars"):
    """
    Uploads the image bytes to GCS and returns its public URL.
    """
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    
    # Path for generated avatars
    path = f"{filename_prefix}/{user_id}/{uuid.uuid4()}.png"
        
    blob = bucket.blob(path)
    blob.upload_from_string(image_bytes, content_type='image/png')
    blob.make_public() # Make generated avatars publicly accessible for demo.
    
    return blob.public_url

def get_drift_prompt(drift_score, user_desc):
    """
    Uses Gemini to describe the future self based on drift.
    """
    model = GenerativeModel("gemini-1.5-pro-002") # Using the latest stable version
    
    # Base descriptions based on drift_score (simpler for MVP)
    if drift_score <= -5: # Very good
        context = "The user is highly consistent. Describe them looking extremely healthy, vibrant, sharp, exuding confidence, in a professional and active setting. Focus on glowing skin, perfect posture, and modern clothing."
    elif drift_score <= 0: # On track/Slightly good
        context = "The user is consistent. Describe them looking healthy, energetic, focused, and well-groomed, in a pleasant work or active setting. Focus on clear skin, good posture, and smart casual attire."
    elif drift_score <= 5: # Slipping
        context = "The user is slipping. Describe them looking slightly fatigued, perhaps with a neutral expression, some minor dishevelment, or a slightly less vibrant look. The environment is neutral."
    else: # Falling behind (drift_score > 5)
        context = "The user is significantly failing habits. Describe them looking tired, slightly rounded face, messy hair, slumped posture, and in a cluttered, less inviting environment. Focus on dull skin, dark circles under eyes, and loose, unkempt clothing."

    prompt_template = f"""
    Act as an image generation prompt engineer. Your goal is to create a highly detailed, photorealistic prompt for Imagen 3.
    Based on this base user description: '{user_desc}'
    And this context about their progress: {context}

    Generate a single, coherent, highly descriptive image generation prompt (max 100 words).
    Focus on facial expression, skin quality, hair, body posture, clothing style, and background environment.
    Maintain facial consistency with the original description as much as possible, while varying the described attributes.
    Output ONLY the prompt string.
    """
    
    response = model.generate_content(prompt_template)
    return response.text

def generate_image(prompt, user_id):
    """
    Generates the image using Imagen 3 and uploads to GCS.
    """
    model = ImageGenerationModel.from_pretrained("imagegeneration@006")
    
    images = model.generate_images(
        prompt=prompt,
        number_of_images=1,
        aspect_ratio="1:1",
        safety_filter_level="block_some",
        person_generation="allow_adult"
    )
    
    img_buffer = BytesIO()
    images[0].save(img_buffer, format='PNG')
    image_bytes = img_buffer.getvalue()
    
    image_public_url = upload_image_to_gcs(image_bytes, user_id)
    
    return image_public_url
```

---

#### **File: `app.py` (MVP Version)**

```python
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
```

---

#### **File: `cloudbuild.yaml`**

```yaml
# This Cloud Build configuration automates building your Docker image
# and deploying it to Cloud Run. This acts as your "MCP Toolbox" for CI/CD.

steps:
# Step 1: Build the Docker image
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/dorian-engine:$COMMIT_SHA', '.']

# Step 2: Push the Docker image to Artifact Registry
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/dorian-engine:$COMMIT_SHA']

# Step 3: Deploy the Docker image to Cloud Run
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'deploy', 'dorian-engine', '--image', 'gcr.io/$PROJECT_ID/dorian-engine:$COMMIT_SHA', '--region', 'us-central1', '--allow-unauthenticated']
  env:
    - 'PROJECT_ID=$PROJECT_ID'
```

---

### **Phase 3: Deployment (GitHub & Cloud Build)**

* **Purpose:** Push your code to GitHub and set up an automated deployment pipeline using Cloud Build.
* **Action:**
    1.  **Initialize Git in your `dorian-engine` folder (in Cloud Shell):**
        ```bash
        git init
        git add .
        git commit -m "Initial Dorian Engine MVP setup"
        ```
    2.  **Create a NEW GitHub Repository:**
        * Go to [github.com/new](https://github.com/new).
        * Give it a name like `the-dorian-engine-mvp`.
        * Make it **Public**.
        * Click "Create repository."
    3.  **Connect your local Git to GitHub and push:**
        * Follow the instructions GitHub gives you for "Push an existing repository from the command line." It will look something like this (replace with *your* GitHub username and repo name):
            ```bash
            git remote add origin [https://github.com/YOUR_GITHUB_USERNAME/the-dorian-engine-mvp.git](https://github.com/YOUR_GITHUB_USERNAME/the-dorian-engine-mvp.git)
            git branch -M main
            git push -u origin main
            ```
    4.  **Set up Cloud Build Trigger (in Google Cloud Console):**
        * Go to **Cloud Build** in your Google Cloud Console (ensure project `dorian-engine-478520` is selected).
        * Navigate to **Triggers** in the left menu.
        * Click **"CREATE TRIGGER"**.
        * **Name:** `dorian-engine-mvp-deploy`
        * **Event:** `Push to a branch`.
        * **Source:**
            * **Repository:** Connect to your GitHub repository (`the-dorian-engine-mvp`). You might need to authorize Google Cloud to access GitHub.
            * **Branch:** `^main$` (to trigger on pushes to the `main` branch).
        * **Configuration:**
            * **Type:** `Cloud Build configuration file`.
            * **Location:** `cloudbuild.yaml` (should be the default).
        * Click **"CREATE"**.
    5.  **Trigger Initial Deployment:**
        * Make a tiny change to your `app.py` (e.g., add a comment line).
        * Save, `git add .`, `git commit -m "Trigger initial MVP deploy"`, `git push origin main`.
        * Go back to **Cloud Build -> History** in the GCP Console to watch your build and deployment happen.
* **Expected Outcome:** Your "The Dorian Engine" MVP application is deployed and accessible via a public URL on Google Cloud Run, automatically updating with every code push to GitHub.

---

## Final Checks & Testing (MVP)

1.  **Cloud Run URL:** Get the URL from the Cloud Run service in the GCP Console.
2.  **Test:** Open the URL in your browser.
    * Fill in user details in the sidebar.
    * Click "Update My Timeline."
    * Observe the "Drift Score" and the generated image for "Universe B."
    * Experiment with "Yes, I crushed it" and "No, I slipped" to see the visual changes.

This revised `plan.md` now focuses purely on the core MVP. Once this is working, we can easily add the mentor's features on top of this stable base.