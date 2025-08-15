This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

<!-- Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
 -->

# 🚗 C-VISION V2X Website – Firebase Realtime Database Setup

This document explains the **Firebase Realtime Database structure**, **security rules**, and **approval workflow** for the V2X visualization website.

---

## 📂 Database Structure

Our Realtime Database contains the following top-level nodes:

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

---

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

---

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
  "6uD5hKWrZ5bcYxWMJInYFROFR932": true
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

## 🛡 Notes
- Only admins can **approve users** or view the list of approved users.
- Regular users can **only see their own approval status**.
- All V2X data nodes are **read-only** for approved users and **hidden** from non-approved users.
- Ensure all UIDs are exact matches from Firebase Authentication.

---
