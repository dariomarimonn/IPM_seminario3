import cv2
import numpy as np

from ..zonas import Circulo, Poligono, Segmento


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


def draw_objetos(frame, objetos, sprites: dict) -> None:
    """sprites: {tipo: SpriteTipo}."""
    for obj in objetos:
        sprite = sprites.get(obj.tipo)
        if sprite is None or not obj.vivo:
            continue
        anim = sprite.para(obj.estado.name)
        img = anim.fotograma(obj.edad, obj.avance)
        tam = int(2 * obj.radio * anim.escala * (obj.progreso if anim.ajustar else 1.0))
        if tam < 2:
            continue
        img = cv2.resize(img, (tam, tam))
        if anim.giro:
            img = _rotar(img, (obj.edad * anim.giro) % 360)
        _pegar(frame, img, *obj.posicion)


def draw_zonas(frame, zonas, color=(255, 200, 0), grosor=2) -> None:
    """Dibuja el contorno de cada zona; la función se elige por la forma (sin if por tipo)."""
    for zona in zonas:
        _DIBUJAR_ZONA[type(zona)](frame, zona, color, grosor)


def _dibujar_circulo(frame, zona, color, grosor):
    cx, cy = zona.centro
    cv2.circle(frame, (int(cx), int(cy)), int(zona.radio), color, grosor)


def _dibujar_poligono(frame, zona, color, grosor):
    pts = np.array(zona.vertices, np.int32).reshape(-1, 1, 2)
    cv2.polylines(frame, [pts], True, color, grosor)


def _dibujar_segmento(frame, zona, color, grosor):
    """Con grosor < 0, la cápsula entera (el ancho real de la zona); si no, una línea de ese grosor."""
    a, b = tuple(map(int, zona.a)), tuple(map(int, zona.b))
    cv2.line(frame, a, b, color, max(1, int(2 * zona.grosor)) if grosor < 0 else grosor, cv2.LINE_AA)


_DIBUJAR_ZONA = {Circulo: _dibujar_circulo, Poligono: _dibujar_poligono, Segmento: _dibujar_segmento}


def draw_imagen_en_zona(frame, zona, img, opacidad=1.0) -> None:
    """Efecto ventana: la imagen ocupa toda la pantalla, fija, y solo se ve dentro del polígono."""
    h, w = frame.shape[:2]
    pts = np.array(zona.vertices, np.int32)
    x0, y0 = np.maximum(pts.min(axis=0), 0)
    x1, y1 = np.minimum(pts.max(axis=0) + 1, (w, h))
    if x0 >= x1 or y0 >= y1:
        return
    fondo = cv2.resize(img, (w, h))[y0:y1, x0:x1]
    mascara = np.zeros((y1 - y0, x1 - x0), np.float32)
    cv2.fillPoly(mascara, [pts - (x0, y0)], 1.0)
    alfa = mascara[:, :, None] * opacidad
    if fondo.shape[2] == 4:
        alfa = alfa * (fondo[:, :, 3:4] / 255.0)
    roi = frame[y0:y1, x0:x1]
    roi[:] = (fondo[:, :, :3] * alfa + roi * (1 - alfa)).astype(np.uint8)


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


def _rotar(img, grados):
    h, w = img.shape[:2]
    n = int(np.ceil(np.hypot(h, w)))
    lienzo = np.zeros((n, n, 4), np.uint8)
    y0, x0 = (n - h) // 2, (n - w) // 2
    lienzo[y0:y0 + h, x0:x0 + w] = img
    M = cv2.getRotationMatrix2D((n / 2, n / 2), grados, 1.0)
    return cv2.warpAffine(lienzo, M, (n, n))
