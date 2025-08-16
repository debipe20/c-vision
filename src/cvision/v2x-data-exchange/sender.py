"""
**********************************************************************************
sender.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------
Receives V2X messages (SPaT, MAP, BSM) over UDP, identifies message type based on payload prefix,
and uploads structured data to Firebase Realtime Database. It also updates a unified
`/LatestV2XMessage` node with the latest message for real-time forwarding.

Bonus:
------
Run with `--seed` to write one demo BSM and SPaT to Firebase for testing the web UI:
    python3 sender.py --seed

Usage (normal mode):
    python3 sender.py
**********************************************************************************
"""

import os
import platform
import socket
import time
import json
import argparse
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

# Load the Firebase service account key
current_os = platform.system()

if current_os == "Linux":
    service_account_path = os.path.expanduser("~") + "/Documents/cvision-firebase-key.json"
    config_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "debashis-workspace", "config", "anl-master-config.json")
    
elif current_os == "Windows":  # For Windows
    service_account_path = os.path.join(os.path.expanduser("~"), "Documents", "cvision-firebase-key.json")
    config_file_path = os.path.join("C:\\", "Users", "Documents", "debashis-workspace", "config", "anl-master-config.json")
        
else:
    raise OSError(f"Unsupported operating system: {current_os}")

cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://c-vision-7e1ec-default-rtdb.firebaseio.com/'
})

def main():
    config_file = open(config_file_path, "r")
    config = json.load(config_file)
    config_file.close()
    
    host_ip = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["V2XDataSender"]
    msgReceiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msgReceiverSocket.bind((host_ip, port))

    payload_prefix = "Payload="
    map_identifier = "0012"
    spat_identifier = "0013"
    bsm_identifier = "0014"
    

    print(f"📡 Listening on {host_ip}:{port}")

    while True:
        try:
            data, _ = msgReceiverSocket.recvfrom(1024)
            decoded_data = data.decode(errors='ignore')

            prefix_index = decoded_data.find(payload_prefix)
            if prefix_index == -1:
                continue

            payload = decoded_data[prefix_index + len(payload_prefix):].strip()

            print(f"Received payload: {payload}")

            # Detect payload type
            if payload.startswith(map_identifier):
                ref = db.reference('/MAPData')
                msg_type = "MAP"

            elif payload.startswith(spat_identifier):
                ref = db.reference('/SPaTData')
                msg_type = "SPaT"
                
            elif payload.startswith(bsm_identifier):
                ref = db.reference('/BSMData')
                msg_type = "BSM"
            
            else:
                print("Unknown payload type, skipping...")
                continue

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

            print(f"{msg_type} message uploaded to Firebase")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print("Error:", e)

    msgReceiverSocket.close()

# ------------------------------------------------------------------------------
# Seed demo BSM/SPaT for the web UI (/bsm, /spat)
# ------------------------------------------------------------------------------
# -----------------------------
# Test seed (writes to /bsm and /spat for the web UI)
# Usage: python3 sender.py --seed
# -----------------------------

def seed_test_records():
    spat_payload = {
        "SPaTInfo": [
            {
                "IntersectionName": "KearneyRd & WaterTower",
                "IntersectionID": 2351,
                "phaseStates": [
                    {"phase": 2, "state": "permissiveMovementAllowed", "maneuver":"left-through", "direction": "NorthBound"},
                    {"phase": 4, "state": "stopAndRemain", "maneuver":"left-right", "direction": "WestBound"},
                    {"phase": 6, "state": "protectedMovementAllowed", "maneuver":"through-right", "direction": "SouthBound"}
                ],
                "lat": 41.711326,
                "lon": -87.992046,
                "timestamp": time.time()
            },
            {
                "IntersectionName": "KearneyRd & WestgateRd",
                "IntersectionID": 2350,
                "phaseStates": [
                    {"phase": 2, "state": "stopAndRemain", "maneuver":"left-through-right", "direction": "EastBound"},
                    {"phase": 4, "state": "permissiveMovementAllowed", "maneuver":"left-through-right", "direction": "SouthBound"},
                    {"phase": 6, "state": "stopAndRemain", "maneuver":"left-through-right", "direction": "WestBound"},
                    {"phase": 8, "state": "permissiveMovementAllowed", "maneuver":"left-through-right", "direction": "NorthBound"}
                ],
                "lat": 41.715538,
                "lon": -87.992211,
                "timestamp": time.time()
            }
        ]
    }

    # Write to /spat (overwrites existing)
    db.reference("spat").set(spat_payload)

    # Vehicle near Argonne
    db.reference("bsm/test-veh-1").set({
        "lat": 41.710676,
        "lon": -87.992046,
        "speed_mps": 11.5,
        "heading_deg": 360,
        "ts": int(time.time() * 1000)
    })

    # Optional: also bump a "latest" node for debugging/visibility
    db.reference("LatestV2XMessage").set({
        "type": "SEED",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "payload": "Seeded SPaTInfo with two intersections."
    })

    print("✅ Seeded SPaTInfo demo at /spat")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="V2X sender")
    parser.add_argument("--seed", action="store_true",
                        help="Write one demo BSM and SPaT to Firebase and exit.")
    args, _ = parser.parse_known_args()

    if args.seed:
        seed_test_records()
    else:
        main()


# if __name__ == '__main__':
#     main()