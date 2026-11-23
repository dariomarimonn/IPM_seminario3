import math

from .base import Movimiento
from .directo import HaciaObjetivo


class Quiebro(Movimiento):
    """Va directo al objetivo, pero una vez, durante un momento, se desvía hacia un lado y luego sigue directo."""

    def __init__(self, obtener_objetivo, velocidad: float, inicio: float, duracion: float, angulo: float):
        self._directo = HaciaObjetivo(obtener_objetivo, velocidad)
        self._obtener_objetivo = obtener_objetivo
        self._velocidad = velocidad
        self._inicio = inicio                  # s moviéndose hasta que quiebra
        self._fin = inicio + duracion
        self._angulo = math.radians(angulo)    # desvío respecto al rumbo directo; el signo elige el lado
        self._t = 0.0

    def paso(self, objeto, dt: float) -> None:
        self._t += dt
        if not self._inicio <= self._t < self._fin:
            self._directo.paso(objeto, dt)
            return
        objetivo = self._obtener_objetivo()
        if objetivo is None:
            return
        rumbo = math.atan2(objetivo[1] - objeto.y, objetivo[0] - objeto.x) + self._angulo
        objeto.x += math.cos(rumbo) * self._velocidad * dt
        objeto.y += math.sin(rumbo) * self._velocidad * dt
