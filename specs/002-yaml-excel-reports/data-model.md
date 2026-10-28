# Diccionario normalizado v1

Norma de interfaces: [contracts/report-v1.md](contracts/report-v1.md). Sustituye el diseño anterior de dataclasses por decisión humana al generar tareas. No se crea model.py ni se añade una biblioteca de modelos.

## Claves y tipos exactos

El resultado es un dict estándar con exactamente estas claves:

| Ruta | Tipo Python | Contenido |
| --- | --- | --- |
| schema_version | int exacto | 1; bool no cuenta como entero |
| title | str | Título original |
| headers | list[str] | Encabezados originales en orden |
| rows | list[list[str &#124; int &#124; float]] | Filas originales en orden; sin coerción |
| chart | dict | Exactamente type, category_column, value_columns |
| chart.type | str | column |
| chart.category_column | int exacto | Índice cero basado en headers |
| chart.value_columns | list[int] | Índices cero basados, en orden de series, únicos |

Ejemplo normalizado del YAML del contrato:

```json
{
  "schema_version": 1,
  "title": "Ventas por región",
  "headers": ["Región", "Ventas"],
  "rows": [["Norte", 120], ["Sur", 90]],
  "chart": {"type": "column", "category_column": 0, "value_columns": [1]}
}
```

A transforma exclusivamente nombres de columnas del gráfico en índices y estructura de entrada en listas/dicts estándar. Preserva cadenas, tipos numéricos y orden. B consume el mismo diccionario sin modificarlo, sin reinterpretar YAML y sin introducir claves de presentación. No transportar rutas, colores, fórmulas, objetos PyYAML o tipos de XlsxWriter.

## Validación normativa

- Versión: «entero exacto 1; bool no cuenta como entero».
- Título y encabezados: «cadenas no vacías tras comprobar espacios; conservar texto original». Encabezados «únicos según casefold».
- Filas: «al menos una, longitud idéntica a encabezados». Solo «str/int/float finitos; excluir bool, null, fechas, objetos y estructuras anidadas».
- Referencias: nombres exactos resueltos a índices. «Categoría distinta de las series; categorías de texto no vacías». Series «numéricas en cada fila, no vacías y sin repetición». Categorías repetidas, cero y negativos permitidos.
- Texto: «caracteres representables en XML 1.0, máximo 32.767 caracteres; encabezados de tabla máximo 255». Sin truncamiento; cadenas que parecen fórmulas son válidas como texto.
- Números: «finitos entre -1.000.000.000 y 1.000.000.000 inclusive, máximo 15 cifras significativas». A DEBE preservar el texto original y el tag de cada escalar numérico mediante composición segura de nodos o constructores locales de SafeLoader que no conviertan a float. Validar con Decimal antes de cualquier conversión; no validar valores ya redondeados por yaml.safe_load ni usar Decimal(str(valor_float)) para reconstruir el original. Los enteros se interpretan de forma exacta; para escalares float se admite notación decimal, incluido exponente y separadores `_` retirados únicamente para construir Decimal; cualquier otra forma numérica no soportada produce ValueError explícito, sin conversión aproximada.
- Comprobar primero que Decimal es finito, después el rango inclusivo y las cifras significativas sobre sus dígitos exactos, ignorando ceros finales y sin aplicar normalizaciones que redondeen según el contexto Decimal; cero cuenta como una cifra. Rechazar NaN, infinito, exceso de rango o de cifras antes de convertir. Solo tras validar, devolver int para escalares enteros y float para escalares decimales; verificar que la conversión siga siendo finita y que Decimal(str(resultado_float)) sea igual al Decimal original, rechazando desbordamiento, subdesbordamiento o pérdida adicional. Esta última comprobación no sustituye la validación del original. No devolver Decimal ni nodos al diccionario normalizado; no convertir cadenas YAML entrecomilladas en números.
- Regresión obligatoria: el escalar original `1.0000000000000001` se rechaza por exceder 15 cifras significativas, sin convertirse primero en `1.0`. Probar además ambos extremos inclusivos, valores inmediatamente fuera del rango, cero, negativos, un valor decimal válido con 15 cifras, uno con 16, NaN e infinito.
- Dimensiones: «máximo 16.384 columnas y 255 series». Con N filas, gráfico anclado en fila cero basada N+4 y altura 360 puntos sobre filas vacías de 15 puntos: «N+28 <= 1.048.576».
- «Claves desconocidas o repetidas se rechazan en cualquier objeto». No se aceptan colores, fórmulas configurables, documentos adicionales ni tags ejecutables.
- La entrada a parse_report debe ser str; violación de tipo Python produce TypeError. Contenido inválido produce ValueError con ubicación. No normalizar espacios o mayúsculas para cambiar datos ni convertir cadenas numéricas en números.

## Flujo y errores

CLI B lee UTF-8 → parse_report de A valida → dict normalizado → build_xlsx de B → bytes completos → CLI B publica archivo nuevo. Ninguna de las dos funciones hace E/S de archivos o red.

parse_report usa ValueError para YAML/contenido inválido, sin filtrar excepciones PyYAML. build_xlsx usa RuntimeError para fallos de generación, sin filtrar excepciones XlsxWriter. No se necesita módulo compartido de excepciones. La precondición del constructor es un dict conforme a este contrato, no un segundo validador de YAML.

No hay estados de negocio o persistencia. Paleta exclusivamente en palette.py de B.
