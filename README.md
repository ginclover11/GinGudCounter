# Git Gud Counter

Tracker de runs no-hit Overlay para OBS/Streamlabs via Browser Source.

## Descarga

Bajá el `.exe` desde la sección [Releases](../../releases) — no necesitás instalar Python.

Descomprimí la carpeta y ejecutá `GitGudCounter.exe`.

## Uso en OBS

1. Abrí el programa
2. Copiá la URL que aparece arriba: `http://localhost:7373/overlay`
3. En OBS: **+ → Browser Source**
4. Pegá la URL y ajustá el ancho para que coincida con tu overlay

## Hotkeys por defecto

| Acción | Tecla |
|---|---|
| Hit en Boss | F1 |
| Block | F2 |
| Hit en el camino | F3 |
| Iniciar Timer | F4 |
| Detener Timer | F5 |
| Reset Boss Actual | F6 |
| Guardar PB | F7 |
| Siguiente Boss | F8 |
| Boss Anterior | F9 |
| Reset Run | F10 |

Los hotkeys funcionan aunque el programa esté minimizado. Son configurables desde el tab Hotkeys.

## Logos de juegos

Poné los logos en la carpeta `assets/` con estos nombres exactos:

```
assets/
  sekiro_logo.png
  ds1_logo.png
  ds2_logo.png
  ds3_logo.png
  elden_ring_logo.png
  bloodborne_logo.png
  demon_souls_logo.png
```

Se aplican automáticamente al iniciar un run con el template correspondiente.

## Ejecutar desde el código fuente

Requiere Python 3.9+.

```bash
pip install -r requirements.txt
python main.py
```

## Compilar el .exe

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "GitGudCounter" main.py
```

El ejecutable queda en `dist/GitGudCounter.exe`. Copialo a su propia carpeta junto con la carpeta `assets/`.
