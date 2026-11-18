import time
import cv2
import mediapipe as mp

from config import Landmark


class PoseTracker:
    def __init__(self, model_path: str, num_poses: int = 1):
        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_poses=num_poses,
        )
        self._landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)
        self._t0 = time.time()

    def process(self, frame_bgr) -> dict | None:
        """Devuelve {Landmark: (x_px, y_px)} o None si no detecta a nadie."""
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        imagen = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        ts = int((time.time() - self._t0) * 1000)
        resultado = self._landmarker.detect_for_video(imagen, ts)
        if not resultado.pose_landmarks:
            return None
        lms = resultado.pose_landmarks[0]
        return {p: (int(lms[p].x * w), int(lms[p].y * h)) for p in Landmark}

    def close(self) -> None:
        self._landmarker.close()