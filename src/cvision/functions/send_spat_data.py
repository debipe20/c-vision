import requests
import json
import datetime
import time # For simulating continuous sending

# --- Configuration ---
# !!! IMPORTANT: Replace this with the actual URL of your deployed 'ingestSpatData' Cloud Function !!!
CLOUD_FUNCTION_URL = "https://ingest-spat-data-aj7y3rjc4a-uc.a.run.app"
# Example: CLOUD_FUNCTION_URL = "https://us-central1-spat-data-exchange.cloudfunctions.net/ingestSpatData"

# --- Sample SPaT Data (as JSON) ---
# This function generates a simplified SPaT-like JSON payload.
# Adjust this function to accurately reflect the structure of your decoded J2735 SPaT data.
def generate_spat_json_payload(intersection_id, current_phase_state="unknown"):
    # This is a basic example structure. Your actual J2735 JSON will be more detailed.
    payload = {
        "intersectionId": intersection_id,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(), # ISO 8601 format
        "signalGroups": [
            {
                "id": 1,
                "state": current_phase_state, # e.g., "RED", "GREEN", "YELLOW"
                "minEndTime": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=5)).isoformat(),
                "maxEndTime": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=15)).isoformat()
            },
            {
                "id": 2,
                "state": "PED_CLEAR",
                "minEndTime": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=2)).isoformat(),
                "maxEndTime": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=10)).isoformat()
            }
        ],
        "vehicleApproaches": [
            { "lane": 1, "detectorStatus": "occupied" },
            { "lane": 2, "detectorStatus": "clear" }
        ]
        # ... add more fields as per your decoded J2735 structure
    }
    return payload

def send_data(payload):
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(CLOUD_FUNCTION_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Sent SPaT for {payload.get('intersectionId', 'N/A')}. Status: {response.status_code}, Response: {response.text}")
        return True
    except requests.exceptions.HTTPError as errh:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] HTTP Error for {payload.get('intersectionId', 'N/A')}: {errh}")
        print(f"Response content: {errh.response.text}")
    except requests.exceptions.ConnectionError as errc:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Connection Error for {payload.get('intersectionId', 'N/A')}: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Timeout Error for {payload.get('intersectionId', 'N/A')}: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] An unexpected error occurred for {payload.get('intersectionId', 'N/A')}: {err}")
    return False

if __name__ == "__main__":
    print("Starting SPaT data sender...")
    intersection_id_1 = "Intersection_MainAndFirst"
    intersection_id_2 = "Intersection_ElmAndOak"

    phase_states = ["RED", "GREEN", "YELLOW"]
    current_phase_index_1 = 0
    current_phase_index_2 = 1

    for i in range(10): # Send 10 updates
        # Simulate SPaT data for Intersection 1
        current_phase_index_1 = (current_phase_index_1 + 1) % len(phase_states)
        spat_payload_1 = generate_spat_json_payload(intersection_id_1, phase_states[current_phase_index_1])
        send_data(spat_payload_1)

        # Simulate SPaT data for Intersection 2
        current_phase_index_2 = (current_phase_index_2 + 1) % len(phase_states)
        spat_payload_2 = generate_spat_json_payload(intersection_id_2, phase_states[current_phase_index_2])
        send_data(spat_payload_2)

        time.sleep(2) # Wait for 2 seconds before sending the next update

    print("Finished sending sample SPaT data.")