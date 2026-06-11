export interface VideoUploadResponse {
  video_id: string;
  status: string;
  filename: string;
}

export interface VideoStatusResponse {
  video_id: string;
  status: string;
  progress: number;
  stage_name: string;
  error_message: string | null;
}

export interface Keypoint2D {
  x: number;
  y: number;
  z: number;
  visibility: number;
}

export interface PoseFrameResult {
  frame_number: number;
  timestamp_ms: number;
  landmarks_2d: Keypoint2D[];
  landmarks_3d: Record<string, number>[] | null;
  confidence: number;
}

export interface HoldResult {
  frame_number: number;
  bbox: { x: number; y: number; w: number; h: number };
  hold_type: string | null;
  confidence: number;
}

export interface MovementEvent {
  type: string;
  start_frame: number;
  end_frame: number;
  confidence: number;
  label_cn: string;
}

export interface BiomechanicsFeedbackItem {
  rule: string;
  severity: string;
  title: string;
  description: string;
  frames: number[];
}

export interface JointAngleStat {
  min: number;
  max: number;
  avg: number;
}

export interface VideoResultsResponse {
  video: {
    id: string;
    filename: string;
    duration: number;
    fps: number;
    width: number;
    height: number;
  };
  poses: PoseFrameResult[];
  holds: HoldResult[];
  movements: MovementEvent[];
  biomechanics_feedback: BiomechanicsFeedbackItem[];
  coaching_summary: string | null;
  joint_angle_stats: Record<string, JointAngleStat>;
}
