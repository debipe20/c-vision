import firebase_admin
from firebase_admin import credentials, db
import os
import platform

# Load the Firebase service account key
current_os = platform.system()

if current_os == "Linux":
    service_account_path = os.path.expanduser(
        "~") + "/Documents/cvision-firebase-key.json"
    config_file_path = os.path.join(os.path.expanduser(
        "~"), "Desktop", "debashis-workspace", "config", "anl-master-config.json")

elif current_os == "Windows":  # For Windows
    service_account_path = os.path.join(os.path.expanduser(
        "~"), "Documents", "cvision-firebase-key.json")
    config_file_path = os.path.join(
        "C:\\", "Users", "ddas", "Documents", "debashis-workspace", "config", "anl-master-config.json")

else:
    raise OSError(f"Unsupported operating system: {current_os}")

# Firebase Initialization
cred = credentials.Certificate(service_account_path)  # path to your Firebase service account credentials
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://c-vision-7e1ec-default-rtdb.firebaseio.com/'
})

# Function to listen for updates
def listen_for_updates():
    ref = db.reference('/vehicle_status')

    # Set up a listener to respond to any new updates in the Firebase database
    def listener(event):
        # The data published to Firebase (message from the cloud)
        update_data = event.data
        print(f"Received update from cloud: {update_data}")
        # Here, you can process the data (e.g., update navigation, apply changes, etc.)
        # Example: Display new route instructions
        # if 'route' in update_data:
        #     print(f"New route: {update_data['route']}")
        # if 'traffic_condition' in update_data:
        #     print(f"Traffic condition: {update_data['traffic_condition']}")

    # Attach the listener to the Firebase path
    ref.listen(listener)

# Example usage (Vehicle listens for cloud updates)
listen_for_updates()
