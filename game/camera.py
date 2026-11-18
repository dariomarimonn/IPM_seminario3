import cv2


class Camera:
    def __init__(self, index: int, width: int, height: int, mirror: bool):
        self._cap = cv2.VideoCapture(index)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self._mirror = mirror

    def read(self):
        """Devuelve un frame BGR, o None si no hay."""
        ok, frame = self._cap.read()
        if not ok:
            return None
        return cv2.flip(frame, 1) if self._mirror else frame

    def release(self) -> None:
        self._cap.release()