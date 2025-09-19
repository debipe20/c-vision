"""
**********************************************************************************
BsmManager.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------
Handles ingestion of Basic Safety Messages (BSM) and writes structured records
to Firebase Realtime Database (RTDB). Ensures Firebase is initialized exactly once
for the current process.
**********************************************************************************
"""
import time
import os
import platform
import firebase_admin
from firebase_admin import credentials, db

class BsmManager:
    """Manages BSM data lifecycle and persistence to Firebase RTDB."""
    def __init__(self):
        """
        Initialize the BSM manager and ensure Firebase is ready.
        This constructor calls :meth:`get_firebase_credential` to guarantee a
        single Firebase app instance exists for the process.
        """
        self.get_firebase_credential()

    def get_firebase_credential(self):
        """
        Initialize Firebase if it hasn't been initialized yet.

        Detects the OS (Linux or otherwise) and loads a service account key from
        `~/Documents/cvision-firebase-key.json`. If a default Firebase app already
        exists, this method is a no-op.

        Side Effects:
            Initializes (or reuses) the default Firebase app and sets the RTDB URL.

        Raises:
            FileNotFoundError: If the service account JSON file is missing.
            ValueError: If the service account file appears invalid.
        """
        current_os = platform.system()
        if current_os == "Linux":
            service_account_path = os.path.expanduser(
                "~") + "/Documents/cvision-firebase-key.json"

        cred = credentials.Certificate(service_account_path)
        try:
            # If already initialized, this succeeds; else it raises ValueError
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://c-vision-7e1ec-default-rtdb.firebaseio.com/'
            })

    def manage_bsm_data(self, jsonString):
        """
        Parse a Basic Safety Message (BSM) and write a normalized vehicle record to Firebase RTDB.

        Args:
        jsonString: Parsed BSM message as a dict.

        Returns:
            None

        Side Effects:
            Persists data to Firebase Realtime Database at `vehicle_status/{temporaryID}`.

        Raises:
            KeyError: If required fields are missing from `jsonString`.
            TypeError: If `jsonString` is not a dict or contains unexpected types.
        """
        vehicle_id = jsonString['BasicVehicle']['temporaryID']
        lattitude = jsonString['BasicVehicle']['position']['latitude_DecimalDegree']
        longitude = jsonString['BasicVehicle']['position']['longitude_DecimalDegree']
        elevation = jsonString['BasicVehicle']['position']['elevation_Meter']
        speed_mps = jsonString['BasicVehicle']['speed_MeterPerSecond']
        heading_degree = jsonString['BasicVehicle']['heading_Degree']
        lane_id = jsonString['BasicVehicle']['laneID']
        approach_id = jsonString['BasicVehicle']['approachID']
        signal_group = jsonString['BasicVehicle']['signalGroup']

        now_ms = int(time.time() * 1000)

        vehicle_data_dictionary = {
            "lat": lattitude,
            "lon": longitude,
            "elev": elevation,
            "speed": speed_mps,
            "heading": heading_degree,
            "lane_id": lane_id,
            "approach_id": approach_id,
            "signal_group": signal_group,
            "timestamp": now_ms,
        }

        db.reference(
            f"vehicle_status/{vehicle_id}").set(vehicle_data_dictionary)
