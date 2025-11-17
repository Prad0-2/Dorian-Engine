import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from vertexai.generative_models import GenerativeModel
from google.cloud import storage
import uuid
from io import BytesIO

# --- CONFIGURATION (UPDATE THIS) ---
PROJECT_ID = "dorian-engine-478520" # Pre-filled with your Project ID
LOCATION = "us-central1"
GCS_BUCKET_NAME = "dorian-engine-avatars-1763411045" # <<< --- !!! REPLACE THIS !!! --- <<<
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
