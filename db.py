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
