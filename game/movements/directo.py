import math
from typing import Callable, Optional

from .base import Movimiento

class HaciaObjetivo(Movimiento):
    """Línea recta hacia un objetivo que puede moverse entre frames.

    obtener_objetivo: función sin argumentos que devuelve (x_px, y_px) o None
                      (p. ej. None si la pose no detecta a nadie).
    velocidad: píxeles por segundo.
    """

    def __init__(self, obtener_objetivo: Callable[[], Optional[tuple[float, float]]], velocidad: float):
        self._obtener_objetivo = obtener_objetivo
        self._velocidad = velocidad

    def paso(self, objeto, dt: float) -> None:
        objetivo = self._obtener_objetivo()
        if objetivo is None:
            return                                   # sin objetivo: el objeto se queda quieto

        dx = objetivo[0] - objeto.x
        dy = objetivo[1] - objeto.y
        distancia = math.hypot(dx, dy)
        avance = self._velocidad * dt

        if distancia <= avance:                      # llega este frame (cubre distancia 0)
            objeto.x, objeto.y = objetivo
            return

        objeto.x += dx / distancia * avance
        objeto.y += dy / distancia * avance
