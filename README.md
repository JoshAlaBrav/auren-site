# Sitio público de Auren

Landing informativa del proyecto personal Auren. Es un sitio estático, sin JavaScript,
formularios, analítica ni dependencias de producción.

## Desarrollo local

Desde la raíz del repositorio:

```powershell
python -m http.server 8000
```

Después, abre `http://localhost:8000/`.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

Las pruebas comprueban la estructura HTML, los enlaces locales, el contenido mínimo,
la ausencia de recursos remotos de terceros y que no reaparezca el correo personal que
figuraba en la versión anterior.

## Publicación prevista

El sitio está preparado para GitHub Pages desde la raíz de `main`. Después de revisar y
fusionar la rama de la landing, un administrador del repositorio puede elegir en
**Settings → Pages → Build and deployment → Deploy from a branch**, seleccionar `main`
y la carpeta `/ (root)`.

La URL prevista es <https://joshalabrav.github.io/auren-site/>. La activación de Pages no
forma parte de este cambio.

## Privacidad

- No se carga JavaScript.
- No hay formularios, cookies ni analítica configurados por Auren.
- No se incluyen credenciales ni datos de la aplicación privada.
- El alojamiento mediante GitHub Pages queda sujeto a las prácticas de GitHub.

Contacto público: [auren.assistant@gmail.com](mailto:auren.assistant@gmail.com)