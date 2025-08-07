# firebase_config.py

import firebase_admin
from firebase_admin import credentials, firestore

# Use a singleton pattern to avoid re-initialization
if not firebase_admin._apps:
    cred = credentials.Certificate("C:/Users/ASUS/Desktop/Thesis/sentinels-a61ff-firebase-adminsdk-fbsvc-35c84e60a7.json")  # update path if needed
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()