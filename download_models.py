import os
import urllib.request

URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"
DESTINO = os.path.join(os.path.dirname(__file__), "models", "pose_landmarker_full.task")

if os.path.exists(DESTINO):
    print("El modelo ya existe.")
else:
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    urllib.request.urlretrieve(URL, DESTINO)
    print("Modelo descargado.")
