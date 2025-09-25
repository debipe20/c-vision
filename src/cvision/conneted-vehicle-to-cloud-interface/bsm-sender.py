
"""
**********************************************************************************
bsm-sender.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------
Reads V2X messages (BSM) from a file and
Uploads structured data to Firebase Realtime Database. 
It also updates a unified `/LatestV2XMessage` node with the latest message for real-time forwarding.

Usage:
    python3 bsm-sender.py               
**********************************************************************************
"""
import os
import platform
import time
import firebase_admin
from firebase_admin import credentials, db


def load_config_paths():
    current_os = platform.system()

    if current_os == "Linux":
        service_account_path = os.path.expanduser("~") + "/Documents/cvision-firebase-key.json"
        config_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "debashis-workspace", "config", "anl-master-config.json")

    elif current_os == "Windows":  # For Windows
        service_account_path = os.path.join(os.path.expanduser("~"), "Documents", "cvision-firebase-key.json")
        config_file_path = os.path.join("C:\\", "Users", "ddas", "Documents", "debashis-workspace", "config", "anl-master-config.json")

    else:
        raise OSError(f"Unsupported operating system: {current_os}")
 
    return service_account_path, config_file_path

def initialize_firebase(service_account_path: str):
    cred = credentials.Certificate(service_account_path)
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app(cred, {'databaseURL': 'https://c-vision-7e1ec-default-rtdb.firebaseio.com/'})

def main():

    # --- setup paths & firebase ---
    service_account_path, config_file_path = load_config_paths()
    initialize_firebase(service_account_path)

   
    file_name = "bsm-hex.txt"
    # file_name = "bsm-hex-mixed-id.txt"

    send_period = 0.1  # 10 Hz
    next_time = time.perf_counter()


    try:
        with open(file_name, "r") as file:
            while True:
                line = file.readline()
                if not line: # EOF reached -> rewind to loop the file
                    file.seek(0)
                    continue

                payload = line.strip()
                if not payload:
                    continue  # skip blank lines

                now = time.perf_counter()
                sleep_s = next_time - now
                if sleep_s > 0:
                    time.sleep(sleep_s)
                next_time += send_period

                ref = db.reference('/BSMData')
                msg_type = "BSM"

                 # Send to Firebase
                ref.set({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "payload": payload
                })

                # Send to unified /LatestV2XMessage
                ref_latest = db.reference('/LatestV2XMessage')
                ref_latest.set({
                    "type": msg_type,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "payload": payload
                })

                print(f"{msg_type} message uploaded to Firebase at time {time.time():.6f}")

    except FileNotFoundError:
        print(f"Input file not found: {file_name}")
        
    except KeyboardInterrupt:
        print("\nStopped by user.")

if __name__ == "__main__":
    main()