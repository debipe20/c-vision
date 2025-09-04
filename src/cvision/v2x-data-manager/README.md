# C-VISION V2X Data Manager

A lightweight Python service that ingests V2X messages (SPaT + BSM), normalizes them, and publishes clean, structured records to Firebase Realtime Database (RTDB).

It’s designed to pair with a small Node forwarder (listener.js) that watches Firebase (e.g., /LatestV2XMessage) and emits each update over UDP, but you can feed it any UDP JSON source.

```bash
Firebase RTDB  ──>  listener.js  ──(UDP JSON)──>  v2x-data-manager.py
                                  ├─> SPaTManager.py  ──> intersection_status/{id}
                                  └─> BsmManager.py   ──> vehicle_status/{temporaryID}

```

---

## Features

- SPaT normalization: Maps raw J2735-ish states to a canonical schema (stopAndRemain, permissiveMovementAllowed, etc.) and preserves min/max end times.

- BSM parsing: Extracts position, speed, and heading; writes compact records keyed by vehicle temp ID.

- One-time Firebase init: Safe to construct both managers in one process without “default app already exists” errors.

- Config-driven intersections: Uses intersections-config.json to know which phases exist for each intersection and their display names.

---

## Repo Layout

- v2x-data-manager.py — Entry point. Opens a UDP socket, parses incoming JSON, dispatches to SPaT/BSM managers.

- SPaTManager.py — Normalizes SPaT messages and writes to RTDB: intersection_status/{intersection_id}.

- BsmManager.py — Parses Basic Safety Message (BSM/BasicVehicle) and writes to RTDB: vehicle_status/{temporaryID}.

- intersections-config.json — Static config: valid phases and display names for each intersection ID.

---
## Prerequisites

Python 3.8+

Firebase service account key JSON with Database access
Place it at:

Linux: ~/Documents/cvision-firebase-key.json

(Adjust the path in code if you prefer a different location.)

Firebase RTDB URL
The code defaults to:
```arduino

https://c-vision-7e1ec-default-rtdb.firebaseio.com/

```

Change this string in BsmManager.py / SPaTManager.py if you’re targeting a different project.

---

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install firebase-admin
```
---

## Acknowledgments

Developed within the Transportation & Power Systems context; thanks to contributors maintaining the V2X pipelines and Firebase infrastructure.
