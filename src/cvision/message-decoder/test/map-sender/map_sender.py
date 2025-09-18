import socket
import json
import time
import os
import platform


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
# port = config["PortNumber"]["V2XDataSender"]
port = 5001
map_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
map_sender_socket.bind((hostIp,port))

msg_decoder_port = config["PortNumber"]["MessageDecoder"]
client_info = (hostIp, msg_decoder_port)

file_name = "map-hex.txt"
file = open(file_name, "r")
send_period = 1.0  # 1 Hz
next_time = time.perf_counter()

try:
    with open(file_name, "r") as file:
        while True:
            line = file.readline()
            if not line: # EOF reached -> rewind to loop the file
                file.seek(0)
                continue

            data = line.strip()
            if not data:
                continue  # skip blank lines

            payload = data.encode()

            now = time.perf_counter()
            sleep_s = next_time - now
            if sleep_s > 0:
                time.sleep(sleep_s)
            next_time += send_period

            map_sender_socket.sendto(payload,client_info)
            print(f"sent payload at time {time.time():.6f}")

except KeyboardInterrupt:
    print("\nStopped by user.")
    
finally:
    map_sender_socket.close()