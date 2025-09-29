# firebase_config.py

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Avoid re-initialization
if not firebase_admin._apps:
    firebase_creds = os.getenv("FIREBASE_CREDENTIALS")

    if firebase_creds:
        # Running on Render → credentials come from environment variable
        cred_dict = json.loads(firebase_creds)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    else:
        # Running locally → load from JSON file
        cred = credentials.Certificate(
            os.path.join(os.path.dirname(__file__), "sentinels-a61ff-firebase-adminsdk-fbsvc-aaf9572a3f.json")
        )
        firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()
