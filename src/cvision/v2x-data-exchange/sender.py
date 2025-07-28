import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import random
import os

# Load the Firebase service account key
sevrice_account_path = os.path.expanduser("~") + "/Documents/cvision-firebase-key.json"
cred = credentials.Certificate(sevrice_account_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://c-vision-7e1ec-default-rtdb.firebaseio.com/'
})

# Create dummy data
data = {
    'timestamp': datetime.utcnow().isoformat(),
    'speed': random.randint(0, 100),
    'heading': random.randint(0, 360)
}

# Write to Firebase at a fixed path (overwrites old data)
ref = db.reference('/latestSensorData')
ref.set(data)

print('✅ Data pushed successfully:', data)
