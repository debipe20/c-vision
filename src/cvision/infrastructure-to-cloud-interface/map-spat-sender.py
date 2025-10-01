"""
**********************************************************************************
map-spatsender.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------
Receives V2X messages (SPaT & MAP) over UDP from a traffic signal controller.
Identifies message type based on payload prefix, and 
Uploads structured data to Firebase Realtime Database. 
It also updates a unified `/LatestV2XMessage` node with the latest message for real-time forwarding.

Usage:
    python3 map-spatsender.py               # without header, payload only
    python3 map-spatsender.py --header      # with 'Payload=' prefix header

**********************************************************************************
"""

import os
import platform
import socket
import time
import json
import argparse
import firebase_admin
from firebase_admin import credentials, db


def load_config_paths():
    current_os = platform.system()

    if current_os == "Linux":
        service_account_path = os.path.expanduser("~") + "/Documents/cvision-firebase-key.json"
        config_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "c-vision", "config", "anl-master-config.json")

    elif current_os == "Windows":  # For Windows
        service_account_path = os.path.join(os.path.expanduser("~"), "Documents", "cvision-firebase-key.json")
        config_file_path = os.path.join("C:\\", "Users", "ddas", "Documents", "c-vision", "config", "anl-master-config.json")

    else:
        raise OSError(f"Unsupported operating system: {current_os}")
 
    return service_account_path, config_file_path

def initialize_firebase(service_account_path: str):
    cred = credentials.Certificate(service_account_path)
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app(cred, {'databaseURL': 'https://c-vision-7e1ec-default-rtdb.firebaseio.com/'})


def main(args):
    """
    Main function for the MAP & SPaT sende
    """
   
    # --- setup paths & firebase ---
    service_account_path, config_file_path = load_config_paths()
    initialize_firebase(service_account_path)

    # --- load config ---
    config_file = open(config_file_path, "r")
    config = json.load(config_file)
    config_file.close()

    host_ip = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["V2XDataSender"]

    # --- UDP socket ---
    map_spat_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    map_spat_sender_socket.bind((host_ip, port))
    map_spat_sender_socket.settimeout(1.0)

    # --- identifiers & constants ---
    payload_prefix = "Payload="
    map_identifier = "0012"
    spat_identifier = "0013"
    bsm_identifier = "0014"

    print(f"Listening on {host_ip}:{port}")
    print("Press Ctrl+C to quit.")

    try:
        while True:
            try:
                data, _ = map_spat_sender_socket.recvfrom(2048)
                decoded_data = data.decode(errors='ignore')

                # Check if data contains header or just the payload
                if args.header:
                    # Process with header
                    prefix_index = decoded_data.find(payload_prefix)
                    if prefix_index == -1:
                        continue  # No Payload prefix found, skip this message

                    payload = decoded_data[prefix_index + len(payload_prefix):].strip()
                    # print(f"Received payload (with header): {payload}")
                    # print("Received payload (with header)")

                else:
                    # Process without header (only payload)
                    payload = decoded_data.strip()
                    # print(f"Received payload (without header): {payload}")
                    # print("Received payload (without header)")

                # Detect payload type
                if payload.startswith(map_identifier):
                    # ref = db.reference('/MAPData')
                    msg_type = "MAP"

                elif payload.startswith(spat_identifier):
                    # ref = db.reference('/SPaTData')
                    msg_type = "SPaT"

                elif payload.startswith(bsm_identifier):
                    # ref = db.reference('/BSMData')
                    msg_type = "BSM"

                else:
                    print("Unknown payload type, skipping...")
                    continue

                # Send to Firebase
                # ref.set({
                #     "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                #     "payload": payload
                # })

                # Send to unified /LatestV2XMessage
                ref_latest = db.reference('/LatestV2XMessage')
                ref_latest.set({
                    "msg_type": msg_type,
                    "posix_timestamp": time.time(),
                    # "verbose_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "payload": payload
                })

                print(f"{msg_type} message uploaded to Firebase")

            except socket.timeout:
                continue

    except KeyboardInterrupt:
        print("Stopping the program...")
    finally:
        map_spat_sender_socket.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MAP/SPaT UDP → Firebase sender")
    parser.add_argument("--header", action="store_true", help="Incoming UDP has 'Payload=' prefix header")
    args = parser.parse_args()
    main(args)

