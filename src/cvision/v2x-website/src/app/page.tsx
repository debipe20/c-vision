"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

import { initializeApp, getApps } from "firebase/app";
import { getDatabase, onValue, ref as dbRef, set as dbSet } from "firebase/database";
import {
  getAuth,
  onAuthStateChanged,
  signOut,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
} from "firebase/auth";

/** <-- NEW: static intersection config lives in a separate file */
// import { INTERSECTIONS, type StaticIntersectionMap, type StaticPhase } from "@/config/intersections";
// If your TS config doesn’t support "@/..." aliases, use:
// import { INTERSECTIONS, type StaticIntersectionMap, type StaticPhase } from "../config/intersections";
import { INTERSECTIONS, type StaticPhase } from "@/config/intersections";


/* ==================== MAPBOX ==================== */
mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || "";

/* ==================== FIREBASE ==================== */
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY!,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN!,
  databaseURL: process.env.NEXT_PUBLIC_FIREBASE_DATABASE_URL!,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID!,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET!,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID!,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID!,
};

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

/* ==================== TYPES ==================== */
type Vehicle = {
  id: string;
  lat: number;
  lon: number;
  speed_mps?: number;
  heading_deg?: number;
  ts?: number;
};

type PhaseStateRaw = { phase: number; state: string; direction?: string; maneuver?: string };
type SpatItemRaw = {
  IntersectionName?: string;
  IntersectionID?: number | string;
  phaseStates?: PhaseStateRaw[];
  lat?: number;
  lon?: number;
  timestamp?: number;
};

type PhaseState = { phase: number; state: string; direction?: string; maneuver?: string };
type Spat = {
  intersection_id: string;
  intersection_name?: string;
  phaseStates: PhaseState[];
  timestamp?: number;
  lat?: number;
  lon?: number;
};

type Approach = "N" | "E" | "S" | "W";

/* ==================== HELPERS ==================== */
function directionToApproach(d?: string): Approach {
  const s = (d || "").trim().toLowerCase();
  if (s.includes("north")) return "N";
  if (s.includes("east")) return "E";
  if (s.includes("south")) return "S";
  if (s.includes("west")) return "W";
  return "N";
}

function lampHex(state: string): string {
  const s = state.toLowerCase();
  if (s.includes("stop")) return "#e11d48";
  if (s.includes("perm") || s.includes("protect")) return "#16a34a";
  if (s.includes("caution") || s.includes("pre") || s.includes("yellow")) return "#f59e0b";
  return "#6b7280";
}
function arrowsForManeuver(m?: string): string {
  const mvr = (m || "").toLowerCase();
  const left = "↰",
    thru = "↑",
    right = "↱";
  const parts: string[] = [];
  if (mvr.includes("left")) parts.push(left);
  if (mvr.includes("through")) parts.push(thru);
  if (mvr.includes("right")) parts.push(right);
  return parts.length ? parts.join(" ") : "↑";
}

/* ======= Color palette per-vehicle (deterministic) ======= */
function hashToHue(id: string) {
  let h = 0;
  for (let i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) >>> 0;
  return h % 360;
}
function colorFor(id: string) {
  const hue = hashToHue(id);
  return {
    core: `hsl(${hue} 80% 45%)`,
    ring: `hsl(${hue} 85% 65%)`,
  };
}

/** Merge live phase states into static config */
function mergePhases(
  config: StaticPhase[],
  live?: Array<{ phase: number; state?: string; direction?: string; maneuver?: string }>
): PhaseState[] {
  const byPhase = new Map<number, { state?: string; direction?: string; maneuver?: string }>();
  (live || []).forEach((p) => byPhase.set(Number(p.phase), p));
  return config.map((c) => {
    const l = byPhase.get(c.phase);
    return {
      phase: c.phase,
      state: l?.state ?? "stopAndRemain", // default red if nothing live yet
      direction: l?.direction ?? c.direction,
      maneuver: l?.maneuver ?? c.maneuver,
    };
  });
}

/* ==================== PAGE ==================== */
export default function Page() {
  const db = useFirebaseDB();
  const auth = useFirebaseAuth();

  // Auth
  const [authed, setAuthed] = useState<boolean | null>(null);
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [authErr, setAuthErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [mode, setMode] = useState<"signin" | "signup">("signin");

  // Optional approval gate
  const [approved, setApproved] = useState<boolean | null>(true);

  // Map
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const [mapStyle, setMapStyle] = useState<"streets" | "satellite">("streets");
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [spats, setSpats] = useState<Spat[]>([]);
  const vehicleMarkersRef = useRef<Record<string, mapboxgl.Marker>>({});
  const spatMarkersRef = useRef<Record<string, mapboxgl.Marker>>({});

  const [selectedId, setSelectedId] = useState<string | null>(null); // SPaT selection
  const [selectedVehicleId, setSelectedVehicleId] = useState<string | null>(null); // Vehicle selection

  /* ==== Auth watcher ==== */
  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => {
      setAuthed(!!u);
      if (u) {
        const r = dbRef(db, `allowed_users/${u.uid}`);
        const off = onValue(
          r,
          (snap) => setApproved(snap.exists() ? Boolean(snap.val()) : false),
          () => setApproved(false)
        );
        return () => off();
      } else {
        setApproved(null);
      }
    });
    return () => unsub();
  }, [auth, db]);

  /* ==== Force default map style after sign-in/approval */
  useEffect(() => {
    if (authed === true && approved !== false) {
      setMapStyle("streets");   // ensure default
    }
  }, [authed, approved]);

  /* ==== Map init (recreates when style changes) ==== */
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current || authed !== true || approved === false) return;

    const defaultCenter: [number, number] = [-87.992046, 41.711326];

    mapRef.current = new mapboxgl.Map({
      container: mapContainerRef.current,
      style:
        mapStyle === "satellite"
          ? "mapbox://styles/mapbox/satellite-streets-v12"
          : "mapbox://styles/mapbox/streets-v12",
      center: defaultCenter,
      zoom: 14,
    });

    mapRef.current.addControl(new mapboxgl.NavigationControl(), "top-right");

    mapRef.current.on("error", (e: unknown) => console.error("Mapbox error:", e));

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, [authed, approved, mapStyle]);

  /* ==== Vehicles (/vehicle_status) ==== */
  useEffect(() => {
    if (authed !== true || approved === false) return;
    const ref = dbRef(db, "vehicle_status");
    const unsub = onValue(ref, (snap) => {
      const val = snap.val() || {};
      const list: Vehicle[] = Object.keys(val).map((key) => ({ ...val[key], id: String(key) }));
      setVehicles(list);

      const map = mapRef.current;
      if (list.length && map && !selectedVehicleId) {
        const v = list[0];
        if (typeof v.lon === "number" && typeof v.lat === "number") {
          if (map.getZoom() < 13) map.flyTo({ center: [v.lon, v.lat], zoom: 14 });
        }
      }
    });
    return () => unsub();
  }, [db, authed, approved, selectedVehicleId]);

  /* ==== SPaT (merge static config with live states from DB) ==== */
  useEffect(() => {
    if (authed !== true || approved === false) return;

    const ref = dbRef(db, "intersection_status");
    const unsub = onValue(ref, (snap) => {
      const root = snap.val() || {};

      // Build a map: id -> { phaseStates, timestamp }
      const liveById: Record<string, { phaseStates?: PhaseStateRaw[]; timestamp?: number }> = {};

      if (Array.isArray(root?.SPaTInfo)) {
        // --- legacy array shape ---
        (root.SPaTInfo as SpatItemRaw[]).forEach((r) => {
          const id = r.IntersectionID != null ? String(r.IntersectionID) : "";
          if (!id) return;
          liveById[id] = { phaseStates: r.phaseStates || [], timestamp: r.timestamp };
        });
      } else if (root && typeof root === "object") {
        // --- new keyed shape: /spat/<id>/{phaseStates, timestamp} ---
        Object.keys(root).forEach((id) => {
          const node = root[id];
          if (node && typeof node === "object" && Array.isArray(node.phaseStates)) {
            liveById[String(id)] = {
              phaseStates: node.phaseStates as PhaseStateRaw[],
              timestamp: typeof node.timestamp === "number" ? node.timestamp : undefined,
            };
          }
        });
      }

      // Drive UI from static INTERSECTIONS + merge live by phase
      const list: Spat[] = Object.keys(INTERSECTIONS).map((id) => {
        const base = INTERSECTIONS[id];
        const live = liveById[id];
        return {
          intersection_id: id,
          intersection_name: base.name,
          phaseStates: mergePhases(base.phases, live?.phaseStates),
          lat: base.lat,
          lon: base.lon,
          timestamp: live?.timestamp,
        };
      });

      setSpats(list);

      // Default selection + camera fly
      if (!selectedId && list.length) setSelectedId(list[0].intersection_id);
      const active =
        list.find((s) => s.intersection_id === (selectedId ?? list[0]?.intersection_id)) || list[0];
      const map = mapRef.current;
      if (active && map && typeof active.lon === "number" && typeof active.lat === "number") {
        map.flyTo({ center: [active.lon, active.lat], zoom: 17 });
      }
    });

    return () => unsub();
  }, [db, authed, approved, selectedId]);

  /* ==== Vehicle markers (colored, pulsing) ==== */
  useEffect(() => {
    const map = mapRef.current;
    if (!map || authed !== true || approved === false) return;

    const cache = vehicleMarkersRef.current;

    vehicles.forEach((v) => {
      if (typeof v.lon !== "number" || typeof v.lat !== "number") return;

      let marker = cache[v.id];
      const { core, ring } = colorFor(v.id);

      if (!marker) {
        // marker container
        const div = document.createElement("div");
        div.style.position = "relative";
        div.style.width = "16px";
        div.style.height = "16px";
        div.style.borderRadius = "50%";
        div.style.background = core;
        div.style.border = "2px solid white";
        div.style.boxShadow = "0 0 6px rgba(0,0,0,0.5)";
        div.style.pointerEvents = "none";
        // arrow (heading triangle)
        const arrow = document.createElement("div");
        arrow.style.position = "absolute";
        arrow.style.top = "-6px";
        arrow.style.left = "50%";
        arrow.style.transform = "translateX(-50%)";
        arrow.style.width = "0";
        arrow.style.height = "0";
        arrow.style.borderLeft = "4px solid transparent";
        arrow.style.borderRight = "4px solid transparent";
        arrow.style.borderBottom = `6px solid ${core}`;
        div.appendChild(arrow);
        // pulse ring
        const pulse = document.createElement("div");
        pulse.style.position = "absolute";
        pulse.style.top = "50%";
        pulse.style.left = "50%";
        pulse.style.width = "16px";
        pulse.style.height = "16px";
        pulse.style.borderRadius = "50%";
        pulse.style.transform = "translate(-50%, -50%)";
        pulse.style.background = ring;
        pulse.style.opacity = "0.6";
        pulse.style.animation = "carPulse 2s infinite";
        div.appendChild(pulse);

        if (!document.getElementById("carPulseKeyframes")) {
          const style = document.createElement("style");
          style.id = "carPulseKeyframes";
          style.textContent =
            "@keyframes carPulse {0%{transform: translate(-50%,-50%) scale(1); opacity:.7}50%{transform: translate(-50%,-50%) scale(1.8); opacity:.25}100%{transform: translate(-50%,-50%) scale(1); opacity:.7}}";
          document.head.appendChild(style);
        }

        marker = new mapboxgl.Marker({ element: div, anchor: "center" });
        cache[v.id] = marker;
      } else {
        // update colors on existing element for consistency
        const el = marker.getElement() as HTMLDivElement;
        el.style.background = core;
        const arrow = el.children[0] as HTMLDivElement | undefined;
        if (arrow) arrow.style.borderBottom = `6px solid ${core}`;
        const pulse = el.children[1] as HTMLDivElement | undefined;
        if (pulse) pulse.style.background = ring;
      }

      // emphasize selected vehicle
      const el = marker.getElement() as HTMLDivElement;
      el.style.outline = selectedVehicleId === v.id ? `2px solid ${ring}` : "none";
      el.style.outlineOffset = selectedVehicleId === v.id ? "2px" : "0";

      // rotate the whole container if heading given
      el.style.transform = typeof v.heading_deg === "number" ? `rotate(${v.heading_deg}deg)` : "";

      marker.setLngLat([v.lon, v.lat]).addTo(map);
    });

    // prune
    Object.keys(cache).forEach((id) => {
      if (!vehicles.some((v) => String(v.id) === String(id))) {
        cache[id].remove();
        delete cache[id];
      }
    });
  }, [vehicles, authed, approved, mapStyle, selectedVehicleId]);

  /* ==== SPaT markers (traffic-light icons) ==== */
  useEffect(() => {
    const map = mapRef.current;
    if (!map || authed !== true || approved === false) return;

    const cache = spatMarkersRef.current;

    spats.forEach((s) => {
      if (typeof s.lon !== "number" || typeof s.lat !== "number") return;

      let marker = cache[s.intersection_id];
      if (!marker) {
        const img = document.createElement("img");
        img.src = "/traffic-light.png";
        img.alt = "intersection";
        img.style.width = "22px";
        img.style.height = "22px";
        img.style.display = "block";
        img.style.userSelect = "none";
        img.style.pointerEvents = "auto";

        marker = new mapboxgl.Marker({ element: img, anchor: "center" });
        cache[s.intersection_id] = marker;

        img.addEventListener("click", () => {
          setSelectedId(s.intersection_id);
          if (mapRef.current) mapRef.current.flyTo({ center: [s.lon as number, s.lat as number], zoom: 18 });
        });
      }

      const imgEl = marker.getElement() as HTMLImageElement;
      imgEl.style.transform = selectedId === s.intersection_id ? "scale(1.1)" : "";

      marker.setLngLat([s.lon, s.lat]).addTo(map);
    });

    Object.keys(cache).forEach((id) => {
      if (!spats.find((x) => x.intersection_id === id)) {
        cache[id].remove();
        delete cache[id];
      }
    });
  }, [spats, authed, approved, selectedId, mapStyle]);

  /* ==================== AUTH UI ==================== */
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

    const onCreate = async () => {
      try {
        setAuthErr(null);
        setBusy(true);
        const cred = await createUserWithEmailAndPassword(auth, email.trim(), pw);

        // Queue the user for admin review (one-time self-create allowed by rules)
        await dbSet(dbRef(db, `pending_users/${cred.user.uid}`), true);

        // Optional minimal profile record
        await dbSet(dbRef(db, `users/${cred.user.uid}`), {
          email: cred.user.email ?? email.trim(),
          createdAt: Date.now(),
        });

        // After signup they will see the "Access pending" screen automatically
        // If you prefer to sign them out immediately, uncomment:
        // await signOut(auth);
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setAuthErr(msg || "Could not create account");
      } finally {
        setBusy(false);
      }
    };

    const isSignUp = mode === "signup";

    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="rounded-2xl shadow p-6 w-80 space-y-3 bg-white">
          <h1 className="font-bold text-lg text-center">{isSignUp ? "Create account" : "Sign in"}</h1>

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
            onClick={isSignUp ? onCreate : onLogin}
          >
            {busy ? (isSignUp ? "Creating..." : "Signing in...") : isSignUp ? "Create account" : "Sign in"}
          </button>

          <div className="text-xs text-center text-gray-600 mt-1">
            {isSignUp ? (
              <>
                Already have an account?{" "}
                <button className="underline" onClick={() => setMode("signin")}>
                  Sign in
                </button>
              </>
            ) : (
              <>
                New here?{" "}
                <button className="underline" onClick={() => setMode("signup")}>
                  Create an account
                </button>
              </>
            )}
          </div>

          {isSignUp && (
            <div className="text-[11px] text-gray-500 text-center">Your account will be pending until an admin approves it.</div>
          )}
        </div>
      </div>
    );
  }

  if (authed === null) return <div className="min-h-screen w-full bg-white" />;

  if (approved === false) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="rounded-2xl shadow p-6 w-[28rem] bg-white">
          <h2 className="text-lg font-bold mb-2">Access pending</h2>
          <p className="text-sm text-gray-700">Your account is not approved yet. Please contact an administrator.</p>
          <div className="mt-4">
            <button className="text-xs px-3 py-1 rounded bg-black text-white" onClick={() => signOut(auth)}>
              Sign out
            </button>
          </div>
        </div>
      </div>
    );
  }

  /* ==================== APP UI ==================== */
  const selected = spats.find((s) => s.intersection_id === selectedId) || spats[0];

  return (
    <div className="min-h-screen w-full flex">
      <div className="w-full h-screen relative">
        <div ref={mapContainerRef} className="absolute inset-0 h-full w-full" />

        {/* HUD */}
        <div className="absolute top-3 left-3 bg-white/90 backdrop-blur rounded-2xl shadow-lg p-4 w-80 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold">C-VISION ANL-AMTL</h2>
            <button className="text-xs px-2 py-1 rounded bg-black text-white" onClick={() => signOut(auth)} title="Sign out">
              Sign out
            </button>
          </div>

          {/* Map style toggle */}
          <div className="flex gap-2">
            <button
              className={`text-xs px-2 py-1 rounded ${mapStyle === "streets" ? "bg-black text-white" : "bg-gray-200"}`}
              onClick={() => setMapStyle("streets")}
            >
              Streets
            </button>
            <button
              className={`text-xs px-2 py-1 rounded ${mapStyle === "satellite" ? "bg-black text-white" : "bg-gray-200"}`}
              onClick={() => setMapStyle("satellite")}
            >
              Satellite
            </button>
          </div>

          {/* Vehicles dropdown */}
          <section>
            <h3 className="text-sm font-semibold mb-1">Vehicles ({vehicles.length})</h3>
            <select
              className="w-full border rounded p-1 text-sm mb-2"
              value={selectedVehicleId ?? (vehicles[0]?.id ?? "")}
              onChange={(e) => {
                const id = e.target.value || null;
                setSelectedVehicleId(id);
                const v = vehicles.find((x) => x.id === id);
                if (v && mapRef.current && typeof v.lon === "number" && typeof v.lat === "number") {
                  mapRef.current.flyTo({ center: [v.lon, v.lat], zoom: 18 });
                }
              }}
            >
              {vehicles.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.id}
                </option>
              ))}
            </select>

            {/* Tiny legend chips */}
            <div className="flex flex-wrap gap-1">
              {vehicles.slice(0, 8).map((v) => {
                const { core } = colorFor(v.id);
                return (
                  <span
                    key={`chip-${v.id}`}
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] border"
                    style={{ borderColor: core }}
                  >
                    <span className="inline-block w-2 h-2 rounded-full" style={{ background: core }} />
                    <span className="font-mono truncate max-w-[9rem]">{v.id}</span>
                  </span>
                );
              })}
            </div>
          </section>

          {/* SPaT selector */}
          <section>
            <h3 className="text-sm font-semibold mb-1">Intersections ({spats.length})</h3>
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
          </section>
        </div>

        {/* Bottom dock with phase cards */}
        {selected?.phaseStates?.length ? (
          <div className="absolute left-0 right-0 bottom-0 px-4 pb-3">
            <div className="mx-auto max-w-6xl grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {selected.phaseStates.map((ps) => {
                const color = lampHex(ps.state);
                const approach = directionToApproach(ps.direction);
                const arrows = arrowsForManeuver(ps.maneuver);
                return (
                  <div key={`card-${ps.phase}`} className="rounded-xl overflow-hidden shadow bg-neutral-800 text-white">
                    <div className="px-3 py-2 flex items-center justify-between border-b border-neutral-700">
                      <div className="text-sm font-semibold">{selected.intersection_name || selected.intersection_id} — P{ps.phase}</div>
                      <div className="flex gap-1" title={ps.state}>
                        <span
                          className="inline-block w-2 h-2 rounded-full"
                          style={{ background: "#16a34a", opacity: color === "#16a34a" ? 1 : 0.2 }}
                        />
                        <span
                          className="inline-block w-2 h-2 rounded-full"
                          style={{ background: "#f59e0b", opacity: color === "#f59e0b" ? 1 : 0.2 }}
                        />
                        <span
                          className="inline-block w-2 h-2 rounded-full"
                          style={{ background: "#e11d48", opacity: color === "#e11d48" ? 1 : 0.2 }}
                        />
                      </div>
                    </div>
                    <div className="px-3 py-3 flex items-center justify-between">
                      <div className="text-lg font-bold">{arrows}</div>
                      <div className="text-xs opacity-80">Dir: {approach}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
