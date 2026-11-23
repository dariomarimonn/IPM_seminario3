"""Métricas de la partida (valor serio: uso de cada brazo, asimetría y tiempo de reacción).

Solo cuentan lo que el motor les dice; no saben de reglas ni de dibujo.
"""
from collections import Counter
from statistics import mean

IZQ, DER, AMBAS = "izquierda", "derecha", "ambas"


class Metricas:
    def __init__(self):
        self.tocados = {IZQ: Counter(), DER: Counter(), AMBAS: Counter()}   # lado → {tipo: n}
        self.reacciones = {IZQ: [], DER: [], AMBAS: []}   # s desde que el premio es tocable
        self.cara = Counter()                             # tipo → n que llegaron a la cara
        self.absorbidos = Counter()
        self.caducados = Counter()
        self.errores_mano = {IZQ: Counter(), DER: Counter()}   # lado con el que se tocó → {tipo: n}

    def tocar(self, lado: str, tipo: str, reaccion: float | None) -> None:
        self.tocados[lado][tipo] += 1
        if reaccion is not None:
            self.reacciones[lado].append(reaccion)

    def llegar_cara(self, tipo: str) -> None:
        self.cara[tipo] += 1

    def absorber(self, tipo: str) -> None:
        self.absorbidos[tipo] += 1

    def caducar(self, tipo: str) -> None:
        self.caducados[tipo] += 1

    def fallar_mano(self, lado: str, tipo: str) -> None:
        self.errores_mano[lado][tipo] += 1

    def aciertos(self, lado: str) -> int:
        return sum(self.tocados[lado].values())

    def reaccion_media(self, lado: str) -> float | None:
        return mean(self.reacciones[lado]) if self.reacciones[lado] else None

    def asimetria(self) -> float:
        """(der - izq) / total, en [-1, 1]: positivo = más aciertos con la derecha; 0 sin aciertos."""
        izq, der = self.aciertos(IZQ), self.aciertos(DER)
        return (der - izq) / (izq + der) if izq + der else 0.0


def resumen(partida, metricas: Metricas, fichas: dict) -> list[str]:
    """Líneas del resumen final (ASCII: cv2.putText no dibuja tildes)."""
    amenazas = [t for t, f in fichas.items() if f["cara"] == "quitar_vida"]
    premios = [t for t, f in fichas.items() if f["duracion"] is not None]
    manos = {f.get("mano") for f in fichas.values()}
    t = metricas.tocados

    paradas = sum(t[lado][a] for lado in t for a in amenazas)
    absorbidas = sum(metricas.absorbidos[a] for a in amenazas)
    cogidos = sum(t[lado][p] for lado in t for p in premios) + sum(metricas.absorbidos[p] for p in premios)
    errores = {lado: sum(metricas.errores_mano[lado].values()) for lado in (IZQ, DER)}
    perdidos = sum(metricas.caducados[p] for p in premios) + sum(errores.values())

    def mano(lado):
        r = metricas.reaccion_media(lado)
        nombre = "Con las dos manos" if lado == AMBAS else f"Mano {lado}"
        return f"{nombre}: {metricas.aciertos(lado)} aciertos" + (f", reaccion media {r:.1f} s" if r else "")

    a = metricas.asimetria()
    lineas = [
        f"Puntos: {partida.puntos}",
        f"Tiempo jugado: {min(partida.tiempo, partida.duracion):.0f} s"
        + (f" (+{partida.tiempo_ganado:.0f} s ganados)" if partida.tiempo_ganado else ""),
        f"Vidas perdidas: {partida.golpes}",
        f"Enemigos parados: {paradas}" + (f" y {absorbidas} con bonus" if absorbidas else ""),
        f"Premios cogidos: {cogidos} de {cogidos + perdidos}",
        mano(IZQ),
        mano(DER),
    ]
    if AMBAS in manos:
        lineas.append(mano(AMBAS))
    lineas.append(f"Asimetria: {abs(a) * 100:.0f} %" + (f" a favor de la {DER if a > 0 else IZQ}" if a else ""))
    if manos & {IZQ, DER}:   # tocados con la mano que no tocaba
        lineas.append(f"Errores de mano: {errores[IZQ]} con la izquierda, {errores[DER]} con la derecha")
    return lineas
