# Ejecución y verificación previstas

Responsable: agente B. B mantendrá esta guía y README de instalación, ejecución y verificación. Borrador de diseño: estos comandos requieren la futura implementación; no se presentan como ejecutados.

## Local

Python 3.12, uv 0.12.23 y dependencias bloqueadas durante preparación serial. Desde raíz del repositorio:

```powershell
uv lock --check
uv sync --locked --python 3.12
uv run --locked --no-sync python -m pytest -q -p no:cacheprovider
New-Item -ItemType Directory -Force output
uv run --locked --no-sync --no-dev python -m reporting --input examples/report.yaml --output output/report.xlsx
```

Esperado: suite satisfactoria, código 0 y XLSX nuevo. Repetir generación sobre mismo destino devuelve 1 y conserva archivo previo. Usar otro nombre para repetir; no borrar resultados automáticamente. Ejemplo definido por [contrato](contracts/report-v1.md).

## Docker

Motor Linux activo. B ampliará contexto permitido/COPY, conservará usuario no root y CMD de salud. Crear output en host y asegurar escritura por UID 10001; en Linux ajustar propietario/permisos explícitamente, sin cambiar a root.

```powershell
docker build --target test -t sdd-report:test .
docker run --rm --network none sdd-report:test
docker build --target runtime -t sdd-report:runtime .
docker run --rm --network none --mount "type=bind,source=$((Get-Location).Path)/examples,target=/input,readonly" --mount "type=bind,source=$((Get-Location).Path)/output,target=/output" sdd-report:runtime uv run --locked --no-sync --no-dev python -m reporting --input /input/report.yaml --output /output/report-docker.xlsx
```

Instalación/construcción puede acceder a registros; ejecución preparada no necesita servicios externos. No montar .venv ni instalar durante docker run.

## Escenarios

1. YAML mal formado, tags ejecutables, versiones inválidas, claves repetidas/desconocidas, tipos erróneos, dimensiones, series no numéricas, referencias ausentes o intento de colores: salida 2 y ningún archivo generado.
2. Entrada ausente, destino previo, padre ausente/no escribible: salida 1, archivo previo intacto. --help no genera archivos.
3. Texto que parece fórmula sigue literal en título, encabezados y datos; cero fórmulas en celdas. Negativos siguen numéricos; referencias del gráfico no se confunden con fórmulas de usuario.
4. Pruebas ZIP/XML de valores/tipos, tabla Datos, estilos de título/encabezados/filas/bordes, gráfico column, Azure y rangos correctos. Verificar salida real, no solo existencia/mocks.
5. Mantener cuatro pruebas de salud. Ejecutar runtime con CMD predeterminado y comprobar tres respuestas HTTP reales 200 con JSON exacto, sin credenciales, usando comandos del README existente.
6. Persona abre los dos reportes en Excel: sin reparación, título/tabla legibles, colores VQ, sin solapamientos/3D/logo, gráfico correcto. Cambia dato numérico de origen y comprueba actualización del gráfico. Registrar resultado y pendientes antes de aceptar.

B registrará comandos, resultados, persona revisora y comprobaciones fallidas/omitidas en tasks.md durante implementación. No se crea evidencia ficticia. XML no demuestra validación visual humana.

## Frontera de integración actualizada

A aporta parse_report(text: str) -> dict; B aporta build_xlsx(report: dict) -> bytes y la CLI de lectura/escritura. Prueba real en tests/test_report_integration.py, no funciones de carga/escritura anteriores. A ejecuta tests/test_report_input.py; B ejecuta tests/test_xlsx_output.py, tests/test_xlsx_security.py y tests/test_report_cli.py. B consolida suite completa e integración local/Docker y revisión humana en el registro de tasks.md; A entrega evidencia sin editar ese registro concurrentemente.
