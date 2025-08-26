from flask import Flask, request
import base64
import datetime
import os

app = Flask(__name__)

# --- Configuration ---
# !!! IMPORTANT: Match the port you use in EXTERNAL_BACKEND_URL in your Node.js function !!!
RECEIVER_PORT = 5000
# !!! IMPORTANT: Match the API Key used in your Node.js function (if applicable) !!!
EXPECTED_API_KEY = "YOUR_SECRET_API_KEY_FOR_BACKEND" # Same as BACKEND_API_KEY in Node.js

@app.route('/spat-receiver', methods=['POST'])
def receive_spat_data():
    # --- 1. API Key Authentication (Optional but Recommended) ---
    api_key = request.headers.get('X-API-Key')
    if EXPECTED_API_KEY != "YOUR_SECRET_API_KEY_FOR_BACKEND" and api_key != EXPECTED_API_KEY:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Unauthorized access attempt: Invalid X-API-Key.")
        return ("Unauthorized: Invalid API Key", 401)

    # --- 2. Get Payload ID (Optional, for tracking) ---
    payload_id = request.headers.get('X-Payload-ID', 'N/A')

    # --- 3. Get the raw encoded SPaT data from the request body ---
    # The Node.js function sends raw bytes, so we receive them directly here.
    encoded_spat_raw_bytes = request.get_data()

    if not encoded_spat_raw_bytes:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] No data received in POST body for payload ID: {payload_id}.")
        return ('No data received in body', 400)

    try:
        # You now have the raw J2735 SPaT bytes in 'encoded_spat_raw_bytes'
        # For demonstration, let's print its hex representation and size
        hex_representation = encoded_spat_raw_bytes.hex()
        data_size_bytes = len(encoded_spat_raw_bytes)

        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Received ENCODED SPaT data for payload ID: {payload_id}")
        print(f"  Size: {data_size_bytes} bytes")
        print(f"  Hex Preview (first 50 chars): {hex_representation[:50]}...")

        # !!! PLACE YOUR J2735 DECODING AND FURTHER PROCESSING LOGIC HERE !!!
        # Example: decoded_spat = your_j2735_decoder(encoded_spat_raw_bytes)

        return (f'Encoded SPaT data received and processed successfully for ID: {payload_id}', 200)

    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error processing received SPaT data for payload ID: {payload_id}: {e}", exc_info=True)
        return (f'Internal Server Error: {e}', 500)

if __name__ == '__main__':
    # IMPORTANT: Configure your firewall and router to allow incoming connections to this IP and port.
    # '0.0.0.0' means listen on all available network interfaces.
    # For testing within a local network, use the computer's actual local IP (e.g., 192.168.1.100).
    # For public access, you'll need a static public IP or a domain name and port forwarding/firewall rules.
    print(f"Starting SPaT receiver on http://0.0.0.0:{RECEIVER_PORT}/spat-receiver")
    app.run(host='0.0.0.0', port=RECEIVER_PORT, debug=False)