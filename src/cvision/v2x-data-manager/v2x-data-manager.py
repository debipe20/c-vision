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
            data, addr = v2x_data_manager_socket.recvfrom(4096)
            data = data.decode()
            receivedMessage = json.loads(data)
            print("Received following message:\n", receivedMessage)
            
            if receivedMessage["MsgType"]== "SPaT":
                spatManager.manage_spat_data(receivedMessage)

            elif receivedMessage["MsgType"]== "BSM":
                print("Received BSM")
                bsmManager.manage_bsm_data(receivedMessage)

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Shutting down gracefully...")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        try:
            v2x_data_manager_socket.close()
            print("Socket closed.")
        finally:
            # Ensure we don't fall through to the __main__ guard below
            sys.exit(0)
    # ----------------------------------------------------------------

    v2x_data_manager_socket.close()
    
if __name__ == "__main__":
    main()
