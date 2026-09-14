# Hercules P32 DJ - Ableton Live Custom Script 🎛️

Script MIDI personalizado (Remote Script) para usar el controlador **Hercules P32 DJ** como superficie de control de **Ableton Live**: lanzador de clips, mezclador con banking automático, loops y beatjump desde los pads, y un modo de finger drumming con teclado cromático de 64 notas y luces tipo piano.

**Mapa MIDI interactivo:** [leandoliri.github.io/hercules-p32-ableton-script](https://leandoliri.github.io/hercules-p32-ableton-script/) muestra el panel del P32 con el mensaje que manda cada control y qué hace el script en Modo 1 y Modo 2, por página de pads y con SHIFT.

> **English summary.** Custom Ableton Live Remote Script for the Hercules P32 DJ. Install: download this repo as ZIP, copy `src/Hercules_P32_DJ` into Live's `MIDI Remote Scripts` folder (paths below), restart Live, then pick **Hercules P32 DJ** as a Control Surface in Preferences → Link, Tempo & MIDI with the P32 as input and output, and enable **Track** and **Remote** on the P32 MIDI input. Mode 1 = clip launcher / mixer / loops; press BROWSE for Mode 2 = right deck becomes a 64‑note chromatic keyboard. Full user manual in [DOCUMENTATION.md](DOCUMENTATION.md) (Spanish). Tested on Live 12.2 (Windows 11).

---

## 📥 Instalación

No hace falta clonar el repositorio ni instalar nada más.

1. Hacé clic en el botón verde **"Code"** arriba de esta página y elegí **"Download ZIP"**. Descomprimilo.
2. Entrá a la carpeta `src/` y copiá la carpeta **`Hercules_P32_DJ`** completa (tres archivos `.py`).
3. Pegala en la carpeta de scripts MIDI de Ableton Live:
   - **Windows:** `C:\ProgramData\Ableton\Live 12 Suite\Resources\MIDI Remote Scripts\` (ajustá el nombre de tu versión: `Live 12 Suite`, `Live 12 Standard`, `Live 11 Suite`, etc.). `ProgramData` es una carpeta oculta; pegá la ruta directamente en la barra del Explorador.
   - **Mac:** carpeta Aplicaciones → clic derecho sobre Ableton Live → **"Mostrar contenido del paquete"** → `Contents/App-Resources/MIDI Remote Scripts/`.
   - Alternativa sin permisos de administrador (ambos sistemas): la carpeta de scripts de usuario, `Biblioteca de usuario/Remote Scripts/` (en Windows suele ser `Documentos\Ableton\User Library\Remote Scripts\`).
4. Si Live estaba abierto, **cerralo y volvé a abrirlo**. Live solo lee los scripts al arrancar.
5. Preferencias → **Link, Tempo & MIDI**. En la lista de **Superficies de control** elegí **Hercules P32 DJ**, y como **Entrada** y **Salida** el puerto `Hercules P32 DJ`.
6. Más abajo, en la lista de puertos MIDI, en la fila **Input: Hercules P32 DJ** activá **Track** y **Remote**. En **Output: Hercules P32 DJ** activá **Remote**.
   - *Track* hace falta para que en el Modo 2 las notas del deck derecho lleguen a la pista armada.
   - *Remote* hace falta para que el script controle Live y para que los knobs de EQ se puedan asignar con Ctrl+M.
7. En la barra de estado de Live debería aparecer **"Hercules P32 DJ Ready"** y los pads se encienden.

**Actualizar a una versión nueva:** repetí los pasos 2 a 4 (reemplazá la carpeta y reiniciá Live). Reseleccionar la superficie de control en Preferencias no alcanza: Live no vuelve a leer el código hasta reiniciar.

### Requisitos y compatibilidad

- Probado en **Ableton Live 12.2.5 en Windows 11**. Usa el framework `_Framework` de Live, que sigue incluido en Live 11 y 12; el código es compatible con Python 2 y 3, así que debería funcionar en Live 10 y 11, pero no está verificado.
- Firmware del P32: **1.47 o superior** para poder apagar el "Light Show" (ver más abajo).
- No hace falta software de Hercules ni DJUCED; el P32 funciona como controlador MIDI genérico.

### Plantilla recomendada

El script está pensado para un banco de **7 pistas** visibles (4 en el deck izquierdo, 3 en el derecho + Master) y funciona con cualquier cantidad de pistas gracias al banking. Conviene crear un proyecto vacío con 7 pistas y guardarlo como plantilla predeterminada (`Archivo → Guardar Live Set como predeterminado`). Los retornos no son obligatorios.

---

## 🎮 Cómo se usa

Guía completa, control por control, en [DOCUMENTATION.md](DOCUMENTATION.md). Resumen:

### Siempre activo (capa base)
- **Knobs FX 1–3 y DRY/WET de cada deck:** volumen de las pistas 1–7 del banco visible (tope en 0 dB) y Master.
- **Botones ON / ON / ON / MACRO bajo los knobs:** Stop Clip de cada pista; el MACRO derecho es Stop All.
- **Página SLICER del deck izquierdo:** Seleccionar / Mute / Solo / Armar de las pistas 1–4.
- **Deck derecho, abajo:** PLAY, CUE = Stop, SYNC = Tap Tempo. **Deck izquierdo, abajo:** PLAY = poner/quitar marcador, CUE = Deshacer, SYNC = Rehacer, SHIFT = alternar Session / Arrangement.
- **LOAD A / LOAD B:** pista anterior / siguiente, con desplazamiento automático del banco. **REC** y **SLIP:** grabar y overdub. **Crossfader:** crossfader de Live.
- **Encoder LOOP/TEMPO izquierdo:** girar = tempo ±1 BPM (con SHIFT ±0,1), presionar = metrónomo.
- **SHIFT derecho + pads (cruz en SAMPLER):** mover el banco de la matriz arriba / abajo / izquierda / derecha. Los 4 pads se iluminan mientras SHIFT está apretado.
- **Knobs HIGH / MID / LOW del centro:** libres en todos los modos, para asignar con Ctrl+M a lo que quieras.

### Modo 1 (predeterminado): lanzamiento y mezcla
- **SAMPLER:** matriz de clips de 7 pistas × 4 escenas (los dos decks juntos); la 4ª columna del deck derecho lanza escenas.
- **SLICER (deck derecho):** Seleccionar / Mute / Solo / Armar de las pistas 5–7.
- **LOOP:** por columna, una pista: loop on/off, ÷2, ×2 y beatjump del clip que está sonando.
- **FILTER:** macros 4 y 8 del dispositivo de la pista seleccionada.

### Modo 2 (presionar BROWSE): finger drumming
- **Deck derecho:** teclado cromático de 64 notas desde C1 a través de sus 4 páginas (SAMPLER, SLICER, LOOP, HOTCUE), con luces tipo piano: blancas violeta, negras azul, las C en rojo, y brillo al presionar.
- **Deck izquierdo:** lanzador de clips 4×4 y el mixer de la página SLICER.

### El "Light Show" del P32
En las páginas HOTCUE y SAMPLER, el firmware del controlador dispara una animación violeta al presionar pads. No depende del script. Para apagarla: mantené **HOTCUE y SAMPLER al mismo tiempo durante más de 3 segundos**. Hay que repetirlo cada vez que desconectás el P32.

---

## 🛠️ Si algo no anda

- **El script no aparece en la lista de superficies:** la carpeta tiene que llamarse exactamente `Hercules_P32_DJ` y contener `__init__.py`; reiniciá Live después de copiarla.
- **Los pads no se encienden o nada responde:** revisá que Entrada y Salida de la superficie de control sean el puerto del P32 y que **Remote** esté activo en ambos.
- **En Modo 2 no suena nada:** el puerto del P32 necesita **Track** activo en la entrada, y la pista MIDI tiene que estar armada.
- **Un botón dispara una nota en el instrumento:** no debería pasar con esta versión; si pasa, abrí un issue con el número de nota. Para verlo: Ctrl+M en Live y mirá la barra de estado, o poné `DEBUG_LOG_MIDI = True` en `hercules_p32_dj.py` y leé `Log.txt`.
- **Errores:** el log de Live está en `%AppData%\Ableton\Live x.x\Preferences\Log.txt` (Windows) o `~/Library/Preferences/Ableton/Live x.x/Log.txt` (Mac). Buscá `RemoteScriptError`.

---

## 📚 Documentación del proyecto

- [DOCUMENTATION.md](DOCUMENTATION.md): manual de usuario completo.
- [DOCUMENTATION_ARCHITECTURE.md](DOCUMENTATION_ARCHITECTURE.md): mapeos exactos (canales, notas, CC), decisiones de diseño y pendientes. Es la fuente de verdad si querés modificar el script.
- [CHANGELOG.md](CHANGELOG.md): resumen de todas las modificaciones sobre el script base.
- [CLAUDE.md](CLAUDE.md): guía técnica para trabajar en el código (flujo de trabajo, reglas del framework de Live, cómo depurar).
- `docs/`: la guía original de Remotify en PDF (EN/FR) y sus páginas como imágenes (describen el script base, no las modificaciones), y `docs/index.html`, el mapa MIDI interactivo publicado en GitHub Pages.

## 🙌 Créditos

Script y documentación por [LeanDoliri](https://github.com/LeanDoliri). Basado en el mapeo generado con [Remotify](https://remotify.io) para el P32 (2017), reescrito y ampliado a mano sobre el framework `_Framework` de Ableton Live. Hercules y P32 DJ son marcas de Guillemot Corporation; este proyecto no está afiliado a Hercules ni a Ableton.
