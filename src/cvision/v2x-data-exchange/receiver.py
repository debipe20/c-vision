import socket
import json

HOST = '127.0.0.1'
PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"📡 Python UDP server listening on {HOST}:{PORT}...")

while True:
    data, addr = sock.recvfrom(4096)
    try:
        message = json.loads(data.decode())
        print("📥 Received from Node.js:", message)
    except Exception as e:
        print("❌ Error decoding message:", e)
