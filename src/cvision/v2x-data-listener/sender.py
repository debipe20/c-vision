import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import random

# Load the Firebase service account key
cred = credentials.Certificate('cvision-firebase-key.json')
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
