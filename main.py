import math
import random
import time

import cv2

from config import config, FICHAS, Landmark
from game import Camera, PoseTracker, cargar_sprites, crear_objeto, draw_objetos

DISTANCIA_IMPACTO = 40   # px, provisional


def punto_en_borde(ancho, alto):
    lado = random.choice("aril")
    if lado == "a":
        return random.randint(0, ancho), 0
    if lado == "r":
        return random.randint(0, ancho), alto
    if lado == "i":
        return 0, random.randint(0, alto)
    return ancho, random.randint(0, alto)


def toca_la_cara(objeto, nariz):
    if nariz is None:
        return False
    ox, oy = objeto.posicion
    return math.hypot(ox - nariz[0], oy - nariz[1]) < DISTANCIA_IMPACTO


def main():
    camara = Camera(config.camera_index, config.camera_width, config.camera_height, config.mirror)
    pose = PoseTracker(str(config.model_path), config.num_poses)
    sprites = {tipo: cargar_sprites(config.assets_dir, tipo, ficha["animaciones"])
               for tipo, ficha in FICHAS.items()}

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

            # detectar siempre antes de dibujar
            puntos = pose.process(frame)
            nariz = puntos[Landmark.NARIZ] if puntos else None

            if bomba is None or not bomba.vivo:
                x, y = punto_en_borde(ancho, alto)
                bomba = crear_objeto(FICHAS["bomba"], "bomba", x, y, lambda: nariz)
            bomba.actualizar(dt)
            if bomba.tocable and toca_la_cara(bomba, nariz):
                bomba.desaparecer()

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