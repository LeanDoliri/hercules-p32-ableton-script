# Manual de Funcionalidades: Hercules P32 DJ (Custom Script) 🎛️

Este documento detalla exhaustivamente todas las funcionalidades, mapeos y modos de operación que han sido programados en este script personalizado para el controlador Hercules P32 DJ en Ableton Live.

---

## 🎚️ Funcionalidades Globales (Siempre Activas)

Sin importar en qué modo te encuentres, la sección de mezcla y transporte siempre estará disponible para garantizar que no pierdas el control principal del proyecto.

### 1. Mezclador (Mixer)
- **Faders de Volumen (1 a 7):** Controlan el volumen de las primeras 7 pistas del recuadro activo.
- **Fader Master:** Controla el volumen general del proyecto (Master Track).
- **Crossfader:** Mapeado directamente al crossfader de Ableton Live.

### 2. Controles por Canal (Pistas 1 a 7)
Para cada una de las 7 pistas, el hardware cuenta con botones físicos mapeados a las siguientes funciones:
- **ARM (Grabar):** Arma la pista para recibir notas MIDI o audio.
- **SOLO:** Aísla el audio de la pista seleccionada.
- **MUTE:** Silencia la pista.
- **SELECT:** Selecciona la pista, cambiando el enfoque de Ableton hacia ella.

### 3. Transporte y Navegación
- **Play, Stop, Record, Overdub:** Controles clásicos de transporte para el flujo de trabajo.
- **Metrónomo:** Activa o desactiva el metrónomo de Live.
- **Tempo Control (Encoders):** 
  - Ajuste Grueso: Sube o baja el tempo global en pasos enteros (+/- 1 BPM).
  - Ajuste Fino: Modifica el tempo con precisión decimal (+/- 0.1 BPM).
- **Navegación de Pistas (< / >):** Te permite desplazarte lateralmente pista por pista a través de todo tu Live Set.

---

## 🟢 MODO 1: Lanzamiento de Clips y Macros (Modo Predeterminado)

Este es el modo principal al encender el controlador. Está diseñado para producir, improvisar y lanzar clips de forma masiva aprovechando al máximo la matriz de pads.

### Grilla de Sesión (7x4)
- **Matriz de Lanzamiento:** 28 pads iluminados que representan 7 pistas de ancho por 4 escenas de alto. Reflejan exactamente lo que ves en la vista Session de Ableton. Al presionar un pad, se dispara el clip correspondiente.
- **Lanzamiento de Escenas:** 4 botones laterales dedicados a disparar filas completas (Scenes 1 a 4).
- **Stop Clips:** 7 botones inferiores que detienen la reproducción de los clips en sus respectivas pistas.
- **Navegación de Cuadrícula (Up/Down/Left/Right):** Botones para desplazar el recuadro rojo de Ableton hacia cualquier parte de tu sesión.

### Macros de Dispositivos (Efectos/Plugins)
- **Perillas de Efectos (8 Encoders):** Las 4 perillas superiores del deck izquierdo y las 4 perillas del deck derecho se fusionan para controlar **automáticamente los primeros 8 Macros** del dispositivo (plugin, instrumento o Audio Effect Rack) que esté insertado en la pista actualmente seleccionada. 

---

## 🔵 MODO 2: Envíos Dinámicos y Drumming (Activado vía BROWSE)

Al presionar el encoder central **BROWSE**, el controlador entra en el **Modo 2**. Este modo reconfigura el deck izquierdo para enfocarse en el diseño sonoro espacial y la interpretación rítmica.

### Los Envíos Dinámicos (Funcionalidad Exclusiva)
Las perillas superiores del **Deck Izquierdo** se desconectan de los Macros del instrumento y pasan a inyectar señal a las pistas de retorno de la pista que tengas seleccionada en ese momento:
- **Perilla 1 (HIGH):** Sube/Baja el nivel del **Envío A** (ideal para Reverb).
- **Perilla 2 (MID):** Sube/Baja el nivel del **Envío B** (ideal para Delay).
- **Perilla 3 (LOW):** Sube/Baja el nivel del **Envío C** (ideal para Chorus u otro efecto especial).
*(Nota: La 4ta perilla queda libre. ¡Recuerda que tu proyecto de Ableton debe tener creadas las pistas de retorno A, B y C para que esto funcione!)*

### Grilla Compacta de Pads (4x4)
- En este modo, la grilla del deck izquierdo se convierte en una matriz más compacta de 4 pistas por 4 escenas. 
- Los 4 botones inferiores pasan a ser los "Stop Clips" de esas 4 pistas específicas.
- Esta matriz condensada es especialmente útil para interpretar un Drum Rack usando los 16 pads del deck izquierdo sin perder el control de los envíos dinámicos justo arriba de tu mano.

---

## 🔄 Cómo Alternar entre Modos
- Presiona **BROWSE** estando en Modo 1 para entrar al **Modo 2** (Envíos).
- Presiona **BROWSE** estando en Modo 2 para regresar al **Modo 1** (Macros).
