# Connected Vehicle → Cloud Interface

This repo contains two scripts that bridge connected-vehicle data to Firebase and out via UDP:

- **`bsm-sender.py`** – reads hex BSM lines from a file and publishes them to **Firebase Realtime Database** (and a unified `/LatestV2XMessage` node).
- **`vehicle-status-listener.js`** – listens to per-vehicle status in **Firebase Realtime Database** and forwards updates as UDP packets to a configured host/port.

---

## Prerequisites

### Accounts & Credentials
- A Firebase project with **Realtime Database** enabled.
- A **service account key** JSON downloaded from Firebase Console → Project settings → Service accounts → *Generate new private key*.

> Place the key file at:
> - **Windows**: `C:\Users\<YOU>\Documents\cvision-firebase-key.json`
> - **Linux**: `/home/<you>/Documents/cvision-firebase-key.json`

### Configuration JSON (`anl-master-config.json`)
Expected at:
- **Windows**: `C:\Users\<YOU>\Documents\debashis-workspace\config\anl-master-config.json`
- **Linux**: `/home/<you>/Documents/debashis-workspace/config/anl-master-config.json`

Minimal required fields:
This is a sample Json:
``` json
{
  "IPAddress": { "HostIp": "127.0.0.1"}, 
  "PortNumber": { "MessageDecoder": 5000 },
  "VehicleInformation": { "EgoVehicleId": "VEHICLE_123" }
}
```

> Adjust IP/port to your UDP consumer.

---

## Directory Layout (suggested)
```
<workspace>/
└─ src/cvision/conneted-vehicle-to-cloud-interface/
   ├─ bsm-sender.py
   ├─ vehicle-status-listener.js
   ├─ bsm-hex.txt                # input file for sender (hex lines)
   ├─ package.json               # for Node listener
   └─ README.md
```

---

## Python – `bsm-sender.py`

### What it does
- Reads one line at a time from `bsm-hex.txt` (hex string per line).
- At 10 Hz (configurable), updates:
  - `/BSMData` → `{ timestamp, payload }`
  - `/LatestV2XMessage` → `{ type: "BSM", timestamp, payload }`

### Environment Setup
**Windows**
```powershell
# Install Python 3.9+ from python.org or Microsoft Store
py -V

# Create isolated env (recommended)
py -m venv .venv
. .\.venv\Scripts\Activate.ps1

# Install dependencies
py -m pip install --upgrade pip
py -m pip install firebase-admin
```

**Linux**
```bash
python3 -V
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install firebase-admin
```

### Configure Database URL
Inside the script (already present), set your RTDB URL:
```python
DB_URL = "https://c-vision-7e1ec-default-rtdb.firebaseio.com/"  # replace if different
```

### Run
**Windows**
```powershell
# from the script folder
python.exe bsm-sender.py
```
**Linux**
```bash
python3 bsm-sender.py
```

### Common Pitfalls & Fixes

## Node – `vehicle-status-listener.js`

### What it does
- Initializes Firebase Admin SDK using your service account.
- Reads config from `anl-master-config.json`.
- Subscribes to `/vehicle_status/<EgoVehicleId>` in RTDB.
- For each update, builds a JSON payload and sends it via **UDP** to `IPAddress.HostIp : PortNumber.MessageDecoder`.

### Environment Setup
**Windows / Linux**
```bash
# in the project folder with vehicle-status-listener.js
node -v                            # Node 18+ required (you have v22 → OK)

# initialize package.json if not present
npm init -y

# install Firebase Admin SDK
npm install firebase-admin
```

> If behind a proxy:
> ```bash
> npm config set registry https://registry.npmjs.org/
> npm config set proxy http://<proxy>:<port>
> npm config set https-proxy http://<proxy>:<port>
> ```

### Run
```bash
node vehicle-status-listener.js
```

### Windows Firewall
- When first sending UDP, Windows may prompt for network access. Allow Node.js.

---

## Troubleshooting: Firebase Admin on Windows

### Symptom A: `MODULE_NOT_FOUND ... node_modules\firebase-admin\lib\index.js`
- **Cause**: truncated install (only `package.json`, no `lib/`) or running from the wrong directory.
- **Fix** (run in the *project* folder):
  ```powershell
  # remove broken install
  Remove-Item -Recurse -Force node_modules, package-lock.json

  # ensure public registry & clean cache
  npm config set registry https://registry.npmjs.org/
  npm cache clean --force
  npm cache verify

  # reinstall
  npm install

  # verify lib exists now
  Get-ChildItem .\node_modules\firebase-admin\lib | Select-Object -First 10
  ```

### Symptom B: `ERR_PACKAGE_PATH_NOT_EXPORTED` resolving `firebase-admin/package.json`
- **Cause**: attempting to resolve internal subpaths not exposed by `"exports"`.
- **Fix**: use **subpath imports** (`firebase-admin/app`, `firebase-admin/database`) and avoid `require('.../package.json')` or legacy deep paths.

### Symptom C: Works on Linux, fails on Windows
- **Likely**: different working directory, antivirus quarantining files, or proxy.
- **Actions**:
  - Confirm you’re running `node` in the folder that contains `vehicle-status-listener.js` and `package.json`.
  - Temporarily disable AV real-time scanning during `npm install`.
  - Re-run clean install steps above.

---

## End-to-End Test Plan
1. **Populate RTDB** by running `bsm-sender.py` (verify it prints upload logs).
2. In Firebase Console, confirm `/LatestV2XMessage` updates.
3. **Listener**: run `vehicle-status-listener.js` and watch for `Forwarded vehicle status: ...` logs.
4. **UDP consumer**: run `nc -u -l 5000` (Linux/macOS) or a simple Python/Node UDP echo server to see the forwarded JSON.

---

## Notes
- Both scripts use user home directories to locate the service account and config; adjust if your layout differs.
- If you need Base64 for payloads in RTDB, encode in the Python sender:
  ```python
  import base64
  payload_b64 = base64.b64encode(data.encode('utf-8')).decode('ascii')
  ```

---

## Support
If you encounter a different stack trace or behavior, capture:
- OS, Python/Node versions
- Exact command run and working directory
- Full error text

…and share it along with your current `package.json` snippet. We'll iterate quickly.

