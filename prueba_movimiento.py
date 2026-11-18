# prueba_cara.py  (temporal, no se entrega)
import math
import random
import time

import cv2

from config import config, Landmark
from game import Camera, PoseTracker
from game.objects.entities import Objeto
from game.movements import HaciaObjetivo

DISTANCIA_IMPACTO = 40  # px


def punto_en_borde(w, h):
    lado = random.choice("aril")
    if lado == "a":
        return random.randint(0, w), 0
    if lado == "r":
        return random.randint(0, w), h
    if lado == "i":
        return 0, random.randint(0, h)
    return w, random.randint(0, h)


def main():
    cam = Camera(config.camera_index, config.camera_width, config.camera_height, config.mirror)
    pose = PoseTracker(str(config.model_path), config.num_poses)
    nariz = {"pos": None}
    objeto = None
    t_prev = time.time()

    try:
        while True:
            frame = cam.read()
            if frame is None:
                break
            h, w = frame.shape[:2]

            ahora = time.time()
            dt = ahora - t_prev
            t_prev = ahora

            # 1) detectar (antes de dibujar)
            puntos = pose.process(frame)
            nariz["pos"] = puntos[Landmark.NARIZ] if puntos else None

            # 2) lógica
            if objeto is None or not objeto.vivo:
                x, y = punto_en_borde(w, h)
                objeto = Objeto(x, y, 20, 1.0, 0.3, HaciaObjetivo(lambda: nariz["pos"], 100))
            objeto.actualizar(dt)

            if objeto.tocable and nariz["pos"]:
                ox, oy = objeto.posicion
                if math.hypot(ox - nariz["pos"][0], oy - nariz["pos"][1]) < DISTANCIA_IMPACTO:
                    objeto.desaparecer()

            # 3) dibujar
            if nariz["pos"]:
                cv2.circle(frame, tuple(map(int, nariz["pos"])), 6, (0, 255, 0), -1)
            cv2.circle(frame, objeto.posicion, max(1, int(20 * objeto.progreso)), (0, 0, 255), -1)

            cv2.imshow(config.window_name, frame)
            if cv2.waitKey(1) & 0xFF == config.exit_key:
                break
    finally:
        cam.release()
        pose.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()