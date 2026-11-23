"""Dónde nace cada tipo de objeto, por nombre (FICHAS[tipo]["aparicion"]).

Cada función recibe el tamaño del frame, el objetivo (nariz o None), los parámetros de PARTIDA
y un generador aleatorio, y devuelve (x, y) en píxeles.
"""
import math


def borde(ancho, alto, objetivo, params, rng):
    """En el borde superior o en un lateral (abajo no: ahí descansan las manos)."""
    lado = rng.choice(("arriba", "izquierda", "derecha"))
    if lado == "arriba":
        return rng.uniform(0, ancho), 0.0
    return (0.0 if lado == "izquierda" else float(ancho)), rng.uniform(0, alto * 0.75)


def interior(ancho, alto, objetivo, params, rng):
    """Punto al azar lejos de los bordes."""
    m = params["margen_interior"]
    return rng.uniform(ancho * m, ancho * (1 - m)), rng.uniform(alto * m, alto * (1 - m))


def alrededor(ancho, alto, objetivo, params, rng):
    """En un círculo alrededor del objetivo, recortado a la pantalla (para que la espiral quepa)."""
    if objetivo is None:
        return interior(ancho, alto, objetivo, params, rng)
    r = params["radio_alrededor"] * min(ancho, alto)
    a = rng.uniform(0, 2 * math.pi)
    x = min(max(objetivo[0] + r * math.cos(a), 0), ancho)
    y = min(max(objetivo[1] + r * math.sin(a), 0), alto)
    return x, y


POSICIONES = {"borde": borde, "interior": interior, "alrededor": alrededor}
