import time
import json
import os
import platform
import firebase_admin
from firebase_admin import credentials, db


class BsmManager:
    def __init__(self):
        """
        """
        self.get_firebase_credential()

    def get_firebase_credential(self):
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

        vehicle_id = jsonString['BasicVehicle']['temporaryID']
        lattitude = jsonString['BasicVehicle']['position']['latitude_DecimalDegree']
        longitude = jsonString['BasicVehicle']['position']['longitude_DecimalDegree']
        elevation = jsonString['BasicVehicle']['position']['elevation_Meter']
        speed_mps = jsonString['BasicVehicle']['speed_MeterPerSecond']
        heading_degree = jsonString['BasicVehicle']['heading_Degree']
        now_ms = int(time.time() * 1000)

        vehicle_data_dictionary = {
            "lat": lattitude,
            "lon": longitude,
            "elev": elevation,
            "speed": speed_mps,
            "heading": heading_degree,
            "timestamp": now_ms,
        }

        db.reference(
            f"vehicle_status/{vehicle_id}").set(vehicle_data_dictionary)
