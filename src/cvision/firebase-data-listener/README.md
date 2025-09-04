# V2X Data Exchange System

This project enables real-time V2X (Vehicle-to-Everything) communication through Firebase and UDP sockets. It allows structured routing of SPaT, MAP, and BSM messages from a `sender.py` client to a `receiver.py` server, using `listener.js` as a forwarding middleware.

---

## 📂 Components

| Script         | Description |
|----------------|-------------|
| `sender.py`    | Receives V2X messages from a traffic controller or simulation system and uploads them to Firebase. |
| `listener.js`  | Listens to Firebase and forwards the latest message to `receiver.py` via UDP. |
| `receiver.py`  | Receives V2X messages over UDP and logs them. Can be extended to send ACKs. |

---

## ✅ Prerequisites

### 1. Firebase Setup

- A Firebase project with **Realtime Database** enabled
- A downloaded **Service Account Key** named `cvision-firebase-key.json`
- Add the key to your `Documents/` folder:
  - Linux: `~/Documents/cvision-firebase-key.json`
  - Windows: `C:\Users\<your-user>\Documents\cvision-firebase-key.json`

### 2. Configuration File

Create a JSON file at:

- Linux: `~/Desktop/debashis-workspace/config/anl-master-config.json`
- Windows: `C:\Users\<your-user>\Documents\debashis-workspace\config\anl-master-config.json`

Example:

```json
{
  "IPAddress": {
    "HostIp": "127.0.0.1"
  },
  "PortNumber": {
    "V2XDataSender": 5002,
    "V2XDataReceiver": 5005
  }
}
```

### 3. Install Dependencies

```bash
# Python
pip install firebase-admin

# Node.js
npm install firebase-admin
```

---

## 🚦 Run Order & 📡 Data Flow

Run the components in the following order:

```bash
# 1. Start the UDP receiver
python3 receiver.py

# 2. Start the Firebase listener
node listener.js

# 3. Start the V2X data sender
python3 sender.py
```

Then, messages flow as:

```
╭────────────╮         ╭─────────────╮         ╭──────────────╮
│ sender.py  │ ──────► │  Firebase   │ ──────► │ listener.js  │
╰────────────╯         ╰─────────────╯         ╰──────┬───────╯
                                                       │
                                                 ┌─────▼──────┐
                                                 │ receiver.py│
                                                 ╰────────────╯
```

- Messages are identified by prefixes:
  - `0012` → MAP
  - `0013` → SPaT
  - `0014` → BSM
- All messages are sent to `/LatestV2XMessage` in Firebase for forwarding

---

## 🧩 Notes

- Ensure your machine's firewall allows UDP traffic on configured ports
- If the sender uses a cellular (Uu) interface behind NAT, use Firebase for ACKs instead of direct UDP
- You can extend `receiver.py` to return ACKs or parse messages for visualization

---

## 📦 License

This project is for academic and research use. Customize and extend for your integration needs.