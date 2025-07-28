const admin = require('firebase-admin');
const fs = require('fs');
const dgram = require('dgram');

const os = require('os');
const path = require('path');

let configFilePath;
const currentOS = os.platform();

if (currentOS === 'linux') 
{
  configFilePath = path.join(os.homedir(), 'Desktop', 'debashis-workspace', 'config', 'anl-master-config.json');
  const service_account_path = path.join(os.homedir(), 'Documents', 'cvision-firebase-key.json');
} 

else if (currentOS === 'win32') 
{
  configFilePath = path.join('C:', 'Users', 'Documents', 'debashis-workspace', 'config', 'anl-master-config.json');
  const service_account_path = path.join('C:', 'Users', 'Documents', 'cvision-firebase-key.json');
} 

else 
{
  throw new Error(`Unsupported operating system: ${currentOS}`);
}

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
  console.error('❌ Failed to load config file:', err);
  process.exit(1);
}

const host_ip = config?.IPAddress?.HostIp;
const receiver_port = config?.PortNumber?.V2XDataReceiver;

// 🔁 Listen to only the unified latest message path
const ref = db.ref('/LatestV2XMessage');

ref.on('value', (snapshot) => {
  const data = snapshot.val();
  if (!data) return;

  console.log('📥 Latest V2X message received:', data);

  // Save to file
  fs.writeFileSync('latest.json', JSON.stringify(data, null, 2));

  // Send via UDP
  const udpPayload = Buffer.from(JSON.stringify(data));
  udpClient.send(udpPayload, 0, udpPayload.length, receiver_port, host_ip, (err) => {
    if (err) console.error('❌ UDP send error:', err);
  });
});