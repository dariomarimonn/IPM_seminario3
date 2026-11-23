"""Formas geométricas de las zonas. Solo datos + la pregunta `contiene`; no dibujan."""
import math
from dataclasses import dataclass

Punto = tuple[float, float]


@dataclass(frozen=True)
class Circulo:
    centro: Punto
    radio: float

    def contiene(self, punto: Punto) -> bool:
        return math.dist(punto, self.centro) < self.radio


@dataclass(frozen=True)
class Poligono:
    vertices: tuple[Punto, ...]   # en orden, recorriendo el contorno

    def contiene(self, punto: Punto) -> bool:
        """Cruce de rayos: un rayo horizontal desde el punto corta el borde un número impar de veces si está dentro."""
        x, y = punto
        dentro = False
        n = len(self.vertices)
        for i in range(n):
            (x1, y1), (x2, y2) = self.vertices[i], self.vertices[(i + 1) % n]
            if (y1 > y) != (y2 > y):                        # el lado cruza la horizontal del punto
                x_corte = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                if x < x_corte:
                    dentro = not dentro
        return dentro

    @property
    def area(self) -> float:
        """Fórmula del cordón (shoelace)."""
        n = len(self.vertices)
        s = sum(self.vertices[i][0] * self.vertices[(i + 1) % n][1]
                - self.vertices[(i + 1) % n][0] * self.vertices[i][1] for i in range(n))
        return abs(s) / 2

    @property
    def lados(self) -> list[float]:
        n = len(self.vertices)
        return [math.dist(self.vertices[i], self.vertices[(i + 1) % n]) for i in range(n)]


@dataclass(frozen=True)
class Segmento:
    """Segmento con grosor (cápsula): contiene los puntos a menos de `grosor` del segmento a-b."""
    a: Punto
    b: Punto
    grosor: float

    def contiene(self, punto: Punto) -> bool:
        (ax, ay), (bx, by), (px, py) = self.a, self.b, punto
        dx, dy = bx - ax, by - ay
        largo2 = dx * dx + dy * dy
        # proyección del punto sobre el segmento, recortada a sus extremos
        t = 0.0 if largo2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / largo2))
        return math.dist(punto, (ax + t * dx, ay + t * dy)) < self.grosor
