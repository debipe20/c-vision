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
port = config["PortNumber"]["V2XDataSender"]
msg_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
msg_sender_socket.bind((hostIp,port))

msg_decoder_port = config["PortNumber"]["V2XDataReceiver"]
client_info = (hostIp, msg_decoder_port)

msg_sending_time = 0.0

bsm = "001425004000009670D465F99BB7113E3626083F7FFFFFFFF0F312C0FDFA1FA1007FFF8000962580"
spat = "00136b455fbd01838cc00028055fbd4a920b00104343a264650001021a1d131d8b000c10d0e899194000808a87424747e00504343a264650003021a1d131d8b001c10d0e899194001008a87424747e00904343a263b16005023a1d091d09002c10d0e898ec5801808e8742474240"

while True:
    if time.time()-msg_sending_time >= 0.1:
        data = bsm
        msg_sender_socket.sendto(data.encode(),client_info)
        msg_sending_time = time.time()
        print("sent BSM at time", time.time())

msg_sender_socket.close()