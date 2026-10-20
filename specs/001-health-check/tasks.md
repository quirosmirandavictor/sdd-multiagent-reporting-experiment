# Tasks: Health check mínimo

**Input**: Documentos de diseño en `specs/001-health-check/`.
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contrato HTTP](contracts/health.openapi.json) y [quickstart.md](quickstart.md).
**Branch**: `001-health-check` | **Fecha**: 2026-10-14

**Tests**: Incluidos porque la especificación exige verificar los cuatro escenarios y una prueba de integración del contrato antes de integrar. No se añaden objetivos de carga, disponibilidad ni pruebas de otros métodos o rutas.

**Organization**: Una sola historia P1 (US1). Setup y Foundational preparan el proyecto; la fase US1 entrega y valida la capacidad; la fase final documenta y revisa el resultado. Todas las tareas comienzan pendientes; este archivo no acredita ejecución.

## Format: `[ID] [P?] [Story] Description`

- `[P]`: Puede realizarse junto con la tarea indicada en el grafo, una vez resueltas sus dependencias; trabajan sobre archivos distintos.
- `[US1]`: Pertenece a la historia «Consultar el health check mínimo».
- Las rutas de tareas son relativas a la raíz del repositorio.
- Ejecutar secuencialmente por defecto con un único responsable. Las oportunidades de paralelismo no autorizan por sí solas a crear agentes ni a modificar un mismo árbol simultáneamente.

## Path Conventions

Un solo proyecto con `app.py`, `pyproject.toml`, `uv.lock`, `Dockerfile`, `.gitignore`, `.dockerignore`, `README.md` y `tests/test_health.py`. La evidencia se registra en `specs/001-health-check/validation.md`. No se crean capas, modelos persistentes ni servicios adicionales.

**Condición para comenzar implementación**: Debe existir aprobación de la especificación conforme a Constitution 1.0.0; `spec.md` sigue en `Draft`. Registrar la referencia de aprobación en T003 antes de comenzar US1. La generación de estas tareas no modifica ni presume esa aprobación. Si falta al iniciar implementación, resolverla antes de ejecutar T001.

**Responsabilidades**: El implementador ejecuta T001–T006; el validador ejecuta T007–T009; documentación atiende T010; el revisor atiende T011; el coordinador consolida T012 y registra la revisión humana prevista en el plan. Una persona o agente puede asumir varios roles, con responsabilidad explícita. No se asigna aprobación humana a un agente.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Definir el proyecto mínimo y excluir archivos locales del repositorio y de la construcción.

- [X] T001 [P] Crear `pyproject.toml` con metadatos mínimos, `requires-python = ">=3.12,<3.13"`, FastAPI `0.143.1` y Uvicorn `0.54.0` sin extras en `dependencies` de `[project]`, pytest `9.1.1` y HTTPX `0.28.1` en `[dependency-groups].dev`, y `package = false` en `[tool.uv]`; no añadir backend de empaquetado, dependencias hipotéticas ni archivos requirements como fuente.
- [X] T002 [P] Crear o ajustar `.gitignore` y `.dockerignore` para excluir entornos virtuales, cachés Python/pytest y secretos locales; excluir además Git y artefactos de herramientas del contexto Docker, manteniendo disponibles `app.py`, `pyproject.toml`, `uv.lock` y `tests/test_health.py` para las etapas que los consumen; no ignorar `uv.lock`.

**Checkpoint**: Definición de dependencias y exclusiones listas; todavía no existe una capacidad funcional.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Obtener un entorno reproducible y abrir el registro de evidencia antes de implementar US1. No se necesita infraestructura de datos, autenticación ni un núcleo de negocio.

- [X] T003 Generar `uv.lock` desde `pyproject.toml` con `uv lock`, verificar con `uv lock --check` y preparar Python 3.12 mediante `uv sync --locked --python 3.12`; crear `specs/001-health-check/validation.md` con fecha, rama, revisión Git, referencia de aprobación de `specs/001-health-check/spec.md`, versiones exactas de Python y uv, comandos y resultados; comprobar resolución compatible y registrar cualquier fallo sin cambiar versiones o alcance silenciosamente.

**Checkpoint**: T001–T003 completadas; bloqueo versionable y entorno preparado. US1 depende de este punto.

## Phase 3: User Story 1 — Consultar el health check mínimo (Priority: P1) — MVP

**Goal**: Atender `GET /health` públicamente con HTTP 200 y el objeto fijo, sin recursos de negocio ni dependencia entre consultas.

**Independent Test**: Con el API iniciado y accesible, consultar sin credenciales y comprobar directamente HTTP 200, tipo de contenido JSON y objeto deserializado igual a `{"status":"ok"}`. Los cuatro escenarios deben aprobarse, incluidas tres consultas consecutivas; repetir la suite en un contenedor sin red externa y consultar la imagen de ejecución real.

### Tests for User Story 1

Escribir primero las pruebas del contrato. El fallo inicial debe corresponder a la capacidad aún ausente, no a una instalación defectuosa; registrar el resultado antes de implementar la respuesta.

- [X] T004 [P] [US1] Crear cuatro pruebas de integración en `tests/test_health.py` con `fastapi.testclient.TestClient` para los escenarios 1–4 de `specs/001-health-check/spec.md`: respuesta HTTP 200 y `application/json`, consulta sin Authorization/cookies/credenciales y sin seguir redirecciones, consulta sin configuración ni recursos de reportes, y tres GET consecutivos con el mismo cliente; comprobar el objeto deserializado exacto con campo `status` de tipo cadena, obligatorio y valor `ok`, respetando literalmente las reglas de `specs/001-health-check/data-model.md`: «El objeto contiene exactamente esta propiedad; no se permiten campos adicionales.», «No se admiten ausencia del campo, `null`, otros tipos ni otros valores.», «Los espacios en blanco de serialización no forman parte del contrato; se compara el JSON deserializado.» y «No hay cuerpo de solicitud ni parámetros obligatorios para la consulta.»; ejecutar `uv run --locked --no-sync python -m pytest -q -p no:cacheprovider` antes de T006 y registrar el fallo esperado en `specs/001-health-check/validation.md`.
 
### Implementation for User Story 1

- [X] T005 [P] [US1] Crear `Dockerfile` con imágenes oficiales Python 3.12 slim y uv fijadas por digest, usando la misma versión uv registrada en T003; preparar `base` con aplicación, `pyproject.toml`, `uv.lock` y `uv sync --locked --no-dev`, `test` con `uv sync --locked` y `tests/test_health.py`, y `runtime` final derivada de `base` sin pruebas ni dependencias del grupo dev; sincronizar antes de cambiar a usuario sin privilegios, mantener accesible el entorno preparado y arrancar con `uv run --locked --no-sync --no-dev python -m uvicorn app:app`, permitiendo `UVICORN_HOST` y `UVICORN_PORT` sin argumentos que las anulen; diferir las construcciones a T008–T009.
- [X] T006 [US1] Implementar la instancia `app` de FastAPI y el manejador público `GET /health` en `app.py` conforme a `specs/001-health-check/contracts/health.openapi.json`: responder directamente HTTP 200 y JSON exacto `{"status":"ok"}`, sin estado entre solicitudes ni campos adicionales; aplicar «El objeto contiene exactamente esta propiedad; no se permiten campos adicionales.» y «No hay cuerpo de solicitud ni parámetros obligatorios para la consulta.»; no añadir autenticación, persistencia, lectura/validación de YAML, generación Excel, imágenes, gráficos, llamadas externas, procesamiento background ni capas para devolver esta constante (FR-001–FR-005).
- [X] T007 [US1] Ejecutar `uv lock --check`, `uv sync --locked --python 3.12` y `uv run --locked --no-sync python -m pytest -q -p no:cacheprovider` sobre `tests/test_health.py`; registrar en `specs/001-health-check/validation.md` el paso de fallo inicial a aprobación, los cuatro escenarios por separado, comandos, salidas y códigos de salida; corregir defectos dentro del contrato y repetir solo las comprobaciones afectadas.
- [X] T008 [US1] Construir la etapa `test` de `Dockerfile` mediante `docker build --target test -t sdd-health-check:test .` y ejecutar `docker run --rm --network none sdd-health-check:test uv run --locked --no-sync python -m pytest -q -p no:cacheprovider`, sin volúmenes, credenciales ni servicios acompañantes; registrar los cuatro resultados, versiones efectivas de Python/uv, digests de las bases y códigos de salida en `specs/001-health-check/validation.md`; la descarga de dependencias se permite durante build, no se necesita durante la prueba.
- [X] T009 [US1] Construir la etapa `runtime` de `Dockerfile` y ejecutar los pasos Docker de `specs/001-health-check/quickstart.md`, configurando host/puerto por ambiente y publicando solo en localhost; comprobar el arranque real de Uvicorn, HTTP 200 sin redirección, tipo de contenido y objeto exacto en tres consultas consecutivas sin credenciales; comprobar usuario sin privilegios y ausencia de tests/dependencias dev en la imagen final; registrar resultados en `specs/001-health-check/validation.md` y detener el contenedor de validación al terminar.

**Checkpoint**: US1 funcional y verificada por integración local, aislamiento sin red y HTTP real en Docker. Una prueba fallida o no ejecutada mantiene pendiente la validación correspondiente.

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Documentar el uso reproducible y completar la evidencia del recorrido SDD sin ampliar la funcionalidad.

- [X] T010 [P] Documentar prerrequisitos, sincronización `uv sync --locked`, ejecución, configuración de host/puerto, pruebas y comandos Docker comprobados en `README.md`; actualizar el estado y cualquier instrucción que ya no corresponda en `specs/001-health-check/quickstart.md`, enlazando el contrato y la evidencia; conservar `pyproject.toml` y `uv.lock` como definición y bloqueo principales.
- [X] T011 [P] Revisar `app.py`, `pyproject.toml`, `uv.lock`, `Dockerfile` y `.dockerignore` frente a FR-001–FR-005, `specs/001-health-check/contracts/health.openapi.json` y Constitution 1.0.0; registrar en `specs/001-health-check/validation.md` ausencia de procesamiento fuera de alcance, inexistencia de dependencia de recursos de reportes/servicios externos, separación de dependencias dev, bloqueo reproducible y ausencia de secretos; complementar explícitamente el aislamiento de T008 con revisión de código y configuración, sin añadir pruebas de otras rutas/métodos.
- [ ] T012 Consolidar en `specs/001-health-check/validation.md` la trazabilidad de SC-001–SC-003: aprobación de especificación, plan, tareas, implementación, cuatro escenarios, validación Docker, revisión de alcance y revisión humana previa a integrar; registrar fallos, omisiones, bloqueantes e intervenciones humanas con su estado real y verificar que las instrucciones finales de `README.md` y `specs/001-health-check/quickstart.md` coincidan con los resultados; no declarar completo SC-003 mientras falte evidencia ni integrar automáticamente en `dev` o `main`.

**Checkpoint**: Documentación y revisión listas para una decisión de integración. `main` solo recibe cambios mediante PR y aprobación humana; esta lista no ejecuta la integración.

## Dependencies & Execution Order

### Phase Dependencies

Setup (T001–T002) → Foundational (T003) → US1 (T004–T009) → Polish (T010–T012).

### User Story Dependencies

US1 es la única historia y no depende de otras. Su entrada exige T003 y su salida funcional exige T009. El objetivo experimental completo exige también T012.

### Task Dependencies

| Tarea | Prerrequisitos |
|---|---|
| T001 | Aprobación de especificación disponible |
| T002 | Aprobación de especificación disponible |
| T003 | T001, T002 |
| T004 | T003 |
| T005 | T003 |
| T006 | T004 |
| T007 | T006 |
| T008 | T005, T007 |
| T009 | T008 |
| T010 | T009 |
| T011 | T009 |
| T012 | T010, T011 |

### Dependency Graph

```text
Aprobación de especificación
          |
    T001 || T002
          |
         T003
        /    \
      T004   T005
       |      |
      T006    |
       |      |
      T007 ---+
          |
         T008
          |
         T009
        /    \
      T010   T011
        \    /
         T012
```

### Within User Story 1

Pruebas y fallo inicial (T004) → respuesta mínima (T006) → integración local (T007) → pruebas aisladas del contenedor (T008) → ejecución HTTP real (T009). La preparación de Docker (T005) puede avanzar junto a T004; construir la imagen requiere que existan aplicación y pruebas. No se crean tareas de modelo/servicio/repositorio porque no hay entidades ni lógica de negocio que las requieran.

### Parallel Opportunities

- T001 y T002: definición del proyecto y exclusiones, en archivos distintos.
- T004 y T005: pruebas/evidencia inicial y Dockerfile, después de T003.
- T010 y T011: documentación y revisión de alcance/evidencia, después de T009.
- Las escrituras de `specs/001-health-check/validation.md` son secuenciales: T003 → T004 → T007 → T008 → T009 → T011 → T012.
- Si se decide usar varios agentes, cada uno debe operar en un árbol independiente y tener archivos/responsabilidad asignados; coordinar integración de cambios antes de ejecutar tareas dependientes. Todo traspaso debe indicar trabajo, archivos, validaciones, decisiones y bloqueantes, conforme al principio XI.

## Parallel Example: User Story 1

Una vez completada T003, posible distribución sin archivos compartidos:

```text
Trabajo A — T004:
  tests/test_health.py
  specs/001-health-check/validation.md
  Crear los cuatro casos y registrar el fallo inicial.

Trabajo B — T005:
  Dockerfile
  Preparar etapas base/test/runtime sin ejecutar builds.

Coordinación:
  Integrar T004 antes de T006.
  Integrar T005 y completar T007 antes de T008.
```

No dividir los cuatro tests entre agentes que editen simultáneamente `tests/test_health.py`.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Confirmar la condición de aprobación y completar T001–T003.
2. Completar T004 y T005; implementar T006 después del fallo inicial.
3. Verificar T007–T009 y corregir únicamente defectos del alcance acordado.
4. Entregar como MVP la única consulta pública; no añadir funciones del motor de reportes.
5. Completar T010–T012 antes de declarar cumplido el recorrido experimental completo.

### Incremental Delivery

Definición y bloqueo → contrato verificado en proceso → ejecución reproducible en Docker → documentación y evidencia revisadas. No hay historias adicionales ni un segundo incremento funcional implícito.

### Parallel Team Strategy

El modo por defecto es secuencial. Si se asignan responsables adicionales, usar únicamente los pares indicados y árboles independientes; un coordinador integra sus cambios y mantiene una sola secuencia de evidencia. Los roles definidos arriba describen responsabilidades, no solicitan ni crean agentes en esta fase.

## Traceability

| Requisito / resultado | Tareas |
|---|---|
| FR-001: HTTP 200 | T004, T006, T007, T008, T009 |
| FR-002: JSON exacto | T004, T006, T007, T008, T009 |
| FR-003: consulta pública | T004, T006, T007, T008, T009 |
| FR-004: sin recursos/procesamiento excluidos | T004, T005, T006, T008, T011 |
| FR-005: consultas independientes | T004, T006, T007, T008, T009 |
| SC-001: todos los escenarios aprobados | T007, T008, T009, T012 |
| SC-002: sin credenciales/definiciones/servicios | T004, T006, T008, T009, T011 |
| SC-003: recorrido SDD con evidencia y revisión | T003, T004, T007, T008, T009, T010, T011, T012 |
| Constitution VIII y decisión de usar uv | T001, T002, T003, T005, T008, T009, T010 |

## Notes

- 12 tareas: Setup 2, Foundational 1, US1 6, Polish 3.
- Seis tareas `[P]` forman tres pares potenciales; no pueden ejecutarse antes de sus prerrequisitos.
- Mantener el contrato acordado; cualquier nueva decisión que lo cambie requiere actualizar la especificación antes de implementar.
- Marcar una tarea completada solo cuando su resultado y verificación requeridos estén disponibles; pruebas omitidas o bloqueadas se reportan como tales.
