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

// Your SPaT seed format -> /spat/SPaTInfo = Array<SpatItemRaw>
type PhaseStateRaw = {
  phase: number;
  state: string; // e.g., stopAndRemain | permissiveMovementAllowed | protectedMovementAllowed
  maneuver?: string; // e.g., left-through, through-right, etc. (not used for markers now)
  direction?: string; // e.g., NorthBound, SouthBound...
};
type SpatItemRaw = {
  IntersectionName?: string;
  IntersectionID?: number | string;
  phaseStates?: PhaseStateRaw[];
  lat?: number;
  lon?: number;
  timestamp?: number;
};

// Normalized for UI
type PhaseState = { phase: number; state: string; maneuver?: string; direction?: string };
type Spat = {
  intersection_id: string;
  intersection_name?: string;
  phaseStates: PhaseState[];
  timestamp?: number;
  lat?: number;
  lon?: number;
};

export default function Page() {
  const db = useFirebaseDB();
  const auth = useFirebaseAuth();

  // ---------- Auth state ----------
  const [authed, setAuthed] = useState<boolean | null>(null);
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [authErr, setAuthErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // Optional approval gate (set to true if you aren’t enforcing /allowed_users)
  const [approved, setApproved] = useState<boolean | null>(true);

  // ---------- Map/markers state ----------
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const [center] = useState<[number, number]>([-87.992046, 41.711326]); // default center (ANL site)
  const [mapStyle, setMapStyle] = useState<"streets" | "sat">("streets");

  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [spats, setSpats] = useState<Spat[]>([]);

  // Markers
  const vehicleMarkersRef = useRef<Record<string, mapboxgl.Marker>>({});
  const spatCenterMarkersRef = useRef<Record<string, mapboxgl.Marker>>({});

  // Selection
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // ---------- Auth watcher ----------
  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => {
      setAuthed(!!u);
      if (u) {
        // If you enforce approval, uncomment the lines below
        // const r = dbRef(db, `allowed_users/${u.uid}`);
        // const off = onValue(
        //   r,
        //   (snap) => setApproved(snap.exists() ? Boolean(snap.val()) : false),
        //   () => setApproved(false)
        // );
        // return () => off();
      } else {
        setApproved(null);
      }
    });
    return () => unsub();
  }, [auth, db]);

  // ---------- Map init / style toggle ----------
  useEffect(() => {
    if (!mapContainerRef.current) return;

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style:
        mapStyle === "streets"
          ? "mapbox://styles/mapbox/streets-v12"
          : "mapbox://styles/mapbox/satellite-streets-v12",
      center,
      zoom: 15,
    });
    map.addControl(new mapboxgl.NavigationControl(), "top-right");

    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [center, mapStyle]); // recreate map when style toggles

  // ---------- BSM subscription ----------
  useEffect(() => {
    if (authed !== true || approved === false) return;
    const ref = dbRef(db, "bsm");
    const unsub = onValue(ref, (snap) => {
      const val = snap.val() || {};
      const list: Vehicle[] = Object.keys(val).map((id) => ({ id, ...val[id] }));
      setVehicles(list);

      // Auto-center once if not selected and we have a vehicle
      if (list.length && mapRef.current) {
        const v = list[0];
        if (typeof v.lon === "number" && typeof v.lat === "number" && mapRef.current.getZoom() < 13) {
          mapRef.current.flyTo({ center: [v.lon, v.lat], zoom: 14 });
        }
      }
    });
    return () => unsub();
  }, [db, authed, approved]);

  // ---------- SPaT subscription ----------
  useEffect(() => {
    if (authed !== true || approved === false) return;
    const ref = dbRef(db, "spat");
    const unsub = onValue(ref, (snap) => {
      const root = snap.val() || {};
      const arr: SpatItemRaw[] = Array.isArray(root?.SPaTInfo)
        ? (root.SPaTInfo as SpatItemRaw[])
        : [];

      const list: Spat[] = arr.map((r, idx) => ({
        intersection_id:
          r.IntersectionID != null ? String(r.IntersectionID) : `int-${idx + 1}`,
        intersection_name: r.IntersectionName,
        phaseStates: (r.phaseStates || []).map((p) => ({
          phase: Number(p.phase),
          state: String(p.state),
          maneuver: p.maneuver,
          direction: p.direction,
        })),
        lat: r.lat,
        lon: r.lon,
        timestamp: r.timestamp,
      }));

      setSpats(list);

      // Default selection + flyTo
      if (!selectedId && list.length) {
        setSelectedId(list[0].intersection_id);
      }
      const sel =
        list.find((s) => s.intersection_id === (selectedId ?? list[0]?.intersection_id)) ||
        list[0];

      if (sel && mapRef.current && typeof sel.lon === "number" && typeof sel.lat === "number") {
        mapRef.current.flyTo({ center: [sel.lon, sel.lat], zoom: 17 });
      }
    });
    return () => unsub();
  }, [db, authed, approved, selectedId]);

  // ---------- Vehicle markers (car icons) ----------
  useEffect(() => {
    const map = mapRef.current;
    if (!map || authed !== true || approved === false) return;

    const cache = vehicleMarkersRef.current;

    vehicles.forEach((v) => {
      if (typeof v.lon !== "number" || typeof v.lat !== "number") return;

      let marker = cache[v.id];
      if (!marker) {
        const el = document.createElement("div");
        el.style.width = "32px";
        el.style.height = "32px";
        el.style.backgroundImage = "url('/car-icon.webp')";
        el.style.backgroundSize = "contain";
        el.style.backgroundRepeat = "no-repeat";
        el.style.backgroundPosition = "center";
        el.style.transform = "translate(-50%, -50%)";
        marker = new mapboxgl.Marker({ element: el, anchor: "center" }).addTo(map);
        cache[v.id] = marker;
      }
      marker.setLngLat([v.lon, v.lat]);

      // rotate if heading available
      const el = marker.getElement();
      el.style.transform =
        "translate(-50%, -50%)" +
        (typeof v.heading_deg === "number" ? ` rotate(${v.heading_deg}deg)` : "");
    });

    // Remove stale car markers
    Object.keys(cache).forEach((id) => {
      if (!vehicles.find((v) => v.id === id)) {
        cache[id].remove();
        delete cache[id];
      }
    });
  }, [vehicles, authed, approved]);

  // ---------- Intersection center markers (one traffic-light icon per intersection) ----------
  useEffect(() => {
    const map = mapRef.current;
    if (!map || authed !== true || approved === false) return;

    const cache = spatCenterMarkersRef.current;

    spats.forEach((s) => {
      if (typeof s.lon !== "number" || typeof s.lat !== "number") return;

      let marker = cache[s.intersection_id];
      if (!marker) {
        const el = document.createElement("div");
        el.style.width = "28px";
        el.style.height = "28px";
        el.style.backgroundImage = "url('/traffic-light.png')";
        el.style.backgroundSize = "contain";
        el.style.backgroundRepeat = "no-repeat";
        el.style.backgroundPosition = "center";
        el.style.transform = "translate(-50%, -50%)";
        el.title = s.intersection_name || s.intersection_id;

        marker = new mapboxgl.Marker({ element: el, anchor: "center" }).addTo(map);
        cache[s.intersection_id] = marker;
      }
      marker.setLngLat([s.lon!, s.lat!]);
    });

    // Remove stale intersection markers
    Object.keys(cache).forEach((id) => {
      if (!spats.find((s) => s.intersection_id === id)) {
        cache[id].remove();
        delete cache[id];
      }
    });
  }, [spats, authed, approved]);

  // ----- LOGIN UI -----
  if (authed === false) {
    const onLogin = async () => {
      try {
        setAuthErr(null);
        setBusy(true);
        await signInWithEmailAndPassword(auth, email.trim(), pw);
      } catch (e) {
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
            onChange={(e) => setEmail(e.target.value)}
          />
        <input
            className="border rounded p-2 w-full"
            type="password"
            placeholder="Password"
            value={pw}
            onChange={(e) => setPw(e.target.value)}
          />
          {authErr && <div className="text-red-600 text-sm">{authErr}</div>}
          <button
            className="rounded-xl px-4 py-2 shadow bg-black text-white w-full disabled:opacity-60"
            disabled={busy}
            onClick={onLogin}
          >
            {busy ? "Signing in..." : "Sign in"}
          </button>
        </div>
      </div>
    );
  }

  // While checking auth, render blank page (prevents flash)
  if (authed === null) return <div className="min-h-screen w-full bg-white" />;

  // Optional approval gate
  if (approved === false) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="rounded-2xl shadow p-6 w-[28rem] bg-white">
          <h2 className="text-lg font-bold mb-2">Access pending</h2>
          <p className="text-sm text-gray-700">
            Your account is not approved yet. Please contact an administrator.
          </p>
          <div className="mt-4">
            <button
              className="text-xs px-3 py-1 rounded bg-black text-white"
              onClick={() => signOut(auth)}
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ----- UI: authed → show map + HUD -----
  const selected = spats.find((s) => s.intersection_id === selectedId) || spats[0];

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

          {/* Map style toggle */}
          <div className="flex gap-2">
            <button
              className={`text-xs px-2 py-1 rounded border ${mapStyle === "streets" ? "bg-black text-white" : "bg-white"}`}
              onClick={() => setMapStyle("streets")}
            >
              Street
            </button>
            <button
              className={`text-xs px-2 py-1 rounded border ${mapStyle === "sat" ? "bg-black text-white" : "bg-white"}`}
              onClick={() => setMapStyle("sat")}
            >
              Satellite
            </button>
          </div>

          {/* Vehicles */}
          <section>
            <h3 className="text-sm font-semibold mb-1">Vehicles ({vehicles.length})</h3>
            <div className="max-h-32 overflow-auto text-sm">
              {vehicles.length === 0 && <div className="text-gray-500">No vehicles yet…</div>}
              {vehicles.map((v) => (
                <div key={v.id} className="flex items-center justify-between py-1 border-b border-gray-100">
                  <span className="font-mono truncate">{v.id}</span>
                  <span className="text-gray-600">
                    {typeof v.speed_mps === "number" ? `${(v.speed_mps * 2.23694).toFixed(0)} mph` : "—"}
                  </span>
                </div>
              ))}
            </div>
          </section>

          {/* SPaT selector */}
          <section>
            <h3 className="text-sm font-semibold mb-1">SPaT Intersections ({spats.length})</h3>

            <select
              className="w-full border rounded p-1 text-sm mb-2"
              value={selectedId ?? (spats[0]?.intersection_id ?? "")}
              onChange={(e) => {
                const id = e.target.value || null;
                setSelectedId(id);
                const sel = spats.find((s) => s.intersection_id === id);
                if (sel && mapRef.current && typeof sel.lon === "number" && typeof sel.lat === "number") {
                  mapRef.current.flyTo({ center: [sel.lon, sel.lat], zoom: 18 });
                }
              }}
            >
              {spats.map((s) => (
                <option key={s.intersection_id} value={s.intersection_id}>
                  {s.intersection_name || s.intersection_id}
                </option>
              ))}
            </select>

            <div className="max-h-40 overflow-auto text-sm">
              {spats.length === 0 && <div className="text-gray-500">No intersections yet…</div>}
              {spats.map((s) => (
                <div
                  key={s.intersection_id}
                  className={`flex items-center justify-between py-1 border-b border-gray-100 cursor-pointer ${
                    selectedId === s.intersection_id ? "bg-gray-100" : ""
                  }`}
                  onClick={() => {
                    setSelectedId(s.intersection_id);
                    if (mapRef.current && typeof s.lon === "number" && typeof s.lat === "number") {
                      mapRef.current.flyTo({ center: [s.lon, s.lat], zoom: 18 });
                    }
                  }}
                >
                  <span className="font-mono truncate">{s.intersection_name || s.intersection_id}</span>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* (Optional) Bottom dock still shows per-phase cards; leave it out if you only want icons */}
        {selected?.phaseStates?.length ? (
          <div className="absolute left-0 right-0 bottom-0 px-4 pb-3 pointer-events-none">
            <div className="mx-auto max-w-6xl grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {selected.phaseStates.map((ps) => (
                <div key={`card-${ps.phase}`} className="rounded-xl overflow-hidden shadow bg-neutral-800 text-white pointer-events-auto">
                  <div className="px-3 py-2 flex items-center justify-between border-b border-neutral-700">
                    <div className="text-sm font-semibold">
                      {selected.intersection_name || selected.intersection_id} — P{ps.phase}
                    </div>
                  </div>
                  <div className="px-3 py-3 flex items-center justify-between">
                    {/* You can render maneuver text here if you want */}
                    <div className="text-xs opacity-80">
                      {ps.maneuver ? ps.maneuver.replaceAll("-", " / ") : "—"}
                    </div>
                    <div className="text-xs opacity-80">
                      {ps.direction ? ps.direction : ""}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
