# sdd-multiagent-reporting-experiment

## Feature 002: reportes locales — entrega B

El generador XLSX, paleta, gráfico y CLI están implementados. **El parser A
(`reporting/yaml_input.py`) aún no está integrado en este árbol.** Los comandos
de generación YAML siguientes se podrán ejecutar al integrar A; por ahora no
se declara validado el flujo E2E. No se incluye un parser sustituto.
El contrato está en [report-v1.md](specs/002-yaml-excel-reports/contracts/report-v1.md).
Las secciones históricas posteriores describen el incremento 001.

### Windows: instalación desde cero

Usar PowerShell, Git, Python 3.12 y uv 0.12.23. Excel es necesario solo para
la revisión visual. Para contenedores, instalar Docker Desktop y activar su
motor Linux. Ejecutar desde la raíz de este repositorio/clon.

```powershell
winget install --exact --id Python.Python.3.12
winget install --exact --id astral-sh.uv --version 0.12.23
# Abrir una consola nueva si cambió PATH.
uv --version
uv lock --check
uv sync --locked --python 3.12
uv run --locked --no-sync python -m reporting --help
uv run --locked --no-sync python -m pytest -q
```

No es necesario activar .venv. No ejecutar `uv lock` para instalar.
Las dependencias aprobadas ya están fijadas; no se requieren bibliotecas de
lectura Excel ni dependencias adicionales.

### Generar el ejemplo después de integrar A

```powershell
New-Item -ItemType Directory -Force output | Out-Null
uv run --locked --no-sync python -m reporting --input examples/report.yaml --output output/report.xlsx
Resolve-Path output/report.xlsx
Invoke-Item output/report.xlsx
```

La salida será `<raíz del repositorio>\output\report.xlsx`; la CLI imprime su
ruta absoluta. El archivo debe ser nuevo: elegir otro nombre para repetir.
El libro tiene una hoja `Reporte`, título A1, tabla `Datos` desde A3 y dos
filas con Norte/120 y Sur/90. El gráfico vertical toma sus datos de las celdas,
debajo de la tabla. Título Navy, encabezados Azure con texto blanco, filas
blancas/azul claro y barras Azure; el violeta se reserva sin aplicarlo.

Para comprobar B mientras falta A, este comando usa exclusivamente el dict
normalizado contractual, sin procesar YAML:

```powershell
New-Item -ItemType Directory -Force output | Out-Null
@'
from pathlib import Path
from reporting.xlsx_output import build_xlsx
report = {
    'schema_version': 1, 'title': 'Ventas por región',
    'headers': ['Región', 'Ventas'],
    'rows': [['Norte', 120], ['Sur', 90]],
    'chart': {'type': 'column', 'category_column': 0, 'value_columns': [1]},
}
target = Path('output/report-b.xlsx')
with target.open('xb') as stream:
    stream.write(build_xlsx(report))
print(target.resolve())
'@ | uv run --locked --no-sync python -
Invoke-Item output/report-b.xlsx
```

Se generó realmente `output/report-b.xlsx` en este árbol. La presentación en
Excel sigue pendiente: revisar legibilidad, colores, ausencia de reparación y
solapamientos, y cambiar un número de la tabla para comprobar el gráfico.

### Docker reproducible

Estos comandos requieren Docker Desktop iniciado y el parser A integrado para
la generación. El build descarga las imágenes fijadas por digest y dependencias;
la ejecución preparada funciona sin red ni instalaciones.

```powershell
docker build --target test -t sdd-reports:test .
docker run --rm --network none sdd-reports:test
docker build --target runtime -t sdd-reports:runtime .
New-Item -ItemType Directory -Force output | Out-Null
$reportOutput = (Resolve-Path output).Path
$reportInput = (Resolve-Path examples/report.yaml).Path
docker run --rm --network none --mount "type=bind,source=$reportInput,target=/input.yaml,readonly" --mount "type=bind,source=$reportOutput,target=/output" sdd-reports:runtime uv run --locked --no-sync --no-dev python -m reporting --input /input.yaml --output /output/report-docker.xlsx
Invoke-Item output/report-docker.xlsx
```

El XLSX se recupera directamente en `output/report-docker.xlsx` mediante el
montaje. El usuario del contenedor es UID/GID 10001 y debe poder escribir en
esa carpeta. En Linux preparar una carpeta propiedad de 10001:10001 o conceder
permisos mediante ACL; no montar .venv. La entrada se monta en solo lectura.
Alternativa sin montaje de salida, conservando el contenedor hasta copiar:

```powershell
docker run --name sdd-report-export --network none sdd-reports:runtime uv run --locked --no-sync --no-dev python -m reporting --input examples/report.yaml --output /tmp/report.xlsx
docker cp sdd-report-export:/tmp/report.xlsx ./output/report-export.xlsx
docker rm sdd-report-export
```

### Verificar GET /health

El CMD por defecto conserva el servicio existente. En una consola:

```powershell
uv run --locked --no-sync python -m uvicorn app:app --host 127.0.0.1 --port 8000
# Alternativa Docker:
# docker run --rm --name sdd-report-health -p 127.0.0.1:8000:8000 sdd-reports:runtime
```

En otra consola:

```powershell
1..3 | ForEach-Object { curl.exe --silent --show-error --fail-with-body --max-time 10 --include http://127.0.0.1:8000/health }
```

Cada consulta debe devolver HTTP 200 y `{"status":"ok"}`. Detener el servidor
local con Ctrl+C o el contenedor con `docker stop sdd-report-health`.

### Evidencia de B y pendientes

- `uv lock --check`: correcto; `uv sync --locked --python 3.12`: correcto.
- `uv run --locked --no-sync python -m pytest -q`: 26 aprobadas, 1 módulo
  omitido por ausencia del parser A y una advertencia existente de Starlette.
- Inspección ZIP/XML: datos, tipos, no mutación, posiciones, tabla, colores,
  alternancia, bordes, gráfico vertical, series y referencias. Seguridad:
  cadenas literales, cero fórmulas de celdas y cero hipervínculos automáticos.
- CLI: ayuda/argumentos, composición con sustitutos solo en tests, UTF-8,
  validación, destino existente, permisos simulados, generación y escritura
  fallidas, limpieza de archivo parcial. El sustituto no valida YAML.
- Generación real con dict normalizado: `output/report-b.xlsx`.
- Salud: cuatro pruebas existentes aprobadas y tres consultas HTTP reales
  locales con HTTP 200 y objeto exacto. No se modificó `app.py`.
- Reintentos: uv falló inicialmente por acceso a caché; lock, sync y pytest
  pasaron con ejecución autorizada fuera del sandbox. El primer comando de
  sondeo HTTP falló por comillas de PowerShell, sin iniciar el servidor;
  se corrigió usando un script por entrada estándar y las tres consultas pasaron.
- Docker: `docker version` y el build runtime fallaron por daemon Linux
  ausente, incluso al reintentar fuera del sandbox. No se ejecutaron imagen,
  suite Docker, exportación Docker ni salud HTTP en contenedor.
- Pendientes: handoff A, E2E YAML/CLI real, suite integrada completa,
  Docker y revisión humana en Excel. Los tests reales de integración se
  habilitan automáticamente cuando exista el módulo A.

No se editaron SDD/contrato, pyproject.toml, uv.lock ni archivos de A; no hubo
commit, merge ni push. Las tareas B cubiertas son T006, T008–T012, T016,
T018–T020; documentación y preparación Docker están implementadas con
validación integrada pendiente. La regresión local de T023 está comprobada.

### Errores comunes

- `No module named reporting.yaml_input`: falta integrar A; no es un fallo
  de instalación de PyYAML. Usar solo las pruebas B/dict hasta el handoff.
- Destino existente: usar otro nombre `.xlsx`; nunca se sobrescribe.
- Padre inexistente o permisos: crear previamente la carpeta, cerrar archivos
  bloqueados en Excel y comprobar permisos del usuario/UID del contenedor.
- Error de validación (código 2): revisar UTF-8 y el campo/fila indicado según
  el contrato; no se genera salida. Errores de archivos/generación usan código 1.
- Caché uv denegada: ejecutar desde una cuenta con acceso a su caché o fijar
  `UV_CACHE_DIR` a una carpeta propia. En esta sesión el sandbox exigió acceso
  autorizado para usar la caché existente y ejecutar las comprobaciones.
- TLS de uv: si el emisor es de confianza en Windows, probar
  `uv --system-certs sync --locked --python 3.12`.
- Docker no conecta al named pipe: iniciar Docker Desktop con motor Linux
  y comprobar `docker version` antes de repetir el build.
- Puerto ocupado: usar otro puerto en uvicorn o en el lado host de `-p`.


### Desarrollo guiado por especificaciones · ORCA AI · 2 agentes Codex · Human in the loop

![Enfoque: SDD](https://img.shields.io/badge/Enfoque-Spec--Driven_Development-2563EB?style=for-the-badge)
![Entorno: ORCA AI](https://img.shields.io/badge/Entorno-ORCA_AI-7C3AED?style=for-the-badge)
![Agentes: 2 Codex](https://img.shields.io/badge/Agentes-2_CODEX-111827?style=for-the-badge)
[![Gobernanza: human in the loop](https://img.shields.io/badge/Gobernanza-Human_in_the_loop-F59E0B?style=for-the-badge)](#colaboración-y-gobernanza)

[![Health check: 11 de 12 tareas](https://img.shields.io/badge/Health_check-11%2F12_tareas-0284C7?style=flat-square)](specs/001-health-check/tasks.md)
[![Evidencia: 4 escenarios aprobados](https://img.shields.io/badge/Evidencia-4_escenarios_aprobados-16A34A?style=flat-square)](specs/001-health-check/validation.md)
[![Revisión humana: pendiente](https://img.shields.io/badge/Revisi%C3%B3n_humana-Pendiente-F59E0B?style=flat-square)](specs/001-health-check/validation.md#t012-consolidación-lista-para-revisión-humana)
![Python: 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![API: FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Ejecución: Docker](https://img.shields.io/badge/Ejecuci%C3%B3n-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

## Objetivo del experimento

Explorar cómo construir un motor de reportes con **desarrollo guiado por especificaciones (SDD)**, trabajando con **ORCA AI y dos agentes Codex**, bajo la supervisión del autor, [Víctor Quirós Miranda](https://github.com/quirosmirandavictor), como **human in the loop**. El experimento busca observar la trazabilidad entre requisitos, decisiones, tareas, código y pruebas, así como la coordinación entre agentes y las intervenciones humanas necesarias para aceptar cada entrega.

El primer incremento es deliberadamente pequeño: un health check que permite recorrer el flujo SDD y reunir evidencia antes de ampliar el producto. La [Constitución 1.0.0](.specify/memory/constitution.md) establece los principios técnicos y de colaboración.

```mermaid
flowchart LR
    O["Experimento: ORCA AI + 2 agentes Codex"] --> S["SDD: alcance y contratos explícitos"]
    S --> I["Incrementos pequeños y verificables"]
    I --> E["Evidencia: código, pruebas y decisiones"]
    E --> H["Autor: revisión y aprobación humana"]
    H --> A["Avance aceptado hacia el motor de reportes"]
    H -->|Cambios solicitados| S

    classDef process fill:#DBEAFE,stroke:#2563EB,color:#172554
    classDef human fill:#FEF3C7,stroke:#D97706,color:#78350F
    classDef result fill:#DCFCE7,stroke:#16A34A,color:#14532D
    class O,S,I,E process
    class H human
    class A result
```

## Colaboración y gobernanza

El repositorio se trabaja con un modelo protegido: **los agentes solamente pueden trabajar en la rama `dev`**. Los **pull requests son revisados y aprobados por el autor**; `main` recibe los cambios mediante PR con aprobación humana. Los agentes preparan cambios y evidencia; la decisión de aceptación corresponde al autor.

| Participante | Responsabilidad en el experimento |
|---|---|
| ORCA AI | Entorno de trabajo del experimento con los dos agentes Codex. |
| Agentes Codex 1 y 2 | Ejecutar las responsabilidades asignadas de planificación, implementación, validación o revisión sobre los artefactos acordados, dentro de `dev`. |
| Autor / human in the loop | Aprobar el alcance, resolver ambigüedades, revisar resultados y aprobar los PR. |

Si los dos agentes trabajan en paralelo, deben usar árboles de trabajo independientes, con archivos y responsabilidades delimitados. Cada traspaso debe indicar trabajo realizado, archivos afectados, validaciones, decisiones y bloqueantes, conforme al principio XI de la Constitución.

```mermaid
flowchart TD
    H["Autor / human in the loop"] -->|Aprueba alcance y asigna responsabilidades| O["Trabajo con ORCA AI"]
    O --> C1["Agente Codex 1"]
    O --> C2["Agente Codex 2"]
    S["Especificación, plan, tareas y contratos compartidos"] --> C1
    S --> C2
    C1 -->|Trabajo autorizado| D["dev: cambios coordinados"]
    C2 -->|Trabajo autorizado| D
    D --> V["Pruebas y evidencia de validación"]
    V --> P["Pull request de dev hacia main"]
    P --> R{"Revisión del autor"}
    R -->|Solicita cambios| D
    R -->|Aprueba| M["main: integración aprobada"]

    classDef agent fill:#EDE9FE,stroke:#7C3AED,color:#4C1D95
    classDef human fill:#FEF3C7,stroke:#D97706,color:#78350F
    classDef branch fill:#DBEAFE,stroke:#2563EB,color:#172554
    class O,C1,C2 agent
    class H,R human
    class D,M branch
```

Este diagrama describe el modelo de colaboración del experimento. La evidencia de la primera implementación registra trabajo de un único agente; todavía no acredita una ejecución paralela de ambos agentes.

## Avance al 20 de octubre de 2026

**Health check implementado y validado técnicamente: 11 de 12 tareas completadas.** La revisión humana de T012 y el cierre de SC-003 siguen pendientes. Los badges resumen la evidencia registrada; no representan un estado de CI en vivo ni el porcentaje de avance del motor de reportes.

| Hito | Estado y evidencia |
|---|---|
| Reglas del experimento | Constitución 1.0.0 ratificada: SDD, contratos, simplicidad, aislamiento y revisión humana. |
| Especificación y diseño | Especificación, plan, investigación, modelo de datos y contrato OpenAPI disponibles en [`specs/001-health-check/`](specs/001-health-check/). La autorización operativa está registrada en `validation.md`; el metadato histórico de la especificación conserva `Draft`. |
| Implementación | `GET /health` público con HTTP 200 y JSON exacto `{"status":"ok"}`. |
| Validación funcional | Cuatro escenarios aprobados en local y en contenedor sin red externa; consulta HTTP real sobre la imagen `runtime`. |
| Reproducibilidad | Dependencias bloqueadas con uv, imágenes base fijadas por digest y etapas Docker `base`, `test` y `runtime`. |
| Revisión técnica | Alcance y documentación revisados; imagen final con UID 10001, sin pruebas ni dependencias de desarrollo. |
| Correcciones registradas | Confianza TLS local, permisos de caché uv en Docker e importación de `app` al ejecutar `uv run pytest`; evidencia de fallos y soluciones conservada. |
| Cierre humano | T012 pendiente: revisión del resultado y registro de aprobación o cambios solicitados. La evidencia todavía no registra integración en `dev` ni `main`. |

### Conceptos puestos en práctica

- **SDD y trazabilidad:** especificación → plan → tareas → implementación → validación → revisión humana, con enlaces entre los artefactos.
- **Contrato explícito:** una única operación y respuesta exacta, verificadas desde la frontera HTTP.
- **Ciclo de prueba, fallo y corrección:** fallo inicial por capacidad ausente, implementación mínima y pruebas aprobadas; incidencias posteriores documentadas.
- **Reproducibilidad y mínimo privilegio:** bloqueo de dependencias, contenedores y separación entre pruebas y ejecución.
- **Disciplina de alcance:** cada dependencia y abstracción debe resolver una necesidad actual aprobada.
- **Responsabilidad multiagente y control humano:** trabajo delimitado, traspasos con evidencia y aceptación final a cargo del autor.

## Visión del motor de reportes

La Constitución define como objetivo un API Python/FastAPI que reciba definiciones declarativas YAML y genere archivos XLSX mediante XlsxWriter. El alcance inicial contempla títulos, tablas, imágenes controladas por el servidor y gráficos de líneas, barras, circulares y dona. Las solicitudes protegidas usarán tokens OAuth2/JWT con firma RSA y un servicio de identidad separado basado en OpenID Connect.

**Esta es la arquitectura objetivo; esas capacidades siguen fuera del incremento actual.** Su implementación requiere las especificaciones y aprobaciones correspondientes.

```mermaid
flowchart LR
    C["Consumidor"] -->|Autenticación OIDC| ID["Servicio de identidad separado"]
    ID -->|Token de acceso| C
    C -->|YAML + token OAuth2| API["API de reportes / FastAPI"]
    API --> AUTH["Validación JWT RSA con información pública"]
    AUTH --> Y["Validación de definición YAML"]
    Y --> CORE["Núcleo de reportes"]
    IMG["Imágenes permitidas por el servidor"] --> CORE
    CORE --> X["Adaptador XlsxWriter"]
    X --> F["Archivo XLSX nuevo"]
    F --> C

    classDef future fill:#F1F5F9,stroke:#64748B,color:#0F172A,stroke-dasharray:5 5
    class ID,API,AUTH,Y,CORE,IMG,X,F future
```

## Capacidad actual: health check mínimo

La única operación cubierta es `GET /health`: responde HTTP 200 y el objeto JSON `{"status":"ok"}`, sin credenciales. Confirma que la consulta fue atendida; no diagnostica el motor de reportes ni otros componentes.

## Requisitos

- Para ejecución local: Python 3.12 y uv 0.12.23.
- Para ejecución reproducible: Docker con motor Linux activo. Las imágenes de Python y uv están fijadas por digest en `Dockerfile`.
- Acceso a los registros durante la instalación o construcción. La consulta no necesita servicios externos.

Los ejemplos usan PowerShell desde la raíz del repositorio. `pyproject.toml` define las dependencias y `uv.lock` conserva el bloqueo completo. Los comandos habituales no regeneran el lock.

## Preparar y probar en local

```powershell
uv lock --check
uv sync --locked --python 3.12
uv run --locked --no-sync python -m pytest -q -p no:cacheprovider
```

Resultado esperado: cuatro pruebas aprobadas para respuesta exacta, acceso público, ausencia de recursos de reportes y tres consultas consecutivas independientes.

Si uv encuentra un emisor TLS desconocido y el certificado es de confianza en el sistema, usar `uv --system-certs sync --locked --python 3.12`. Esta opción fue necesaria en el entorno Windows de validación; no desactiva la comprobación TLS.

## Ejecutar en local

```powershell
$env:UVICORN_HOST = '127.0.0.1'
$env:UVICORN_PORT = '8000'
uv run --locked --no-sync --no-dev python -m uvicorn app:app
```

En otra consola:

```powershell
curl.exe --silent --show-error --fail-with-body --max-time 10 --max-redirs 0 --include http://127.0.0.1:8000/health
```

Se espera HTTP 200, `Content-Type: application/json` y el objeto indicado. Detener el servidor con Ctrl+C. En Linux puede usarse `curl` en lugar de `curl.exe`.

## Construir y validar en Docker

```powershell
docker build --target test -t sdd-health-check:test .
docker run --rm --network none sdd-health-check:test uv run --locked --no-sync python -m pytest -q -p no:cacheprovider
docker build --target runtime -t sdd-health-check:runtime .
docker run --rm --name sdd-health-check-validation -e UVICORN_HOST=0.0.0.0 -e UVICORN_PORT=8000 -p 127.0.0.1:8000:8000 sdd-health-check:runtime
```

Consultar desde otra consola con el mismo comando curl. Al terminar:

```powershell
docker stop sdd-health-check-validation
```

`runtime` ejecuta como UID 10001 y excluye tests y dependencias del grupo `dev`. `test` añade ese grupo y permite verificar los cuatro escenarios sin red externa, volúmenes ni credenciales. Los entornos preparados se ejecutan con `uv run --locked --no-sync`.

## Configuración y dependencias

- `UVICORN_HOST`: dirección de escucha; en Docker el valor predeterminado es `0.0.0.0`.
- `UVICORN_PORT`: puerto interno; predeterminado `8000`. Si se cambia, ajustar también el destino de `-p`.
- Para cambiar solo el puerto del host, usar por ejemplo `-p 127.0.0.1:8081:8000` y consultar el puerto 8081.
- Producción sincroniza con `uv sync --locked --no-dev`; desarrollo usa `uv sync --locked`.
- Al cambiar dependencias, editar `pyproject.toml`, ejecutar `uv lock`, revisar ambos archivos y repetir las validaciones. No hay archivos requirements como fuente principal.

Las pruebas emiten una advertencia de deprecación de Starlette por el uso de HTTPX; las cuatro pasan. Se mantienen las versiones del plan.

## Artefactos y evidencia

- [Especificación](specs/001-health-check/spec.md) y [plan](specs/001-health-check/plan.md).
- [Contrato HTTP](specs/001-health-check/contracts/health.openapi.json) y [tareas](specs/001-health-check/tasks.md).
- [Guía detallada de validación](specs/001-health-check/quickstart.md).
- [Resultados, incidencias y estado de revisión](specs/001-health-check/validation.md).

La implementación y las comprobaciones técnicas están registradas. La revisión humana previa a integración permanece pendiente; no se han integrado cambios en `dev` ni `main`.
