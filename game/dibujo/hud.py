"""HUD y pantallas superpuestas (pausa y resumen final). Solo dibujan lo que reciben.

Textos sin tildes: las fuentes de cv2.putText solo tienen ASCII.
"""
import math

import cv2
import numpy as np

from .render import _pegar

FUENTE = cv2.FONT_HERSHEY_SIMPLEX
BLANCO = (255, 255, 255)
ROJO = (0, 0, 255)
GRIS = (90, 90, 90)
VERDE = (80, 230, 80)
AMARILLO = (0, 220, 255)
GRIS_CLARO = (175, 175, 175)


def draw_hud(frame, partida, bonus_activos, icono_vida, opciones: dict) -> None:
    """Vidas (iconos), puntos, tiempo (+N s al ganarlo), aviso de modo extremo, una barra por bonus activo y
    borde rojo al recibir un golpe. bonus_activos: [(texto, fraccion 0-1, color BGR)]. opciones: HUD de config."""
    h, w = frame.shape[:2]
    tam = icono_vida.shape[0]
    apagado = (icono_vida * np.array([0.25, 0.25, 0.25, 1.0])).astype(np.uint8)
    for i in range(partida.vidas_max):
        x = 20 + tam // 2 + i * (tam + opciones["hueco_vidas"])
        _pegar(frame, icono_vida if i < partida.vidas else apagado, x, 20 + tam // 2)

    _texto_derecha(frame, f"Puntos: {partida.puntos}", w - 20, 50)
    color_tiempo = ROJO if partida.restante < opciones["aviso_tiempo"] else BLANCO
    _texto_derecha(frame, f"Tiempo: {math.ceil(partida.restante)}", w - 20, 95, color=color_tiempo)
    if partida.tiempo - partida.t_extra < opciones["t_aviso_extra"]:
        _texto_derecha(frame, f"+{partida.ultimo_extra:.0f} s", w - 20, 140, 1.1, VERDE, 3)
    if partida.extremo:
        _centrado(frame, "MODO EXTREMO", 55, 1.3, ROJO, 3)

    for i, (texto, fraccion, color) in enumerate(bonus_activos):
        x0, x1, y = w // 4, 3 * w // 4, h - 40 - 80 * i
        cv2.rectangle(frame, (x0, y - 14), (x1, y + 14), GRIS, -1)
        cv2.rectangle(frame, (x0, y - 14), (x0 + int((x1 - x0) * fraccion), y + 14), color, -1)
        _centrado(frame, texto, y - 30, 0.9, color)

    if partida.tiempo - partida.t_golpe < opciones["t_aviso_golpe"]:
        cv2.rectangle(frame, (0, 0), (w - 1, h - 1), ROJO, 25)


def draw_pausa(frame, empezada: bool) -> None:
    _oscurecer(frame, 0.5)
    h = frame.shape[0]
    if empezada:
        _centrado(frame, "PAUSA: no te veo", h // 2 - 20, 1.6)
        _centrado(frame, "Vuelve frente a la camara", h // 2 + 40, 1.0)
    else:
        _centrado(frame, "Colocate frente a la camara", h // 2 - 20, 1.4)
        _centrado(frame, "con los hombros y las manos a la vista", h // 2 + 40, 1.0)


def draw_resumen(frame, titulo: str, lineas: list[str], pie: str) -> None:
    _oscurecer(frame, 0.7)
    h = frame.shape[0]
    alto_linea = 42
    y = (h - alto_linea * (len(lineas) + 3)) // 2 + 40
    _centrado(frame, titulo, y, 1.6, AMARILLO, 3)
    y += 70
    for linea in lineas:
        _centrado(frame, linea, y, 0.9)
        y += alto_linea
    _centrado(frame, pie, y + 30, 0.8, (180, 180, 180))


def _oscurecer(frame, alfa: float) -> None:
    frame[:] = (frame * (1 - alfa)).astype(np.uint8)


def _texto(frame, texto, x, y, escala=1.0, color=BLANCO, grosor=2) -> None:
    """Con contorno negro para que se lea sobre cualquier fondo."""
    cv2.putText(frame, texto, (x, y), FUENTE, escala, (0, 0, 0), grosor + 4, cv2.LINE_AA)
    cv2.putText(frame, texto, (x, y), FUENTE, escala, color, grosor, cv2.LINE_AA)


def _centrado(frame, texto, y, escala=1.0, color=BLANCO, grosor=2, cx=None) -> None:
    """Centrado en la x `cx` (por defecto, el centro del frame)."""
    (ancho, _), _ = cv2.getTextSize(texto, FUENTE, escala, grosor)
    cx = frame.shape[1] // 2 if cx is None else cx
    _texto(frame, texto, cx - ancho // 2, y, escala, color, grosor)


def _texto_derecha(frame, texto, x_dcha, y, escala=1.0, color=BLANCO, grosor=2) -> None:
    (ancho, _), _ = cv2.getTextSize(texto, FUENTE, escala, grosor)
    _texto(frame, texto, x_dcha - ancho, y, escala, color, grosor)


def draw_palmas(frame, palmas, lados, colores: dict) -> None:
    """Contorno de cada palma con la inicial de su lado (I/D), en el color de esa mano."""
    for lado, palma in zip(lados, palmas):
        cx, cy = map(int, palma.centro)
        cv2.circle(frame, (cx, cy), int(palma.radio), colores[lado], 3)
        _texto(frame, lado[0].upper(), cx - 10, cy + 10, 0.9, colores[lado])


def draw_menu(frame, menu, niveles: dict, textos: dict, hay_jugador: bool) -> None:
    """Pantalla principal: título, una tarjeta por nivel (botón con su imagen, que se llena con un arco al
    mantener la palma, y su ficha debajo) y un pie común.
    niveles: {clave: {"nombre", "descripcion", "icono" (BGRA cuadrado), "lineas": [(etiqueta, valor)]}}.
    textos: {"titulo", "subtitulo", "pie"}."""
    h, w = frame.shape[:2]
    _oscurecer(frame, 0.35)
    _centrado(frame, textos["titulo"], 75, 1.9, AMARILLO, 4)
    if hay_jugador:
        _centrado(frame, textos["subtitulo"], 118, 0.75)
    else:
        _centrado(frame, "Colocate frente a la camara con las manos a la vista", 118, 0.75, AMARILLO)
    n_lineas = max(len(n["lineas"]) for n in niveles.values())
    media_col = w // (2 * len(niveles))
    for clave, boton in menu.botones.items():
        nivel = niveles[clave]
        (cx, cy), r = map(int, boton.centro), int(boton.radio)
        y = cy + r + 40                                    # primera línea de texto bajo el botón
        _panel(frame, cx - media_col + 12, cy - r - 14, cx + media_col - 12, y + 72 + 30 * n_lineas)
        progreso = min(1.0, menu.progreso[clave])
        cv2.circle(frame, (cx, cy), r, (35, 35, 35), -1, cv2.LINE_AA)
        _pegar(frame, nivel["icono"], cx, cy)
        cv2.circle(frame, (cx, cy), r, AMARILLO if progreso > 0 else BLANCO, 3, cv2.LINE_AA)
        if progreso > 0:                                   # con 0, cv2.ellipse pinta un punto en el centro
            cv2.ellipse(frame, (cx, cy), (r, r), -90, 0, 360 * progreso, AMARILLO, 10, cv2.LINE_AA)
        _insignia(frame, clave, cx + int(0.72 * r), cy - int(0.72 * r))
        _centrado(frame, nivel["nombre"], y, 0.75, cx=cx)
        _centrado(frame, nivel["descripcion"], y + 32, 0.85, AMARILLO, cx=cx)
        _tabla(frame, nivel["lineas"], cx, y + 72, 0.6, 30)
    _centrado(frame, textos["pie"], h - 28, 0.7, GRIS_CLARO)


def _panel(frame, x0, y0, x1, y1, alfa=0.55) -> None:
    """Rectángulo oscurecido con borde: el fondo de cada tarjeta del menú."""
    h, w = frame.shape[:2]
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, w - 1), min(y1, h - 1)
    roi = frame[y0:y1, x0:x1]
    roi[:] = (roi * (1 - alfa)).astype(np.uint8)
    cv2.rectangle(frame, (x0, y0), (x1, y1), GRIS, 1)


def _tabla(frame, lineas, cx, y, escala, paso, grosor=1) -> None:
    """Etiquetas (gris) y valores (blanco) en dos columnas alineadas; el bloque, centrado en cx.
    Una etiqueta vacía continúa la línea anterior."""
    def medir(t):
        return cv2.getTextSize(t, FUENTE, escala, grosor)[0][0]
    ancho_etq = max(medir(e + ":") for e, _ in lineas if e) + 12
    x = cx - (ancho_etq + max(medir(v) for _, v in lineas)) // 2
    for i, (etiqueta, valor) in enumerate(lineas):
        if etiqueta:
            _texto(frame, etiqueta + ":", x, y + i * paso, escala, GRIS_CLARO, grosor)
        _texto(frame, valor, x + ancho_etq, y + i * paso, escala, BLANCO, grosor)


def _insignia(frame, texto, cx, cy, radio=18) -> None:
    """Círculo amarillo con la tecla del nivel."""
    cv2.circle(frame, (cx, cy), radio, AMARILLO, -1, cv2.LINE_AA)
    (ancho, alto), _ = cv2.getTextSize(texto, FUENTE, 0.7, 2)
    cv2.putText(frame, texto, (cx - ancho // 2, cy + alto // 2), FUENTE, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
