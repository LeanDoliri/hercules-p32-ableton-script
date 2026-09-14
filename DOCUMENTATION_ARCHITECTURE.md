# Estado de Arquitectura y Mapeos del Hercules P32 DJ

> [!NOTE]
> Este documento sirve como "fuente de la verdad" para consolidar exactamente qué hace cada control en el script actual y evitar confusiones sobre qué páginas están libres o mapeadas.

## 1. Modos Principales
El script opera en dos modos principales que se alternan presionando el botón central **BROWSE**, sobre una capa base que nunca se desmonta.
*   **Capa base** (`_mode0` en el código, activa en ambos modos): faders de volumen, crossfader, Arm/Solo/Mute/Select de las pistas 1‑4 (SLICER del deck izquierdo), transporte, tempo, LOAD A/B y botones inferiores.
*   **Modo 1:** Enfocado en el lanzamiento de clips (Session View), mezcla y loops.
*   **Modo 2:** Enfocado en tocar instrumentos virtuales (Finger Drumming) con el deck derecho como teclado cromático.
*   **Knobs de EQ del centro (HIGH/MID/LOW, CC 4/3/2 en canales 1 y 2):** `[100% LIBRES]` en todos los modos, reservados al mapeo manual del usuario. No asignarles nada desde el script.

---

## 2. Modo 1 (Modo por defecto)

### 2.1. Las 4 Páginas de Pads (¡IMPORTANTE!)
Dado que cada modo de pads envía distintas notas MIDI, el script las utiliza para diferentes funciones:

*   **Página SAMPLER:** `[Mapeada]` 
    *   **Función:** Lanzador de Clips (Clip Launcher).
    *   **Uso:** La cuadrícula funciona como una matriz de 7 pistas x 4 escenas para disparar clips de audio o MIDI.
*   **Página SLICER:** `[Mapeada]`
    *   **Función:** Mixer de Pistas.
    *   **Uso:** Sirve para Armar, Mutear, Solear y Seleccionar las pistas 1 a 7.
*   **Página LOOP:** `[Mapeada]`
    *   **Función:** Control Dinámico de Loops Nativos (Beatjump).
    *   **Uso:** Dispuesto en 8 columnas verticales (Pistas 1-4 Izq, Pistas 5-8 Der) para prender/apagar (Rojo), achicar/agrandar (Violeta) y mover el loop (Azul). Las columnas siguen el offset del banco; la 8ª columna controla la pista siguiente a las 7 visibles en la matriz.
*   **Página HOTCUE:** `[Sin función, capturada]`
    *   **Función:** Ninguna.
    *   **Uso:** El script captura sus notas (ver §2.4) para que ni los pads ni el selector de página disparen notas en una pista armada. No es mapeable manualmente en Modo 1.

### 2.2. Knobs FILTER (Macros) y Knobs de EQ (libres)
*   En el Modo 1, solo los dos knobs **FILTER** (CC 1 de cada deck) controlan macros del primer dispositivo de la pista seleccionada: el izquierdo el **Macro 4** y el derecho el **Macro 8** (se conservan las posiciones 4 y 8 de la tupla original de 8 controles; las otras seis son `None`).
*   Los 6 knobs **HIGH / MID / LOW** no están mapeados. Antes controlaban los macros 1‑3 y 5‑7; se liberaron el 2026‑09‑14 a pedido del usuario.

### 2.3. Faders y Knobs de Volumen
*   Los faders/knobs de volumen de las pistas 1 a 7 (4 en Deck Izq, 3 en Deck Der + 1 Master) se reasignan dinámicamente al desplazarse por las pistas o bancos (`MixerComponent` sincronizado con `SessionComponent`), siguiendo siempre las 7 pistas visibles en la matriz de pads.

### 2.4. Swallow global de notas (selectores de página y botones libres)
*   El script captura **todas** las notas de los 16 canales MIDI salvo las de una lista explícita de paso (`_passthrough_notes()` en `build_midi_map`). Así ningún botón físico (selectores HOTCUE / LOOP / SLICER / SAMPLER, ON, MACRO, SYNC, etc.) puede disparar notas en una pista armada, sin importar qué mensaje emita.
*   Notas que **sí** llegan a la pista armada:
    *   **Modo 1:** ninguna.
    *   **Modo 2:** las 4 páginas del deck derecho (notas 36‑99, canal 2). El deck izquierdo no pasa nada.
*   Los CC no se tocan (no disparan notas). Las capas SHIFT + pads (canales 3‑5) también se capturan salvo los 4 botones de navegación, que son elementos propios del script.
*   Selectores de página del deck derecho, medidos con `DEBUG_LOG_MIDI` (canal 2): HOTCUE = nota 11, LOOP = 12, SLICER = 13, SAMPLER = 14. El deck izquierdo usa las mismas notas en canal 1.
*   Notas 3‑6 del canal de cada deck = botones ON / ON / ON / MACRO bajo los knobs (Stop Clip por pista; MACRO derecho = Stop All). Nota 1 del deck izquierdo = presión del encoder LOOP/TEMPO (metrónomo). Un commit del 2026‑09‑14 los había eliminado creyendo que eran los selectores de página; están restaurados.
*   Valores de LED de los pads (medidos): 1 / 41 / 81 = rojo / azul / violeta tenue; 125 / 126 / 127 = rojo / azul / violeta a pleno. Los valores 40 y 80 **no** son brillo intermedio: el firmware los interpreta como una animación de expansión en violeta.
*   Para ver qué emite un botón físico: poner `DEBUG_LOG_MIDI = True` al tope de `hercules_p32_dj.py`, recargar el script y leer `Log.txt` (líneas `P32 MIDI in:`). Como casi todo se captura, casi todo aparece en el log.

---

## 3. Modo 2 (Secundario)

### 3.1. Las Páginas de Pads
*   **Deck Izquierdo (Clip Launcher Reducido):**
    *   Solo la página **SAMPLER** del deck izquierdo funciona como lanzador de clips (4 pistas x 4 escenas).
*   **Deck Derecho (Escala Cromática Continua de 64 Notas / Finger Drumming):**
    *   `[100% LIBRE]` En el Modo 2, los pads del deck derecho a través de sus 4 páginas forman una escala cromática continua ascendente de 64 notas:
        *   **Página SAMPLER:** Notas 36 a 51 (C1 a D#2). El pad inferior izquierdo es exactamente **C1** (Nota 36).
        *   **Página SLICER:** Notas 52 a 67 (E2 a G3).
        *   **Página LOOP:** Notas 68 a 83 (G#3 a B4).
        *   **Página HOTCUE:** Notas 84 a 99 (C5 a D#6).
    *   Ideal para tocar instrumentos cromáticos (pianos, sintetizadores) o recorrer las 4 páginas de un *Drum Rack* completo de 64 pads.
    *   **Luces (las 4 páginas):** patrón de piano. Teclas blancas en violeta, negras en azul y todas las C en rojo; al presionar, el pad sube de brillo y al soltar vuelve al color base. Constantes `KEYBOARD_LED_*` y `KEYBOARD_LED_PAGES`.
    *   **Cómo:** en `build_midi_map`, esas notas se forwardean con `Live.MidiMap.forward_midi_note(..., should_consume_event=False)`: la pista recibe la nota normalmente y el script recibe una copia que usa solo para las luces (`_reported_notes` en `receive_midi`).
    *   **"Light Show" del firmware (páginas HOTCUE y SAMPLER):** el P32 tiene una animación propia de expansión en violeta al presionar pads en esas dos páginas. No la genera el script ni se puede apagar por MIDI. Según las notas del firmware 1.47 de Hercules, se desactiva manteniendo **HOTCUE + SAMPLER a la vez durante más de 3 segundos**; es volátil y hay que repetirlo cada vez que se desconecta el controlador. Con el Light Show apagado, las cuatro páginas se ven iguales.

### 3.2. Knobs en Modo 2
*   Los 6 knobs **HIGH / MID / LOW**: `[100% LIBRES]` (ver §1). Hasta el 2026‑09‑14 el deck izquierdo controlaba los Envíos A/B/C de la pista seleccionada y el derecho el volumen de los Retornos A/B/C; `_mode2_devices()` y `_remove_mode2_devices()` quedaron vacíos a propósito.
*   Los dos knobs **FILTER**: `[100% LIBRES]` en Modo 2 (en Modo 1 son macros). El tempo se controla con el encoder LOOP/TEMPO (CC 10), que es parte de la capa base y no depende del modo.

---

## 4. Controles Globales (Botones Inferiores y Centrales)
*   **Botones Centrales (REC, SLIP):** Funciones estándar de grabar sesión y overdub.
*   **ON / ON / ON / MACRO (bajo los knobs):** Stop Clip de las pistas 1‑7 del banco visible (en Modo 2 solo las 4 del deck izquierdo); el MACRO derecho es Stop All Clips.
*   **Presión del encoder LOOP/TEMPO izquierdo:** Metrónomo on/off.
*   **Botones Inferiores Deck Derecho:**
    *   **PLAY:** Play (Iniciar transporte)
    *   **CUE:** Stop (Detener transporte)
    *   **SYNC:** Tap Tempo
    *   **SHIFT:** Modificador nativo
*   **Botones Inferiores Deck Izquierdo:**
    *   **PLAY:** Poner / Quitar Marcador (Locator)
    *   **CUE:** Deshacer (Undo)
    *   **SYNC:** Rehacer (Redo)
    *   **SHIFT:** Alternar Vista Session / Arrangement
*   **LOAD A / LOAD B:** Desplazamiento por las pistas (Izquierda / Derecha). Si la pista seleccionada supera el banco visible actual, el cuadrante de sesión, los pads y los faders de volumen se desplazan automáticamente para mantenerla a la vista.
*   **SHIFT + Pads (ambos modos):** Navegación de la cuadrícula (Bank Up/Down/Left/Right) con las notas 37/40/42/45 del canal 5 (0‑based). Al mover el banco horizontal, los pads, faders de volumen, mute/solo/arm y LEDs de selección se actualizan en sincronía. *A verificar en hardware:* el canal 4 es SHIFT + deck izquierdo (tempo fino), por lo que el canal 5 probablemente sea SHIFT + deck **derecho** y no el izquierdo como decía la documentación anterior.
*   **SHIFT izquierdo:** además de ser modificador de hardware, al presionarlo alterna Session/Arrangement. Cada uso de SHIFT como modificador (por ejemplo para el tempo fino) también cambia de vista. Pendiente de decisión (ver §5.5).

---

## 5. Tareas Pendientes / Problemas a Resolver

### 5.1. Fuga de notas MIDI al cambiar de página en los pads (SAMPLER / SLICER)
*   **Objetivo:** Al presionar los botones físicos de selección de página (**SAMPLER**, **SLICER**, **LOOP**, **HOTCUE**) en el controlador, Ableton no debe recibir ninguna señal ni disparar notas en las pistas armadas con instrumentos virtuales.
*   **Estado actual:** Con el swallow parcial anterior (notas 0‑35 en canales 0‑5) las páginas **SAMPLER** y **SLICER** seguían filtrando una nota. Un mensaje que el script fuerza a forwarding no puede llegar a la pista, así que ese mensaje estaba fuera del rango capturado.
*   **Resuelto (confirmado en hardware el 2026‑09‑14):** `build_midi_map` captura todas las notas de los 16 canales salvo las de `_passthrough_notes()` (ver §2.4). Con `DEBUG_LOG_MIDI` se vio que los selectores del deck derecho emiten **canal 2, notas 13 y 14** (SLICER/SAMPLER), dentro del rango capturado.
*   **Si sigue filtrando:** solo puede pasar en Modo 2 y el mensaje es una nota del deck derecho dentro de 36‑99 (en Modo 1 no pasa ninguna nota). Activar `DEBUG_LOG_MIDI`, presionar el selector y buscar en `Log.txt` qué (canal, nota) aparece; luego excluirla del rango de paso en `_passthrough_notes()`.

### 5.2. Escala cromática en páginas SLICER y LOOP del Deck Derecho (Modo 2)
*   **Objetivo:** En el **Modo 2**, las cuatro páginas del deck derecho deben permitir tocar una escala cromática continua ascendente de 64 notas (pad inferior izquierdo de Sampler en **C1 / Nota 36**):
    *   **SAMPLER:** Notas 36 a 51 (C1 a D#2).
    *   **SLICER:** Notas 52 a 67 (E2 a G3).
    *   **LOOP:** Notas 68 a 83 (G#3 a B4).
    *   **HOTCUE:** Notas 84 a 99 (C5 a D#6).
*   **Estado anterior:** Las páginas **SAMPLER** y **HOTCUE** respondían, pero en **SLICER** y **LOOP** no sonaba ninguna nota en Modo 2.
*   **Contexto técnico para Claude / desarrollador:**
    *   En el **Modo 1**, las notas 52 a 67 son usadas por el mezclador (`arm_specific_*`, `solo_specific_*`, `mute_specific_*`, `trackselect*`) y las notas 68 a 83 por el control de loops (`_setup_loop_controls`).
    *   **Resuelto (confirmado en hardware el 2026‑09‑14).** Causa real, leída del bytecode de `_Framework` de Live 12: `InputControlElement.script_wants_forwarding()` solo pide forwarding si el elemento tiene listeners y no está suprimido, pero `ConfigurableButtonElement` lo pisaba y devolvía verdadero siempre. Así, los botones del Modo 1 desconectados seguían capturando sus notas (y, al presionarlos, reventaban con `begin_undo_step` porque `disconnect()` deja `_undo_step_handler = None`). Se eliminó el override. Las dos causas de abajo también se corrigieron y quedan como defensa adicional.
    *   **Causa 1 (corregida):** en `_remove_mode1()` se llamaba a `btn.set_enabled(False)` (que pone `suppress_script_forwarding = True`, es decir "esta nota pasa a la pista") e inmediatamente después se volvía a poner `btn.suppress_script_forwarding = False`, deshaciendo el efecto. Se eliminó esa línea.
    *   **Causa 2 (corregida):** en `_Framework`, `disconnect()` no quita el elemento de `ControlSurface._controls`. En cada `build_midi_map` la superficie vuelve a instalar forwarding para todo elemento registrado cuyo `script_wants_forwarding()` sea verdadero, incluidos los pads y botones del Modo 1 que quedaron huérfanos al pasar al Modo 2. Ahora `build_midi_map` recorre `self._controls` antes de llamar a `super()` y a todo elemento de nota cuya (canal, nota) esté en `_passthrough_notes()` le fuerza `suppress_script_forwarding = True` y `script_wants_forwarding = lambda: False`, de modo que no se instale forwarding para esas notas.
    *   *Verificación:* en Modo 2, con una pista MIDI armada, las 4 páginas del deck derecho deben tocar las notas 36‑99 en orden ascendente (SAMPLER 36, SLICER 52, LOOP 68, HOTCUE 84). Si alguna página sigue muda, activar `DEBUG_LOG_MIDI`: si sus notas aparecen en `Log.txt`, algún elemento sigue capturándolas y hay que revisar `_note_elements()`.
    *   *Solución de fondo (refactor mayor, §5.3):* crear cada elemento una sola vez en `__init__` y cambiar de modo reasignándolos a los componentes y alternando `set_enabled`, seguido de `request_rebuild_midi_map()`. `set_pad_translations` no aplica porque Live solo lo usa para remapear notas hacia Drum Racks, no para liberar forwarding.

### 5.3. Fuga de elementos en cada recarga de dispositivos
*   **Problema:** `_reload_active_devices()` se dispara en cada cambio de pista seleccionada, de dispositivo seleccionado y en cada pulsación (con 127 y con 0) de los 4 botones de navegación de banco. Cada vez crea un `DeviceComponent` + 8 `EncoderElement` (Modo 1) o 6 `CappedEncoderElement` (Modo 2) nuevos. Los viejos nunca se desmontan: quedan registrados en la superficie y se acumulan durante toda la sesión.
*   **Solución:** crear el `DeviceComponent` y sus encoders una sola vez al entrar al Modo 1 y en la recarga llamar solo a `set_device(devices[0])`. En Modo 2 asignar sends/returns una sola vez: `MixerComponent.selected_strip()` ya sigue la pista seleccionada. Filtrar `value > 0` en los listeners de los botones de navegación.

### 5.4. Simplificaciones pendientes (sin cambio funcional)
*   Código muerto heredado de Remotify: `_activate_mode0`, `_activate_shift_mode0/1/2`, `_is_prev_device_on_or_off`, `_is_nxt_device_on_or_off`, `selected_device_idx`, los globales `shift_previous_is_active` / `previous_shift_mode*`, las ramas `hasattr(self, '_turn_on_device_select_leds' / '_all_prev_device_leds' / '_all_nxt_device_leds' / 'update_all_ab_select_LEDs' / '_mode0_devices')`, `self._display_reset_delay`, y las listas `session_types` / `session_is_momentary` (todos sus valores son iguales).
*   `track_select_1..7`, `_set_track_select_led` y `_turn_off_track_select_leds` son 7 copias del mismo bloque; `arm/solo/mute_specific_N` se arman y desarman a mano. Reemplazar por listas indexadas.
*   Canales, notas y valores de LED (1, 10, 30, 40, 41, 80, 81, 125, 126, 127) son números mágicos: mover a constantes con nombre.
*   `tempo_control_updown_mode0` / `tempo_fine_control_updown_mode0`: la lógica de dirección pierde el primer clic tras cargar (`lv == 0`) y usa límites distintos (20 vs 22). Con `relative_smooth_two_compliment`, `value < 64` sube y `value > 64` baja. Confirmar en hardware qué envía el encoder antes de simplificar.
*   `ConfigurableButtonElement.py` usa tabs y el resto espacios; unificar a 4 espacios. Reemplazar los headers de uncompyle6 por un docstring.
*   Se usa API privada de `_Framework` (`_session._track_offset`, `_scene_offset`, `_reassign_scenes`, `_enable_skinning`, `_link` / `_unlink`, `selected_strip()._track`). Preferir `track_offset()` / `scene_offset()` públicos donde existan.

### 5.5. SHIFT izquierdo: modificador y toggle de vista a la vez
*   `left_shift_btn` (ch1 nota 7) dispara `_do_toggle_session_view` al presionarse, pero SHIFT es también el modificador de hardware de la capa ch4 (tempo fino). Cada vez que se usa SHIFT como modificador se cambia de vista.
*   Opciones: mover el toggle de vista a otro botón libre, o dispararlo en el release solo si no llegó ningún mensaje de la capa shift entre la pulsación y el release.

### 5.6. Checklist de prueba en hardware tras cada cambio
1.  Cambiar a Modo 2 y tocar SLICER y LOOP del deck derecho con una pista MIDI armada: deben sonar las notas 52‑83.
2.  Con una pista armada, presionar cada selector de página (HOTCUE, LOOP, SLICER, SAMPLER) en ambos decks: no debe sonar nada.
3.  En Modo 1, página LOOP, fila 4: el cabezal del clip debe saltar hacia adelante junto con el loop.
4.  Agregar una pista con el Modo 1 activo y cambiar a Modo 2 y volver: sin `RemoteScriptError` en `Log.txt`.
5.  Seleccionar un return o el master y presionar LOAD A / LOAD B: no debe pasar nada.
6.  Cambiar la superficie de control a None y volver a Hercules P32 DJ: sin errores en `Log.txt`.

