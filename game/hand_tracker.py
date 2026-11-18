import time
import cv2
import mediapipe as mp

from config import HandLandmark


class HandTracker:
    def __init__(self, model_path: str, num_hands: int = 2):
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=num_hands,
        )
        self._landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self._t0 = time.time()

    def process(self, frame_bgr) -> dict:
        """Devuelve {"Left": {HandLandmark: (x, y)}, "Right": {...}}; vacío si no hay manos."""
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        imagen = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        ts = int((time.time() - self._t0) * 1000)
        res = self._landmarker.detect_for_video(imagen, ts)

        manos = {}
        for lms, lado in zip(res.hand_landmarks, res.handedness):
            etiqueta = lado[0].category_name          # "Left" o "Right"
            manos[etiqueta] = {p: (int(lms[p].x * w), int(lms[p].y * h)) for p in HandLandmark}
        return manos

    def close(self) -> None:
        self._landmarker.close()