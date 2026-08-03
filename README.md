# Hercules P32 DJ - Ableton Live Custom Script 🎛️

¡Bienvenido al repositorio oficial de tu script personalizado para el controlador **Hercules P32 DJ** en Ableton Live! Este proyecto adapta el controlador para brindarte un flujo de trabajo ultra-dinámico y profesional.

## 📥 Cómo Instalar el Script en Ableton

Sigue estos pasos para que Ableton reconozca tu controlador con este script:

1. **Descarga el proyecto:** Si no lo has hecho, clona o descarga este repositorio.
2. **Copia el Código Fuente:** Entra a la carpeta `src/` de este repositorio y copia la carpeta entera llamada `Hercules_P32_DJ`.
3. **Pégalo en Ableton:** 
   - **Windows:** Pega la carpeta en `\ProgramData\Ableton\Live x.x\Resources\MIDI Remote Scripts\`
   - **Mac:** Ve a tu carpeta de Aplicaciones, haz clic derecho en el ícono de Ableton Live -> "Mostrar contenido del paquete" (Show Package Contents) -> y navega hasta `Contents/App-Resources/MIDI Remote Scripts/`. Pega la carpeta ahí.
4. **Configura Ableton:** 
   - Abre Ableton Live.
   - Ve a **Opciones -> Preferencias -> Link / MIDI**.
   - En "Superficie de Control" (Control Surface), selecciona **Hercules P32 DJ**.
   - Asegúrate de encender el botón de **"Remote"** en las entradas y salidas MIDI de la parte inferior.

---

## 🛠️ El "Proyecto Base" (Requisito Indispensable)

Para que el controlador funcione al 100% y sin errores, **necesitas trabajar sobre una plantilla base específica**. 
Ableton es muy estricto con las asignaciones de código, por lo que tu proyecto debe tener siempre la siguiente estructura mínima:

- **7 Pistas de Audio/MIDI** (Para que los faders y la navegación se alineen perfectamente).
- **3 Pistas de Retorno (Envíos)** (¡CRÍTICO! Necesitas tener Envío A, B y C. Si tienes menos, el script de Envíos Dinámicos fallará).

> [!TIP]
> **Crea tu Plantilla por Defecto:** Abre un proyecto vacío en Ableton, presiona `Ctrl + T` hasta tener 7 pistas, y `Ctrl + Alt + T` hasta tener 3 pistas de retorno. Luego ve a `Archivo -> Guardar Live Set como predeterminado`. ¡Así nunca tendrás problemas!

---

## 🎮 Modos y Funcionalidades

Tu controlador ha sido modificado para tener dos modos de operación principales:

### Modo 1: Lanzamiento y Macros (Predeterminado)
- **Grilla de Pads:** Lanza clips en Ableton (una matriz de 7x4).
- **Mezclador:** Controla volúmenes y navegación entre pistas.
- **Macros:** Las 8 perillas superiores controlan los **Macros** del dispositivo (plugin) que tengas seleccionado.

### Modo 2: Finger Drumming y Envíos Dinámicos (¡Exclusivo!)
Para entrar a este modo, presiona el encoder de **BROWSE**.
- **Finger Drumming:** Los pads cambian para enviar notas MIDI puras, ideal para tocar un Drum Rack.
- **Envíos Dinámicos:** Las perillas superiores del **Deck Izquierdo** dejan de controlar los macros y pasan a controlar los **Envíos** de la pista que tengas seleccionada:
  - **HIGH:** Envío A (ej. Reverb)
  - **MID:** Envío B (ej. Delay)
  - **LOW:** Envío C (ej. Chorus)

---

## 🖼️ Guía Visual (Mapeo Original)

A continuación te dejamos las ilustraciones oficiales de referencia sobre cómo están distribuidos los controles base.

````carousel
![Guía Visual - Página 1](docs/images/page_1.png)
<!-- slide -->
![Guía Visual - Página 2](docs/images/page_2.png)
<!-- slide -->
![Guía Visual - Página 3](docs/images/page_3.png)
<!-- slide -->
![Guía Visual - Página 4](docs/images/page_4.png)
<!-- slide -->
![Guía Visual - Página 5](docs/images/page_5.png)
<!-- slide -->
![Guía Visual - Página 6](docs/images/page_6.png)
<!-- slide -->
![Guía Visual - Página 7](docs/images/page_7.png)
````

*(Puedes encontrar los PDFs originales en la carpeta `docs/` de este repositorio).*
