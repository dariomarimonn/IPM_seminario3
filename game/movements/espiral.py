import math

from .base import Movimiento


class Espiral(Movimiento):
    """Se acerca al objetivo girando a su alrededor."""

    def __init__(self, obtener_objetivo, velocidad, giro):
        self.obtener_objetivo = obtener_objetivo
        self.velocidad = velocidad        # px/s hacia el objetivo
        self.giro = math.radians(giro)    # grados/s alrededor del objetivo (positivo = antihorario)

    def paso(self, objeto, dt):
        objetivo = self.obtener_objetivo()
        if objetivo is None:
            return
        dx, dy = objeto.x - objetivo[0], objeto.y - objetivo[1]   # posición relativa al objetivo
        r = max(0.0, math.hypot(dx, dy) - self.velocidad * dt)    # el radio baja a ritmo constante
        theta = math.atan2(dy, dx) - self.giro * dt               # el ángulo avanza a ritmo constante
        objeto.x = objetivo[0] + r * math.cos(theta)
        objeto.y = objetivo[1] + r * math.sin(theta)