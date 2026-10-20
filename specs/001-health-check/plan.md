# Implementation Plan: Health check mínimo

**Branch**: `001-health-check` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

**Input**: `specs/001-health-check/spec.md` y Constitution 1.0.0.

**Estado**: Diseño completado hasta fase 1; implementación y validación funcional pendientes. El campo `Feature Branch` de la especificación conserva el contexto de su creación en `dev`; este plan registra la rama efectiva devuelta por `setup-plan.ps1`. No se cambia la especificación ni su estado `Draft`.

## Summary

Implementar exclusivamente la consulta pública `GET /health`, con HTTP 200 y el objeto JSON exacto definido en FR-002. Un único módulo `app.py` contendrá la aplicación FastAPI y el manejador de la respuesta fija; Uvicorn atenderá HTTP. No existe lógica de negocio que requiera un núcleo, un servicio de aplicación o una interfaz adicional.

La entrega posterior incluirá dependencias bloqueadas, ejecución independiente mediante Docker y pruebas de integración para los cuatro escenarios. La selección técnica y sus alternativas están en [research.md](research.md); el contrato está en [contracts/health.openapi.json](contracts/health.openapi.json). Esta fase produce diseño, no código ni resultados de ejecución.

## Technical Context

**Language/Version**: Python 3.12; la imagen oficial slim de esta línea se fijará por digest en el Dockerfile al implementar.

**Primary Dependencies**: FastAPI 0.143.1 y Uvicorn 0.54.0, sin extras. Dependencias declaradas en `pyproject.toml` y bloqueo completo de versiones y hashes en `uv.lock` durante la implementación; uv será la herramienta principal para resolver, sincronizar y ejecutar.

**Storage**: No aplica; sin persistencia, archivos de negocio, sesiones ni cachés de aplicación.

**Testing**: pytest 9.1.1 y HTTPX 0.28.1, mediante `fastapi.testclient.TestClient`; comprobación HTTP adicional contra el contenedor en ejecución.

**Target Platform**: Contenedor Linux con Python 3.12. Desarrollo local opcional en Windows o Linux con Python 3.12. Docker es la vía reproducible de aceptación.

**Project Type**: Servicio web mínimo con una sola operación dentro del contrato.

**Performance Goals**: No se establecen metas de latencia, rendimiento ni concurrencia, conforme a `Assumptions` de la especificación.

**Constraints**: Consulta pública sin dependencias de negocio ni servicios externos; sin autenticación, YAML de reportes, XLSX, imágenes, gráficos ni procesamiento background. Configuración del servidor por variables `UVICORN_HOST` y `UVICORN_PORT`; dependencias reproducibles y ausencia de secretos en el repositorio.

**Scale/Scope**: Una historia, cinco requisitos funcionales y cuatro escenarios de aceptación. Tres consultas consecutivas verifican independencia entre solicitudes; no constituyen una prueba de carga.

## Constitution Check

*Gate antes de fase 0 y revalidación después de fase 1. Las condiciones de implementación e integración se mantienen como obligaciones futuras, sin presentarlas como cumplidas.*

| Principio / restricción | Antes de investigación | Después del diseño / evidencia |
|---|---|---|
| I. Especificación como fuente de verdad | PASS para planificar: alcance explícito, sin ambigüedades críticas en clarify | PASS de diseño: FR-001 a FR-005 trazados abajo; registrar aprobación de la especificación antes de implementar, pues sigue `Draft` |
| II. Arquitectura limpia mínima | PASS: no hay lógica de reportes en esta feature | PASS: un módulo HTTP; ninguna capa, repositorio, fábrica o interfaz sin necesidad actual |
| III. Contratos explícitos | PASS: método, ruta, respuesta y acceso público definidos | PASS: OpenAPI estático y prueba de integración consumidor/API previstos |
| IV. YAML declarativo de reportes | No aplica a esta feature | No se introduce lectura de YAML ni un esquema de reportes; el contrato HTTP usa JSON |
| V. XlsxWriter | No aplica a esta feature | No se instala XlsxWriter ni se añade generación XLSX; se preserva el alcance futuro del motor |
| VI. Seguridad | PASS: la especificación autoriza expresamente la consulta pública | PASS: sin flujo de identidad ni secretos; no modifica las obligaciones futuras para rutas protegidas |
| VII. Fuentes de imágenes | No aplica a esta feature | No se reciben ni resuelven imágenes o URLs externas |
| VIII. Contenedores y reproducibilidad | PASS de diseño: ejecución Docker obligatoria | PASS: imagen base y herramienta uv fijadas por digest, `pyproject.toml` y `uv.lock` versionados, sincronización con `uv sync --locked` y configuración de ambiente externa |
| IX. Verificación | PASS de diseño: cuatro escenarios definidos | PASS: estrategia y quickstart; resultados reales pendientes, deben registrarse antes de declarar terminado el trabajo |
| X. Decisiones ausentes | PASS: no quedan ambigüedades funcionales críticas | PASS: la especificación delega decisiones de implementación al plan; decisiones y alternativas registradas en research |
| XI. Responsabilidad multiagente | PASS: autor único de archivos | PASS: apoyo de investigación web de solo lectura, sin operaciones sobre árboles de código; tareas futuras definirán responsables y árboles independientes si hay implementación paralela |
| XII. Simplicidad y dependencias | PASS: solamente necesidades presentes | PASS: justificación de cada dependencia en research; sin servicios, frameworks ni abstracciones adicionales |
| Flujo obligatorio e integración | PASS para esta fase de planificación | Antes de implementar: aprobación de especificación y tareas con responsables. Antes de integrar: pruebas y revisión; destino `dev`; `main` mediante PR y aprobación humana |

**Resultado**: Sin violaciones ni aclaraciones técnicas pendientes para completar el diseño. La planificación no sustituye la aprobación de la especificación ni acredita el recorrido SDD completo.

## Project Structure

### Documentation (this feature)

```text
specs/001-health-check/
├── spec.md
├── checklists/requirements.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/health.openapi.json
├── tasks.md              # Futuro: speckit-tasks; no generado por plan
└── validation.md         # Futuro: evidencia de implementación, pruebas y revisión
```

### Source Code (repository root)

Estructura prevista; estos archivos de implementación aún no existen:

```text
app.py
pyproject.toml
uv.lock
Dockerfile
.dockerignore
.gitignore
README.md
tests/
└── test_health.py
```

**Structure Decision**: Un proyecto Python sin empaquetado distribuible. `app.py` expone `app`, que ejecutará `uv run --locked --no-sync --no-dev python -m uvicorn app:app` después de sincronizar el entorno de ejecución. `tests/test_health.py` comprueba el contrato por la frontera HTTP mediante TestClient. No se crea un modelo Pydantic propio para una constante sin datos de entrada; el modelo conceptual documentado no exige una clase.

`pyproject.toml` declara FastAPI y Uvicorn en una lista `dependencies` dentro de `[project]`, y pytest y HTTPX en `[dependency-groups].dev`. `requires-python` limita la ejecución a Python 3.12 (`>=3.12,<3.13`) y `[tool.uv] package = false` evita añadir empaquetado distribuible. `uv.lock` conserva una resolución compartida para ejecución y pruebas. uv es la herramienta principal: `uv lock` genera el bloqueo, `uv lock --check` comprueba su vigencia y `uv sync --locked` sincroniza el entorno sin modificarlo. Producción usa `uv sync --locked --no-dev`. No se usan archivos requirements como fuente de dependencias.

El Dockerfile tendrá una etapa común `base` con uv, `pyproject.toml`, `uv.lock`, dependencias de producción y aplicación, una etapa `test` que sincroniza también el grupo de desarrollo y añade los archivos de pruebas, y una etapa final `runtime` derivada de `base`. uv se obtendrá de su imagen oficial con referencia fija por digest. Las sincronizaciones (`uv sync --locked --no-dev` en `base` y `uv sync --locked` en `test`) se harán antes de cambiar a usuario sin privilegios. La ejecución posterior con `uv run --locked --no-sync` usará el entorno ya preparado, sin reinstalar ni resolver paquetes. Las pruebas no se incorporarán a `runtime`. `.dockerignore` excluirá Git, entornos locales, configuración sensible y artefactos ajenos a la ejecución. No hacen falta Compose ni servicios acompañantes.

## Phase 0: Research

Completada en [research.md](research.md): versiones compatibles con Python 3.12, servidor ASGI, prueba HTTP en proceso, bloqueo con uv, contenedor independiente y configuración por ambiente. Se consultaron fuentes primarias; no se instalaron ni resolvieron dependencias en esta fase. La compatibilidad ejecutada de la combinación corresponde a implementación.

## Phase 1: Design and Contracts

- [data-model.md](data-model.md): objeto de respuesta inmutable, sin entidades persistentes ni estados de negocio.
- [contracts/health.openapi.json](contracts/health.openapi.json): una operación pública, sin entradas obligatorias, con respuesta JSON estricta.
- [quickstart.md](quickstart.md): sincronización desde `uv.lock`, comandos de pruebas locales y Docker, consulta real y registro de evidencia.

El contrato estático es la referencia de esta feature. No se exige igualdad estructural con el documento OpenAPI que FastAPI pueda generar automáticamente; se verifica el comportamiento observable. Otras rutas y métodos permanecen fuera del contrato.

## Validation Strategy and Traceability

| Requisito / criterio | Verificación prevista | Evidencia esperada |
|---|---|---|
| FR-001, FR-002; escenario 1 | TestClient comprueba HTTP 200, tipo de contenido JSON y objeto exacto; la comparación admite espacios en blanco distintos | Resultado de pytest y consulta HTTP al contenedor |
| FR-003; escenario 2 | Solicitud sin `Authorization`, cookies ni credenciales, con seguimiento de redirecciones desactivado; debe responder directamente HTTP 200 | Caso de prueba y consulta pública del quickstart |
| FR-004; escenario 3 | Misma aplicación en imagen `test`, sin red externa, credenciales, servicios, volúmenes ni datos de reportes; revisión de código y dependencias para excluir procesamiento fuera de alcance | Resultado de `docker run --network none` y revisión de alcance; la prueba aislada por sí sola no demuestra ausencia de toda lectura de archivos |
| FR-005; escenario 4 | Tres GET consecutivos con el mismo cliente, cada uno con HTTP 200 y objeto exacto | Caso de prueba de repetición |
| SC-001, SC-002 | Los cuatro escenarios pasan sin servicios ni datos de negocio; consulta HTTP real de imagen `runtime` | Salidas y códigos de salida de pruebas y consulta |
| SC-003 | Trazar especificación y aprobación, plan, tareas, implementación, validaciones y revisión previa a integración | `specs/001-health-check/validation.md`, creado y completado posteriormente |

No se incluyen pruebas de carga ni objetivos de disponibilidad que la especificación excluye. Los logs estándar de Uvicorn permiten inspeccionar arranque y solicitudes durante la validación; no se añaden métricas, tracing ni endpoints operativos adicionales.

El registro futuro de validación debe incluir fecha, revisión Git, versiones de Python y herramientas, digest de imagen base, comandos, resultados, fallos u omisiones, revisión de alcance, referencias de aprobación y revisión humana. Una prueba bloqueada se registra como bloqueada; no se presenta como aprobada.

## Complexity Tracking

Sin violaciones constitucionales ni complejidad adicional que justificar.
