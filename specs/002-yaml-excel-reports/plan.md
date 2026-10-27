# Implementation Plan: Reportes XLSX locales desde YAML

**Branch**: `dev` | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)

**Input**: Decisiones humanas de tecnología, VQM y reparto A/B. Actualizado al generar tareas: dict/bytes y CLI de B sustituyen dataclasses y CLI de A. Implementación no iniciada.

## Summary

Python 3.12: A implementa parse_report(text: str) -> dict (YAML, validación y normalización); B implementa build_xlsx(report: dict) -> bytes, paleta, gráfico, CLI, Docker y documentación. CLI compone funciones sin nuevas capas. Contrato único y archivos exclusivos, congelación previa al paralelo.

## Technical Context

**Language/Version**: Python 3.12.
**Primary Dependencies**: PyYAML y XlsxWriter. Conservar uv 0.12.23, pytest, FastAPI/uvicorn de salud. B fija versiones exactas compatibles y uv.lock antes del paralelo.
**Storage**: Solo YAML de entrada y XLSX nuevo.
**Testing**: pytest, zipfile, ElementTree y subprocess de biblioteca estándar.
**Target Platform**: Windows/Linux local y Docker Linux con digests existentes.
**Project Type**: CLI de repositorio: python -m reporting.
**Performance Goals**: Sin SLA arbitrario; respetar límites explícitos del formato.
**Constraints**: Sin fórmulas de usuario, red en ejecución, sobrescritura, estilos YAML o dependencias HTTP/Docker en lógica de reportes.
**Scale/Scope**: Un libro, una hoja, título, tabla y gráfico column con una o más series.

## Constitution Check

Evaluación previa/postdiseño: PASS de diseño, sin afirmar implementación validada.

| Principios | Aplicación |
| --- | --- |
| I, X y flujo SDD | Tareas tras planificación; aprobación y congelación antes de implementación paralela. Cambios de contrato solicitados expresamente por humano. |
| II, V, XII | Dos funciones concretas, dict estándar y CLI. Sin modelos, interfaces o capas artificiales. Modelo sin XlsxWriter; dependencia solo del escritor. |
| III, IV | Contrato explícito versionado y prueba productor-consumidor. Validar todo antes de generar. |
| VI, VII | Sin nuevos endpoints, identidad ni imágenes. Salud pública conservada. |
| VIII | uv.lock, versiones exactas y Docker existente; ejecución preparada sin red. |
| IX | Pruebas separadas, integración real y revisión humana Excel registrada. |
| XI | Árboles independientes desde mismo commit, archivos exclusivos, evidencia serializada. |

Sin cambios a Constitution v1.0.0 ni excepciones arquitectónicas.

## Project Structure

### Documentation (this feature)

spec.md, checklists/requirements.md, plan.md, research.md, data-model.md, contracts/report-v1.md, quickstart.md y tasks.md. No documento adicional para handoffs o evidencia: usar tasks.md.

### Source Code (proposed, not created)

```text
reporting/__init__.py           # B, vacío, preparación serial
reporting/yaml_input.py         # A: parse_report
reporting/xlsx_output.py        # B: build_xlsx
reporting/palette.py            # B
reporting/__main__.py           # B: CLI y E/S
examples/report.yaml            # B
tests/test_report_input.py      # A
tests/test_xlsx_output.py       # B
tests/test_xlsx_security.py     # B
tests/test_report_cli.py        # B
tests/test_report_integration.py # B
tests/test_health.py            # existente, sin cambiar contrato
app.py                         # existente
```

**Structure Decision**: Sin model.py ni excepciones propias. A depende de PyYAML/stdlib; B del dict, paleta, XlsxWriter/stdlib. Solo CLI importa ambos. El API no importa reportes.

## Phase 0 — Decisions

[research.md](research.md): carga segura, tipos estrictos, dict normalizado, texto literal, gráfico por referencias y reproducción Docker. No incógnitas de diseño; resolver versiones exactas en preparación serial.

## Phase 1 — Contract and design

[Contrato v1](contracts/report-v1.md), [datos normalizados](data-model.md). build_xlsx genera bytes completos en memoria y no muta report. CLI de B controla UTF-8, rutas, códigos y escritura exclusiva; ante errores no deja salida parcial ni modifica destinos previos.

Validación numérica de A: preservar escalares originales mediante nodos seguros o constructores locales de SafeLoader sin float previo; validar con Decimal finitud, rango inclusivo [-1.000.000.000, 1.000.000.000] y máximo 15 cifras significativas. Solo después normalizar a int/float conforme a data-model.md. T017 incluye regresión para `1.0000000000000001`, límites y valores no finitos. No cambia el dict compartido, ownership ni las dependencias.

Hoja Reporte: A1 título, fila 3 encabezados, fila 4 datos y gráfico debajo con fila vacía. B ajusta anchos/altos/texto y usa tabla Datos. Azure en todas las barras, sin violeta porque no hay significado secundario. Paleta completa en un único módulo; sin HEX duplicados en consumidores. Pruebas de estilos consumen constantes y revisión contrasta con FR-005.

### Freeze and ownership

Contrato y data-model definidos antes de tareas. T001 y T004 de tasks.md registran revisión humana y commit base común antes del paralelo. No afirmar congelación operativa mientras estén pendientes. B prepara dependencias e inicializador serialmente. Luego árboles independientes desde mismo commit; sin cambios privados a claves, firmas, reglas o errores.

| Responsable | Archivos exclusivos |
| --- | --- |
| A | reporting/yaml_input.py, tests/test_report_input.py |
| B | reporting/xlsx_output.py, reporting/palette.py, reporting/__main__.py, tests/test_xlsx_output.py, tests/test_xlsx_security.py, tests/test_report_cli.py, tests/test_report_integration.py, examples/report.yaml |
| B, serial/coordinación | reporting/__init__.py, pyproject.toml, uv.lock, Dockerfile, .dockerignore, README.md, quickstart.md, tasks.md y mantenimiento de artefactos SDD |

A nunca escribe presentación, CLI o documentación de B. B no modifica parser/tests de A; ante fallo pide corrección con evidencia. A entrega resultados y decisiones por handoff; solo B consolida marcadores/evidencia en tasks.md durante ejecución para evitar conflictos. Cambiar contrato requiere parar dependientes y revisión antes de continuar.

### Verification and Docker

Pruebas A: dict y validación, sin XLSX. Pruebas B: bytes, estilos/gráfico/seguridad y CLI con parser sustituido. Integración B usa parser y constructor reales después de reunir ambos trabajos. No basta probar mocks.

B reutiliza base/test/runtime, imágenes por digest, usuario no root y CMD de salud. Amplía COPY/.dockerignore para reporting, ejemplo y todas las pruebas. CLI sobrescribe comando runtime; entradas de solo lectura, salida escribible por UID 10001, sin montar .venv.

Cobertura: FR-001/008/010 CLI; FR-002/006 parser; FR-003/005/011 ZIP/XML de datos y estilos; FR-004 gráfico y referencias; FR-007 ausencia de fórmulas en celdas; FR-009 pruebas existentes y HTTP real. Ejecutar local, Docker test y generación runtime sin red. Revisión humana Excel final de legibilidad y actualización del gráfico al modificar tabla. Registrar comandos, resultados y omisiones en tasks.md.

## Complexity Tracking

Sin violaciones ni capas adicionales. PyYAML y XlsxWriter responden a requisitos actuales.
