"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

import { initializeApp, getApps } from "firebase/app";
import { getDatabase, onValue, ref as dbRef } from "firebase/database";
import {
  getAuth,
  onAuthStateChanged,
  signOut,
  signInWithEmailAndPassword,
} from "firebase/auth";

// ===== Mapbox token (from .env.local) =====
mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || "";

// ===== Firebase config (from .env.local) =====
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY!,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN!,
  databaseURL: process.env.NEXT_PUBLIC_FIREBASE_DATABASE_URL!,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID!,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET!,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID!,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID!,
};

// Lazy-init Firebase services
function useFirebaseDB() {
  return useMemo(() => {
    if (!getApps().length) initializeApp(firebaseConfig);
    return getDatabase();
  }, []);
}
function useFirebaseAuth() {
  return useMemo(() => {
    if (!getApps().length) initializeApp(firebaseConfig);
    return getAuth();
  }, []);
}

// ===== Types =====
type Vehicle = {
  id: string;
  lat: number;
  lon: number;
  speed_mps?: number;
  heading_deg?: number;
  ts?: number;
};
type PhaseState = { phase: number; state: string; minEndTime?: number };
type Spat = {
  intersection_id: string;
  phaseStates: PhaseState[];
  timestamp?: number;
  lat?: number;
  lon?: number;
};

// Map SPaT state → short label & color
function stateToShortColor(state: string): { text: string; color: string } {
  const s = state.toLowerCase();
  if (s.includes("stop")) return { text: "RED", color: "#e11d48" };
  if (s.includes("protected") || s.includes("permissive")) return { text: "GREEN", color: "#16a34a" };
  if (s.includes("caution") || s.includes("pre-movement")) return { text: "YEL", color: "#f59e0b" };
  return { text: state.slice(0, 3).toUpperCase(), color: "#6b7280" };
}

export default function Page() {
  const db = useFirebaseDB();
  const auth = useFirebaseAuth();

  // ---------- Auth & approval state ----------
  const [authed, setAuthed] = useState<boolean | null>(null); // null = checking
  const [approved, setApproved] = useState<boolean | null>(null); // null = checking

  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [authErr, setAuthErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // ---------- Map/markers state ----------
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const [center] = useState<[number, number]>([-97.7431, 30.2672]); // Austin, TX
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [spats, setSpats] = useState<Spat[]>([]);
  const vehicleMarkersRef = useRef<Record<string, mapboxgl.Marker>>({});
  const spatMarkersRef = useRef<Record<string, mapboxgl.Marker>>({});

  // Watch auth state
  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => {
      setAuthed(!!u);
      setApproved(null); // reset approval check whenever auth changes
    });
    return () => unsub();
  }, [auth]);

  // When authed, check approval flag at /allowed_users/<uid> (STRICT true)
  useEffect(() => {
    if (authed !== true) return;
    const u = auth.currentUser;
    if (!u) return;

    const r = dbRef(db, `allowed_users/${u.uid}`);
    const off = onValue(
      r,
      (snap) => setApproved(snap.val() === true),
      () => setApproved(false)
    );
    return () => off();
  }, [authed, auth, db]);

  // Init map after auth & approval pass
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;
    if (!(authed === true && approved === true)) return;

    mapRef.current = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: "mapbox://styles/mapbox/streets-v12",
      center,
      zoom: 12,
    });
    mapRef.current.addControl(new mapboxgl.NavigationControl(), "top-right");

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, [center, authed, approved]);

  // Subscribe to BSM (/bsm) — only if approved
  useEffect(() => {
    if (!(authed === true && approved === true)) return;
    const ref = dbRef(db, "bsm");
    const unsub = onValue(ref, (snap) => {
      const val = snap.val() || {};
      const list: Vehicle[] = Object.keys(val).map((id) => ({ id, ...val[id] }));
      setVehicles(list);

      if (list.length && mapRef.current) {
        const v = list[0];
        if (typeof v.lon === "number" && typeof v.lat === "number") {
          if (mapRef.current.getZoom() < 13) {
            mapRef.current.flyTo({ center: [v.lon, v.lat], zoom: 14 });
          }
        }
      }
    });
    return () => unsub();
  }, [db, authed, approved]);

  // Subscribe to SPaT (/spat) — only if approved
  useEffect(() => {
    if (!(authed === true && approved === true)) return;
    const ref = dbRef(db, "spat");
    const unsub = onValue(ref, (snap) => {
      const val = snap.val() || {};
      const list: Spat[] = Object.keys(val).map((intersection_id) => ({
        intersection_id,
        ...val[intersection_id],
      }));
      setSpats(list);
    });
    return () => unsub();
  }, [db, authed, approved]);

  // Vehicle markers (car icon, rotate by heading)
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !(authed === true && approved === true)) return;

    const cache = vehicleMarkersRef.current;

    vehicles.forEach((v) => {
      if (typeof v.lon !== "number" || typeof v.lat !== "number") return;

      const el = document.createElement("div");
      el.className = "vehicle-marker";
      el.style.width = "32px";
      el.style.height = "32px";
      el.style.backgroundImage = "url('/car-icon.webp')"; // ensure this file exists in /public
      el.style.backgroundSize = "contain";
      el.style.backgroundRepeat = "no-repeat";
      el.style.backgroundPosition = "center";
      el.style.transform = "translate(-50%, -50%)";
      if (typeof v.heading_deg === "number") el.style.transform += ` rotate(${v.heading_deg}deg)`;

      const marker = cache[v.id] || new mapboxgl.Marker({ element: el, anchor: "center" });
      marker.setLngLat([v.lon, v.lat]).addTo(map);
      cache[v.id] = marker;
    });

    // Remove stale markers
    Object.keys(cache).forEach((id) => {
      if (!vehicles.find((v) => v.id === id)) {
        cache[id].remove();
        delete cache[id];
      }
    });
  }, [vehicles, authed, approved]);

  // SPaT markers
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !(authed === true && approved === true)) return;

    const cache = spatMarkersRef.current;

    spats.forEach((s) => {
      if (typeof s.lon !== "number" || typeof s.lat !== "number") return;

      const { color, text } = stateToShortColor(s.phaseStates?.[0]?.state || "unknown");

      const el = document.createElement("div");
      el.className = "spat-marker";
      el.style.padding = "4px 6px";
      el.style.borderRadius = "6px";
      el.style.background = color;
      el.style.color = "white";
      el.style.fontSize = "12px";
      el.style.fontWeight = "700";
      el.style.boxShadow = "0 0 0 2px white";
      el.textContent = text;

      const m = cache[s.intersection_id] || new mapboxgl.Marker({ element: el, anchor: "bottom" });
      m.setLngLat([s.lon, s.lat]).addTo(map);
      cache[s.intersection_id] = m;
    });

    // Remove stale
    Object.keys(cache).forEach((id) => {
      if (!spats.find((s) => s.intersection_id === id)) {
        cache[id].remove();
        delete cache[id];
      }
    });
  }, [spats, authed, approved]);

  // ----- UI: not signed in → show login form -----
  if (authed === false) {
    const onLogin = async () => {
      try {
        setAuthErr(null);
        setBusy(true);
        await signInWithEmailAndPassword(auth, email.trim(), pw);
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        setAuthErr(msg || "Login failed");
      } finally {
        setBusy(false);
      }
    };

    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="rounded-2xl shadow p-6 w-80 space-y-3 bg-white">
          <h1 className="font-bold text-lg">Sign in</h1>
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
          {authErr && <div className="text-red-600 text-sm">{authErr}</div>}
          <button
            className="rounded-xl px-4 py-2 shadow bg-black text-white w-full disabled:opacity-60"
            disabled={busy}
            onClick={onLogin}
          >
            {busy ? "Signing in..." : "Sign in"}
          </button>
          <div className="text-xs text-gray-600 text-center">
            No account?{" "}
            <a className="underline" href="/signup">
              Create one
            </a>
          </div>
        </div>
      </div>
    );
  }

  // While checking auth or approval, render a lightweight placeholder
  if (authed === null || approved === null) {
    return <div className="min-h-screen w-full bg-white" />;
  }

  // If signed in but not approved yet
  if (authed === true && approved === false) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="rounded-2xl shadow p-6 w-96 space-y-3 bg-white">
          <h1 className="font-bold text-lg">Awaiting approval</h1>
          <p className="text-sm text-gray-700">
            Your account is created but not yet approved by an administrator.
          </p>
          <div className="flex justify-end">
            <button
              className="text-xs px-2 py-1 rounded bg-black text-white"
              onClick={() => signOut(auth)}
              title="Sign out"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ----- UI: authed + approved → show map + HUD -----
  return (
    <div className="min-h-screen w-full flex">
      <div className="w-full h-screen relative">
        <div ref={mapContainerRef} className="absolute inset-0 h-full w-full" />

        {/* HUD panel */}
        <div className="absolute top-3 left-3 bg-white/90 backdrop-blur rounded-2xl shadow-lg p-4 w-80 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold">V2X Live View</h2>
            <button
              className="text-xs px-2 py-1 rounded bg-black text-white"
              onClick={() => signOut(auth)}
              title="Sign out"
            >
              Sign out
            </button>
          </div>

          <section>
            <h3 className="text-sm font-semibold mb-1">Vehicles ({vehicles.length})</h3>
            <div className="max-h-40 overflow-auto text-sm">
              {vehicles.length === 0 && <div className="text-gray-500">No vehicles yet…</div>}
              {vehicles.map((v) => (
                <div key={v.id} className="flex items-center justify-between py-1 border-b border-gray-100">
                  <span className="font-mono">{v.id}</span>
                  <span className="text-gray-600">
                    {typeof v.speed_mps === "number" ? `${(v.speed_mps * 2.23694).toFixed(0)} mph` : "—"}
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h3 className="text-sm font-semibold mb-1">SPaT ({spats.length})</h3>
            <div className="max-h-40 overflow-auto text-sm">
              {spats.length === 0 && <div className="text-gray-500">No intersections yet…</div>}
              {spats.map((s) => {
                const { color, text } = stateToShortColor(s.phaseStates?.[0]?.state || "unknown");
                return (
                  <div key={s.intersection_id} className="flex items-center justify-between py-1 border-b border-gray-100">
                    <span className="font-mono">{s.intersection_id}</span>
                    <span className="px-2 py-0.5 rounded text-white font-semibold" style={{ background: color }}>
                      {text}
                    </span>
                  </div>
                );
              })}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
