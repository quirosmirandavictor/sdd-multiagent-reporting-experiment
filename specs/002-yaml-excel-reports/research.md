# Decisiones técnicas

## Carga y validación

- **Decision**: SafeLoader específico de PyYAML, sin constructores ejecutables, con rechazo de claves repetidas; un documento UTF-8. Validación estricta antes de crear salida.
- **Rationale**: La carga segura no sustituye validación; tipos implícitos como fechas y booleanos deben rechazarse por contrato.
- **Decision — corrección A1 autorizada**: Preservar texto/tag de escalares numéricos con composición segura o constructores locales SafeLoader, sin float previo. Validar el original con Decimal: finito, rango inclusivo [-1.000.000.000, 1.000.000.000] y hasta 15 cifras significativas; convertir a int/float solo después. No reconstruir el original desde valores ya cargados por yaml.safe_load. Regresión planificada para `1.0000000000000001`, extremos, exceso de cifras, NaN e infinito; detalles normativos en data-model.md. Decimal es biblioteca estándar, sin dependencias nuevas.
- **Alternatives considered**: Carga arbitraria insegura, Pydantic o JSON Schema como dependencias adicionales innecesarias.
- **Source**: [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation).

## Texto y gráfico seguros

- **Decision**: write_string para todas las cadenas; strings_to_formulas=False y strings_to_urls=False. Números mediante escritura numérica. Gráfico type=column y rangos internos por índices; nombres de serie referidos a encabezados.
- **Rationale**: write genérico reconoce fórmulas y URLs por defecto. Ningún texto de usuario debe convertirse en expresión; referencias internas de gráfico sí son necesarias.
- **Alternatives considered**: Apóstrofos que alteran texto, valores copiados al gráfico o fórmulas de usuario.
- **Sources**: [Worksheet](https://xlsxwriter.readthedocs.io/worksheet.html), [Workbook](https://xlsxwriter.readthedocs.io/workbook.html), [Chart](https://xlsxwriter.readthedocs.io/chart.html).

## Reproducibilidad

- **Decision**: Mantener Python 3.12, uv 0.12.23 y digests/etapas existentes. Resolver nuevas versiones una vez, fijarlas y bloquearlas. Preparar con uv sync --locked; ejecutar con uv run --locked --no-sync.
- **Rationale**: --locked detecta divergencia con metadatos; --frozen omite esa comprobación. Reutilizar lo existente evita nueva infraestructura.
- **Alternatives considered**: Otro gestor, Dockerfile separado, Compose o instalación durante ejecución.
- **Sources**: [uv sync](https://docs.astral.sh/uv/concepts/projects/sync/), [uv Docker](https://docs.astral.sh/uv/guides/integration/docker/).

## Modelo y pruebas

- **Decision**: Diccionario estándar con claves y tipos congelados en el contrato; pytest, zipfile y ElementTree para inspeccionar salida real; revisión humana final en Excel.
- **Rationale**: Frontera dict→bytes estable sin dependencia de presentación; XML comprueba valores, estilos y referencias sin otra biblioteca.
- **Alternatives considered**: Interfaces abstractas, modelos de XlsxWriter u openpyxl solo para pruebas.
- **Basis**: Decisión de diseño derivada de FR-007/011 y principios II, III, IX y XII. La inspección XML no demuestra legibilidad visual.

No quedan incógnitas de diseño. Versiones exactas se resolverán y registrarán en pyproject/lock durante preparación serial antes del paralelo.

## Cambio humano de contrato y ownership

- **Decision**: parse_report(text: str) -> dict para A; build_xlsx(report: dict) -> bytes y CLI/E/S para B; funciones sin acceso a archivos. Sustituir dataclasses y firmas anteriores, sin modelo adicional.
- **Rationale**: Instrucción explícita al generar tareas, contrato sencillo compartido antes del paralelo. ValueError/RuntimeError estándar evitan otro módulo compartido.
- **Alternatives considered**: Mantener dataclasses y CLI en A (contradice el reparto actualizado); compartir archivos de pruebas o documentación (riesgo de conflictos).
