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
const ref = db.ref('/latestSensorData');

// Create UDP socket
const udpClient = dgram.createSocket('udp4');
const UDP_PORT = 5005;
const UDP_HOST = '127.0.0.1';

ref.on('value', (snapshot) => {
  const data = snapshot.val();
  const message = Buffer.from(JSON.stringify(data));

  console.log('📥 Firebase update received:', data);
  fs.writeFileSync('latest.json', JSON.stringify(data, null, 2));

  // Send data to Python via UDP
  udpClient.send(message, 0, message.length, UDP_PORT, UDP_HOST, (err) => {
    if (err) console.error('❌ UDP send error:', err);
  });
});
