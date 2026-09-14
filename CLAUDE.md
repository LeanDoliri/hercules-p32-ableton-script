# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es este repo

MIDI Remote Script para el controlador **Hercules P32 DJ** en Ableton Live. Usa el framework legacy `_Framework` de Live (no `ableton.v2`). El código nació de un mapeo generado con Remotify para Live 9 (`docs/Remotify_Source/hercules_p32_dj.json`), fue decompilado con uncompyle6 y desde entonces se edita a mano. Toda la documentación y los comentarios van en español; los mensajes de commit siguen en inglés con prefijo `feat:` / `fix:` / `docs:`.

Código: `src/Hercules_P32_DJ/` (tres archivos). Docs: `README.md` (instalación), `DOCUMENTATION.md` (manual de usuario), `DOCUMENTATION_ARCHITECTURE.md` (fuente de verdad de mapeos y pendientes), `CHANGELOG.md` (resumen de modificaciones, sin versiones).

## Comandos y flujo de trabajo

No hay build, tests ni lint. Los módulos `Live` y `_Framework` solo existen dentro de Ableton, así que el script no se puede importar ni ejecutar fuera de Live.

Lo único verificable desde la terminal es la sintaxis (mantener compatible con Python 2.7 y 3.x, porque Live 9/10 usan 2.7 y Live 11+ usa 3.x):

```bash
python -m py_compile src/Hercules_P32_DJ/hercules_p32_dj.py src/Hercules_P32_DJ/ConfigurableButtonElement.py src/Hercules_P32_DJ/__init__.py
```

Instalar para probar (Windows, ajustar la versión de Live):

```powershell
Copy-Item -Recurse -Force src\Hercules_P32_DJ "$env:ProgramData\Ableton\Live 12 Suite\Resources\MIDI Remote Scripts\Hercules_P32_DJ"
```

En Mac la carpeta es `Ableton Live x.app/Contents/App-Resources/MIDI Remote Scripts/`. **Después de copiar hay que cerrar y volver a abrir Live**: reseleccionar la superficie de control en Preferencias crea una instancia nueva pero reutiliza el módulo Python ya importado, así que los cambios en el `.py` no se ven (comprobado en Live 12.2). Borrar el `__pycache__` de la carpeta instalada al copiar.

Live 12 corre Python 3.11 y `_Framework` viene solo como `.pyc`. Para leer su código real: `pip install --target <dir> xdis` y `python -m xdis.bin.pydisasm <archivo>.pyc`. Hechos verificados así, en los que se apoya el script:
- `ControlSurface.build_midi_map` recorre `self.controls` (sin guión bajo) y llama a `install_connections` de cada elemento; nunca desregistra elementos.
- `_install_forwarding` escribe `self._forwarding_registry[(status, nota)] = control`: el último registrado gana, sin assert.
- `InputControlElement.script_wants_forwarding()` es `(not suppress_script_forwarding and _input_signal_listener_count > 0) or _report_input`: un elemento **sin listeners no se forwardea**. `ConfigurableButtonElement` no debe pisar ese método.
- `ButtonElement.disconnect()` deja `_undo_step_handler = None`; si ese botón vuelve a recibir MIDI revienta en `receive_value` con `'NoneType' object has no attribute 'begin_undo_step'`.
- `Live.MidiMap.forward_midi_note(handle, midi_map_handle, canal, nota, should_consume_event)`: el quinto argumento es opcional. Con `False` la nota llega a la pista **y** el script recibe una copia en `receive_midi` (lo usa `ableton.v2` para `ScriptForwarding.non_consuming`). Es la única forma de tener feedback de luz sin quitarle la nota a la pista.

Depurar: `self.log_message(...)` escribe en el log de Live y `self.show_message(...)` en la barra de estado. El log está en `%AppData%\Ableton\Live x.x\Preferences\Log.txt` (Windows) o `~/Library/Preferences/Ableton/Live x.x/Log.txt` (Mac). Los errores de Python aparecen como `RemoteScriptError`. Para ver qué mensaje MIDI emite un control físico, usar el modo de mapeo de Live (Ctrl+M) y mirar la barra de estado.

## Arquitectura

`__init__.py` expone `create_instance`, que instancia `hercules_p32_dj(ControlSurface)` en `hercules_p32_dj.py`. `ConfigurableButtonElement.py` es el botón con valores on/off configurables tomado del script de Push.

### Tres capas de mapeo

- `_mode0()` es la **capa base, siempre activa**: se llama una vez en `__init__` y nunca se desmonta. Contiene faders de volumen, crossfader, arm/solo/mute/select de las pistas 1‑4 (página SLICER del deck izquierdo), transporte, tempo, LOAD A/B y los botones de utilidad inferiores.
- `_mode1()` (clip launcher 7×4, macros, página LOOP, mixer del deck derecho) y `_mode2()` (clip launcher 4×4 en el deck izquierdo, sends/returns, deck derecho libre) **se alternan** con el encoder BROWSE (ch0 nota 1).
- Cada modo tiene su par `_modeN()` / `_remove_modeN()`. `_set_active_mode()` y `_remove_active_mode()` despachan según el global `active_mode`. Los `_activate_mode0` y `_activate_shift_mode*` son restos de Remotify sin uso.

### Componentes compartidos

Hay un único `MixerComponent(7, 24)` creado en `__init__`. Cada modo crea su propio `SessionComponent` (7×4 o 4×4), lo enlaza con `set_mixer(self.mixer)` y registra `_on_session_offset_changed`, que propaga el offset de pistas al mixer. Así los faders, arm/solo/mute y LEDs de selección siguen al banco visible de la matriz. Los offsets sobreviven al cambio de modo vía `current_track_offset` / `current_scene_offset`.

### Mapa MIDI (canales 0‑based en el código)

| Canal | Uso |
|-------|-----|
| 0 | Global: BROWSE (nota 1), REC (2), SLIP (3), crossfader (CC 1) |
| 1 | Deck izquierdo (A) |
| 2 | Deck derecho (B) |
| 4 | SHIFT + deck A (tempo fino, CC 10) |
| 5 | SHIFT + pads: navegación de banco (notas 37/40/42/45) |

Pads por página (ambos decks): SAMPLER 36‑51, SLICER 52‑67, LOOP 68‑83, HOTCUE 84‑99. La fila superior son las notas más altas. Knobs EQ: CC 4/3/2/1 = High/Mid/Low/Filter; faders CC 6‑9; tempo = encoder relativo CC 10 en ch1. El JSON de Remotify usa canales 1‑based (restar 1 para pasar al código).

### Reglas del framework que hay que respetar

- Todo lo que el script **no** fuerza a forwarding llega a la pista MIDI armada. El script invierte esa regla en su override de `build_midi_map`: captura todas las notas de los 16 canales salvo las de `_passthrough_notes()`, que hoy es una sola excepción: en Modo 2, el deck derecho completo (notas 36‑99 en ch2). En Modo 1 no pasa ninguna nota, HOTCUE incluido; los selectores de página nunca deben llegar a una pista. Para liberar o capturar una nota se edita esa función, no se crean botones con listener vacío. Los selectores de página son las notas 11‑14 (HOTCUE, LOOP, SLICER, SAMPLER) en el canal del deck; las notas 3‑6 son los botones ON/ON/ON/MACRO bajo los knobs (Stop Clip / Stop All) y la nota 1 del deck izquierdo es el metrónomo. Un commit anterior los confundió y los eliminó; están restaurados.
- `ConfigurableButtonElement.set_enabled(False)` pone `suppress_script_forwarding = True`, lo que hace que esa nota pase a la pista en el próximo `build_midi_map`. No pisar ese flag después.
- Los elementos y componentes deben crearse dentro de `with self.component_guard():` (así se registran en la superficie). Los callbacks de `receive_midi` ya corren dentro del guard; los listeners crudos de Live (`add_selected_device_listener`) no. El guard es reentrante.
- `disconnect()` de un elemento **no** lo desregistra de la superficie: sigue en `self._controls` y `build_midi_map` le vuelve a instalar forwarding si `script_wants_forwarding()` es verdadero. Por eso `build_midi_map` apaga el forwarding de todo elemento huérfano cuya nota deba pasar a la pista antes de llamar a `super()`. Llamar `request_rebuild_midi_map()` después de cambiar mapeos.
- Para ver qué emite un control físico: `DEBUG_LOG_MIDI = True` al tope de `hercules_p32_dj.py` y leer las líneas `P32 MIDI in:` en `Log.txt`.
- `CappedEncoderElement` reemplaza el mapeo nativo por un listener que escribe `parameter.value = v/127*0.85` (0.85 = 0 dB en volumen, sends y returns).
- Se usa bastante API privada de `_Framework` (`_session._track_offset`, `_reassign_scenes`, `_enable_skinning`, `_link`, `selected_strip()._track`). Puede romper entre versiones de Live.

## Pendientes conocidos

Detalle y diagnóstico propuesto en `DOCUMENTATION_ARCHITECTURE.md` §5. Resumen:

1. **Fuga de nota al presionar SAMPLER/SLICER** (5.1): resuelto y confirmado en hardware el 2026‑09‑14 con el swallow global de `build_midi_map`. Los selectores del deck derecho emiten canal 2, notas 13 y 14.
2. **SLICER y LOOP del deck derecho mudos en Modo 2** (5.2): resuelto y confirmado en hardware. La causa real era el override de `script_wants_forwarding` en `ConfigurableButtonElement`, que forwardeaba botones sin listeners y desconectados. Solución de fondo pendiente: crear cada elemento una sola vez en `__init__` y alternar `set_enabled` por modo.
3. **Luces en Modo 2**: resuelto. Las 4 páginas del deck derecho usan patrón de piano con brillo al presionar (`_keyboard_led_value`, constantes `KEYBOARD_LED_*`). Se apoya en `forward_midi_note(..., should_consume_event=False)`. La animación de expansión violeta en HOTCUE/SAMPLER es el "Light Show" del firmware del P32, no del script: se apaga en el hardware con HOTCUE + SAMPLER 3 s (volátil).
4. **Fuga de elementos**: `_reload_active_devices` crea un `DeviceComponent` + encoders nuevos en cada cambio de pista/device/banco y nunca desmonta los viejos.
5. **SHIFT izquierdo** es modificador de hardware y a la vez alterna Session/Arrangement al presionarlo.

Al cambiar cualquier mapeo, actualizar `DOCUMENTATION_ARCHITECTURE.md` en el mismo commit.
