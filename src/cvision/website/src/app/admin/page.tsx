"use client";

import { useEffect, useState } from "react";
import { initializeApp, getApps } from "firebase/app";
import { getAuth, onAuthStateChanged, signOut } from "firebase/auth";
import { getDatabase, ref, onValue, set, remove } from "firebase/database";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY!,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN!,
  databaseURL: process.env.NEXT_PUBLIC_FIREBASE_DATABASE_URL!,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID!,
};
if (!getApps().length) initializeApp(firebaseConfig);
const auth = getAuth();
const db = getDatabase();

type Pending = { email?: string; createdAt?: number };

export default function AdminPage() {
  const [authed, setAuthed] = useState(false);
  const [pending, setPending] = useState<Record<string, Pending>>({});

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => setAuthed(!!u));
    return () => unsub();
  }, []);

  useEffect(() => {
    if (!authed) return;
    // Only admins can read this per DB rules; non-admins will fail silently
    const r = ref(db, "pending_users");
    const off = onValue(r, (snap) => setPending(snap.val() || {}), () => setPending({}));
    return () => off();
  }, [authed]);

  const approve = async (uid: string) => {
    await set(ref(db, `allowed_users/${uid}`), true);
    await remove(ref(db, `pending_users/${uid}`));
  };

  const reject = async (uid: string) => {
    await remove(ref(db, `pending_users/${uid}`));
  };

  if (!authed) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="p-6 bg-white rounded-2xl shadow">
          Sign in as an admin to continue.
        </div>
      </div>
    );
  }

  const entries = Object.entries(pending);

  return (
    <div className="min-h-screen p-6 bg-gray-50">
      <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-bold">Admin — Pending Users</h1>
          <button className="text-xs px-2 py-1 rounded bg-black text-white" onClick={() => signOut(auth)}>
            Sign out
          </button>
        </div>

        {entries.length === 0 ? (
          <div className="text-gray-600">No pending users.</div>
        ) : (
          <ul className="space-y-3">
            {entries.map(([uid, p]) => (
              <li key={uid} className="flex items-center justify-between border rounded p-3">
                <div>
                  <div className="font-mono">{p.email || "(no email)"}</div>
                  <div className="text-xs text-gray-500">uid: {uid}</div>
                  {p.createdAt && (
                    <div className="text-xs text-gray-400">
                      requested: {new Date(p.createdAt).toLocaleString()}
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <button className="px-3 py-1 rounded bg-green-600 text-white" onClick={() => approve(uid)}>
                    Approve
                  </button>
                  <button className="px-3 py-1 rounded bg-red-600 text-white" onClick={() => reject(uid)}>
                    Reject
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
