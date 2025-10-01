# 🚗 C-VISION V2X Website – Firebase Realtime Database Setup

This project is a **Next.js** application that visualizes Vehicle-to-Everything (V2X) data using a **Firebase Realtime Database**.  
It includes a **user-approval system** managed by administrators.

---

## 🧰 Getting Started

These instructions will help you set up the project locally for development and testing.

### Prerequisites

- **Node.js**: Version **18 or newer**.  
  Check your version:
```bash
node -v
```

### Installation

1.  **Clone the repository**:
```bash
git clone https://github.com/debipe20/c-vision
cd c-vision
git checkout <branch_name>
```

2.  **Install dependencies**:
```bash
npm install
```

3.  **Create `.env.local`**:
    Create a file named `.env.local` in the project's root directory. Copy the sample variables below and populate them with your own **Mapbox token** and **Firebase configuration**.

    ```env
    NEXT_PUBLIC_MAPBOX_TOKEN=pk.xxxxxx
    NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
    NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
    NEXT_PUBLIC_FIREBASE_DATABASE_URL=https://your-project-id-default-rtdb.firebaseio.com
    NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
    NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
    NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=1234567890
    NEXT_PUBLIC_FIREBASE_APP_ID=1:1234567890:web:abcdef123456
    ```

4.  **Run the development server**:
    ```bash
    npm run dev
    ```

---

## 🔧 Firebase Setup 

1. **Enable Authentication**

In Firebase Console, go to Authentication → Sign-in method.

Enable Email/Password.

2. **Create a Realtime Database**

Go to Firebase Console → Realtime Database → Create Database.

Select your region and start in Locked Mode.


## 🔐 Security Rules

Paste the following rules in **Firebase Console → Realtime Database → Rules**:

```json
{
  "rules": {
    ".read": false,
    ".write": false,

    "admins": {
      "$uid": {
        ".read": "root.child('admins').child(auth.uid).val() === true",
        ".write": false
      }
    },

    "pending_users": {
      "$uid": {
        ".read": "root.child('admins').child(auth.uid).val() === true",
        ".write": "(auth != null && auth.uid === $uid && !data.exists()) || root.child('admins').child(auth.uid).val() === true"
      }
    },

    "allowed_users": {
      "$uid": {
        ".read": "(auth != null && auth.uid === $uid) || root.child('admins').child(auth.uid).val() === true",
        ".write": "root.child('admins').child(auth.uid).val() === true"
      }
    },

    "bsm":  { ".read": "auth != null && (root.child('allowed_users').child(auth.uid).val() === true || root.child('admins').child(auth.uid).val() === true)", ".write": false },
    "spat": { ".read": "auth != null && (root.child('allowed_users').child(auth.uid).val() === true || root.child('admins').child(auth.uid).val() === true)", ".write": false },

    "BSMData":          { ".read": "auth != null && (root.child('allowed_users').child(auth.uid).val() === true || root.child('admins').child(auth.uid).val() === true)", ".write": false },
    "SPaTData":         { ".read": "auth != null && (root.child('allowed_users').child(auth.uid).val() === true || root.child('admins').child(auth.uid).val() === true)", ".write": false },
    "MAPData":          { ".read": "auth != null && (root.child('allowed_users').child(auth.uid).val() === true || root.child('admins').child(auth.uid).val() === true)", ".write": false },
    "LatestV2XMessage": { ".read": "auth != null && (root.child('allowed_users').child(auth.uid).val() === true || root.child('admins').child(auth.uid).val() === true)", ".write": false }
  }
}
```

## 📂 Database Structure

Realtime Database contains the following top-level nodes:

```
/
├── admins
│   └── <admin_uid>: true
│
├── allowed_users
│   └── <approved_user_uid>: true
│
├── pending_users
│   └── <user_uid>: <optional_info>
│
├── bsm
├── spat
├── BSMData
├── SPaTData
├── MAPData
└── LatestV2XMessage
```

### Node Purpose
| Node | Description |
|------|-------------|
| `/admins` | List of admin UIDs who can approve new users and manage permissions. |
| `/allowed_users` | List of approved user UIDs who can access live V2X data. |
| `/pending_users` | Users awaiting admin approval. |
| `/bsm`, `/spat` | Core V2X message feeds (read-only for approved users). |
| `/BSMData`, `/SPaTData`, `/MAPData`, `/LatestV2XMessage` | Additional V2X message storage for visualization. |


## 👤 Adding an Admin

1. Go to **Firebase Console → Realtime Database → Data tab**.
2. Expand `/admins`.
3. Click **+ Add child**.
4. Enter:
   - **Key:** `<admin_uid>` (from Firebase Authentication → Users → UID column)
   - **Value:** `true`
5. Click **Add**.

Example:
```json
"admins": {
  "6uD5hHPrZ5dvYxWDEBnYFROFR435": true
}
```

---

## ✅ Approving a User

1. Go to **Firebase Console → Realtime Database → Data tab**.
2. Expand `/allowed_users`.
3. Click **+ Add child**.
4. Enter:
   - **Key:** `<approved_user_uid>` (from Authentication → Users)
   - **Value:** `true`
5. Click **Add**.

Example:
```json
"allowed_users": {
  "i3Vs99WmPgSQmIJyByTJDHCoQfT2": true
}
```

Once approved, the user will be able to access `/bsm`, `/spat`, and other data nodes after signing in.

---

## 🔄 Approval Workflow

1. **New User Signs Up** → Their UID is stored in `/pending_users` (if frontend supports auto-pending).
2. **Admin Reviews** `/pending_users` in Firebase.
3. **Admin Adds UID to `/allowed_users`** with value `true`.
4. **User Refreshes** or signs out and signs back in → Access is granted.

---

## 🌐 Frontend Logic for Approval

The frontend checks:
```js
firebase.database()
  .ref(`/allowed_users/${currentUser.uid}`)
  .once('value', snapshot => {
    if (snapshot.val() === true) {
      // ✅ User approved
    } else {
      // ❌ Access denied
    }
  });
```

---
## 🚀 Deployment to Firebase Hosting
**1. Install Firebase CLI**
```bash
npm install -g firebase-tools
```

**2. Initialize Hosting**
```bash
firebase login
firebase init hosting
```
Use "out" as the public directory.
Choose Yes for single-page app.
Skip GitHub deploy if not needed.

**3. Update config files**
- firebase.json
```js
{
  "hosting": {
    "public": "out",
    "cleanUrls": true,
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ]
  }
}
```

- For multi-site hosting, it should look following:
```js
{
  "hosting": [
    {
      "site": "c-vision-7e1ec",
      "public": "out",
      "cleanUrls": true,
      "ignore": ["firebase.json", "**/.*", "**/node_modules/**"]
    }
  ]
}
```

- next.config.ts

```js
const nextConfig = {
  output: 'export'
};
export default nextConfig;
```
**4. Build and Deploy**
```bash
npm run build
firebase deploy --only hosting
```

## 🛡 Notes
- Only admins can **approve users** or view the list of approved users.
- Regular users can **only see their own approval status**.
- All V2X data nodes are **read-only** for approved users and **hidden** from non-approved users.
- Ensure all UIDs are exact matches from Firebase Authentication.

---
