import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

def init_db():
    """
    Initializes the Firebase Admin SDK.
    Uses the service account credentials from the environment variable if available.
    """
    if not firebase_admin._apps:
        creds_json = os.environ.get("FIREBASE_ADMIN_SDK_CREDENTIALS")
        if creds_json:
            creds_dict = json.loads(creds_json)
            creds_dict['private_key'] = creds_dict['private_key'].replace('\\\\n', '\\n')
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback for local development or environments without the secret
            firebase_admin.initialize_app(credentials.ApplicationDefault(), {
                'projectId': 'dorian-engine-478520',
            })
    return firestore.client()

db = init_db()

def create_user(user_id, name, email, main_goal, target_date):
    """
    Creates a new user document in Firestore.
    """
    user_ref = db.collection('users').document(user_id)
    user_data = {
        'name': name,
        'email': email,
        'createdAt': datetime.now(),
        'mainGoal': main_goal,
        'targetDate': target_date,
        'currentAvatarUrl': None,
        'latestDriftScore': 0,
    }
    user_ref.set(user_data)
    return user_data

def get_user_data(user_id):
    """
    Retrieves a user's document from Firestore.
    """
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None

def update_user_data(user_id, data):
    """
    Updates a user's document in Firestore.
    """
    doc_ref = db.collection('users').document(user_id)
    doc_ref.update(data)

def log_habit(user_id, completed):
    """
    Logs a daily habit check-in for a user.
    """
    today = datetime.now().strftime('%Y-%m-%d')
    habit_ref = db.collection('users').document(user_id).collection('habits').document(today)
    habit_data = {
        'completed': completed,
        'timestamp': datetime.now(),
    }
    habit_ref.set(habit_data)

def get_habit_history(user_id, limit=7):
    """
    Retrieves the last N days of habit history for a user.
    """
    habits_ref = db.collection('users').document(user_id).collection('habits').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
    return [doc.to_dict() for doc in habits_ref.stream()]

def save_avatar(user_id, avatar_url, is_initial=False):
    """
    Saves a new avatar URL for the user.
    If it's the initial avatar, it also updates the main user document.
    """
    avatar_ref = db.collection('users').document(user_id).collection('avatars').document()
    avatar_data = {
        'url': avatar_url,
        'createdAt': datetime.now(),
    }
    avatar_ref.set(avatar_data)

    if is_initial:
        update_user_data(user_id, {'currentAvatarUrl': avatar_url})

def save_weekly_report(user_id, report_data):
    """
    Saves a weekly summary report for the user.
    """
    report_ref = db.collection('users').document(user_id).collection('weekly_reports').document()
    report_ref.set(report_data)
