from .directo import HaciaObjetivo


class HaciaObjetivoGiratorio(HaciaObjetivo):
    """Igual que HaciaObjetivo, pero además gira sobre sí mismo."""

    def __init__(self, obtener_objetivo, velocidad, giro):
        super().__init__(obtener_objetivo, velocidad)
        self.giro = giro  # grados/s (positivo = sentido antihorario)

    def paso(self, objeto, dt):
        super().paso(objeto, dt)
        objeto.angulo = (objeto.angulo + self.giro * dt) % 360