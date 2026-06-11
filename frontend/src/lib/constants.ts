export const POSE_CONNECTIONS: [number, number][] = [
  [11, 12], // shoulders
  [11, 13], // left upper arm
  [13, 15], // left forearm
  [12, 14], // right upper arm
  [14, 16], // right forearm
  [11, 23], // left torso
  [12, 24], // right torso
  [23, 24], // hips
  [23, 25], // left thigh
  [25, 27], // left shin
  [24, 26], // right thigh
  [26, 28], // right shin
];

export const POSE_LANDMARKS = {
  NOSE: 0,
  LEFT_EYE: 1,
  RIGHT_EYE: 2,
  LEFT_EAR: 7,
  RIGHT_EAR: 8,
  MOUTH_LEFT: 9,
  MOUTH_RIGHT: 10,
  LEFT_SHOULDER: 11,
  RIGHT_SHOULDER: 12,
  LEFT_ELBOW: 13,
  RIGHT_ELBOW: 14,
  LEFT_WRIST: 15,
  RIGHT_WRIST: 16,
  LEFT_HIP: 23,
  RIGHT_HIP: 24,
  LEFT_KNEE: 25,
  RIGHT_KNEE: 26,
  LEFT_ANKLE: 27,
  RIGHT_ANKLE: 28,
};

export const SEVERITY_COLORS: Record<string, string> = {
  good: "text-green-600 bg-green-50 border-green-200",
  info: "text-blue-600 bg-blue-50 border-blue-200",
  warning: "text-yellow-600 bg-yellow-50 border-yellow-200",
  critical: "text-red-600 bg-red-50 border-red-200",
};

export const SEVERITY_ICONS: Record<string, string> = {
  good: "✓",
  info: "ℹ",
  warning: "⚠",
  critical: "✗",
};

export const MOVEMENT_COLORS: Record<string, string> = {
  flag: "#22c55e",
  drop_knee: "#3b82f6",
  dyno: "#ef4444",
  deadpoint: "#f59e0b",
  campusing: "#8b5cf6",
  cut_loose: "#ec4899",
  rock_over: "#06b6d4",
  barn_door: "#f97316",
  matching: "#84cc16",
  stemming: "#14b8a6",
  knee_bar: "#a855f7",
  side_body: "#eab308",
  static: "#6b7280",
  rest: "#9ca3af",
};
