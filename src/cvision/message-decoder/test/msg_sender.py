import socket
import json
import time
import os
import platform


# Read a config file into a json object:
current_os = platform.system()
        
if current_os == "Linux":
    config_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "c-vision", "config", "anl-master-config.json")

elif current_os == "Windows":
    config_file_path = os.path.join("C:\\", "Users", "ddas", "c-vision", "config", "anl-master-config.json")

else:
    raise OSError(f"Unsupported operating system: {current_os}")

config_file = open(config_file_path, "r")
config = json.load(config_file)
config_file.close()

hostIp = config["IPAddress"]["HostIp"]
port = config["PortNumber"]["V2XDataSender"]
msg_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
msg_sender_socket.bind((hostIp,port))

msg_decoder_port = config["PortNumber"]["MessageDecoder"]
client_info = (hostIp, msg_decoder_port)

msg_sending_time = 0.0

bsm = "001425004000009670D465F99BB7113E3626083F7FFFFFFFF0F312C0FDFA1FA1007FFF8000962580"
spat = "00136b455fbd01838cc00028055fbd4a920b00104343a264650001021a1d131d8b000c10d0e899194000808a87424747e00504343a264650003021a1d131d8b001c10d0e899194001008a87424747e00904343a263b16005023a1d091d09002c10d0e898ec5801808e8742474240"
map =  "001281173801302030e330054e818fe836d74be7178002dc051178296008a000000c000cad627c9028285b62feacc30e075028517b29824014144d66a0bd271b506433865821409e25e7da04204fb0a4110001120c4000830044400000400002b55d9500a0a663ab0538141458066800000500042a0987c40a0a6407a3ba8141448230aac640d46ca813ecd80c35521027d99038154205053604054dbc09f66c0432d36813d8d80a75e0802851b01bea98e04fb0a41a0000920440004300884000004000029be47400a0a1c164140580aa80000060003899cfac46fefc550df39d5b23edfa7531f5ecfc009f623edfa48b1f4ddeb00a0a23f439c8b5fb62ac8409ec148240003240900018601988000008000013dbf6c11fbddc9c"
while True:
    if time.time()-msg_sending_time >= 0.1:
        data = map
        msg_sender_socket.sendto(data.encode(),client_info)
        msg_sending_time = time.time()
        print("sent payload at time", time.time())

msg_sender_socket.close()