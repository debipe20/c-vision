// Types the page imports
export type StaticPhase = { phase: number; direction: string; maneuver?: string };
export type StaticIntersection = {
  name: string;
  lat: number;
  lon: number;
  phases: StaticPhase[];
};
export type StaticIntersectionMap = Record<string, StaticIntersection>;

/** Configure your 5 intersections here */
export const INTERSECTIONS: StaticIntersectionMap = {
  "2351": {
    name: "Kearney Rd & WaterTower Rd",
    lat: 41.711326,
    lon: -87.992046,
    phases: [
      { phase: 2, direction: "NorthBound", maneuver: "through-right" },
      { phase: 4, direction: "WestBound", maneuver: "left-right" },
      { phase: 6, direction: "SouthBound", maneuver: "left-through" },
    ],
  },
  "2350": {
    name: "Kearney Rd & Westgate Rd",
    lat: 41.715538,
    lon: -87.992211,
    phases: [
      { phase: 2, direction: "EastBound", maneuver: "left-through-right" },
      { phase: 4, direction: "SouthBound", maneuver: "left-through-right" },
      { phase: 6, direction: "WestBound", maneuver: "left-through-right" },
      { phase: 8, direction: "NorthBound", maneuver: "left-through-right" },
    ],
  },
  "3002": {
    name: "Roosevelt Rd & Canal St",
    lat: 41.867226,
    lon: -87.639224, 
    phases: [
      {phase: 1, direction: "WestBound", maneuver: "left"},
      {phase: 2, direction: "EastBound", maneuver: "through-right"},
      {phase: 3, direction: "NorthBound", maneuver: "left"},
      {phase: 4, direction: "SouthBound", maneuver: "through-right"},
      {phase: 5, direction: "EastBound", maneuver: "left"},
      {phase: 6, direction: "WestBound", maneuver: "through-right"},
      {phase: 7, direction: "SouthBound", maneuver: "left"},
      {phase: 8, direction: "NorthBound", maneuver: "through-right"},
    ],
  },
  "3006": {
    name: "Roosevelt Rd & Michigan Ave",
    lat: 41.867454, 
    lon: -87.624141, 
    phases: [
      {phase: 1, direction: "WestBound", maneuver: "left"},
      {phase: 2, direction: "EastBound", maneuver: "through-right"},
      {phase: 3, direction: "NorthBound", maneuver: "left"},
      {phase: 4, direction: "SouthBound", maneuver: "through-right"},
      {phase: 5, direction: "EastBound", maneuver: "left"},
      {phase: 6, direction: "WestBound", maneuver: "through-right"},
      {phase: 7, direction: "SouthBound", maneuver: "left"},
      {phase: 8, direction: "NorthBound", maneuver: "through-right"},
    ],
  },
  "44383": {
    name: "DaisyMountain Dr & GavilanPeak Pkwy",
    lat: 33.842918,
    lon: -112.135202,
    phases: [
      {phase: 1, direction: "WestBound", maneuver: "left"},
      {phase: 2, direction: "EastBound", maneuver: "through-right"},
      {phase: 3, direction: "NorthBound", maneuver: "left"},
      {phase: 4, direction: "SouthBound", maneuver: "through-right"},
      {phase: 5, direction: "EastBound", maneuver: "left"},
      {phase: 6, direction: "WestBound", maneuver: "through-right"},
      {phase: 7, direction: "SouthBound", maneuver: "left"},
      {phase: 8, direction: "NorthBound", maneuver: "through-right"},
    ],
  },
};