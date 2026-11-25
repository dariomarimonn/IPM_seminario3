import time

import cv2

from config import config, BONUS, FICHAS, HUD, MENU, MODOS, PARTIDA, ZONAS
from game import (Bonus, Camera, Circulo, HandTracker, Menu, Motor, PoseTracker, calcular_zonas, cargar_sprites,
                  draw_hud, draw_imagen_en_zona, draw_menu, draw_objetos, draw_palmas, draw_pausa, draw_resumen,
                  draw_zonas, icono, resumen)
from game.zonas.agujero import dedos_manos

# Con la imagen en espejo, la pose etiqueta al revés: su "izquierda" (puntos 15, 17, 19) es la mano
# derecha real del jugador. Orden = el de ZonasJugador.palmas.
LADOS_PALMAS = ("derecha", "izquierda") if config.mirror else ("izquierda", "derecha")


def nuevo_motor(modo: str, tamano):
    fichas = {tipo: FICHAS[tipo] for tipo in MODOS[modo]["tipos"]}
    bonus = {nombre: Bonus(b["duracion"], b["t_estable"], b["solo_amenazas"]) for nombre, b in BONUS.items()}
    return Motor(fichas, dict(PARTIDA, **MODOS[modo].get("partida", {})), bonus, tamano, LADOS_PALMAS)


def nuevo_menu(tamano):
    return Menu(list(MODOS), tamano, MENU["t_elegir"], MENU["radio"], MENU["altura"])


def contenido_menu(sprites, radio_boton: float) -> dict:
    """Lo que el menú enseña de cada nivel: la imagen de su botón (ajustada al botón) y sus líneas de
    información, rellenas con los valores reales de la partida y de las fichas."""
    lado = int(2 * radio_boton * MENU["icono"])
    niveles = {}
    for clave, modo in MODOS.items():
        partida = {**PARTIDA, **modo.get("partida", {})}
        niveles[clave] = {
            "nombre": modo["nombre"],
            "descripcion": modo["descripcion"],
            "icono": icono(sprites[modo["icono"]].para("ACTIVO").frames[0], lado),
            "lineas": [(etiqueta, valor.format(partida=partida, **FICHAS)) for etiqueta, valor in modo["info"]],
        }
    return niveles


def dibujar_juego(frame, motor, zonas, manos, sprites, anim_agujero, icono_vida):
    agujero, barrera = motor.bonus["agujero"], motor.bonus["barrera"]
    if agujero.zona:                       # galaxia vista a través del cuadrilátero de los dedos
        img = anim_agujero.fotograma(agujero.edad, 1.0)
        draw_imagen_en_zona(frame, agujero.zona, img, BONUS["agujero"]["opacidad"])
        draw_zonas(frame, [agujero.zona], BONUS["agujero"]["color"], 2)
    if barrera.zona:                       # línea entre las palmas, más fina que su zona (solo visual)
        grosor = max(1, round(2 * barrera.zona.grosor * BONUS["barrera"]["ancho_linea"]))
        draw_zonas(frame, [barrera.zona], BONUS["barrera"]["color"], grosor)
    draw_objetos(frame, motor.objetos, sprites)
    draw_palmas(frame, zonas.palmas, LADOS_PALMAS, HUD["colores_mano"])
    if motor.dos_manos and zonas.juntas:   # zona para coger con las dos manos: solo con las palmas cerca
        draw_zonas(frame, [zonas.juntas], HUD["color_juntas"], 3)
    if agujero.activo:                     # puntas de los dedos que forman el agujero
        draw_zonas(frame, [Circulo(p, 8) for p in dedos_manos(manos) or []], BONUS["agujero"]["color"], -1)
    activos = [(BONUS[n]["texto"], b.fraccion, BONUS[n]["color"]) for n, b in motor.bonus.items() if b.activo]
    draw_hud(frame, motor.partida, activos, icono_vida, HUD)

    if motor.terminado:
        motivo = "sin vidas" if motor.partida.sin_vidas else "tiempo agotado"
        draw_resumen(frame, f"Fin de la partida: {motivo}", resumen(motor.partida, motor.metricas, motor.fichas),
                     "R: repetir     M: menu     ESC: salir")
    elif motor.pausado:
        draw_pausa(frame, empezada=motor.partida.tiempo > 0)


def main():
    camara = Camera(config.camera_index, config.camera_width, config.camera_height, config.mirror)
    pose = PoseTracker(str(config.model_path), config.num_poses)
    manos_tracker = HandTracker(str(config.hand_model_path), config.num_hands)
    sprites = {tipo: cargar_sprites(config.assets_dir, tipo, ficha["animaciones"]) for tipo, ficha in FICHAS.items()}
    anim_agujero = cargar_sprites(config.assets_dir, "agujero", BONUS["agujero"]["animaciones"]).para("ACTIVO")
    icono_vida = icono(sprites["corazon"].para("ACTIVO").frames[0], HUD["icono_vida"])

    textos_menu = {"titulo": MENU["titulo"], "subtitulo": MENU["subtitulo"],
                   "pie": MENU["pie"].format(partida=PARTIDA)}
    menu = motor = modo = niveles_menu = None   # motor None = estamos en el menú
    resumen_impreso = False
    t_prev = time.time()

    try:
        while True:
            frame = camara.read()
            if frame is None:
                break
            alto, ancho = frame.shape[:2]
            if menu is None and motor is None:
                menu = nuevo_menu((ancho, alto))
                niveles_menu = niveles_menu or contenido_menu(sprites, menu.radio)   # una vez: el tamaño no cambia

            ahora = time.time()
            dt = ahora - t_prev
            t_prev = ahora

            # detectar siempre antes de dibujar; las manos solo hacen falta con el agujero activo
            puntos = pose.process(frame)
            con_manos = motor is not None and motor.bonus["agujero"].activo
            manos = manos_tracker.process(frame) if con_manos else {}
            zonas = calcular_zonas(puntos, ZONAS, manos)

            elegido = None
            if motor is None:
                elegido = menu.actualizar(dt, zonas.palmas)
                draw_menu(frame, menu, niveles_menu, textos_menu, hay_jugador=zonas.cara is not None)
                draw_palmas(frame, zonas.palmas, LADOS_PALMAS, HUD["colores_mano"])
            else:
                motor.actualizar(dt, zonas)
                dibujar_juego(frame, motor, zonas, manos, sprites, anim_agujero, icono_vida)
                if motor.terminado and not resumen_impreso:
                    print(f"{MODOS[modo]['nombre']}:\n  " + "\n  ".join(resumen(motor.partida, motor.metricas,
                                                                               motor.fichas)))
                    resumen_impreso = True

            cv2.imshow(config.window_name, frame)
            tecla = cv2.waitKey(1) & 0xFF
            if tecla == config.exit_key:
                break
            if motor is None and chr(tecla) in MODOS:
                elegido = chr(tecla)
            if elegido or (tecla == config.restart_key and motor is not None and motor.terminado):
                modo = elegido or modo
                motor, menu, resumen_impreso = nuevo_motor(modo, (ancho, alto)), None, False
            elif tecla == config.menu_key and motor is not None:
                motor, menu = None, nuevo_menu((ancho, alto))
    finally:
        camara.release()
        pose.close()
        manos_tracker.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
