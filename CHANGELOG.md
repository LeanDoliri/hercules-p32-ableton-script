# Resumen de Modificaciones: Hercules P32 DJ

Este documento detalla todas las modificaciones realizadas sobre el script base (generado con Remotify) del Hercules P32 DJ. No es un changelog versionado: el historial exacto está en `git log`.

## 1. Topes Absolutos en Encoders (Volumen y Envíos/Retornos)
Se implementó una nueva clase personalizada llamada `CappedEncoderElement` que hereda del elemento nativo de codificador de Ableton.
*   **¿Qué hace?** Escucha todos los mensajes entrantes de las perillas rotativas de la consola y matemáticamente corta cualquier valor superior a `0.85` de la escala MIDI (lo cual equivale exactamente a **0 dB** en la interfaz de Ableton Live).
*   **¿A qué afecta?**
    *   Capa base (`_mode0` en el código, siempre activa): Perillas de volumen general de todas las pistas.
    *   (Hasta el 2026‑09‑14 también a los envíos A/B/C y a los retornos A/B/C en Modo 2; esos mapeos se quitaron, ver sección 5.)
*   **Beneficio:** Permite al DJ girar las perillas físicas rápidamente hasta el tope físico sabiendo que la señal de audio nunca superará el umbral de los 0 dB.

## 2. Botones de Transporte Personalizados
Para aprovechar al máximo el espacio físico y no desperdiciar los pads de las páginas libres, se reprogramaron los botones de transporte inferiores que estaban desconectados.

*   **Deck Derecho:**
    *   `PLAY`: Inicia la reproducción general del set.
    *   `CUE`: Detiene el transporte (Stop).
    *   `SYNC`: Establece el tempo global en vivo (Tap Tempo).
    *   `SHIFT`: Actúa como modificador nativo (ej. para navegar la grilla).
*   **Deck Izquierdo:**
    *   `PLAY`: Coloca o borra un marcador (Locator) en la posición actual para saltar rápidamente en la vista Arrangement.
    *   `CUE`: Función global de Deshacer (Undo).
    *   `SYNC`: Función global de Rehacer (Redo).
    *   `SHIFT`: Alterna rápidamente entre la vista de Sesión y la vista Arrangement de Ableton (Atajo "Tab").

## 3. Control Dinámico de Loops Nativos (Beatjump)
En el **Modo 1**, la página **LOOP** fue programada desde cero para controlar los bucles de los clips de audio/MIDI.
*   **Disposición:** Funciona en columnas verticales. Deck Izquierdo controla Pistas 1 a 4; Deck Derecho controla Pistas 5 a 8.
*   **Fila 1 (Loop Toggle):** Enciende o apaga el loop del clip.
*   **Fila 2 (Halve):** Divide el tamaño del loop a la mitad.
*   **Fila 3 (Double):** Multiplica el tamaño del loop al doble.
*   **Fila 4 (Beatjump Adelante):** Salta hacia adelante una distancia equivalente al tamaño del loop.

## 4. Reasignación Dinámica de Faders de Volumen y Mezclador (Banking & Auto-Scroll)
Se rediseñó la interacción entre `SessionComponent` y `MixerComponent` para que los controles de mezcla sigan al cuadrante de sesión.
*   **¿Qué hace?** Los 7 faders de volumen físico (4 Deck Izq, 3 Deck Der) y los botones de Arm/Solo/Mute de la página SLICER se reasignan en tiempo real al desplazarse horizontalmente por el proyecto (mediante *SHIFT + Pads de Banco*).
*   **Auto-Scroll en Navegación (`LOAD A / LOAD B`):** Al cambiar de pista seleccionada con los botones `LOAD`, si la pista elegida queda fuera del banco visible actual de 7 pistas, el cuadrante de sesión y los faders se desplazan automáticamente para mantenerla visible y bajo control.
*   **Sincronización con Página LOOP:** Las acciones de Loop y Beatjump (`_get_playing_clip`) ahora respetan el offset de pistas activo.

> [!NOTE]
> Las luces LED de estos controles funcionan mediante la lógica nativa del script original cuando detectan señales entrantes válidas. Las páginas "HOTCUE" no tienen asignaciones nativas, pero desde el swallow global (sección 5) sus notas tampoco llegan a las pistas en Modo 1; la única página libre es el deck derecho en Modo 2.

## 5. Correcciones de Robustez (septiembre 2026)
*   **Selectores HOTCUE y LOOP ya no disparan Tap Tempo ni Redo:** SYNC estaba mapeado a las notas 8, 11 y 12 de cada deck, pero 11 y 12 son los selectores de página HOTCUE y LOOP. Queda solo la nota 8 (SYNC real).
*   **Luces de navegación con SHIFT derecho:** al mantener SHIFT derecho, los 4 pads de navegación (cruz en la página SAMPLER del deck derecho) se encienden en azul tenue y suben a azul pleno al presionarlos; al soltar SHIFT vuelven a mostrar el estado de los clips (Modo 1) o el teclado (Modo 2).
*   **Knobs de EQ libres:** los 6 knobs HIGH/MID/LOW del centro ya no se mapean en ningún modo (antes: macros 1‑3 y 5‑7 en Modo 1; envíos A/B/C y retornos A/B/C en Modo 2). Quedan para mapeo manual con Ctrl+M. Los dos FILTER siguen como macros 4 y 8 en Modo 1.
*   **Stop Clip, Stop All y metrónomo restaurados:** un commit del 2026‑09‑14 los había eliminado creyendo que las notas 3‑6 (ON/ON/ON/MACRO) y la nota 1 (encoder LOOP/TEMPO izquierdo) eran los selectores de página. Los selectores reales son las notas 11‑14. Vuelven a funcionar como en la versión de agosto: 7 Stop Clip en Modo 1, 4 en Modo 2, MACRO derecho = Stop All, encoder izquierdo = metrónomo.
*   **Diagnóstico ampliado con `DEBUG_LOG_MIDI`:** además de la entrada y salida MIDI, se vuelca el mapa de CC tras cada `build_midi_map` y cada `CappedEncoderElement` loguea a qué parámetro se conecta y qué valor escribe.
*   **Swallow global de notas:** el script ahora captura todas las notas de los 16 canales salvo las que deben llegar a la pista armada (solo las 4 páginas del deck derecho en Modo 2; en Modo 1 no pasa ninguna). Reemplaza al bucle de 200 botones con listener vacío y cubre los selectores de página SAMPLER/SLICER emitan lo que emitan. Nuevo flag `DEBUG_LOG_MIDI` para loguear lo que llega.
*   **Luces del teclado en Modo 2:** las 4 páginas del deck derecho se iluminan como piano (blancas violeta, negras azul, C rojo) y el pad sube de brillo mientras está presionado. Se logra con forwarding no exclusivo (`should_consume_event=False`): la pista recibe la nota y el script solo una copia para la luz. La animación violeta de expansión en HOTCUE/SAMPLER es el "Light Show" del firmware del P32 y se apaga en el hardware (HOTCUE + SAMPLER más de 3 s, volátil).
*   **`ConfigurableButtonElement` ya no pisa `script_wants_forwarding()`:** la versión base de `_Framework` solo forwardea botones con listeners; el override forwardeaba también botones desconectados, que capturaban notas ajenas y lanzaban `begin_undo_step` al presionarlos. Confirmado en hardware el 2026‑09‑14.
*   **Modo 2, deck derecho (escala cromática 36‑99):** dos causas corregidas. Al salir del Modo 1 se dejaba de nuevo en `False` el flag `suppress_script_forwarding` justo después de deshabilitar los botones de SLICER/LOOP. Además, los pads y botones del Modo 1 quedaban registrados en la superficie y volvían a capturar sus notas en cada reconstrucción del mapa MIDI; ahora `build_midi_map` les apaga el forwarding cuando la nota debe pasar a la pista. Confirmado en hardware el 2026‑09‑14.
*   **Beatjump (LOOP fila 4):** se asignaba `clip.playing_position`, que es de solo lectura, y el error se silenciaba. Ahora usa `clip.move_playing_pos()`.
*   **Loop x2:** se limita `loop_end` al final del clip en clips de audio.
*   **Cambio de modo tras agregar pistas:** los listeners de dispositivo se agregan y quitan solo si corresponde (`selected_device_has_listener`), evitando un `RuntimeError` que abortaba el cambio de modo.
*   **Desconexión de la superficie:** `disconnect()` ahora desmonta el modo activo, la capa base y los listeners crudos de Live.
*   **LOAD B con un return o el master seleccionado:** ya no salta a la pista 2.
*   Los callbacks que llegan desde listeners de Live corren dentro de `component_guard()`.
*   Ver `CLAUDE.md` y `DOCUMENTATION_ARCHITECTURE.md` §5 para lo que sigue pendiente.
