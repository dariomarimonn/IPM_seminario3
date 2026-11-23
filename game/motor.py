"""Motor del juego: las reglas. Lógica pura (sin OpenCV, MediaPipe ni config).

Cada frame recibe las zonas del jugador y decide qué aparece, qué toca a qué y con qué efecto.
Los efectos y las condiciones de aparición son datos de la ficha (FICHAS[tipo]["cara"/"palma"/"condicion"])
resueltos por nombre en EFECTOS y CONDICIONES (regla 5).
"""
import math
import random
from dataclasses import dataclass

from .bonus import Bonus
from .aparicion import POSICIONES
from .fabrica import crear_objeto
from .metricas import AMBAS, Metricas


@dataclass
class Partida:
    """Estado cambiante de la partida (regla 3)."""
    vidas: int
    vidas_max: int
    duracion: float                 # s; crece al ganar tiempo
    restante_max: float | None = None   # tope del tiempo restante al ganar tiempo; None = sin tope
    t_extremo: float | None = None  # s de partida desde los que se avisa de modo extremo; None = nunca
    puntos: int = 0
    tiempo: float = 0.0
    golpes: int = 0
    t_golpe: float = -math.inf      # instante del último golpe en la cara (aviso visual)
    tiempo_ganado: float = 0.0
    ultimo_extra: float = 0.0       # s ganados la última vez y cuándo (aviso visual)
    t_extra: float = -math.inf

    @property
    def restante(self) -> float:
        return max(0.0, self.duracion - self.tiempo)

    @property
    def sin_vidas(self) -> bool:
        return self.vidas <= 0

    @property
    def terminado(self) -> bool:
        return self.sin_vidas or self.tiempo >= self.duracion

    @property
    def extremo(self) -> bool:
        return self.t_extremo is not None and self.tiempo >= self.t_extremo


def interpolar(puntos: list, t: float) -> float:
    """Valor en el segundo t de una lista [(segundo, valor), ...]: lineal entre puntos;
    antes del primero y después del último se mantiene el del extremo."""
    t0, v0 = puntos[0]
    if t <= t0:
        return v0
    for t1, v1 in puntos[1:]:
        if t <= t1:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
        t0, v0 = t1, v1
    return v0


# Efectos por nombre: reciben el motor y el objeto. El objeto desaparece siempre al aplicarse uno.
def _quitar_vida(motor, obj):
    motor.partida.vidas -= 1
    motor.partida.golpes += 1
    motor.partida.t_golpe = motor.partida.tiempo


def _dar_puntos(motor, obj):
    motor.partida.puntos += motor.fichas[obj.tipo]["puntos"]


def _curar(motor, obj):
    if motor.partida.vidas < motor.partida.vidas_max:
        motor.partida.vidas += 1
    else:
        _dar_puntos(motor, obj)


def _sumar_tiempo(motor, obj):
    p = motor.partida
    antes = p.restante
    p.duracion += motor.fichas[obj.tipo]["segundos"]
    if p.restante_max is not None:
        p.duracion = min(p.duracion, p.tiempo + p.restante_max)
    p.ultimo_extra, p.t_extra = p.restante - antes, p.tiempo
    p.tiempo_ganado += p.ultimo_extra


def _activar(nombre):
    """Efecto que activa el bonus `nombre` del motor."""
    return lambda motor, obj: motor.bonus[nombre].activar()


EFECTOS = {
    "eliminar": lambda motor, obj: None,
    "quitar_vida": _quitar_vida,
    "dar_puntos": _dar_puntos,
    "curar": _curar,
    "activar_agujero": _activar("agujero"),
    "activar_barrera": _activar("barrera"),
    "sumar_tiempo": _sumar_tiempo,
}

# Condiciones de aparición por nombre: mientras no se cumplen, el tipo no sale ni corre su espera.
CONDICIONES = {
    "pocas_vidas": lambda motor, ficha: motor.partida.vidas <= ficha["umbral"],
    "falta_tiempo": lambda motor, ficha: motor.partida.restante < ficha["umbral"],
}


class Motor:
    def __init__(self, fichas: dict, partida: dict, bonus: dict[str, Bonus], tamano: tuple[int, int],
                 lados_palmas: tuple[str, str], rng: random.Random | None = None):
        """bonus: {nombre: Bonus}; cada nombre es también el campo de ZonasJugador con su zona.
        tamano: (ancho, alto) del frame. lados_palmas: lado real ("izquierda"/"derecha") de cada
        palma de ZonasJugador.palmas, en su orden."""
        for tipo, f in fichas.items():
            for clave in ("cara", "palma"):
                if f[clave] is not None and f[clave] not in EFECTOS:
                    raise ValueError(f"{tipo}: efecto desconocido {f[clave]!r} (válidos: {list(EFECTOS)})")
            if f.get("mano") not in (None, AMBAS, *lados_palmas):
                raise ValueError(f"{tipo}: mano desconocida {f['mano']!r} (válidas: {(*lados_palmas, AMBAS)})")
            if f.get("condicion") not in (None, *CONDICIONES):
                raise ValueError(f"{tipo}: condición desconocida {f['condicion']!r} (válidas: {list(CONDICIONES)})")
            for clave, puntos in f.get("progresion", {}).items():
                segundos = [t for t, _ in puntos]
                if not puntos or any(a >= b for a, b in zip(segundos, segundos[1:])):
                    raise ValueError(f"{tipo}: la progresión de {clave!r} necesita segundos crecientes: {puntos}")
        self.fichas = fichas
        self.partida = Partida(partida["vidas"], partida["vidas"], partida["duracion"], partida["tiempo_max"],
                               partida["extremo"])
        self.dos_manos = any(f.get("mano") == AMBAS for f in fichas.values())   # usa la zona de manos juntas
        self.bonus = bonus
        self._amenazas = {t for t, f in fichas.items() if f["cara"] == "quitar_vida"}
        self.metricas = Metricas()
        self.objetos = []
        self.pausado = True             # sin pose no corre nada; también antes de la primera detección
        self._params = partida
        self._ancho, self._alto = tamano
        self._lados = lados_palmas
        self._rng = rng or random.Random()
        self._objetivo = None           # centro de la cara (nariz) del último frame con pose
        self._espera = {tipo: self._con_progresion(f)["espera"] for tipo, f in fichas.items()}

    @property
    def terminado(self) -> bool:
        return self.partida.terminado

    def actualizar(self, dt: float, zonas) -> None:
        if self.terminado:
            return
        self.pausado = zonas.cara is None
        if self.pausado:
            return
        self.partida.tiempo += dt
        self._objetivo = zonas.cara.centro

        self._aparecer(dt)
        for o in self.objetos:
            o.actualizar(dt)
        self._caducar()

        # bonus primero, luego palmas y por último cara: lo ya tocado deja de ser tocable
        for nombre, b in self.bonus.items():
            b.actualizar(dt, getattr(zonas, nombre))
            candidatos = [o for o in self.objetos if o.tipo in self._amenazas] if b.solo_amenazas else self.objetos
            for o in b.absorber(candidatos):
                self.metricas.absorber(o.tipo)
                self._aplicar("palma", o)
        self._tocar_palmas(zonas.palmas, zonas.juntas)
        self._tocar_cara(zonas.cara)

        self.objetos = [o for o in self.objetos if o.vivo]

    # --- aparición y caducidad ---

    def _aparecer(self, dt):
        for tipo, base in self.fichas.items():
            ficha = self._con_progresion(base)
            hay_hueco = sum(o.tipo == tipo for o in self.objetos) < round(ficha["cantidad"])
            condicion = ficha.get("condicion")
            if not hay_hueco or (condicion and not CONDICIONES[condicion](self, ficha)):
                continue                 # la espera no corre: siempre hay pausa antes de que salga
            self._espera[tipo] -= dt
            if self._espera[tipo] > 0:
                continue
            x, y = POSICIONES[ficha["aparicion"]](self._ancho, self._alto, self._objetivo, self._params, self._rng)
            self.objetos.append(crear_objeto(ficha, tipo, x, y, lambda: self._objetivo, self._rng))
            self._espera[tipo] = ficha["espera"]

    def _con_progresion(self, ficha: dict) -> dict:
        """La ficha con los valores de su "progresion" para el segundo de partida actual."""
        t = self.partida.tiempo
        return dict(ficha, **{k: interpolar(puntos, t) for k, puntos in ficha.get("progresion", {}).items()})

    def _caducar(self):
        for o in self.objetos:
            d = self.fichas[o.tipo]["duracion"]
            if d is not None and o.tocable and self._t_activo(o) > d:
                o.desaparecer()
                self.metricas.caducar(o.tipo)

    def _t_activo(self, obj) -> float:
        return obj.edad - self.fichas[obj.tipo]["t_aparecer"]

    # --- colisiones y efectos ---

    def _tocar_palmas(self, palmas, juntas):
        """juntas: zona entre las palmas cuando están cerca (o None); la usan los objetos de mano "ambas"."""
        for o in self.objetos:
            if not o.tocable:
                continue
            mano = self.fichas[o.tipo].get("mano")      # None = vale cualquiera
            if mano == AMBAS:                           # con una sola palma no pasa nada
                if juntas is not None and juntas.contiene(o.posicion) and self._aplicar("palma", o):
                    self.metricas.tocar(AMBAS, o.tipo, self._t_activo(o))
                continue
            lados = [lado for lado, palma in zip(self._lados, palmas) if palma.contiene(o.posicion)]
            if not lados:
                continue
            if mano in self._lados and mano not in lados:   # solo la equivocada: se pierde sin efecto
                o.desaparecer()
                self.metricas.fallar_mano(lados[0], o.tipo)
            elif self._aplicar("palma", o):
                # reacción solo de los premios (los que caducan): se miden contra reloj
                reaccion = self._t_activo(o) if self.fichas[o.tipo]["duracion"] is not None else None
                self.metricas.tocar(mano or lados[0], o.tipo, reaccion)

    def _tocar_cara(self, cara):
        for o in self.objetos:
            if o.tocable and cara.contiene(o.posicion) and self._aplicar("cara", o):
                self.metricas.llegar_cara(o.tipo)

    def _aplicar(self, clave: str, obj) -> bool:
        """Aplica FICHAS[tipo][clave] y hace desaparecer el objeto. False si el tipo no reacciona (None)."""
        nombre = self.fichas[obj.tipo][clave]
        if nombre is None:
            return False
        EFECTOS[nombre](self, obj)
        obj.desaparecer()
        return True
