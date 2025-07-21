# main.py
import json
import datetime
import firebase_admin
from firebase_admin import credentials, db
from firebase_functions.https_fn import on_request

# Global variable to hold the initialized app instance.
_firebase_app = None

@on_request()
def ingest_spat_data(request):
    """
    Receives SPaT JSON data via HTTP POST and stores it in Firebase Realtime Database.
    Includes sender's IP address and X-Forwarded-For header in the stored data.
    """
    global _firebase_app

    # Initialize Firebase Admin SDK ONLY when the function is first invoked
    if _firebase_app is None or not firebase_admin._apps:
        try:
            _firebase_app = firebase_admin.initialize_app(options={
                'databaseURL': 'https://spat-data-exchange-default-rtdb.firebaseio.com/'
            })
            print("Firebase Admin SDK initialized.")
        except ValueError as e:
            print(f"Firebase Admin SDK already initialized or error during init: {e}")
            if firebase_admin._apps:
                _firebase_app = firebase_admin.get_app()
            else:
                raise

    ref = db.reference('spatData', app=_firebase_app)

    if request.method != 'POST':
        print(f"Method not allowed: {request.method}")
        return ('Method Not Allowed', 405, {'Allow': 'POST'})

    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            print("Request body is not valid JSON or is empty.")
            return ('Request body must be JSON', 400)

        intersection_id = request_json.get('intersectionId')
        if not intersection_id:
            print("Missing 'intersectionId' in JSON payload.")
            return ('Missing "intersectionId" in JSON payload', 400)

        # --- START: ADDED CODE FOR SENDER IDENTIFICATION ---
        sender_ip = request.remote_addr
        x_forwarded_for = request.headers.get('X-Forwarded-For')

        sender_info = {
            'ipAddress': sender_ip,
            'xForwardedForHeader': x_forwarded_for, # Store the full header value
            'receivedAtCloudFunction': datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        # --- END: ADDED CODE ---

        data_to_store = {
            **request_json,
            'receivedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'senderInfo': sender_info # Add the sender information here
        }

        ref.child(intersection_id).set(data_to_store)

        print(f"Successfully ingested SPaT data for Intersection ID: {intersection_id} from IP: {sender_ip}")
        return ('SPaT data received and stored successfully', 200)

    except Exception as e:
        print(f"Error processing SPaT data: {e}", exc_info=True)
        return (f'Internal Server Error: {e}', 500)