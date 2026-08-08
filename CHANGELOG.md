# Resumen de Modificaciones: Hercules P32 DJ

Este documento detalla todas las modificaciones recientes realizadas al script base del Hercules P32 DJ.

## 1. Topes Absolutos en Encoders (Volumen y Envíos/Retornos)
Se implementó una nueva clase personalizada llamada `CappedEncoderElement` que hereda del elemento nativo de codificador de Ableton.
*   **¿Qué hace?** Escucha todos los mensajes entrantes de las perillas rotativas de la consola y matemáticamente corta cualquier valor superior a `0.85` de la escala MIDI (lo cual equivale exactamente a **0 dB** en la interfaz de Ableton Live).
*   **¿A qué afecta?**
    *   Modo 0: Perillas de volumen general de todas las pistas.
    *   Modo 2: Perillas de Envíos A, B y C de la pista seleccionada (Deck Izquierdo).
    *   Modo 2: Perillas de Volumen Maestro de los canales de Retorno A, B y C (Deck Derecho).
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

> [!NOTE]
> Las luces LED de estos controles funcionan mediante la lógica nativa del script original cuando detectan señales entrantes válidas. Las páginas "HOTCUE" de ambos decks continúan 100% libres de asignaciones nativas, permitiendo un mapeo MIDI manual por parte del usuario para instrumentos o efectos VST.
