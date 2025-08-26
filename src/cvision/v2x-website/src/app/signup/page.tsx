"use client";

import { useEffect, useState } from "react";
import { initializeApp, getApps } from "firebase/app";
import {
  getAuth,
  onAuthStateChanged,
  createUserWithEmailAndPassword,
  sendEmailVerification,
} from "firebase/auth";
import { getDatabase, ref, set } from "firebase/database";
import Link from "next/link";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY!,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN!,
  databaseURL: process.env.NEXT_PUBLIC_FIREBASE_DATABASE_URL!,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID!,
};
if (!getApps().length) initializeApp(firebaseConfig);
const auth = getAuth();
const db = getDatabase();

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);

  // If already authed, go home
  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => {
      if (u) window.location.href = "/";
    });
    return () => unsub();
  }, []);

  const doSignup = async () => {
    setErr(null);
    setBusy(true);
    try {
      const cred = await createUserWithEmailAndPassword(auth, email.trim(), pw);
      // optional email verification (does not block approval)
      try {
        await sendEmailVerification(cred.user);
      } catch {}
      // create pending record for admin approval
      await set(ref(db, `pending_users/${cred.user.uid}`), {
        email: cred.user.email,
        createdAt: Date.now(),
      });
      setDone(true);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setErr(msg);
    } finally {
      setBusy(false);
    }
  };

  if (done) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="rounded-2xl shadow p-6 w-96 space-y-3 bg-white">
          <h1 className="font-bold text-lg">Account created</h1>
          <p className="text-sm text-gray-700">
            Thanks! Your account is created. An administrator must approve your access before you can view data.
          </p>
          <Link className="text-sm underline" href="/">
            Back to sign in
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="rounded-2xl shadow p-6 w-80 space-y-3 bg-white">
        <h1 className="font-bold text-lg">Create account</h1>
        <input
          className="border rounded p-2 w-full"
          placeholder="Email"
          value={email}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
        />
        <input
          className="border rounded p-2 w-full"
          type="password"
          placeholder="Password"
          value={pw}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPw(e.target.value)}
        />
        {err && <div className="text-red-600 text-sm">{err}</div>}
        <button
          className="rounded-xl px-4 py-2 shadow bg-black text-white w-full disabled:opacity-60"
          disabled={busy}
          onClick={doSignup}
        >
          {busy ? "Creating…" : "Sign up"}
        </button>

        <div className="text-xs text-gray-600 text-center">
          Already have an account?{" "}
          <Link className="underline" href="/">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
