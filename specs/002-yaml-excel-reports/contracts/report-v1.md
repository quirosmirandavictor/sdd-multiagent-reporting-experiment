# Contrato común v1 — YAML, dict y bytes XLSX

Definido por petición humana al generar tareas: sustituye las firmas anteriores load_report/write_report y las dataclasses. Antes del paralelo, registrar en tasks.md la revisión y el commit aprobado de este contrato y data-model.md. No se declara congelado un commit todavía no registrado. Ambos agentes parten de ese mismo contrato; cambios incompatibles suspenden trabajo dependiente hasta revisión.

## Entrada YAML

Un documento UTF-8 con exactamente estas claves obligatorias:

```yaml
schema_version: 1
title: "Ventas por región"
headers: ["Región", "Ventas"]
rows:
  - ["Norte", 120]
  - ["Sur", 90]
chart:
  type: column
  category: "Región"
  values: ["Ventas"]
```

chart admite exactamente type/category/values. type solo column; category es nombre exacto de encabezado y values lista no vacía de nombres exactos de columnas numéricas, ordenada por series. Sin índices, rangos Excel ni expresiones de entrada. Claves/nombres sensibles a mayúsculas; encabezados únicos también según casefold. Rigen las restricciones de [data-model.md](../data-model.md), sin coerciones. Rechazar estilos, tags ejecutables, claves duplicadas y documentos adicionales.

## Frontera Python obligatoria

```text
reporting.yaml_input.parse_report(text: str) -> dict
reporting.xlsx_output.build_xlsx(report: dict) -> bytes
```

- A es propietario de parse_report: recibe texto, usa carga segura, valida todo y devuelve exclusivamente el dict de data-model.md. No lee archivos ni importa presentación. Contenido inválido: ValueError con campo/fila o ubicación YAML cuando corresponda; argumento no str: TypeError.
- A preserva el escalar numérico original mediante nodos seguros o constructores locales de SafeLoader sin conversión previa a float. Valida con Decimal valores finitos en [-1.000.000.000, 1.000.000.000], ambos extremos incluidos, y máximo 15 cifras significativas antes de normalizar a int/float. Aplicar las reglas exactas de notación, cifras y conversión de data-model.md; rechazar NaN, infinito y `1.0000000000000001`. El contrato público sigue devolviendo solo dict/list/str/int/float; no Decimal ni nodos YAML.
- B es propietario de build_xlsx: recibe el dict validado y devuelve bytes XLSX completos después de cerrar Workbook en BytesIO. No modifica el dict ni realiza E/S de archivos. Fallo de generación: RuntimeError con causa encadenada; no devolver bytes parciales.
- Diccionario exacto: schema_version:int, title:str, headers:list[str], rows:list[list[str|int|float]], chart:dict con type:str="column", category_column:int y value_columns:list[int]. Los índices son cero basados y ya están resueltos por A. Detalles, ejemplo y límites normativos en data-model.md.
- Sin clases de dominio, tipos de XlsxWriter en contrato, protocolos, fachada adicional ni módulo de errores. built-ins bastan. No compartir código de presentación ni mutar datos entre agentes.

## CLI de B

```text
python -m reporting --input <archivo.yaml> --output <archivo.xlsx>
```

- B lee archivo UTF-8, llama parse_report, luego build_xlsx y finalmente escribe bytes. Errores de decodificación se presentan como validación.
- Dos argumentos obligatorios, sin subcomandos/sobrescritura. --help estándar argparse sin crear archivos.
- Rutas relativas al directorio de trabajo. Salida .xlsx sin distinguir mayúsculas; padre existente y escribible; destino nuevo.
- Código 0: bytes escritos correctamente; stdout: Reporte generado: <ruta absoluta>, con salto de línea.
- Código 2: argumentos inválidos (argparse) o ValueError de parse_report/decodificación; stderr: Error de validación: <detalle>.
- Código 1: OSError de archivos o RuntimeError de build_xlsx; stderr: Error de archivo: <ruta>: <detalle>, usando salida para errores de generación.
- Sin traceback en errores esperados ni mensaje de éxito prematuro. Detalle identifica campo/fila o ruta sin congelar puntuación interna.
- Generar bytes antes de abrir salida; reservar con creación exclusiva (xb) y rechazar destino previo sin alterarlo. En error de escritura, limpiar solo archivo creado por la misma operación. No crear directorios automáticamente. Lectura y validación siempre antes de generación.

## XLSX e identidad

Una hoja Reporte: título A1, fila 2 vacía, encabezados fila 3 y datos desde fila 4. Tabla estructurada Datos, sin totales. Gráfico bajo tabla tras fila vacía. Rangos construidos desde índices y filas; nombres de series referidos a encabezados. No fórmulas de celdas ni hipervínculos automáticos desde cadenas; referencias internas del gráfico permitidas.

Paleta FR-005 desde palette.py: título Navy, encabezados Azure/blanco, primera fila blanca y siguientes alternadas azul claro/blanco, bordes gris aprobado, barras Azure. No violeta por falta de significado secundario, logo ni 3D. Sin tema predeterminado que sustituya estilos. Ninguna clave YAML puede cambiar paleta.

## Compatibilidad e integración

GET /health conserva HTTP 200 y exactamente {"status":"ok"}, público y sin dependencia de reportes.

Prueba real de B: texto ejemplo → parse_report real de A → dict → build_xlsx real de B → inspección de bytes y CLI que crea archivo. Verificar datos, tipos, estilos, gráfico/rangos y no mutación. Mocks de CLI y datos de prueba del constructor no sustituyen integración. Registrar comandos, resultados, commit y pendientes en tasks.md antes de aceptar.
