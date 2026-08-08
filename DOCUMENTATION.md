# Manual de Referencia: Hercules P32 DJ - Ableton Live Script

Este documento detalla todas las funcionalidades implementadas en el script remoto para el controlador **Hercules P32 DJ** en Ableton Live. El script organiza el controlador en diferentes modos y secciones para ofrecer control sobre el transporte, la mezcla, los dispositivos y el lanzamiento de clips.

## 1. Controles Globales y de Transporte
Estos controles están disponibles en todo momento, independientemente del modo activo:

*   **Cambio de Modo (BROWSE)**: Al presionar el encoder **BROWSE** (centro superior), el controlador alterna entre el **Modo 1 (Clip Launcher)** y el **Modo 2 (Finger Drumming)**.
*   **Tempo y Metrónomo**:
    *   **Giro del Encoder Izquierdo (Filter/Low)**: Modifica el tempo del proyecto (Tempo general).
    *   **SHIFT + Giro del Encoder Izquierdo**: Ajuste fino del tempo (décimas de BPM).
    *   **Presionar Encoder Izquierdo**: Activa o desactiva el Metrónomo.
*   **Navegación de Pistas (LOAD)**: Los botones **A** y **B** (LOAD) permiten desplazarse hacia la pista izquierda o derecha respectivamente.
*   **Transporte Básico**:
    *   **PLAY (▶)**: Inicia la reproducción (Ubicado en la esquina inferior derecha).
    *   **CUE**: Detiene la reproducción (Stop) (Ubicado junto al botón Play).
    *   **REC**: Activa el modo de grabación general de Live (Record).
    *   **SLIP**: Activa la sobregrabación MIDI (Overdub).

---

## 2. Modo 1: Clip Launcher (Modo por Defecto)
Al iniciar Ableton, el controlador entra en el Modo 1. Este modo está diseñado para el lanzamiento masivo de clips y el control de efectos/macros.

### Matriz de Clips (7x4)
La cuadrícula de pads de ambos decks funciona unificada como una matriz de lanzamiento de 7 pistas por 4 escenas (utilizando 28 pads en total). Los pads se iluminan para reflejar el estado del clip:
*   **Morado**: El slot contiene un clip.
*   **Azul**: El clip se está reproduciendo.
*   **Rojo tenue**: El slot está listo para grabar.
*   **Rojo brillante**: El clip se está grabando.

### Funciones de Mezcla (Pads en Modo SLICER)
Al activar el modo **SLICER** en los pads del controlador, la cuadrícula de 7x4 cambia su función para controlar los parámetros de mezcla de las 7 pistas:
*   **Fila 1 (Superior)**: Seleccionar pista (el pad se ilumina brillante en la pista activa).
*   **Fila 2**: Activador de Pista (Mute / Unmute).
*   **Fila 3**: Activar Solo en la pista.
*   **Fila 4 (Inferior)**: Armar pista para grabación.

### Control de Loops Nativos y Beatjump (Pads en Modo LOOP)
Al activar el modo **LOOP** en los pads del controlador, ambos decks asumen el control en tiempo real de los bucles (loops) de las 8 pistas (Pistas 1-4 en el deck izquierdo, Pistas 5-8 en el deck derecho). Cada columna vertical de 4 pads controla una pista específica.

Funciones de los 4 pads por columna (de arriba hacia abajo):
*   **Fila 1 (Pad Superior - Rojo)**: Activar/Desactivar el Loop del clip que está sonando en esa pista.
*   **Fila 2 (Pad Medio-Superior - Violeta)**: Divide el tamaño del loop a la mitad (/2).
*   **Fila 3 (Pad Medio-Inferior - Violeta)**: Multiplica el tamaño del loop al doble (x2).
*   **Fila 4 (Pad Inferior - Azul)**: Beatjump hacia adelante (mueve el loop y el cabezal de reproducción saltando una cantidad equivalente al tamaño actual del loop).

### Control de Dispositivos (Macros)
Los knobs de la parte superior están vinculados a los controles del dispositivo (Device) de la pista seleccionada:
*   Los 8 knobs correspondientes a **High, Mid, Low y Filter** (4 en el deck izquierdo y 4 en el derecho) controlan automáticamente los **8 Macros** del dispositivo principal o Rack activo en la pista seleccionada.

### Detención y Navegación de Clips
*   **Stop Clip**: Los 4 botones inferiores de la sección de efectos izquierda (**ON, ON, ON, MACRO**) y los 3 primeros de la derecha (**ON, ON, ON**) detienen el clip de su respectiva pista (Pistas 1 a 7).
*   **Stop All Clips**: El botón **MACRO** del lado derecho detiene todos los clips del proyecto simultáneamente.
*   **Navegación de la Matriz**: Usando **SHIFT + los pads de la esquina inferior derecha del deck izquierdo**, es posible desplazar el recuadro de la matriz (Track/Scene Bank) hacia Arriba, Abajo, Izquierda o Derecha.

---

## 3. Modo 2: Finger Drumming y Control de Envíos
Al presionar el encoder **BROWSE**, el controlador entra en el Modo 2. Este modo está optimizado para tocar instrumentos virtuales y controlar efectos de envío.

### Matriz Dividida (4x4 + Notas MIDI)
*   **Deck Izquierdo (Clip Launcher 4x4)**: La matriz de lanzamiento de clips se reduce a una cuadrícula de 4 pistas por 4 escenas, utilizando únicamente los 16 pads del deck izquierdo.
*   **Deck Derecho (Libre / MIDI Genérico)**: Los 16 pads del deck derecho se desconectan por completo del control de sesión y sus luces (LEDs) se apagan automáticamente. Esto permite utilizarlos libremente en todas sus páginas internas (HOTCUE, LOOP, SLICER y SAMPLER) para enviar notas MIDI estándar, ideales para mapeo manual, sintes, o tocar Drum Racks.

### Control de Envíos y Retornos (Sends & Returns)
Se reasignan los controles de ecualización para manejar de forma avanzada los envíos y los retornos del proyecto:
*   **Knobs de EQ Izquierdos (Cantidades de Envío)**:
    *   **Knob HIGH (Izq)**: Controla el nivel del **Envío A** (Send A) de la pista actualmente seleccionada.
    *   **Knob MID (Izq)**: Controla el nivel del **Envío B** (Send B) de la pista seleccionada.
    *   **Knob LOW (Izq)**: Controla el nivel del **Envío C** (Send C) de la pista seleccionada.
*   **Knobs de EQ Derechos (Volumen de Retornos)**:
    *   **Knob HIGH (Der)**: Controla el volumen general del **Canal de Retorno A** (Return A).
    *   **Knob MID (Der)**: Controla el volumen general del **Canal de Retorno B** (Return B).
    *   **Knob LOW (Der)**: Controla el volumen general del **Canal de Retorno C** (Return C).

### Controles Mantenidos
*   Los botones **Stop Clip** debajo de los knobs izquierdos detienen los clips de las pistas 1 a 4.
*   La navegación de la matriz de clips (con SHIFT + Pads) sigue operativa en el deck izquierdo.
*   Los controles de transporte y navegación de pistas siguen funcionando normalmente.

---
*Nota: Este documento describe la funcionalidad programada en el script Python del proyecto. Para que los cambios físicos (como el comportamiento del modo SLICER o SHIFT) ocurran, dependen del firmware interno de la Hercules P32 DJ actuando en conjunto con el script.*
