import os
import platform
import socket
import time
import json
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

            print(f"📥 Received payload: {payload}")

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
                print("⚠️ Unknown payload type, skipping...")
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

            print(f"✅ {msg_type} message uploaded to Firebase")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print("❌ Error:", e)

    msgReceiverSocket.close()

if __name__ == '__main__':
    main()