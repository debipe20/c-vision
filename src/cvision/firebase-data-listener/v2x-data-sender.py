import firebase_admin
from firebase_admin import credentials, db
import struct
import json
import socket
import time
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

# Function to get the local Wi-Fi IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # Connect to an external server to determine the IP (but without sending data)
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'  # Fallback to localhost if unable to determine
    finally:
        s.close()
    return ip

# Function to simulate generating V2X data (BSM, SPaT, or MAP)
def generate_v2x_data():
    # For example, a Basic Safety Message (BSM) in hexadecimal format
    payload_bsm = '00142a408994048f46d62740399e1b6ba9830c73ffffffffa042f04c7d7d07d07f7fff00007312c0000d0c0000'
    return payload_bsm

# Function to send data to Firebase
def send_to_firebase(payload, local_ip):
    ref = db.reference('/v2x_data')
    timestamp = int(time.time())  # Use current timestamp as unique key for messages
    
    # Push the data to Firebase
    ref.child(str(timestamp)).set({
        'message': payload,  # The V2X data payload (e.g., BSM, SPaT, MAP)
        'wifi_ip': local_ip,  # The local Wi-Fi IP address of the device
        'timestamp': timestamp
    })
    print(f"Data published to Firebase with timestamp: {timestamp}")

# Main function to run the process
def main():
    # Get local Wi-Fi IP address
    local_ip = get_local_ip()
    
    # Generate V2X data (e.g., BSM, SPaT, MAP)
    v2x_data = generate_v2x_data()
    
    # Send the V2X data along with the Wi-Fi IP address to Firebase
    send_to_firebase(v2x_data, local_ip)

# Run the main function
if __name__ == "__main__":
    main()
