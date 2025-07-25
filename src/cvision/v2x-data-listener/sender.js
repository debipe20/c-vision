const admin = require('firebase-admin');
const serviceAccount = require('./cvision-firebase-key.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://c-vision-7e1ec-default-rtdb.firebaseio.com/'
});

const db = admin.database();
const ref = db.ref('/latestSensorData'); // fixed location

const data = {
  timestamp: new Date().toISOString(),
  speed: Math.floor(Math.random() * 100),
  heading: Math.floor(Math.random() * 360)
};

// Overwrite previous data every time
ref.set(data)
  .then(() => {
    console.log('✅ Latest data sent:', data);
    process.exit(0);
  })
  .catch((error) => {
    console.error('❌ Error:', error);
    process.exit(1);
  });
