import socket
import json
import time
import os
import platform
from itertools import cycle

FILENAMES = ["bsm.json", "bsm1.json"]

# Read a config file into a json object:
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

hostIp = config["IPAddress"]["HostIp"]
port = config["PortNumber"]["MessageDecoder"]
bsm_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
bsm_sender_socket.bind((hostIp,port))

vehicleServerPort = config["PortNumber"]["VehicleServer"]
client_info = (hostIp, vehicleServerPort)

# Load/validate JSON once
fileName = "bsm.json"
with open(fileName, "r", encoding="utf-8") as f:
    obj = json.load(f)                          # validates JSON
encoded_data = json.dumps(obj).encode("utf-8")       # normalized JSON bytes

send_period = 0.1  # 10HZ
next_time = time.perf_counter()

try:
    for fname in cycle(FILENAMES):
        # pace at fixed period
        now = time.perf_counter()
        sleep_s = next_time - now
        if sleep_s > 0:
            time.sleep(sleep_s)
        next_time += send_period

        # read & send
        try:
            with open(fname, "r", encoding="utf-8") as f:
                data = f.read()
            bsm_sender_socket.sendto(data.encode("utf-8"), client_info)
            print(f"Sent {fname} at {time.time():.3f}")
        except FileNotFoundError:
            print(f"[WARN] {fname} not found; skipping.")

except KeyboardInterrupt:
    print("Stopping…")
    
finally:
    bsm_sender_socket.close()