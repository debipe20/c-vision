"""
**********************************************************************************
receiver.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
Description:
------------
Listens for V2X messages forwarded from Firebase by listener.js over UDP.
Prints/logs received messages. Can be extended to validate and acknowledge BSM messages.

Usage:
    python3 receiver.py
**********************************************************************************
"""

import socket
import json
import os
import platform

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
port = config["PortNumber"]["MessageDecoder"]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host_ip, port))

print(f"Python UDP server listening on {host_ip}:{port}...")

while True:
    data, addr = sock.recvfrom(4096)
    try:
        message = json.loads(data.decode())
        print("Received from Node.js:", message)
        
    except Exception as e:
        print("Error decoding message:", e)
