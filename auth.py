import os
import json
import firebase_admin
from firebase_admin import auth, credentials

def init_auth():
    """
    Initializes the Firebase Admin SDK for authentication purposes.
    Uses the mounted secret file if available, otherwise falls back to other methods.
    """
    if not firebase_admin._apps:
        secret_path = '/etc/secrets/firebase-admin-sdk-credentials.json'
        if os.path.exists(secret_path):
            cred = credentials.Certificate(secret_path)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback for local development or environments without the secret
            firebase_admin.initialize_app(credentials.ApplicationDefault())

init_auth()

def verify_token(id_token):
    """
    Verifies the Firebase ID token sent from the client.

    :param id_token: The Firebase ID token to verify.
    :return: The decoded token dictionary if the token is valid, otherwise None.
    """
    if not id_token:
        return None
        
    try:
        # Verify the ID token while checking if the token is revoked.
        decoded_token = auth.verify_id_token(id_token, check_revoked=True)
        return decoded_token
    except auth.RevokedIdTokenError:
        # Token has been revoked. Inform the user to reauthenticate.
        return None
    except auth.InvalidIdTokenError:
        # Token is invalid.
        return None
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred during token verification: {e}")
        return None
