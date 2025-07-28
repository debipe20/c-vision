# main.py - TEMPORARY CONTENT
from firebase_functions.https_fn import on_request, HttpsRequest, Response

@on_request()
def helloWorld(request: HttpsRequest) -> Response:
    return Response("Hello from Firebase Python!")



# import json
# import datetime
# import firebase_admin
# from firebase_admin import credentials, db
# from firebase_functions.https_fn import on_request
# # REMOVED: from firebase_functions.database import on_write, DataSnapshot # Keep this line commented out or removed
# import base64
# import requests
# import uuid # Added for generating unique IDs

# # Global variable to hold the initialized app instance.
# _firebase_app = None

# def _initialize_firebase():
#     global _firebase_app
#     if _firebase_app is None or not firebase_admin._apps:
#         try:
#             _firebase_app = firebase_admin.initialize_app(options={
#                 'databaseURL': 'https://v2x-data-exchange-default-rtdb.firebaseio.com/'
#             })
#             print("Firebase Admin SDK initialized.")
#         except ValueError as e:
#             print(f"Firebase Admin SDK already initialized or error during init: {e}")
#             if firebase_admin._apps:
#                 _firebase_app = firebase_admin.get_app()
#             else:
#                 raise

# @on_request()
# def ingest_spat_data(request):
#     _initialize_firebase()

#     if request.method != 'POST':
#         print(f"Method not allowed: {request.method}")
#         return ('Method Not Allowed', 405, {'Allow': 'POST'})

#     try:
#         encoded_spat_data_bytes = request.get_data()

#         if not encoded_spat_data_bytes:
#             print("No raw data received in the request body.")
#             return ('No data received in body', 400)

#         unique_payload_id = str(uuid.uuid4()) # Generate a unique ID

#         encoded_data_for_db = base64.b64encode(encoded_spat_data_bytes).decode('utf-8')

#         sender_ip = request.remote_addr
#         x_forwarded_for = request.headers.get('X-Forwarded-For')
#         sender_info = {
#             'ipAddress': sender_ip,
#             'xForwardedForHeader': x_forwarded_for,
#             'receivedAtCloudFunction': datetime.datetime.now(datetime.timezone.utc).isoformat()
#         }

#         data_to_store = {
#             'encodedSpat': encoded_data_for_db,
#             'receivedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
#             'senderInfo': sender_info
#         }

#         # Store data under a unique ID directly under 'spatData'
#         ref = db.reference(f'spatData/{unique_payload_id}')
#         ref.set(data_to_store)

#         print(f"Successfully ingested ENCODED SPaT data with ID: {unique_payload_id} from IP: {sender_ip}")
#         return ('Encoded SPaT data received and stored successfully', 200)

#     except Exception as e:
#         print(f"Error processing encoded SPaT data in ingest_spat_data: {e}", exc_info=True)
#         return (f'Internal Server Error: {e}', 500)

# # The 'forward_spat_to_backend' Python function should remain commented out or removed
# # as the Node.js function will handle the forwarding.
# # @on_write(reference='spatData/{intersectionId}')
# # def forward_spat_to_backend(event: DataSnapshot):
# #     # ... (your original Python forwarding code, commented out or deleted)




# # import json
# # import datetime
# # import firebase_admin
# # from firebase_admin import credentials, db
# # from firebase_functions.https_fn import on_request
# # # REMOVED: from firebase_functions.database import on_write, DataSnapshot
# # import base64
# # import requests
# # import uuid # Added for generating unique IDs

# # # Global variable to hold the initialized app instance.
# # _firebase_app = None

# # def _initialize_firebase():
# #     global _firebase_app
# #     if _firebase_app is None or not firebase_admin._apps:
# #         try:
# #             _firebase_app = firebase_admin.initialize_app(options={
# #                 'databaseURL': 'https://v2x-data-exchange-default-rtdb.firebaseio.com/'
# #             })
# #             print("Firebase Admin SDK initialized.")
# #         except ValueError as e:
# #             print(f"Firebase Admin SDK already initialized or error during init: {e}")
# #             if firebase_admin._apps:
# #                 _firebase_app = firebase_admin.get_app()
# #             else:
# #                 raise

# # @on_request()
# # def ingest_spat_data(request):
# #     _initialize_firebase()

# #     if request.method != 'POST':
# #         print(f"Method not allowed: {request.method}")
# #         return ('Method Not Allowed', 405, {'Allow': 'POST'})

# #     try:
# #         encoded_spat_data_bytes = request.get_data()

# #         if not encoded_spat_data_bytes:
# #             print("No raw data received in the request body.")
# #             return ('No data received in body', 400)

# #         # Removed: intersection_id from query parameter is no longer required

# #         # Generate a unique ID for this specific SPaT payload record
# #         # Using a UUID ensures uniqueness even if multiple data points arrive at the exact same microsecond
# #         unique_payload_id = str(uuid.uuid4())

# #         encoded_data_for_db = base64.b64encode(encoded_spat_data_bytes).decode('utf-8')

# #         sender_ip = request.remote_addr
# #         x_forwarded_for = request.headers.get('X-Forwarded-For')
# #         sender_info = {
# #             'ipAddress': sender_ip,
# #             'xForwardedForHeader': x_forwarded_for,
# #             'receivedAtCloudFunction': datetime.datetime.now(datetime.timezone.utc).isoformat()
# #         }

# #         data_to_store = {
# #             # Removed: 'intersectionId' field, as it's not known
# #             'encodedSpat': encoded_data_for_db,
# #             'receivedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
# #             'senderInfo': sender_info
# #         }

# #         # Store data under a unique ID directly under 'spatData'
# #         ref = db.reference(f'spatData/{unique_payload_id}')
# #         ref.set(data_to_store)

# #         print(f"Successfully ingested ENCODED SPaT data with ID: {unique_payload_id} from IP: {sender_ip}")
# #         return ('Encoded SPaT data received and stored successfully', 200)

# #     except Exception as e:
# #         print(f"Error processing encoded SPaT data in ingest_spat_data: {e}", exc_info=True)
# #         return (f'Internal Server Error: {e}', 500)
    
    
# # REMOVE THIS ENTIRE FUNCTION
# # @on_write(reference='spatData/{intersectionId}')
# # def forward_spat_to_backend(event: DataSnapshot):
# #     _initialize_firebase()
# #
# #     data_from_db = event.data
# #
# #     if not data_from_db:
# #         print(f"No data at path: {event.reference.path}. Possibly a delete event or empty write.")
# #         return
# #
# #     intersection_id = event.params['intersectionId']
# #     encoded_spat_b64 = data_from_db.get('encodedSpat')
# #
# #     if not encoded_spat_b64:
# #         print(f"No 'encodedSpat' field found for {intersection_id} at path {event.reference.path}. Skipping forward.")
# #         return
# #
# #     try:
# #         encoded_spat_raw_bytes = base64.b64decode(encoded_spat_b64)
# #
# #         EXTERNAL_BACKEND_URL = "https://your.external.backend.com/spat-receiver"
# #         BACKEND_API_KEY = "YOUR_SECRET_API_KEY_FOR_BACKEND"
# #
# #         headers = {
# #             'Content-Type': 'application/octet-stream',
# #             'X-Intersection-ID': intersection_id,
# #             'X-API-Key': BACKEND_API_KEY
# #         }
# #
# #         response = requests.post(EXTERNAL_BACKEND_URL, data=encoded_spat_raw_bytes, headers=headers, timeout=10)
# #         response.raise_for_status()
# #
# #         print(f"Successfully forwarded ENCODED SPaT for {intersection_id} to backend. Status: {response.status_code}")
# #     except requests.exceptions.RequestException as e:
# #         print(f"Error forwarding ENCODED SPaT for {intersection_id} to backend: {e}")
# #         if hasattr(e, 'response') and e.response is not None:
# #             print(f"Backend response content: {e.response.text}")
# #     except Exception as e:
# #         print(f"An unexpected error occurred in forward_spat_to_backend for {intersection_id}: {e}", exc_info=True)