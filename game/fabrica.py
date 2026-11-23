import random

from .movements import Espiral, HaciaObjetivo, Ondulado, Quiebro, Quieto
from .objeto import Objeto

MOVIMIENTOS = {
    "directo": lambda ficha, obtener_objetivo, rng: HaciaObjetivo(obtener_objetivo, ficha["velocidad"]),
    "espiral": lambda ficha, obtener_objetivo, rng: Espiral(
        obtener_objetivo, ficha["velocidad"], rng.choice((-1, 1)) * ficha["giro_orbital"]),   # sentido al azar
    "quieto": lambda ficha, obtener_objetivo, rng: Quieto(),
    "ondulado": lambda ficha, obtener_objetivo, rng: Ondulado(
        obtener_objetivo, ficha["velocidad"],
        amplitud=rng.choice((-1, 1)) * ficha["amplitud"],       # hacia qué lado empieza, al azar
        frecuencia=ficha["frecuencia"]),
    "quiebro": lambda ficha, obtener_objetivo, rng: Quiebro(
        obtener_objetivo, ficha["velocidad"],
        inicio=rng.uniform(*ficha["quiebro"]["cuando"]),
        duracion=ficha["quiebro"]["duracion"],
        angulo=rng.choice((-1, 1)) * ficha["quiebro"]["angulo"]),
}


def crear_objeto(ficha: dict, tipo: str, x: float, y: float, obtener_objetivo,
                 rng: random.Random | None = None) -> Objeto:
    """Construye un Objeto desde su ficha de FICHAS."""
    rng = rng or random.Random()
    movimiento = MOVIMIENTOS[_elegir(ficha["movimiento"], rng)](ficha, obtener_objetivo, rng)
    return Objeto(x, y, ficha["radio"], ficha["t_aparecer"], ficha["t_desaparecer"], movimiento, tipo=tipo)


def _elegir(movimiento: str | dict, rng: random.Random) -> str:
    """Un nombre, o {nombre: peso} para sortear el movimiento de cada objeto."""
    if isinstance(movimiento, str):
        return movimiento
    nombres, pesos = zip(*movimiento.items())
    return rng.choices(nombres, weights=pesos)[0]
