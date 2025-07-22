import requests
import json
import datetime
import time # For simulating continuous sending
import uuid # Added if you want to generate unique IDs for local tracking in the sender script

# --- Configuration ---
# Your deployed Cloud Function URL remains the same
CLOUD_FUNCTION_URL = "https://ingest-spat-data-hww35uderq-uc.a.run.app"

# --- Sample Encoded J2735 SPaT Data (as Hex String) ---
ENCODED_SPAT_HEX_PAYLOAD = "001380820018800001F58300001D4C1C3510B001043C00190032004B001023600258032003E800C10F001F4025802BC0080878015E019001C2005043C00E100FA011300302360089809600A2801C10F00514057805DC010087802EE0320035200A048C01A901C201DB006021E00ED80FA0106803812300834089808FC0200878047E04B004E2"

def send_encoded_spat_data(encoded_hex_data: str):
    # Convert hex string to bytes
    try:
        raw_bytes_payload = bytes.fromhex(encoded_hex_data)
    except ValueError as e:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error converting hex string to bytes: {e}")
        return False

    headers = {
        'Content-Type': 'application/octet-stream' # Generic binary content type
    }
    # Removed: 'params' dictionary for intersectionId as it's no longer a query param

    try:
        # Send POST request without query parameters
        response = requests.post(CLOUD_FUNCTION_URL, data=raw_bytes_payload, headers=headers)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Sent ENCODED SPaT. Status: {response.status_code}, Response: {response.text}")
        return True
    except requests.exceptions.HTTPError as errh:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] HTTP Error: {errh}")
        print(f"Response content: {errh.response.text}")
    except requests.exceptions.ConnectionError as errc:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Connection Error: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] An unexpected error occurred: {err}")
    return False

if __name__ == "__main__":
    print("Starting ENCODED SPaT data sender (without intersection ID query param)...")

    for i in range(3): # Send 3 updates of the same encoded payload
        print(f"\n--- Sending Round {i+1} ---")
        send_encoded_spat_data(ENCODED_SPAT_HEX_PAYLOAD)
        time.sleep(2) # Wait for 2 seconds before sending the next update

    print("\nFinished sending sample ENCODED SPaT data.")