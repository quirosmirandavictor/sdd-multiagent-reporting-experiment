# Quickstart: Health check mínimo

## Estado y prerrequisitos

La aplicación, `pyproject.toml`, `uv.lock`, Dockerfile y las cuatro pruebas están implementados. Esta guía describe cómo repetir las verificaciones técnicas; los resultados y las incidencias observadas están en [validation.md](validation.md). La revisión humana previa a integración sigue pendiente.

Usar la raíz del repositorio y la rama `001-health-check`. Se necesita Docker con daemon activo y contenedores Linux para la validación reproducible. La ejecución local opcional requiere Python 3.12 y uv, usando la misma versión de uv registrada para la imagen Docker. Descargar imágenes y dependencias durante la construcción requiere acceso a sus registros; atender la consulta y ejecutar las pruebas ya construidas no requiere servicios externos.

Consultar [contrato HTTP](contracts/health.openapi.json), [modelo de respuesta](data-model.md) y [plan](plan.md). No se requieren credenciales, configuración de reportes ni servicios acompañantes.

Los ejemplos de consola usan PowerShell. Si el puerto de ejemplo está ocupado, elegir otro puerto del host y actualizar la URL de consulta.

## 1. Entorno local opcional

Usar `pyproject.toml` y `uv.lock` versionados. uv creará o sincronizará el entorno `.venv` del proyecto, incluyendo el grupo de desarrollo.

```powershell
uv --version
uv lock --check
uv sync --locked --python 3.12
uv run --locked --no-sync python --version
uv run --locked --no-sync python -m pytest -q -p no:cacheprovider
```

Resultado esperado: Python 3.12, dependencias coherentes y todos los escenarios de integración aprobados. La implementación debe cubrir los cuatro escenarios indicados en la matriz de la sección 4.

Los comandos uv son iguales en Windows y Linux; no es necesario activar manualmente el entorno.

En el entorno Windows validado fue necesario usar el almacén de certificados del sistema para descargar paquetes: `uv --system-certs sync --locked --python 3.12`. Usar esta opción si aparece un error de emisor TLS desconocido y el certificado es de confianza en el sistema; no desactiva TLS. La suite emite una advertencia de deprecación de Starlette por HTTPX, conservada en la evidencia sin cambiar las versiones del plan.

Para consultar un servidor local, ejecutar en una consola:

```powershell
$env:UVICORN_HOST = '127.0.0.1'
$env:UVICORN_PORT = '8000'
uv run --locked --no-sync --no-dev python -m uvicorn app:app
```

Consultar desde otra consola mediante el paso 3. Detener el servidor con Ctrl+C.

La regeneración de `uv.lock` no forma parte de sincronizar o probar una revisión. Cuando cambien dependencias, editar `pyproject.toml`, ejecutar `uv lock`, revisar ambos archivos y repetir la validación según [research.md](research.md). Para preparar solo dependencias de ejecución, usar `uv sync --locked --no-dev`.

## 2. Construir y probar en Docker

```powershell
docker version
docker build --target test -t sdd-health-check:test .
docker run --rm --network none sdd-health-check:test uv run --locked --no-sync python -m pytest -q -p no:cacheprovider
docker build --target runtime -t sdd-health-check:runtime .
```

Resultado esperado: construcciones satisfactorias y todos los escenarios aprobados con código de salida cero. La ejecución de pruebas no tiene red externa, volúmenes, secretos ni servicios acompañantes.

El Dockerfile debe copiar `pyproject.toml` y `uv.lock`, sincronizar con `uv sync --locked --no-dev` en `base` y con `uv sync --locked` en `test`, conservar la versión de Python y fijar las imágenes de Python y uv por digest. No regenerar el lock en cada build. La etapa `test` y la `runtime` comparten la aplicación y las versiones de dependencias de producción; las ejecuciones usan `uv run --locked --no-sync` sobre el entorno preparado.

En una consola dedicada, iniciar la imagen final en primer plano:

```powershell
docker run --rm --name sdd-health-check-validation -e UVICORN_HOST=0.0.0.0 -e UVICORN_PORT=8000 -p 127.0.0.1:8000:8000 sdd-health-check:runtime
```

Resultado esperado: Uvicorn inicia el servicio. La publicación de puerto se limita al host local para esta validación. No se montan archivos ni se configura identidad, persistencia o servicios de reportes.

## 3. Consultar la imagen en ejecución

Desde otra consola PowerShell, realizar la consulta sin credenciales y sin seguir redirecciones:

```powershell
curl.exe --silent --show-error --fail-with-body --max-time 10 --max-redirs 0 --include http://127.0.0.1:8000/health
```

Resultado esperado: HTTP 200, tipo de contenido `application/json` y el objeto exacto del contrato, sin propiedades adicionales. Los espacios de serialización son irrelevantes. Esta inspección manual complementa las aserciones automáticas; un código de salida cero de curl por sí solo no verifica que el estado sea exactamente 200.

Repetir la consulta tres veces consecutivas; cada respuesta debe cumplir el mismo contrato. El límite de espera del comando evita que una comprobación se bloquee y no constituye una meta de latencia del producto.

Para cambiar el puerto del host, por ejemplo a 8081, usar `-p 127.0.0.1:8081:8000` al iniciar el contenedor y consultar el puerto 8081. Para cambiar el puerto interno, ajustar tanto `UVICORN_PORT` como el destino de la publicación.

Al terminar:

```powershell
docker stop sdd-health-check-validation
```

El contenedor iniciado con `--rm` se elimina al detenerse.

## 4. Matriz de validación obligatoria

| Escenario | Preparación y acción | Resultado que debe comprobarse |
|---|---|---|
| 1. Respuesta fija | API iniciado; TestClient solicita GET a la ruta del contrato | HTTP 200, JSON con tipo de contenido correcto y objeto exacto |
| 2. Acceso público | Cliente sin Authorization, cookies o credenciales y sin seguir redirecciones | Misma respuesta directa HTTP 200, sin redirección |
| 3. Sin recursos de reportes | Ejecutar imagen de pruebas con `--network none`, sin volúmenes ni servicios; revisar aplicación y dependencias | Respuesta contractual sin procesamiento fuera de alcance; ninguna dependencia de recursos de negocio |
| 4. Independencia entre consultas | Tres GET consecutivos con el mismo cliente | Cada solicitud produce HTTP 200 y objeto exacto |

Los tests deben comparar el JSON deserializado; no basta con comprobar que existe una propiedad `status`. La revisión del escenario 3 complementa el aislamiento: Python, paquetes y pruebas sí necesitan archivos de runtime, pero no debe haber lectura de definiciones o datos de reportes. La consulta de la sección 3 comprueba además el arranque real de Uvicorn y la publicación del puerto.

## 5. Evidencia y cierre SDD

Durante implementación, crear `specs/001-health-check/validation.md` y registrar:

- Fecha, rama y revisión Git; aprobación de la especificación y referencias al plan y tareas.
- Versiones de Python y uv, dependencias de `uv.lock`; referencias exactas y digests de las imágenes de Python y uv.
- Comandos ejecutados, salidas relevantes, códigos de salida y resultado de cada escenario.
- Revisión de alcance: sin autenticación, persistencia, lectura de YAML de reportes, XLSX, imágenes, gráficos, llamadas externas ni procesamiento background.
- Pruebas fallidas, omitidas o bloqueadas y su motivo; intervenciones humanas y decisiones si aparecen ambigüedades.
- Revisión previa a la integración en `dev` y su evidencia.

Si Docker o una prueba no se puede ejecutar, registrarlo expresamente y mantener pendiente esa validación. La implementación y las verificaciones técnicas actuales están registradas en [validation.md](validation.md); SC-003 permanece pendiente hasta incorporar la revisión humana previa a integración.
