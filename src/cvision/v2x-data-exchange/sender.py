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
import signal
import sys
import socket
import time
import json
import random
import argparse
from datetime import datetime
from typing import Dict, List
import firebase_admin
from firebase_admin import credentials, db

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

cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://c-vision-7e1ec-default-rtdb.firebaseio.com/'
})

# Declare the socket globally so the signal handler can access it
msgReceiverSocket = None


def exit_gracefully(signum, frame):
    """
    Signal handler to close the socket and exit the program.
    """
    global msgReceiverSocket
    print(f"\n👋 Received signal {signum}, shutting down gracefully...")
    if msgReceiverSocket:
        msgReceiverSocket.close()
    sys.exit(0)


def main():
    """
    Main function for the V2X sender.
    """
    global msgReceiverSocket

    config_file = open(config_file_path, "r")
    config = json.load(config_file)
    config_file.close()

    host_ip = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["V2XDataSender"]
    msgReceiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msgReceiverSocket.bind((host_ip, port))
    # Add this line here
    msgReceiverSocket.settimeout(1.0)

    payload_prefix = "Payload="
    map_identifier = "0012"
    spat_identifier = "0013"
    bsm_identifier = "0014"

    # Register the signal handler for Ctrl+C and Ctrl+Break on Windows
    signal.signal(signal.SIGINT, exit_gracefully)
    if platform.system() == "Windows":
        signal.signal(signal.SIGBREAK, exit_gracefully)

    print(f"📡 Listening on {host_ip}:{port}")
    print("Press Ctrl+C to quit.")

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

        except socket.timeout:
            # This is where your program checks for signals
            continue
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


PHASES_BY_ID: Dict[str, List[int]] = {
    "2351": [2, 4, 6],  # KearneyRd & WaterTower
    "2350": [2, 4, 6, 8],  # KearneyRd & WestgateRd
    "3002": [1, 2, 3, 4, 5, 6, 7, 8],  # RooseVeltRd & CanalSt
    "3006": [1, 2, 3, 4, 5, 6, 7, 8],  # RooseVeltRd & MichiganAve
    "44383": [1, 2, 3, 4, 5, 6, 7, 8],  # DaisyMountainDr & GavilanPeakPkwy
}

# Allowed phase states (adjust to your pipeline)
PHASE_STATES = [
    "stopAndRemain",
    "permissiveMovementAllowed",
    "protectedMovementAllowed",
    "yellow"
]

# --- SPaT slim updates (/intersection_updates/<id>) ---
def push_spat_update(int_id: str, phases: List[int]) -> None:
    phase_states = [{"phase": ph, "state": random.choice(PHASE_STATES)} for ph in phases]
    payload = {
        "timestamp": int(time.time() * 1000),   # ms
        "phaseStates": phase_states,
    }
    db.reference(f"spat/{int_id}").set(payload)


# --- Vehicle updates (both new + back-compat) ---
def push_vehicle_update(veh_id: str, lat: float, lon: float,
                        speed_mps: float = 0.0, heading_deg: float = 0.0) -> None:
    now_ms = int(time.time() * 1000)

    # New slim path (optional, keep if you plan to migrate UI later)
    db.reference(f"bsm/{veh_id}").set({
        "lat": lat,
        "lon": lon,
        "speed": speed_mps,
        "heading": heading_deg,
        "timestamp": now_ms,
    })

    # Backward-compatible path & field names for the current UI
    db.reference(f"bsm/{veh_id}").set({
        "lat": lat,
        "lon": lon,
        "speed_mps": speed_mps,
        "heading_deg": heading_deg,
        "ts": now_ms,
    })



def seed_test_records(loop: bool = False, period_sec: int = 5) -> None:
    """Seed slim SPaT updates + vehicle updates for testing."""
    def once():
        for iid, phases in PHASES_BY_ID.items():
            push_spat_update(iid, phases)
        print(f"✅ Updated {len(PHASES_BY_ID)} intersections")

        test_vehicles = {
            "101352": (41.710731, -87.992054, 12.3, 360.0),
            "102425": (41.711378, -87.991385, 4.2, 270.0),
            "952784": (41.715576, -87.993336, 3.3, 90.0),
            "712523": (41.715001, -87.992187, 5.4, 0.0),
            "211346": (41.867066, -87.624077, 12.3, 90.0),
            "629178": (41.867391, -87.625334, 5.3, 180.0),
            "321089": (41.867201, -87.639751, 6.2, 270.0),
            "450365": (33.843647, -112.135398, 8.5, 0.0),
            "815342": (33.842752, -112.136389, 6.5, 186.0)
        }
        for vid, (lat, lon, spd, hdg) in test_vehicles.items():
            push_vehicle_update(vid, lat, lon, spd, hdg)
        print("✅ Updated vehicles")

    if loop:
        while True:
            once()
            time.sleep(period_sec)
    else:
        once()


# def seed_test_records():
  
    # spat_payload = {
    #     "SPaTInfo": [
    #         {
    #             "IntersectionName": "KearneyRd & WaterTower",
    #             "IntersectionID": 2351,
    #             "phaseStates": [
    #                 {"phase": 2, "state": "permissiveMovementAllowed",
    #                     "maneuver": "through-right", "direction": "NorthBound"},
    #                 {"phase": 4, "state": "stopAndRemain",
    #                     "maneuver": "left-right", "direction": "WestBound"},
    #                 {"phase": 6, "state": "protectedMovementAllowed",
    #                     "maneuver": "left-through", "direction": "SouthBound"}
    #             ],
    #             "lat": 41.711326,
    #             "lon": -87.992046,
    #             "timestamp": time.time()
    #         },
    #         {
    #             "IntersectionName": "KearneyRd & WestgateRd",
    #             "IntersectionID": 2350,
    #             "phaseStates": [
    #                 {"phase": 2, "state": "stopAndRemain",
    #                     "maneuver": "left-through-right", "direction": "EastBound"},
    #                 {"phase": 4, "state": "permissiveMovementAllowed",
    #                     "maneuver": "left-through-right", "direction": "SouthBound"},
    #                 {"phase": 6, "state": "stopAndRemain",
    #                     "maneuver": "left-through-right", "direction": "WestBound"},
    #                 {"phase": 8, "state": "permissiveMovementAllowed",
    #                     "maneuver": "left-through-right", "direction": "NorthBound"}
    #             ],
    #             "lat": 41.715538,
    #             "lon": -87.992211,
    #             "timestamp": time.time()
    #         }
    #     ]
    # }

    # # Write to /spat (overwrites existing)
    # db.reference("spat").set(spat_payload)

    # # Vehicle near Argonne
    # db.reference("bsm/test-veh-1").set({
    #     "lat": 41.710676,
    #     "lon": -87.992046,
    #     "speed_mps": 11.5,
    #     "heading_deg": 360,
    #     "ts": int(time.time() * 1000)
    # })

    # # Optional: also bump a "latest" node for debugging/visibility
    # db.reference("LatestV2XMessage").set({
    #     "type": "SEED",
    #     "timestamp": datetime.utcnow().isoformat() + "Z",
    #     "payload": "Seeded SPaTInfo with two intersections."
    # })

    # print("✅ Seeded SPaTInfo demo at /spat")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="V2X sender")
    parser.add_argument("--seed", action="store_true",
                        help="Write one demo BSM and SPaT to Firebase and exit.")
    args, _ = parser.parse_known_args()

    if args.seed:
        seed_test_records(loop = True)
    else:
        main()
