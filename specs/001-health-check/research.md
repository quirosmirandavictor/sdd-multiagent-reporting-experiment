# Research: Health check mínimo

**Fecha**: 2026-10-14
**Alcance**: Decisiones técnicas para FR-001 a FR-005, dentro de Constitution 1.0.0. No amplía el contrato funcional.

## 1. Aplicación y servidor

**Decision**: Python 3.12, FastAPI 0.143.1 y Uvicorn 0.54.0 sin extras; un único módulo `app.py` con la aplicación y el manejador de la respuesta constante.

**Rationale**: Python y FastAPI son restricciones constitucionales. Uvicorn proporciona el servidor ASGI necesario para servir HTTP dentro del contenedor. No hay lógica de negocio ni integraciones que justifiquen capas adicionales. Los extras añadirían funciones que esta consulta no necesita. Metadatos y dependencias oficiales: [FastAPI en PyPI](https://pypi.org/project/fastapi/0.143.1/), [Uvicorn en PyPI](https://pypi.org/project/uvicorn/0.54.0/) y [dependencias de FastAPI](https://fastapi.tiangolo.com/#dependencies).

**Alternatives considered**: Otro framework contradice la restricción vigente; un servidor HTTP propio añade trabajo innecesario. `fastapi[standard]`, `uvicorn[standard]` y una separación controlador/servicio/repositorio no resuelven necesidades de esta feature.

## 2. Pruebas del contrato

**Decision**: pytest 9.1.1 y HTTPX 0.28.1 como dependencias de desarrollo; TestClient de FastAPI para los cuatro escenarios y consulta HTTP real de la imagen de ejecución.

**Rationale**: TestClient permite probar la frontera HTTP sin levantar puertos durante pytest. HTTPX es requerido por ese cliente. La guía oficial usa pruebas síncronas ordinarias; no se necesita un plugin de pruebas asíncronas. La consulta al contenedor añade la comprobación del servidor y su configuración. Fuentes: [pruebas FastAPI](https://fastapi.tiangolo.com/tutorial/testing/), [pytest en PyPI](https://pypi.org/project/pytest/9.1.1/) y [HTTPX en PyPI](https://pypi.org/project/httpx/0.28.1/).

**Alternatives considered**: Una prueba unitaria que llame directamente al manejador no verifica el contrato HTTP. Solo una consulta manual deja sin automatizar los escenarios. Levantar un servidor por prueba añade puertos y coordinación innecesarios; se reserva la ejecución real para validar Docker.

## 3. Versiones y bloqueo reproducible con uv

**Decision**: Usar uv como herramienta principal, `pyproject.toml` para definir dependencias y `uv.lock` versionado para el bloqueo reproducible, conforme a la instrucción explícita del usuario. No se usarán archivos requirements como fuente de dependencias.

| Dependencia directa | Versión seleccionada | Python requerido según metadatos | Grupo |
|---|---|---|---|
| FastAPI | 0.143.1 | >=3.10 | Ejecución |
| Uvicorn | 0.54.0 | >=3.10 | Ejecución |
| pytest | 9.1.1 | >=3.10 | Pruebas |
| HTTPX | 0.28.1 | >=3.8 | Pruebas |

Las fuentes de metadatos son las páginas PyPI enlazadas arriba. Estas versiones admiten Python 3.12 según sus metadatos; la combinación completa aún debe resolverse, instalarse y probarse. No se fija Starlette independientemente de FastAPI; el resultado transitivo se conserva en `uv.lock`, siguiendo las [recomendaciones de versiones de FastAPI](https://fastapi.tiangolo.com/deployment/versions/).

`pyproject.toml` declarará las versiones seleccionadas de FastAPI y Uvicorn en una lista `dependencies` dentro de `[project]`, y pytest y HTTPX en `[dependency-groups].dev`. Usará `requires-python = ">=3.12,<3.13"` y `[tool.uv] package = false`: se mantiene Python 3.12 y no se añade un paquete distribuible. Fuente: [configuración de proyectos uv](https://docs.astral.sh/uv/concepts/projects/config/).

Durante implementación se generará el lock y se comprobará el entorno:

```powershell
uv --version
uv lock
uv lock --check
uv sync --locked --python 3.12
uv run --locked --no-sync python -m pytest -q -p no:cacheprovider
```

**Rationale**: Un único bloqueo coordina las versiones de producción y desarrollo. `uv sync --locked` rechaza un bloqueo ausente o desactualizado y sincroniza exactamente las dependencias del entorno; `--no-dev` excluye el grupo de pruebas en producción. `uv run --locked --no-sync` ejecuta sobre el entorno preparado. Fuente: [bloqueo y sincronización uv](https://docs.astral.sh/uv/concepts/projects/sync/).

La versión de uv usada para generar y validar el lock se registrará en la evidencia. La imagen oficial de uv usada en Docker se fijará por digest; los colaboradores usarán esa misma versión para reproducir el flujo. No se regenerará el bloqueo durante las construcciones habituales.

**Alternatives considered**: Bloqueos independientes de producción y desarrollo duplican mantenimiento. El flujo de archivos requirements y pip no corresponde a la elección explícita del usuario. Fijar solo dependencias directas deja variables las transitivas.

## 4. Contenedor y configuración

**Decision**: Imagen oficial Python 3.12 slim y binario uv de su imagen oficial, con referencias por digest registradas en el Dockerfile durante implementación. Un Dockerfile con etapas `base`, `test` y `runtime`, sin Compose. `base` usa `uv sync --locked --no-dev`; `test` usa `uv sync --locked` para añadir el grupo de desarrollo; `runtime` deriva de `base` y excluye herramientas de prueba. Las sincronizaciones se hacen antes de cambiar a usuario sin privilegios. El arranque usa `uv run --locked --no-sync --no-dev python -m uvicorn app:app` sobre el entorno preparado. Fuente para la integración: [uv en Docker](https://docs.astral.sh/uv/guides/integration/docker/).

**Rationale**: Satisface reproducibilidad y ejecución independiente. El digest evita cambios implícitos de la base y el usuario sin privilegios es suficiente para este servicio. Fuente: [prácticas de construcción Docker](https://docs.docker.com/build/building/best-practices/). Resolver y registrar el digest es parte de materializar el Dockerfile, no una decisión arquitectónica pendiente.

**Decision**: Configurar el servidor mediante variables de proceso `UVICORN_HOST` y `UVICORN_PORT`; arranque con `uv run --locked --no-sync --no-dev python -m uvicorn app:app` sin argumentos de host/puerto que anulen esas variables.

**Rationale**: Uvicorn admite variables con ese prefijo y da precedencia a argumentos de línea de comandos. Permite externalizar configuración sin biblioteca propia; los valores de ejemplo son `0.0.0.0` y `8000` dentro del contenedor. Fuente: [configuración de Uvicorn](https://www.uvicorn.org/settings/).

**Alternatives considered**: Compose, identidad, base de datos o volúmenes no son necesarios. Un cargador de configuración o archivos `.env` añade piezas que no requiere este contrato. No se introduce Gunicorn, proxy ni orquestador.

## 5. Aislamiento y alcance de la validación

**Decision**: Ejecutar las pruebas de integración de la imagen `test` con `--network none`, sin volúmenes ni servicios acompañantes. Complementar con revisión de código, configuración y dependencias.

**Rationale**: El [modo de red de Docker](https://docs.docker.com/reference/cli/docker/container/run/#network) permite aislar la ejecución. TestClient trabaja en proceso, por lo que esta prueba no necesita red externa. La revisión sigue siendo necesaria para descartar lógica fuera de alcance; la ejecución aislada no prueba por sí sola que jamás se consulten archivos o se capturen errores de dependencias.

**Alternatives considered**: Levantar servicios ficticios contradice el escenario sin servicios; simular cada componente excluido produciría código de prueba innecesario. Pruebas de rendimiento o disponibilidad no corresponden al alcance acordado.

## 6. Contrato y datos

**Decision**: OpenAPI 3.1.0 estático en JSON con una operación y un esquema de respuesta cerrado, sin autenticación. Modelo conceptual de salida sin persistencia ni clase de dominio obligatoria.

**Rationale**: Documenta la interfaz consumible y la prohibición de propiedades adicionales de FR-002. No introduce lectura de YAML en la aplicación ni una dependencia de validación del contrato en producción. Fuente: [OpenAPI 3.1.0](https://spec.openapis.org/oas/v3.1.0.html).

**Alternatives considered**: Un contrato solo narrativo facilita diferencias entre pruebas y API. Añadir un DTO, servicio o repositorio propios para devolver una constante no aporta una frontera útil.

## Resultado de investigación

Todas las decisiones necesarias para diseñar están resueltas. No se instalaron paquetes ni se construyeron imágenes: `uv.lock` transitivo, digests concretos, pruebas y evidencia corresponden a implementación. No hay ambigüedades funcionales nuevas ni cambios requeridos en la Constitución.
