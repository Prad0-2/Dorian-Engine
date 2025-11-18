import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from vertexai.generative_models import GenerativeModel
from google.cloud import storage
import uuid
from io import BytesIO
import db # Import the updated db module

# --- CONFIGURATION ---
PROJECT_ID = "dorian-engine-478520"
LOCATION = "us-central1"
GCS_BUCKET_NAME = "dorian-engine-avatars-1763411045"
# --- END CONFIGURATION ---

# Initialize Vertex AI SDK
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize Storage Client
storage_client = storage.Client(project=PROJECT_ID)

def calculate_drift_score(user_id):
    """
    Calculates the user's drift score based on their habit history.
    - +2 for each completed day
    - –4 for each missed day
    - –5 extra penalty if user misses 3+ consecutive days
    - Score is clamped between 0 and 100.
    """
    habit_history = db.get_habit_history(user_id, limit=30) # Get last 30 days
    score = 50  # Start from a baseline
    consecutive_misses = 0

    for habit in reversed(habit_history): # Process from oldest to newest
        if habit['completed']:
            score += 2
            consecutive_misses = 0
        else:
            score -= 4
            consecutive_misses += 1
            if consecutive_misses >= 3:
                score -= 5 # Apply penalty

    # Clamp the score between 0 and 100
    score = max(0, min(100, score))
    
    db.update_user_data(user_id, {'latestDriftScore': score})
    return score

def get_avatar_prompt(user_data, drift_score):
    """
    Uses Gemini to describe the future self based on drift score and user goals.
    """
    model = GenerativeModel("gemini-1.5-pro-002")
    
    # More nuanced context based on the 0-100 drift score
    if drift_score >= 80:
        context = "The user is at their peak. Describe them looking exceptionally healthy, confident, and successful, achieving their main goal. The setting is inspiring and reflects their success."
    elif drift_score >= 60:
        context = "The user is doing very well. Describe them looking healthy, energetic, and focused. They are making clear progress towards their goal."
    elif drift_score >= 40:
        context = "The user is on track. Describe them looking stable and determined, with a neutral but focused expression. The environment is normal and orderly."
    elif drift_score >= 20:
        context = "The user is slipping. Describe them looking slightly fatigued and distracted. There might be minor signs of stress or dishevelment."
    else:
        context = "The user is significantly off track. Describe them looking tired, stressed, and further away from their goal. The environment might be cluttered or uninspiring."

    prompt_template = f"""
    Act as an image generation prompt engineer for a photorealistic avatar.
    The user's main goal is: '{user_data['mainGoal']}'.
    The user's current progress is: {context}.
    Base the avatar on this user description: A person with features from their uploaded selfie.

    Generate a single, coherent, highly descriptive image generation prompt (max 100 words).
    Focus on facial expression, skin quality, hair, body posture, clothing style, and background environment that reflects their progress towards their goal.
    Maintain facial consistency with the original user, but alter their appearance based on the context.
    Output ONLY the prompt string.
    """
    
    response = model.generate_content(prompt_template)
    return response.text

def generate_avatar(prompt, user_id, is_initial=False):
    """
    Generates an avatar image using Imagen, uploads it to GCS, and saves the URL to Firestore.
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
    
    # Upload to GCS
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    filename = f"initial.png" if is_initial else f"{uuid.uuid4()}.png"
    path = f"avatars/{user_id}/{filename}"
    blob = bucket.blob(path)
    blob.upload_from_string(image_bytes, content_type='image/png')
    blob.make_public()
    
    # Save URL to Firestore
    db.save_avatar(user_id, blob.public_url, is_initial=is_initial)
    
    return blob.public_url

def upload_base_photo(user_id, file_bytes):
    """
    Uploads the user's base photo to GCS and returns its public URL.
    """
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    path = f"base_photos/{user_id}/base.png"
    blob = bucket.blob(path)
    blob.upload_from_string(file_bytes, content_type='image/png')
    blob.make_public()
    
    return blob.public_url
