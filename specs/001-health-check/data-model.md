# Data Model: Health check mínimo

## Objeto de respuesta: HealthResponse

Objeto JSON de salida correspondiente a FR-002; representa únicamente que la consulta fue atendida.

| Campo | Tipo | Obligatorio | Valor permitido |
|---|---|---|---|
| `status` | cadena | Sí | `ok` |

Reglas:

- El objeto contiene exactamente esta propiedad; no se permiten campos adicionales.
- No se admiten ausencia del campo, `null`, otros tipos ni otros valores.
- Los espacios en blanco de serialización no forman parte del contrato; se compara el JSON deserializado.
- No hay cuerpo de solicitud ni parámetros obligatorios para la consulta.

El esquema normativo está en [contracts/health.openapi.json](contracts/health.openapi.json). Este objeto conceptual no obliga a añadir una clase, un modelo de dominio ni persistencia al código.

## Identidad, relaciones y ciclo de vida

No existen entidades de negocio, identificadores, relaciones, almacenamiento ni transiciones de estado. Cada solicitud produce la misma respuesta sin consultar el estado de solicitudes anteriores (FR-005). No se registran sesiones ni datos del consumidor como requisito de esta feature.

La respuesta no representa disponibilidad de dependencias, salud del motor de reportes ni estado global del sistema. Las condiciones de arranque y accesibilidad del API son precondiciones de la especificación.
