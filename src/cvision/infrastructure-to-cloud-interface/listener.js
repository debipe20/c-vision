/**
**********************************************************************************
listener.js
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
  node listener.js
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
  configFilePath = path.join(os.homedir(), 'Desktop', 'c-vision', 'config', 'anl-master-config.json');
  service_account_path = path.join(os.homedir(), 'Documents', 'cvision-firebase-key.json');
} 

else if (currentOS === 'win32') {
  configFilePath = path.join('C:', 'Users', 'ddas', 'Documents', 'c-vision', 'config', 'anl-master-config.json');
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

// Listen to unified /LatestV2XMessage
const ref = db.ref('/LatestV2XMessage');

ref.on('value', (snapshot) => {
  const data = snapshot.val();
  if (!data) return;

  if (data && data.posix_timestamp) {
    // const now = Date.now() / 1000; // current time in seconds
    // const latency = now - data.posix_timestamp; // in seconds
    // console.log(`Latency: ${latency.toFixed(3)} seconds`);

    const latencyMs = Date.now() - (data.posix_timestamp * 1000);
    console.log(`Latency: ${latencyMs.toFixed(0)} ms`); 
  }

  // console.log('Latest V2X message received:', data);
  
  const udpPayload = Buffer.from(data.payload); // Send only the payload field
  udpClient.send(udpPayload, 0, udpPayload.length, receiver_port, host_ip, (err) => {
    if (err) console.error('UDP send error:', err);
  });
});
