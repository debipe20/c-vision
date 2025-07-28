const admin = require('firebase-admin');
const fs = require('fs');
const dgram = require('dgram');

const path = require('path');
const os = require('os');
const sevrice_account_path = path.join(os.homedir(), 'Documents', 'cvision-firebase-key.json');
const serviceAccount = require(sevrice_account_path);

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://c-vision-7e1ec-default-rtdb.firebaseio.com/'
});

const db = admin.database();
const udpClient = dgram.createSocket('udp4');

const UDP_PORT = 5005;
const UDP_HOST = '127.0.0.1';

function forward(path, type) {
  const ref = db.ref(path);
  ref.on('value', (snapshot) => {
    const data = snapshot.val();
    if (!data) return;

    const message = {
      type: type,
      timestamp: data.timestamp,
      payload: data.payload
    };

    console.log(`📥 Firebase update received for ${type}:`, message);
    fs.writeFileSync(`latest_${type}.json`, JSON.stringify(message, null, 2));

    const udpPayload = Buffer.from(JSON.stringify(message));
    udpClient.send(udpPayload, 0, udpPayload.length, UDP_PORT, UDP_HOST, (err) => {
      if (err) console.error(`❌ UDP send error for ${type}:`, err);
    });
  });
}

// Set up listeners for each message type
forward('/SPaTData', 'SPaT');
forward('/MAPData', 'MAP');
forward('/BSMData', 'BSM');