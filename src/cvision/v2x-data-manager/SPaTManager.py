
import time
import json
import os
import platform
import warnings 
from typing import Dict, List, Tuple
import firebase_admin
from firebase_admin import credentials, db

STATE_MAP: Dict[str, str] = {
    "red": "stopAndRemain",
    "permissive_green": "permissiveMovementAllowed",
    "protected_green": "protectedMovementAllowed",
    "permissive_yellow": "yellow",
    "protected_yellow": "yellow",
    # Fallbacks if they ever appear
    "unknown": "stopAndRemain",
    "dark": "stopAndRemain",
    "flashing_red": "stopAndRemain",
    "flashing_yellow": "yellow",
}

class SpatManager:
    def __init__(self):
        """
        """
        self.get_firebase_credential()
        self.phases_by_intersection_id, self.intersections_name = self.load_phases_and_names()
        self.init_intersections_store()
        
    def get_firebase_credential(self):
        current_os = platform.system()
        if current_os == "Linux":
            service_account_path = os.path.expanduser("~") + "/Documents/cvision-firebase-key.json"
        
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://c-vision-7e1ec-default-rtdb.firebaseio.com/'
        })

    def init_intersections_store(self):
        """Create an in-memory dict for all intersections (lazy-inited)."""
        self.intersections_store = {}
        now_ms = int(time.time() * 1000)
        for intersection_id, phases in self.phases_by_intersection_id.items():
            self.intersections_store[intersection_id] = {
                "intersectionId": intersection_id,
                "name": self.intersections_name.get(intersection_id),
                "timestamp": now_ms,
                "phaseStates": [
                    {"phase": p, "state": "stopAndRemain", "minEndTime": None, "maxEndTime": None}  # J2735 'unknown' mapping
                    for p in phases
                ],
            }

    def load_phases_and_names(self, path: str = "intersections-config.json") -> Tuple[Dict[str, List[int]], Dict[str, str]]:
        with open(path, "r", encoding="utf-8") as intersections_config_file:
            intersections_config_data = json.load(intersections_config_file)

        intersections_config_items = intersections_config_data.get("intersections")
        if not isinstance(intersections_config_items, list):
            raise ValueError("Config must contain an 'intersections' array.")

        phases_by_id: Dict[str, List[int]] = {}
        names_by_id: Dict[str, str] = {}

        for index, data in enumerate(intersections_config_items):
            if not isinstance(data, dict):
                raise ValueError(f"Entry {index} must be an object.")
            id_val = data.get("id")
            phases = data.get("phases")
            name = data.get("name", "")

            if id_val is None or phases is None:
                raise ValueError(f"Entry {index} missing 'id' or 'phases'.")

            key = str(id_val)
            if not isinstance(phases, list) or not all(isinstance(p, int) for p in phases):
                raise ValueError(f"'phases' for id {key} must be a list of integers.")

            phases_by_id[key] = sorted(dict.fromkeys(phases))
            if name:
                names_by_id[key] = str(name)

        return phases_by_id, names_by_id

    def generate_intersection_data_dictionary(self, jsonString):
        """
        Map incoming SPaT JSON into payload and write to Firebase.
        Uses direct indexing (fast) and emits only configured phases.
        """
        intersection_id = str(jsonString["Spat"]["intersectionState"]["intersectionID"])
        intersection_id = str(2351)
        phases_config = self.phases_by_intersection_id.get(intersection_id)
        if phases_config is None:
            raise KeyError(f"Unknown intersection id: {intersection_id}")

        # Build lookup: phaseNo -> raw state from message
        incoming_by_phase = {}
        for phase_data in jsonString["Spat"]["phaseState"]:
            phases = int(phase_data["phaseNo"])
            raw_state = str(phase_data.get("currState", "unknown")).lower()
            min_end = phase_data.get("minEndTime")
            max_end = phase_data.get("maxEndTime")
            incoming_by_phase[phases] = (raw_state, min_end, max_end)

        # --- Warnings for extras/missing (non-fatal) ---
        intersection_configuration_set = set(phases_config)
        incoming_set = set(incoming_by_phase.keys())

        extras = sorted(incoming_set - intersection_configuration_set)       # present in message, not in config
        if extras:
            warnings.warn(
                f"SPaT for intersection id {intersection_id} contains unknown phases {extras}; ignoring.",
                RuntimeWarning,
            )

        missing = sorted(intersection_configuration_set - incoming_set)      # in config, missing in message
        if missing:
            warnings.warn(
                f"SPaT for intersection id {intersection_id} missing phases {missing}; filling as 'unknown'.",
                RuntimeWarning,
            )

        # Build and publish only configured phases, in configured order
        phase_states = []
        for phases in phases_config:
            raw_state = incoming_by_phase.get(phases, "unknown")
            mapped_state = STATE_MAP.get(raw_state, "stopAndRemain")
            phase_states.append({"phase": phases, "state": mapped_state, "minEndTime": min_end, "maxEndTime": max_end,})

        intersection_data_dictionary = {
            "timestamp": int(time.time() * 1000),   # ms
            "phaseStates": phase_states
        }

        return intersection_id, intersection_data_dictionary

    def get_intersections_store(self):
        """Accessor for the whole in-memory store."""
        if not hasattr(self, "intersections_store"):
            self._init_intersections_store()
        return self.intersections_store

    def get_intersection_snapshot(self, intersection_id: str):
        """Accessor for a single intersection snapshot."""
        if not hasattr(self, "intersections_store"):
            self._init_intersections_store()
        return self.intersections_store.get(str(intersection_id))
    
    def manage_spat_data(self, jsonString):
        """
        Map incoming SPaT JSON into payload and write to Firebase.
        Uses direct indexing (fast) and emits only configured phases.
        Also keeps an in-memory store in sync (no duplicated logic).
        """
        # Build payload once via helper
        intersection_id, intersection_data_dictionary = self.generate_intersection_data_dictionary(jsonString)

        
        
        if intersection_id in self.intersections_store:
            self.intersections_store[intersection_id]["timestamp"] = intersection_data_dictionary["timestamp"]
            self.intersections_store[intersection_id]["phaseStates"] = intersection_data_dictionary["phaseStates"]

        # Write to Firebase (your existing path)
        db.reference(f"intersection_status/{intersection_id}").set(intersection_data_dictionary)

        
'''##############################################
                   Unit testing
##############################################'''
if __name__ == "__main__":

    spat_manager = SpatManager()
    PHASES_BY_ID, INTERSECTION_NAMES = spat_manager.load_phases_and_names()
    print(PHASES_BY_ID)
    print(INTERSECTION_NAMES)