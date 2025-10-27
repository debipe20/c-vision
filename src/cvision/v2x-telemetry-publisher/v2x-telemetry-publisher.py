"""
**********************************************************************************
v2x-data-manager.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
Description:
------------
Listens for V2X messages forwarded from Firebase by listener.js over UDP.

Usage:
    python3 v2x-data-manager.py
**********************************************************************************
"""

import socket
import json
import os
import platform
import sys 
from SpatManager import SpatManager
from BsmManager import BsmManager

def main():
    """Entry point for the V2X data manager.

    Creates managers (SPaT/BSM), then listens for incoming messages and dispatches
    them to the appropriate handler. This function is intended to be invoked from
    the module `__main__` guard.
    """
    current_os = platform.system()
        
    if current_os == "Linux":
        config_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "debashis-workspace", "config", "anl-master-config.json")

    elif current_os == "Windows":
        config_file_path = os.path.join("C:\\", "Users", "ddas", "debashis-workspace", "config", "anl-master-config.json")

    else:
        raise OSError(f"Unsupported operating system: {current_os}")

    config_file = open(config_file_path, "r")
    config = json.load(config_file)
    config_file.close()

    host_ip = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["V2XDataManager"]

    v2x_data_manager_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    v2x_data_manager_socket.bind((host_ip, port))

    spatManager = SpatManager()
    bsmManager = BsmManager()

    try:
        while True:
            data, addr = v2x_data_manager_socket.recvfrom(65536)

            # --- Hardened decoding & JSON validation ---
            if not data:
                print(f"Ignoring empty UDP datagram from {addr}")
                continue

            try:
                text = data.decode("utf-8", errors="strict").strip()
            except UnicodeDecodeError as e:
                print(f"Ignoring non-UTF8 datagram from {addr}: {e}")
                continue

            if not text or text[0] not in "{[":
                # Quick filter for clearly non-JSON messages
                preview = text.replace("\n", "\\n")[:200]
                print(f"Ignoring non-JSON datagram from {addr}: '{preview}'")
                continue

            try:
                receivedMessage = json.loads(text)
            except json.JSONDecodeError as e:
                preview = text.replace("\n", "\\n")[:400]
                print(f"Bad JSON from {addr}: {e}. Payload (truncated): '{preview}'")
                continue
            # --- End hardening ---

            # print("Received following message:\n", receivedMessage)

            try:
                msg_type = receivedMessage.get("MsgType")
                if msg_type == "SPaT":
                    spatManager.manage_spat_data(receivedMessage)
                    print("Received SPaT & updated intersection status")
                    
                elif msg_type == "BSM":
                    bsmManager.manage_bsm_data(receivedMessage)
                    print("Received BSM & updated vehicle status")
                
                else:
                    print(f"Unknown MsgType; dropping: {msg_type}")
            
            except Exception as handler_err:
                print(f"Handler error for {receivedMessage.get('MsgType')}: {handler_err}")

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Shutting down gracefully...")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        try:
            v2x_data_manager_socket.close()
            print("Socket closed.")
        finally:
            sys.exit(0)

if __name__ == "__main__":
    main()