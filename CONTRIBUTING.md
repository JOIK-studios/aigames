# Contribuir a aigames

¡Gracias por tu interés en contribuir! Este es un proyecto experimental donde los juegos son generados por IA, pero las mejoras humanas son bienvenidas.

## ¿Cómo contribuir?

### Reportar un bug
1. Abre un **Issue** en GitHub describiendo el problema.
2. Incluye el nombre del archivo afectado (`generated-N.py`), los pasos para reproducirlo y la salida de error si la hay.

### Proponer una mejora
1. Abre un **Issue** con la etiqueta `enhancement`.
2. Describe qué quieres mejorar y por qué.

### Enviar un Pull Request
1. Haz un fork del repositorio.
2. Crea una rama descriptiva: `git checkout -b fix/laberinto-crash` o `git checkout -b feat/nuevo-nivel`.
3. Realiza tus cambios y asegúrate de que el juego sigue ejecutándose con `python3 "1st Generation/generated-N.py"`.
4. Abre un Pull Request con una descripción clara de los cambios.

## Convenciones

- **Python 3.7+**, sin dependencias externas (solo biblioteca estándar).
- Mantén el estilo de código existente en cada archivo (comentarios en español, clases de colores ANSI, función `clear()`).
- Los nombres de variables y funciones pueden estar en inglés o español, siguiendo el archivo correspondiente.

## Añadir un nuevo juego

Si quieres añadir un juego generado por IA a una nueva generación:
1. Crea una carpeta `2nd Generation/` (o la que corresponda).
2. Nombra el archivo `generated-N.py` siguiendo la secuencia.
3. Actualiza `README.md` y `SECURITY.md` con el nombre y descripción del juego.
