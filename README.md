# Hercules P32 DJ - Ableton Live Custom Script 🎛️

Este repositorio contiene un script MIDI personalizado (Remote Script) para utilizar el controlador **Hercules P32 DJ** en Ableton Live. El script optimiza el controlador para flujos de trabajo dinámicos, incluyendo control avanzado de envíos y navegación de pistas.

## 📥 Instalación Rápida

No es necesario clonar el repositorio completo. Para instalar el script:

1. Haz clic en el botón verde **"Code"** en la parte superior de esta página y selecciona **"Download ZIP"**.
2. Descomprime el archivo descargado.
3. Ingresa a la carpeta `src/` y copia la carpeta **`Hercules_P32_DJ`**.
4. Pega la carpeta en el directorio de scripts MIDI de Ableton Live:
   - **Windows:** `\ProgramData\Ableton\Live x.x\Resources\MIDI Remote Scripts\`
   - **Mac:** Ve a la carpeta de Aplicaciones, haz clic derecho en el ícono de Ableton Live -> "Mostrar contenido del paquete" -> navega hasta `Contents/App-Resources/MIDI Remote Scripts/`.
5. Abre Ableton Live, ve a **Preferencias -> Link / MIDI**.
6. En "Superficie de Control", selecciona **Hercules P32 DJ** y asegúrate de encender la casilla **"Remote"** en las entradas y salidas MIDI de la parte inferior.

---

## 🛠️ Requisitos del Proyecto Base

Para garantizar la estabilidad y el correcto funcionamiento de las funciones avanzadas del script, es indispensable trabajar sobre una plantilla base en Ableton con la siguiente estructura:

- **7 Pistas de Audio/MIDI** (Requeridas para la correcta alineación de los faders de volumen y la navegación).
- **3 Pistas de Retorno** (recomendado para la plantilla; el script ya no mapea envíos ni retornos, así que no es obligatorio).

**Sugerencia:** Se recomienda crear un proyecto vacío con 7 pistas y 3 retornos y guardarlo como plantilla predeterminada (`Archivo -> Guardar Live Set como predeterminado`).

**Mapa MIDI interactivo:** [leandoliri.github.io/hercules-p32-ableton-script](https://leandoliri.github.io/hercules-p32-ableton-script/) muestra el panel del P32 con el mensaje que manda cada control y qué hace el script en Modo 1 y Modo 2, por página de pads y con SHIFT. El código está en `docs/index.html` (una sola página, sin build).

**Documentación adicional:** el manual completo está en [DOCUMENTATION.md](DOCUMENTATION.md) y el detalle de mapeos y pendientes en [DOCUMENTATION_ARCHITECTURE.md](DOCUMENTATION_ARCHITECTURE.md). En `docs/` están la guía original de Remotify en PDF (EN/FR) y sus páginas como imágenes (`docs/images/page_1.png` a `page_7.png`, con el diagrama del panel del controlador); esa guía describe el script base, no las modificaciones de este repo.

---

## 🎮 Modos de Operación

El controlador opera bajo dos modos principales:

### Modo 1: Lanzamiento y Macros (Predeterminado)
- **Pads:** Grilla de 7x4 dedicada al lanzamiento de clips en Session View.
- **Mezclador Dinámico:** Control de volumen con faders físicos (pistas 1 a 7 + Master), mute, solo y arm que se desplazan y reasignan automáticamente al navegar entre bancos o pistas (`LOAD A/B`).
- **Macros:** Los dos knobs FILTER controlan los Macros 4 y 8 del dispositivo (plugin) seleccionado.
- **Knobs de EQ libres:** Los 6 knobs HIGH / MID / LOW del centro no están mapeados en ningún modo, para que los asignes a mano con Ctrl+M (por ejemplo, a un EQ Eight).

### Modo 2: Finger Drumming
Se accede a este modo presionando el encoder de **BROWSE**.
- **Pads (Finger Drumming):** El panel de pads derecho se transforma en un teclado cromático de 64 notas (sus 4 páginas, desde C1) con luces tipo piano, ideal para interpretar instrumentos virtuales o Drum Racks.
- **Clip launcher reducido:** El deck izquierdo sigue lanzando clips en una grilla de 4x4.
- Los knobs de EQ siguen libres; los de volumen, faders, transporte y Stop Clip funcionan igual que en el Modo 1.


