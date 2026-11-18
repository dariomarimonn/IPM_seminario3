import cv2
import numpy as np

def draw_points(frame, points: dict, color=(0, 255, 0), radius=8) -> None:
    for landmark, (x, y) in points.items():
        cv2.circle(frame, (x, y), radius, color, -1)
        cv2.putText(frame, str(int(landmark)), (x + 10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


def draw_hands(frame, hands: dict, radius=4) -> None:
    colores = {"Left": (255, 0, 0), "Right": (0, 0, 255)}   # BGR
    for etiqueta, puntos in hands.items():
        color = colores.get(etiqueta, (255, 255, 255))
        for x, y in puntos.values():
            cv2.circle(frame, (x, y), radius, color, -1)
        x, y = puntos[min(puntos)]          # muñeca (HandLandmark.WRIST = 0)
        cv2.putText(frame, etiqueta, (x, y - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        


def draw_objetos(frame, objetos, imagenes):
    """imagenes: {tipo: imagen BGRA}"""
    for obj in objetos:
        img = imagenes.get(obj.tipo)
        tam = int(2 * obj.radio * obj.progreso)
        if img is None or tam < 2:
            continue
        _pegar(frame, cv2.resize(img, (tam, tam)), *obj.posicion)

def _pegar(frame, img, cx, cy):
    h, w = frame.shape[:2]
    tam = img.shape[0]
    x0, y0 = cx - tam // 2, cy - tam // 2
    fx0, fy0 = max(x0, 0), max(y0, 0)
    fx1, fy1 = min(x0 + tam, w), min(y0 + tam, h)
    if fx0 >= fx1 or fy0 >= fy1:
        return
    sub = img[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]
    alfa = sub[:, :, 3:4] / 255.0
    roi = frame[fy0:fy1, fx0:fx1]
    roi[:] = (sub[:, :, :3] * alfa + roi * (1 - alfa)).astype(np.uint8)