from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Landmark(IntEnum):
    """Índices de MediaPipe Pose usados en el juego."""
    NARIZ = 0
    OREJA_IZQ = 7
    OREJA_DER = 8
    HOMBRO_IZQ = 11
    HOMBRO_DER = 12
    CODO_IZQ = 13
    CODO_DER = 14
    MUNECA_IZQ = 15
    MUNECA_DER = 16
    MENIQUE_IZQ = 17
    MENIQUE_DER = 18
    INDICE_IZQ = 19
    INDICE_DER = 20
    PULGAR_IZQ = 21
    PULGAR_DER = 22


class HandLandmark(IntEnum):
    """Los 21 puntos de HandLandmarker."""
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_MCP = 5
    INDEX_PIP = 6
    INDEX_DIP = 7
    INDEX_TIP = 8
    MIDDLE_MCP = 9
    MIDDLE_PIP = 10
    MIDDLE_DIP = 11
    MIDDLE_TIP = 12
    RING_MCP = 13
    RING_PIP = 14
    RING_DIP = 15
    RING_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


# Un tipo nuevo = una entrada aquí + su carpeta en assets/<tipo>/. Claves de cada ficha:
#   radio: px, solo dibujo · movimiento: nombre o {nombre: peso} para sortearlo (MOVIMIENTOS en game/fabrica.py)
#     y sus parámetros (velocidad, amplitud, frecuencia, giro_orbital, quiebro)
#   t_aparecer / t_desaparecer: s · aparicion: dónde nace (POSICIONES en game/aparicion.py)
#   cantidad: máximo a la vez · espera: s entre apariciones del tipo (también antes de la primera)
#   duracion: s tocable antes de caducar (None = no caduca) · puntos
#   cara / palma: efecto al llegar a la cara / al tocarlo con la palma o absorberlo (EFECTOS en game/motor.py;
#     None = nada)
#   mano (opcional): "izquierda", "derecha" o "ambas" (las dos palmas a la vez); sin ella vale cualquiera
#   condicion (opcional): solo aparece mientras se cumple (CONDICIONES en game/motor.py)
#   progresion (opcional): {clave: [(segundo de partida jugada, valor), ...]}; sustituye a esa clave (no se repite
#     fuera): tramos rectos entre puntos y, antes del primero y después del último, el valor de ese extremo
#   animaciones: estado → animación; un estado sin entrada usa la de ACTIVO
FICHAS = {
    # --- Nivel 1: era de la galaxia
    "alien": {                   # enemigo: va a por la cara ondulando; desde la mitad, más agresivo
        "radio": 60,
        "movimiento": "ondulado",
        "frecuencia": 0.5,       # Hz de la oscilación lateral: onda lenta y ancha
        "progresion": {
            "velocidad": [(0, 60), (30, 95), (60, 150)],   # px/s: desde los 30 s acelera más
            "amplitud": [(0, 110), (30, 60), (50, 15)],    # px: cada vez más directo
            "cantidad": [(0, 2), (30, 2), (40, 3)],        # a la vez (se redondea: 3 desde ~35 s)
            "espera": [(0, 3.0), (30, 3.0), (60, 2.0)],    # s entre apariciones
        },
        "t_aparecer": 0.8,
        "t_desaparecer": 0.5,
        "aparicion": "borde",
        "duracion": None,
        "puntos": 0,
        "cara": "quitar_vida",
        "palma": "eliminar",
        "animaciones": {
            "APARECIENDO":    {"carpeta": "aparecer", "modo": "progreso"},
            "ACTIVO":         {"carpeta": "normal", "modo": "bucle", "fps": 4},
            "DESAPARECIENDO": {"carpeta": "desaparecer", "modo": "progreso"},
        },
    },
    "planeta": {                 # premio: alrededor de la cara, unos en órbita y otros quietos; cualquier mano
        "radio": 65,
        "movimiento": {"espiral": 0.6, "quieto": 0.4},
        "velocidad": 0,          # espiral sin acercarse: órbita pura
        "giro_orbital": 6,       # °/s (una vuelta por minuto), sentido al azar: lento para que no maree
        "progresion": {"cantidad": [(0, 2), (30, 2), (35, 3)]},   # uno más desde la mitad (~33 s)
        "t_aparecer": 0.8,
        "t_desaparecer": 0.6,
        "aparicion": "alrededor",
        "espera": 2.0,
        "duracion": 7.0,
        "puntos": 10,
        "cara": None,
        "palma": "dar_puntos",
        "animaciones": {
            "APARECIENDO":    {"carpeta": "aparecer", "modo": "progreso"},
            "ACTIVO":         {"carpeta": "normal", "modo": "bucle", "fps": 3},
            "DESAPARECIENDO": {"carpeta": "desaparecer", "modo": "progreso"},
        },
    },
    "galaxia": {                 # bonus: activa el agujero negro
        "radio": 80,
        "movimiento": "espiral",
        "velocidad": 35,         # px/s hacia el objetivo
        "giro_orbital": 40,      # °/s alrededor del objetivo
        "t_aparecer": 0.5,
        "t_desaparecer": 0.5,
        "aparicion": "alrededor",
        "cantidad": 1,
        "espera": 20.0,
        "duracion": None,
        "puntos": 0,
        "cara": "eliminar",      # si llega a la cara se pierde el bonus
        "palma": "activar_agujero",
        # mismo giro en todas para que no salte al cambiar de estado
        "animaciones": {
            "APARECIENDO":    {"carpeta": "desaparecer", "modo": "progreso", "invertir": True, "giro": 120},
            "ACTIVO":         {"carpeta": "normal", "giro": 120},
            "DESAPARECIENDO": {"carpeta": "desaparecer", "modo": "progreso", "giro": 120},
        },
    },

    # --- Nivel 2: era de la recolección
    "abeja": {                   # enemigo: zigzag rápido hacia la cara
        "radio": 60,
        "movimiento": "ondulado",
        "frecuencia": 1.4,
        "progresion": {"velocidad": [(0, 80), (60, 150)], "amplitud": [(0, 70), (60, 15)]},
        "t_aparecer": 0.7,
        "t_desaparecer": 0.5,
        "aparicion": "borde",
        "cantidad": 2,
        "espera": 2.8,
        "duracion": None,
        "puntos": 0,
        "cara": "quitar_vida",
        "palma": "eliminar",
        "animaciones": {
            "APARECIENDO":    {"carpeta": "aparecer", "modo": "progreso"},
            "ACTIVO":         {"carpeta": "normal", "modo": "bucle", "fps": 10},
            "DESAPARECIENDO": {"carpeta": "desaparecer", "modo": "progreso"},
        },
    },
    "manzana": {                 # premio: solo con la mano izquierda
        "radio": 60,
        "movimiento": "quieto",
        "velocidad": 0,
        "t_aparecer": 0.8,
        "t_desaparecer": 0.4,
        "aparicion": "interior",
        "cantidad": 2,
        "espera": 2.0,
        "duracion": 6.0,
        "puntos": 10,
        "mano": "izquierda",     # con la otra mano se pierde (error de mano)
        "cara": None,
        "palma": "dar_puntos",
        "animaciones": {
            "APARECIENDO":    {"carpeta": "aparecer", "modo": "progreso"},
            "ACTIVO":         {"carpeta": "normal"},
            "DESAPARECIENDO": {"carpeta": "aparecer", "modo": "progreso", "invertir": True},
        },
    },
    "moneda": {                  # premio: solo con la mano derecha
        "radio": 60,
        "movimiento": "quieto",
        "velocidad": 0,
        "t_aparecer": 0.8,
        "t_desaparecer": 0.5,
        "aparicion": "interior",
        "cantidad": 2,
        "espera": 2.0,
        "duracion": 6.0,
        "puntos": 10,
        "mano": "derecha",
        "cara": None,
        "palma": "dar_puntos",
        "animaciones": {
            "APARECIENDO":    {"carpeta": "aparecer", "modo": "progreso"},
            "ACTIVO":         {"carpeta": "normal"},
            "DESAPARECIENDO": {"carpeta": "desaparecer", "modo": "progreso"},
        },
    },
    "rayo": {                    # bonus: activa la barrera
        "radio": 80,             # como la galaxia: el dibujo del rayo es estrecho
        "movimiento": "quieto",
        "velocidad": 0,
        "t_aparecer": 0.5,
        "t_desaparecer": 0.6,
        "aparicion": "interior",
        "cantidad": 1,
        "espera": 20.0,
        "duracion": 6.0,
        "puntos": 0,
        "cara": None,
        "palma": "activar_barrera",
        "animaciones": {
            "APARECIENDO":    {"carpeta": "aparecer", "modo": "progreso"},
            "ACTIVO":         {"carpeta": "normal", "modo": "bucle", "fps": 8},
            "DESAPARECIENDO": {"carpeta": "desaparecer", "modo": "progreso"},
        },
    },

    # --- Nivel 3: era de la ciencia
    "bomba": {                   # enemigo: directa o con quiebro; cada vez más rápida y más seguida
        "radio": 70,
        "movimiento": {"directo": 0.6, "quiebro": 0.4},
        "quiebro": {             # solo si sale "quiebro": una vez se desvía de lado y luego sigue directa
            "cuando": (1.0, 3.0),    # s moviéndose antes del desvío (al azar en el rango)
            "duracion": 0.8,         # s desviándose
            "angulo": 80,            # ° respecto al rumbo directo; el lado se sortea
        },
        "progresion": {          # cada vez más rápida y seguida; desde los 40 s (modo extremo), sin freno
            "velocidad": [(0, 110), (40, 180), (100, 280)],   # px/s
            "espera": [(0, 2.4), (40, 1.5), (100, 0.3)],      # s
            "cantidad": [(0, 2), (40, 2), (100, 12)],         # a la vez
        },
        "t_aparecer": 0.8,
        "t_desaparecer": 0.45,
        "aparicion": "borde",
        "duracion": None,
        "puntos": 0,
        "cara": "quitar_vida",
        "palma": "eliminar",
        "animaciones": {
            "ACTIVO":         {"carpeta": "normal", "modo": "fija", "giro": 90, "ajustar": True},
            "DESAPARECIENDO": {"carpeta": "salida", "modo": "progreso", "escala": 1.5},
        },
    },
    "probeta": {                 # premio: hay que juntar las dos palmas encima
        "radio": 65,
        "movimiento": "quieto",
        "velocidad": 0,
        "t_aparecer": 0.8,
        "t_desaparecer": 0.5,
        "aparicion": "interior",
        "cantidad": 2,
        "espera": 2.0,
        "duracion": 6.0,
        "puntos": 15,
        "mano": "ambas",
        "cara": None,
        "palma": "dar_puntos",
        "animaciones": {
            "APARECIENDO":    {"carpeta": "aparecer", "modo": "progreso"},
            "ACTIVO":         {"carpeta": "normal", "modo": "bucle", "fps": 6},
            "DESAPARECIENDO": {"carpeta": "desaparecer", "modo": "progreso"},
        },
    },
    "reloj": {                   # especial: suma tiempo; solo sale cuando queda poco
        "radio": 60,
        "movimiento": "quieto",
        "velocidad": 0,
        "t_aparecer": 0.8,
        "t_desaparecer": 0.6,
        "aparicion": "interior",
        "cantidad": 1,
        "espera": 8.0,           # con t_aparecer y t_desaparecer, 9,4 s entre relojes > los 7 s que suma cada uno:
        "duracion": 5.0,         # aunque los cojas todos al instante, el tiempo baja y la partida no es infinita
        "puntos": 0,
        "condicion": "falta_tiempo",
        "umbral": 20.0,          # s restantes por debajo de los cuales puede salir
        "segundos": 7.0,         # tiempo que suma (con tope PARTIDA["tiempo_max"])
        "cara": None,
        "palma": "sumar_tiempo",
        "animaciones": {
            "APARECIENDO":    {"carpeta": "aparecer", "modo": "progreso"},
            "ACTIVO":         {"carpeta": "normal", "modo": "bucle", "fps": 3},
            "DESAPARECIENDO": {"carpeta": "desaparecer", "modo": "progreso"},
        },
    },

    # --- Todos los niveles
    "corazon": {                 # recupera una vida; solo sale cuando te queda una
        "radio": 55,
        "movimiento": "quieto",
        "velocidad": 0,
        "t_aparecer": 0.4,
        "t_desaparecer": 0.4,
        "aparicion": "interior",
        "cantidad": 1,
        "espera": 15.0,          # s con una sola vida antes de que salga
        "duracion": 5.0,
        "puntos": 5,             # si las vidas ya están llenas
        "condicion": "pocas_vidas",
        "umbral": 1,             # vidas: solo sale si te quedan estas o menos (con 2 no sale)
        "cara": None,
        "palma": "curar",
        "animaciones": {
            "APARECIENDO":    {"carpeta": "aparecer", "modo": "progreso"},
            "ACTIVO":         {"carpeta": "normal"},
            "DESAPARECIENDO": {"carpeta": "desaparecer", "modo": "progreso"},
        },
    },
}


# Niveles que se eligen en el menú (tecla = clave). Textos sin tildes (cv2.putText). Claves:
#   tipos: fichas del nivel · partida (opcional): cambia valores de PARTIDA
#   icono: tipo cuya imagen va dentro de su botón del menú
#   info: líneas (etiqueta, valor) bajo el botón; "{partida[...]}" y "{<tipo>[...]}" se rellenan con los
#     valores reales del nivel y de FICHAS, para que el menú no se desfase si cambian
MODOS = {
    "1": {"nombre": "Nivel 1", "descripcion": "Era de la galaxia",
          "tipos": ["alien", "planeta", "galaxia", "corazon"],
          "icono": "alien",
          "info": [("Tiempo", "{partida[duracion]:.0f} s"), ("Recompensa", "planeta, cualquier mano"),
                   ("Enemigo", "alien"), ("Bonus", "galaxia")]},
    "2": {"nombre": "Nivel 2", "descripcion": "Era de la recoleccion",
          "tipos": ["abeja", "manzana", "moneda", "rayo", "corazon"],
          "icono": "abeja",
          "info": [("Tiempo", "{partida[duracion]:.0f} s"), ("Recompensa", "manzana, mano izquierda"),
                   ("", "moneda, mano derecha"), ("Enemigo", "abeja"), ("Bonus", "rayo")]},
    "3": {"nombre": "Nivel 3", "descripcion": "Era de la ciencia",
          "tipos": ["bomba", "probeta", "reloj", "corazon"],
          "partida": {"duracion": 30.0, "tiempo_max": 40.0, "extremo": 40.0},   # con "progresion" de bomba
          "icono": "bomba",
          "info": [("Tiempo", "{partida[duracion]:.0f} s"), ("Recompensa", "probeta, manos juntas"),
                   ("Enemigo", "bomba"), ("Bonus", "reloj, suma {reloj[segundos]:.0f} s")]},
}


# Pantalla principal: se elige un nivel manteniendo la palma sobre su botón. Textos sin tildes.
MENU = {
    "titulo": "ERAS EN TUS MANOS",   # nombre del juego
    "subtitulo": "Elige una era: manten la palma sobre ella o pulsa 1, 2 o 3",
    "pie": "Vidas: {partida[vidas]} en todas las eras. Si te queda una, puede salir un corazon (+1 vida)",
    "t_elegir": 1.0,             # s con la palma dentro del botón
    "radio": 0.09,               # radio de cada botón, en fracción del ancho del frame
    "altura": 0.37,              # altura de los botones, en fracción del alto
    "icono": 0.75,               # lado de la imagen del botón, en fracción de su diámetro
}


# Reglas de la partida (cada nivel puede cambiarlas en MODOS[...]["partida"]).
PARTIDA = {
    "vidas": 3,                  # iniciales y máximas
    "duracion": 60.0,            # s; acaba antes si se pierden todas las vidas
    "tiempo_max": None,          # tope del tiempo restante al sumar tiempo (relojes); None = sin tope
    "extremo": None,             # s de partida jugada desde los que se avisa de "MODO EXTREMO"; None = nunca
    "margen_interior": 0.15,     # fracción del borde de pantalla donde no nacen los objetos "interior"
    "radio_alrededor": 0.35,     # distancia a la nariz de los objetos "alrededor", en fracción del lado corto
}


# Tamaños de las zonas del jugador, en anchos de hombros (área en hombros²). Provisionales: ajustar con cámara.
ZONAS = {
    "radio_cara": 0.3,
    "radio_palma": 0.15,         # círculo de cada palma: lo que se dibuja y lo que toca
    "agujero_area_min": 0.05,    # por debajo: dedos casi juntos
    "agujero_area_max": 1.5,     # por encima: brazos demasiado abiertos
    "agujero_lado_min": 0.08,    # lado más corto; evita zonas largas y estrechas
    "barrera_grosor": 0.08,      # media anchura del segmento entre las palmas
    "juntas_radio": 0.3,         # círculo entre las palmas para coger con las dos manos (probeta)
    "juntas_max": 0.8,           # solo existe si los centros de las palmas están a menos de esto
}


# Bonus agujero negro (al coger la galaxia). La imagen se ve solo dentro de la zona de los dedos.
AGUJERO_NEGRO = {
    "duracion": 8.0,             # s activo tras coger la galaxia
    "t_estable": 0.3,            # s que el gesto debe ser válido seguido antes de absorber
    "solo_amenazas": False,      # absorbe todo (y aplica su efecto de palma)
    "texto": "AGUJERO NEGRO: junta pulgares e indices",   # sin tildes (cv2.putText)
    "color": (200, 0, 255),      # BGR
    "opacidad": 0.85,            # 0-1, mezcla de la imagen con la cámara
    "animaciones": {             # assets/agujero/<carpeta>/
        "ACTIVO": {"carpeta": "normal", "modo": "bucle", "fps": 4},
    },
}


# Bonus barrera (al coger el rayo): el segmento entre las palmas destruye los enemigos que toca.
BARRERA = {
    "duracion": 8.0,
    "t_estable": 0.0,
    "solo_amenazas": True,       # no recoge premios: no se salta la regla de la mano
    "texto": "BARRERA: para las abejas con la linea entre tus manos",
    "color": (0, 0, 255),        # BGR: rojo, como el rayo
    "ancho_linea": 0.5,          # grosor dibujado, en fracción de la anchura real de la zona (solo visual)
}

# Nombre del bonus = campo de ZonasJugador con su zona; los efectos "activar_<nombre>" lo activan.
BONUS = {"agujero": AGUJERO_NEGRO, "barrera": BARRERA}


# Dibujo del HUD.
HUD = {
    "icono_vida": 50,            # px, lado del corazón de cada vida (recortado a su contorno)
    "hueco_vidas": 8,            # px entre corazones
    "t_aviso_golpe": 0.4,        # s que dura el borde rojo al recibir un golpe
    "t_aviso_extra": 1.2,        # s que se ve el "+N s" al ganar tiempo
    "aviso_tiempo": 10.0,        # s restantes por debajo de los cuales el tiempo sale en rojo
    "colores_mano": {"izquierda": (60, 60, 235), "derecha": (0, 190, 255)},   # BGR: rojo (manzana) y dorado (moneda)
    "color_juntas": (80, 230, 80),   # BGR: zona de palmas juntas (coger con las dos manos)
}


@dataclass(frozen=True)
class Config:
    # Modelos
    models_dir: Path = BASE_DIR / "models"
    assets_dir: Path = BASE_DIR / "assets"
    model_name: str = "pose_landmarker_full.task"
    num_poses: int = 1
    hand_model_name: str = "hand_landmarker.task"
    num_hands: int = 2

    # Cámara (resolución pedida; la real puede variar)
    camera_index: int = 0
    camera_width: int = 1280
    camera_height: int = 720
    mirror: bool = True

    # Ventana
    window_name: str = "Seminario 3"
    exit_key: int = 27            # ESC
    restart_key: int = ord("r")   # repetir el nivel en la pantalla final
    menu_key: int = ord("m")      # volver al menú (también a mitad de partida)

    @property
    def model_path(self) -> Path:
        return self.models_dir / self.model_name

    @property
    def hand_model_path(self) -> Path:
        return self.models_dir / self.hand_model_name


config = Config()