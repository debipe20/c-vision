import os
import socket
import time
import firebase_admin
from firebase_admin import credentials, db

# Load the Firebase service account key
sevrice_account_path = os.path.expanduser("~") + "/Documents/cvision-firebase-key.json"
cred = credentials.Certificate(sevrice_account_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://c-vision-7e1ec-default-rtdb.firebaseio.com/'
})

def main():
    hostIp = "192.168.26.103"
    port = 50002
    msgReceiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msgReceiverSocket.bind((hostIp, port))

    payload_prefix = "Payload="
    map_identifier = "0012"
    spat_identifier = "0013"
    bsm_identifier = "0014"
    

    print(f"📡 Listening on {hostIp}:{port}")

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
            if payload.startswith(bsm_identifier):
                ref = db.reference('/BSMData')
                msg_type = "BSM"

            elif payload.startswith("0012"):
                ref = db.reference('/MAPData')
                msg_type = "MAP"

            elif payload.startswith(spat_identifier):
                ref = db.reference('/SPaTData')
                msg_type = "SPaT"
            
            else:
                print("⚠️ Unknown payload type, skipping...")
                continue

            # Send to Firebase
            ref.set({
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