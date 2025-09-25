/**
**********************************************************************************
vehicle-status-listener.js
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
Description:
------------
This Node.js script connects to Firebase Realtime Database and listens for updates to
the `/LatestV2XMessage` node. When a new message is received, it forwards it via UDP
to the configured receiver endpoint.
 
Usage:
  node vehicle-status-listener.js
**********************************************************************************
 */

const admin = require('firebase-admin');
const fs = require('fs');
const dgram = require('dgram');
const os = require('os');
const path = require('path');

let configFilePath;
let service_account_path;  // Define it here so it's accessible later
const currentOS = os.platform();

if (currentOS === 'linux') {
  configFilePath = path.join(os.homedir(), 'Desktop', 'debashis-workspace', 'config', 'anl-master-config.json');
  service_account_path = path.join(os.homedir(), 'Documents', 'cvision-firebase-key.json');
} 

else if (currentOS === 'win32') {
  configFilePath = path.join('C:', 'Users', 'ddas', 'Documents', 'debashis-workspace', 'config', 'anl-master-config.json');
  service_account_path = path.join('C:', 'Users', 'ddas', 'Documents', 'cvision-firebase-key.json');
}

else {
  throw new Error(`Unsupported operating system: ${currentOS}`);
}

// Now service_account_path is accessible here
const serviceAccount = require(service_account_path);

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://c-vision-7e1ec-default-rtdb.firebaseio.com/'
});

const db = admin.database();
const udpClient = dgram.createSocket('udp4');

// Read and parse the config file
let config;
try {
  const configRaw = fs.readFileSync(configFilePath, 'utf-8');
  config = JSON.parse(configRaw);
} catch (err) {
  console.error('Failed to load config file:', err);
  process.exit(1);
}

const host_ip = config?.IPAddress?.HostIp;
const receiver_port = config?.PortNumber?.MessageDecoder;
const vehicle_id = config?.VehicleInformation?.EgoVehicleId;

// Listen only to the target vehicle node
const ref = db.ref(`/vehicle_status/${vehicle_id}`);

ref.on('value', (snap) => {
  const v = snap.val();
  if (!v) return; // nothing yet

  // Build a neat JSON payload (adjust fields as you like)
  const msg = {
    vehicle_id,
    timestamp: v.timestamp ?? null,
    position: { lat: v.lat, lon: v.lon, elev: v.elev },
    kinematics: { speed: v.speed, heading: v.heading },
    lane: { lane_id: v.lane_id, approach_id: v.approach_id },
    signal: { group: v.signal_group, status: v.signal_status ?? "" }
  };

  const buf = Buffer.from(JSON.stringify(msg));
  udpClient.send(buf, receiver_port, host_ip, (err) => {
    if (err) console.error('UDP send error:', err);
  });

  console.log('Forwarded vehicle status:', msg);
});
