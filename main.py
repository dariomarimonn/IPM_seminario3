# main_bomba.py
import math
import random
import time

import cv2

from config import config, Landmark
from game import Camera, PoseTracker, cargar_sprites, draw_objetos
from game.objects.objeto import Objeto
from game.movements import HaciaObjetivo
from game.movements import HaciaObjetivoGiratorio
from game.movements import Espiral

# Valores de la bomba (más adelante irán a FICHAS en config.py)
RADIO = 70
VELOCIDAD = 150          # px/s
T_APARECER = 1.0         # s
T_DESAPARECER = 0.45     # s
DISTANCIA_IMPACTO = 40   # px entre la bomba y la nariz


def punto_en_borde(ancho, alto):
    lado = random.choice("aril")
    if lado == "a":
        return random.randint(0, ancho), 0
    if lado == "r":
        return random.randint(0, ancho), alto
    if lado == "i":
        return 0, random.randint(0, alto)
    return ancho, random.randint(0, alto)


def crear_bomba(ancho, alto, obtener_objetivo):
    x, y = punto_en_borde(ancho, alto)
    movimiento = HaciaObjetivoGiratorio(obtener_objetivo, VELOCIDAD, 90)
    return Objeto(x, y, RADIO, T_APARECER, T_DESAPARECER, movimiento, tipo="bomba")


def toca_la_cara(objeto, nariz):
    if nariz is None:
        return False
    ox, oy = objeto.posicion
    return math.hypot(ox - nariz[0], oy - nariz[1]) < DISTANCIA_IMPACTO


def main():
    # 1) Construir las piezas (solo main conoce config)
    camara = Camera(config.camera_index, config.camera_width, config.camera_height, config.mirror)
    pose = PoseTracker(str(config.model_path), config.num_poses)
    sprites = {"bomba": cargar_sprites(config.assets_dir, "bomba", {"salida": 1.5})}

    nariz = None
    bomba = None
    t_prev = time.time()

    try:
        while True:
            frame = camara.read()
            if frame is None:
                break
            alto, ancho = frame.shape[:2]

            ahora = time.time()
            dt = ahora - t_prev
            t_prev = ahora

            # 2) Detectar (siempre antes de dibujar)
            puntos = pose.process(frame)
            nariz = puntos[Landmark.NARIZ] if puntos else None

            # 3) Lógica del juego
            if bomba is None or not bomba.vivo:
                bomba = crear_bomba(ancho, alto, lambda: nariz)  # lee la nariz de cada frame
            bomba.actualizar(dt)
            if bomba.tocable and toca_la_cara(bomba, nariz):
                bomba.desaparecer()

            # 4) Dibujar
            if nariz:
                cv2.circle(frame, tuple(map(int, nariz)), 6, (0, 255, 0), -1)
            draw_objetos(frame, [bomba], sprites)

            cv2.imshow(config.window_name, frame)
            if cv2.waitKey(1) & 0xFF == config.exit_key:
                break
    finally:
        camara.release()
        pose.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()