# Estado de Arquitectura y Mapeos del Hercules P32 DJ

> [!NOTE]
> Este documento sirve como "fuente de la verdad" para consolidar exactamente qué hace cada control en el script actual y evitar confusiones sobre qué páginas están libres o mapeadas.

## 1. Modos Principales
El script opera en dos modos principales que se alternan presionando el botón central **BROWSE**.
*   **Modo 1:** Enfocado en el lanzamiento de clips (Session View), mezcla y loops.
*   **Modo 2:** Enfocado en tocar instrumentos virtuales (Finger Drumming) y control de Envíos/Retornos.

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
    *   **Uso:** Dispuesto en 8 columnas verticales (Pistas 1-4 Izq, Pistas 5-8 Der) para prender/apagar (Rojo), achicar/agrandar (Violeta) y mover el loop (Azul).
*   **Página HOTCUE:** `[100% LIBRE]`
    *   **Función:** Ninguna.
    *   **Uso:** Actualmente los pads de la página HOTCUE en el Modo 1 no son interceptados por el script.

### 2.2. Knobs Superiores (Macros)
*   En el Modo 1, los 8 knobs superiores (High, Mid, Low, Filter de ambos decks) controlan los **8 Macros** del dispositivo (Instrumento o Rack de Efectos) de la pista que esté seleccionada.

### 2.3. Faders y Knobs de Volumen
*   Los faders/knobs de volumen de las pistas 1 a 7 (4 en Deck Izq, 3 en Deck Der + 1 Master) se reasignan dinámicamente al desplazarse por las pistas o bancos (`MixerComponent` sincronizado con `SessionComponent`), siguiendo siempre las 7 pistas visibles en la matriz de pads.

### 2.4. Botones Selectores de Página de Pads (HOTCUE, LOOP, SLICER, SAMPLER)
*   Los 4 botones físicos superiores de cambio de página en ambos decks son interceptados y absorbidos de forma silenciosa por el script. No disparan comandos en Ableton (como stop de clips o metrónomo) ni envían notas MIDI crudas a las pistas armadas.

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

### 3.2. Knobs Superiores (Envíos y Retornos)
*   **Deck Izquierdo (Envíos de la Pista Seleccionada):**
    *   `Knob High`: Nivel del Envío A (Send A).
    *   `Knob Mid`: Nivel del Envío B (Send B).
    *   `Knob Low`: Nivel del Envío C (Send C).
    *   `Knob Filter`: *(Control de Tempo Global)*.
*   **Deck Derecho (Volumen Maestro de Retornos):**
    *   `Knob High`: Volumen del Canal de Retorno A.
    *   `Knob Mid`: Volumen del Canal de Retorno B.
    *   `Knob Low`: Volumen del Canal de Retorno C.
    *   `Knob Filter`: `[100% LIBRE]` (Sin mapear).

---

## 4. Controles Globales (Botones Inferiores y Centrales)
*   **Botones Centrales (REC, SLIP):** Funciones estándar de grabar sesión y overdub.
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
*   **SHIFT + Pads Izq (Modo 1):** Navegación de la cuadrícula (Bank Up/Down/Left/Right). Al mover el banco horizontal, los pads, faders de volumen, mute/solo/arm y LEDs de selección se actualizan en sincronía.

---

## 5. Tareas Pendientes / Problemas a Resolver

### 5.1. Fuga de notas MIDI al cambiar de página en los pads (SAMPLER / SLICER)
*   **Objetivo:** Al presionar los botones físicos de selección de página (**SAMPLER**, **SLICER**, **LOOP**, **HOTCUE**) en el controlador, Ableton no debe recibir ninguna señal ni disparar notas en las pistas armadas con instrumentos virtuales.
*   **Estado actual:** Al cambiar de página usando **SAMPLER** y **SLICER**, se continúa filtrando una nota MIDI que dispara sonidos en el instrumento seleccionado.
*   **Contexto técnico para Claude / desarrollador:**
    *   Se intentó capturar notas 0-35 en los canales 0 al 5 instanciando `ConfigurableButtonElement` con callbacks vacíos en `__init__`.
    *   Sin embargo, los botones físicos de Sampler y Slicer continúan filtrando eventos de Note On hacia la pista armada.
    *   *Acción recomendada:* Identificar el mensaje exacto (Canal MIDI, Note vs CC, y número) que emiten físicamente esos dos botones usando `Ctrl + M` en Ableton o un monitor MIDI, para interceptarlos de forma precisa o evaluar si la controladora envía un mensaje especial (SysEx / CC secundario).

### 5.2. Escala cromática en páginas SLICER y LOOP del Deck Derecho (Modo 2)
*   **Objetivo:** En el **Modo 2**, las cuatro páginas del deck derecho deben permitir tocar una escala cromática continua ascendente de 64 notas (pad inferior izquierdo de Sampler en **C1 / Nota 36**):
    *   **SAMPLER:** Notas 36 a 51 (C1 a D#2).
    *   **SLICER:** Notas 52 a 67 (E2 a G3).
    *   **LOOP:** Notas 68 a 83 (G#3 a B4).
    *   **HOTCUE:** Notas 84 a 99 (C5 a D#6).
*   **Estado actual:** Las páginas **SAMPLER** y **HOTCUE** responden, pero en **SLICER** y **LOOP** no suena ninguna nota en Modo 2.
*   **Contexto técnico para Claude / desarrollador:**
    *   En el **Modo 1**, las notas 52 a 67 son usadas por el mezclador (`arm_specific_*`, `solo_specific_*`, `mute_specific_*`, `trackselect*`) y las notas 68 a 83 por el control de loops (`_setup_loop_controls`).
    *   Al pasar al Modo 2 vía `_remove_mode1()`, los elementos de botón se desconectan (`disconnect()`), pero el framework interno de Ableton (`_Framework.InputControlElement` / C++ core) parece seguir reteniendo (`suppress_script_forwarding = True`) esas notas o manteniéndolas interceptadas en la tabla de mapeo de la superficie de control, impidiendo que el motor de audio las dirija a la pista MIDI armada.
    *   *Acción recomendada:* Considerar no instanciar `ConfigurableButtonElement` fijos para esas notas en Modo 1, o implementar un ruteo explícito mediante `set_pad_translations` de la API nativa de Ableton Live para el Modo 2.

