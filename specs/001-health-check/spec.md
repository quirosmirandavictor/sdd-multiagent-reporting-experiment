# Feature Specification: Health check mínimo

**Feature Branch**: `dev` (rama actual; sin creación de rama para esta especificación)

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "Crear una capacidad mínima de health check cuyo único objetivo sea validar el workflow SDD end-to-end del proyecto. GET /health debe responder HTTP 200 con {\"status\":\"ok\"}. Fuera de alcance: autenticación, persistencia, YAML, generación de Excel, imágenes, gráficos, servicios externos y procesamiento background. Respetar la Constitution 1.0.0 vigente."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar el health check mínimo (Priority: P1)

Como consumidor del API, quiero consultar el health check y recibir una respuesta de éxito conocida para que el equipo pueda verificar una capacidad mínima durante el recorrido SDD de principio a fin.

**Why this priority**: Es la única capacidad funcional de esta feature y permite validar el workflow sin incorporar funciones del motor de reportes.

**Independent Test**: Con el API iniciado y accesible, realizar `GET /health` sin credenciales y comprobar HTTP 200 y un cuerpo JSON igual a `{"status":"ok"}`.

**Acceptance Scenarios**:

1. **Given** el API iniciado y accesible, **When** un consumidor realiza `GET /health`, **Then** recibe HTTP 200 y un objeto JSON con una única propiedad `status` cuyo valor es la cadena `ok`.
2. **Given** el API iniciado y accesible y un consumidor sin credenciales, **When** realiza `GET /health`, **Then** recibe la misma respuesta de éxito sin autenticación ni redirección a un servicio de identidad.
3. **Given** el API iniciado y accesible sin persistencia, definiciones YAML, archivos de reporte ni servicios externos, **When** un consumidor realiza `GET /health`, **Then** recibe la respuesta definida sin necesitar esos recursos.
4. **Given** el API iniciado y accesible, **When** un consumidor realiza tres solicitudes consecutivas a `GET /health`, **Then** cada solicitud recibe HTTP 200 y el mismo objeto JSON, sin requerir información de solicitudes anteriores.

### Edge Cases

- La ausencia de credenciales no impide la consulta: se aplica el escenario 2.
- La ausencia de recursos del motor de reportes o servicios externos no impide la respuesta: se aplica el escenario 3.
- Las consultas repetidas conservan el contrato: se aplica el escenario 4.
- Si el API está detenido o no es accesible, no se cumple la precondición de esta consulta; esta feature no incorpora recuperación ni diagnóstico de esa situación.
- Otras rutas y otros métodos HTTP quedan fuera del contrato de esta feature.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El API DEBE aceptar una solicitud `GET /health` cuando esté iniciado y accesible, y responder HTTP 200. Verificación: escenario 1.
- **FR-002**: El cuerpo de esa respuesta DEBE ser un objeto JSON con exactamente una propiedad `status` de tipo cadena y valor `ok`. La comparación DEBE realizarse sobre el objeto JSON; el espacio en blanco no forma parte del contrato. Verificación: escenarios 1 y 4.
- **FR-003**: El consumidor DEBE poder realizar la consulta sin autenticación, credenciales ni interacción con un servicio de identidad. Verificación: escenario 2.
- **FR-004**: La consulta DEBE resolverse sin persistencia, lectura o validación de YAML, generación de Excel, procesamiento de imágenes o gráficos, llamadas a servicios externos ni procesamiento background. Verificación: escenario 3 y revisión del alcance en plan, tareas e implementación.
- **FR-005**: Cada consulta DEBE producir la respuesta definida sin depender del estado de consultas anteriores. Verificación: escenario 4.

### Scope and Constitutional Constraints

- El alcance funcional se limita a `GET /health` y su respuesta fija. Quedan fuera autenticación, persistencia, YAML, generación de Excel, imágenes, gráficos, servicios externos y procesamiento background.
- Esta exclusión se refiere únicamente a esta feature; no modifica el alcance inicial del motor de reportes ni la Constitution 1.0.0.
- La consulta es pública. Las obligaciones de autorización de solicitudes protegidas del principio VI permanecen vigentes para las funcionalidades a las que correspondan.
- El plan DEBE respetar la arquitectura limpia mínima y justificar cualquier capa, abstracción o dependencia por una necesidad actual, conforme a los principios II y XII.
- La ejecución del servicio DEBE ser reproducible mediante contenedores, con configuración de ambiente externalizada y dependencias declaradas y versionadas de forma reproducible, conforme al principio VIII. Esta obligación no añade comportamiento al contrato de la consulta.
- Antes de implementar DEBEN existir una especificación aprobada, un plan compatible con la Constitución y tareas con responsabilidades definidas. Antes de integrar DEBEN verificarse los criterios de aceptación, incluirse la prueba de integración del contrato y revisarse el resultado, conforme a los principios I, III y IX y al flujo obligatorio de desarrollo.
- Los resultados de validación y cualquier prueba fallida, omitida o imposible de ejecutar DEBEN registrarse. No se considerará validado el recorrido SDD completo por la sola creación de esta especificación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El consumidor obtiene el resultado de éxito acordado en el 100 % de las consultas de los cuatro escenarios de aceptación, incluidas las tres consultas consecutivas.
- **SC-002**: El consumidor puede completar la consulta con cero credenciales, cero definiciones de reporte y cero servicios externos disponibles como prerrequisitos.
- **SC-003**: El equipo dispone de un recorrido SDD completo y trazable para esta única capacidad: especificación aprobada, plan, tareas, implementación, resultados de validación de los cuatro escenarios y revisión previa a la integración. Cada etapa cuenta con evidencia registrada antes de declarar cumplido el objetivo del experimento.

## Assumptions

- Las verificaciones funcionales se realizan con el API iniciado y accesible; no se presupone una capacidad de diagnóstico de dependencias o de disponibilidad de infraestructura.
- La respuesta fija confirma únicamente que se atendió esta consulta. No certifica el funcionamiento del motor de reportes ni de otros componentes.
- Esta especificación no depende de datos de negocio ni de servicios externos. La preparación del entorno reproducible y las decisiones de implementación corresponden al plan, dentro de la Constitution 1.0.0.
- No se añaden objetivos de rendimiento, concurrencia ni funcionalidades adicionales al contrato solicitado.
