"""Bonus agujero negro: mientras está activo, la zona de los dedos absorbe los objetos que entran.

Lógica pura (sin OpenCV ni config): recibe la zona del frame y la lista de objetos.
"""
import math


class AgujeroNegro:
    def __init__(self, duracion: float | None, t_estable: float):
        self._duracion = duracion        # None = permanente
        self._t_estable = t_estable
        self._restante = 0.0
        self._valido = 0.0               # s seguidos con el gesto válido
        self.edad = 0.0                  # s desde que se activó (para la animación)
        self.zona = None                 # zona que absorbe este frame, o None

    @property
    def activo(self) -> bool:
        return self._restante > 0

    @property
    def restante(self) -> float:
        return self._restante

    def activar(self) -> None:
        """Al coger la galaxia. Si ya estaba activo, reinicia la duración."""
        self._restante = math.inf if self._duracion is None else self._duracion
        self.edad = 0.0

    def actualizar(self, dt: float, zona) -> None:
        """zona: el Poligono de los dedos de este frame, o None si el gesto no es válido."""
        self._restante -= dt
        self.edad += dt
        if not self.activo:
            self._valido, self.zona = 0.0, None
            return
        self._valido = self._valido + dt if zona is not None else 0.0
        self.zona = zona if self._valido >= self._t_estable else None

    def absorber(self, objetos) -> list:
        """Hace desaparecer los objetos tocables cuyo punto está dentro de la zona. Devuelve los absorbidos."""
        if self.zona is None:
            return []
        absorbidos = [o for o in objetos if o.tocable and self.zona.contiene(o.posicion)]
        for o in absorbidos:
            o.desaparecer()
        return absorbidos
