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

---

## 3. Modo 2 (Secundario)

### 3.1. Las Páginas de Pads
*   **Deck Izquierdo (Clip Launcher Reducido):**
    *   Solo la página **SAMPLER** del deck izquierdo funciona como lanzador de clips (4 pistas x 4 escenas).
*   **Deck Derecho (Finger Drumming Puro):**
    *   `[100% LIBRE]` Absolutamente TODOS los pads del deck derecho (en las páginas Sampler, Slicer, Loop y Hotcue) están desvinculados de Ableton. Sus luces se apagan y solo envían notas MIDI crudas, ideales para tocar un *Drum Rack*.

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
*   **LOAD A / LOAD B:** Desplazamiento por las pistas (Izquierda / Derecha).
*   **SHIFT + Pads Izq (Modo 1):** Navegación de la cuadrícula (Bank Up/Down/Left/Right).
