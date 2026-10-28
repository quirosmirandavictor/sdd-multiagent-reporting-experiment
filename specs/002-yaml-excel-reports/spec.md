# Feature Specification: Generación local de reportes Excel desde YAML

**Feature Branch**: `dev` (rama actual; sin hook de creación de rama)

**Created**: 2026-10-26

**Status**: Approved — especificación aprobada por el responsable del experimento el 2026-10-26; implementación no iniciada

**Human Approval**: Aprobación explícita registrada en T001 de [tasks.md](tasks.md). Alcance aprobado: entrada YAML local; validación segura y precisa; generación XLSX mediante XlsxWriter; título, tabla y gráfico de barras verticales; paleta visual VQ; CLI, pruebas, Docker y README reproducible; conservación de `GET /health`. Esta aprobación no inicia la implementación ni modifica la Constitution v1.0.0.

**Input**: User description: "Crear una feature final de generación local de reportes Excel desde YAML. Entrada: título, encabezados, filas de datos y definición de gráfico de barras verticales. Salida: archivo XLSX con título y tabla formateados, gráfico basado en datos de la tabla y paleta VQ obligatoria. Ejecución local mediante CLI y ejemplo funcional. Validar datos incorrectos y no ejecutar fórmulas provenientes del YAML. Conservar GET /health. Fuera de alcance: autenticación, nuevos endpoints públicos, persistencia, interfaz gráfica, imágenes, otros gráficos y servicios externos. Respetar Constitution v1.0.0. No agregar funciones no solicitadas."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Obtener un reporte local con identidad VQ (Priority: P1)

Como persona que prepara reportes, quiero ejecutar un comando local con una definición YAML para obtener un libro Excel que presente mis datos y un gráfico de barras verticales con la identidad VQ.

**Why this priority**: Es el resultado completo solicitado y evita preparar manualmente la tabla y su gráfico.

**Independent Test**: Ejecutar el ejemplo documentado en un entorno preparado, sin iniciar el API y sin acceso a servicios externos; abrir el archivo resultante y cotejar título, tabla, colores y gráfico con la definición de entrada.

**Acceptance Scenarios**:

1. **Given** una definición válida con título, encabezados, filas y gráfico, **When** se ejecuta la CLI indicando entrada y salida locales, **Then** se crea un XLSX nuevo, se informa su ubicación y el comando termina con éxito.
2. **Given** el archivo generado, **When** se inspecciona su contenido, **Then** contiene el título y todos los encabezados y valores en el orden declarado, con título destacado, encabezados distinguibles de los datos y contenido sin solapamiento entre título, tabla y gráfico.
3. **Given** una definición que selecciona categorías y valores de la tabla, **When** se inspecciona el gráfico, **Then** es de barras verticales y sus categorías, nombres de series y valores corresponden a las celdas seleccionadas de esa tabla; al cambiar un valor de origen en el libro, el gráfico refleja ese cambio.
4. **Given** el contrato visual VQM Engineering definido en FR-005, **When** se revisan título, encabezados, filas y barras, **Then** el título es Navy, los encabezados tienen fondo Azure y texto blanco, las filas alternan blanco y azul claro y las barras usan Azure como color principal, sin colores aleatorios, efectos 3D ni decoración innecesaria.
5. **Given** el repositorio y sus instrucciones de preparación, **When** se ejecuta el comando documentado para el ejemplo incluido, **Then** se obtiene el reporte anterior sin escribir código adicional, usar credenciales ni iniciar servicios.
6. **Given** una definición que intenta sobrescribir la paleta mediante propiedades de estilo, **When** se valida el YAML, **Then** se rechaza como configuración no admitida y no se genera un reporte.
7. **Given** un reporte generado con sus verificaciones automatizadas satisfactorias, **When** una persona abre el XLSX en Excel para la revisión final, **Then** comprueba legibilidad, formato del título y la tabla, colores VQ y funcionamiento y correspondencia de datos del gráfico; su resultado se registra antes de considerar validada la presentación.

### User Story 2 - Detectar entradas incorrectas y proteger los datos (Priority: P1)

Como persona que ejecuta la herramienta, quiero recibir errores comprensibles ante definiciones inválidas y conservar los textos como datos para evitar reportes incorrectos o ejecución de contenido suministrado.

**Why this priority**: La validación previa y la ausencia de ejecución de fórmulas son condiciones necesarias para generar un reporte seguro.

**Independent Test**: Ejecutar la CLI con entradas inválidas y con cadenas que parecen fórmulas; comprobar los errores y el contenido del libro válido sin depender de la comprobación visual de colores.

**Acceptance Scenarios**:

1. **Given** un YAML mal formado, un campo obligatorio ausente, un tipo incorrecto, una propiedad desconocida o una versión no soportada, **When** se ejecuta la CLI, **Then** termina con error, identifica el problema y no genera un reporte ni altera un archivo de salida existente.
2. **Given** filas incompatibles con los encabezados, referencias inexistentes, valores no numéricos para las barras o un tipo de gráfico distinto del admitido, **When** se ejecuta la CLI, **Then** rechaza la definición completa antes de generar el libro e identifica el campo o fila incorrectos.
3. **Given** cadenas como `=1+1`, `+SUM(A1:A2)`, `-SUM(A1:A2)` y `@SUM(A1:A2)` en título, encabezados o celdas de texto no usadas como valores numéricos, **When** se genera y abre el libro, **Then** permanecen como texto literal y no se ejecutan como fórmulas; los números negativos declarados como números conservan su valor numérico.
4. **Given** una entrada ilegible o una salida no escribible, **When** se ejecuta la CLI, **Then** termina con error e informa la ruta afectada sin presentar la operación como exitosa.
5. **Given** contenido YAML que intenta ejecutar código o cargar objetos ejecutables, **When** se procesa la entrada, **Then** se rechaza sin ejecutar ese contenido.

### User Story 3 - Conservar la consulta de salud (Priority: P2)

Como consumidor del servicio existente, quiero seguir consultando su salud con el mismo contrato después de incorporar la herramienta local.

**Why this priority**: Evita una regresión de la capacidad ya entregada.

**Independent Test**: Iniciar el servicio existente y realizar tres consultas a `GET /health` sin credenciales ni archivos de reporte.

**Acceptance Scenarios**:

1. **Given** el servicio iniciado sin definiciones de reporte ni servicios externos disponibles, **When** se consulta `GET /health` sin credenciales tres veces, **Then** cada respuesta tiene HTTP 200 y exactamente el objeto JSON `{"status":"ok"}`.

### Edge Cases

- Definición vacía, título vacío, encabezados vacíos o repetidos, ausencia de filas y filas con cantidad incorrecta de celdas: rechazo explícito antes de generar.
- Valores anidados donde se esperan celdas simples, números no finitos o valores vacíos en una serie numérica: rechazo con ubicación del problema.
- Gráfico sin categorías o series, referencias ambiguas o inexistentes y gráficos no verticales: rechazo explícito.
- Valores numéricos cero o negativos: se conservan como números y se representan en el gráfico sin convertirlos en texto por la protección contra fórmulas.
- Textos con acentos y caracteres españoles: se conservan en título, encabezados, tabla y etiquetas.
- Ruta de entrada inexistente, salida bloqueada o falta de permisos: error de operación con estado de salida fallido.
- Destino existente: no modificarlo ni sobrescribirlo; la herramienta genera únicamente archivos nuevos.
- Datos que exceden la capacidad del formato de salida: error explícito, sin truncamiento silencioso.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La herramienta DEBE ejecutarse localmente mediante CLI con una ruta de entrada YAML y una ruta de salida XLSX, sin depender del API, de autenticación ni de servicios externos. DEBE comunicar éxito y ubicación del archivo o fracaso mediante mensaje y estado de salida. Verificación: historia 1, escenarios 1 y 5; historia 2, escenario 4.
- **FR-002**: La entrada DEBE definir un título, encabezados, filas y un único gráfico de barras verticales que seleccione categorías y una o más series numéricas de la misma tabla. El contrato DEBE identificar su versión y rechazar versiones no soportadas. Los nombres concretos de campos y argumentos se definirán explícitamente en el plan antes de implementar y se usarán sin variaciones en documentación, ejemplo y pruebas. Verificación: historias 1 y 2.
- **FR-003**: El archivo DEBE contener el título destacado y una tabla con encabezados visualmente diferenciados y todas las filas originales, conservando valores, tipos de texto o número y orden, sin truncamiento ni solapamiento entre los componentes. Verificación: historia 1, escenario 2.
- **FR-004**: El gráfico DEBE ser de barras verticales y basarse en referencias a las celdas de la tabla generada, con categorías y series correspondientes a la selección declarada. No se admiten otros tipos de gráfico. Verificación: historia 1, escenario 3; historia 2, escenario 2.
- **FR-005**: El reporte DEBE aplicar obligatoriamente el contrato visual VQM Engineering indicado a continuación. El YAML NO DEBE poder sobrescribir la paleta; los intentos de configuración visual no admitida se rechazan conforme a FR-006. Verificación: historia 1, escenarios 4 y 6.

  | Color aprobado | HEX | Uso |
  | --- | --- | --- |
  | Azure principal | `#0078D4` | Fondo de encabezados y color principal de barras |
  | Navy | `#0F172A` | Color del título del reporte |
  | Violeta secundario | `#6D5DF6` | Acento secundario opcional, únicamente cuando tenga un significado visual claro |
  | Azul claro | `#EAF2FF` | Fondo alterno de filas de datos |
  | Blanco | `#FFFFFF` | Texto de encabezados y fondo alterno de filas de datos |
  | Gris de bordes | `#E2E8F0` | Color de los bordes de la tabla |

  Las filas DEBEN alternar blanco y azul claro con contraste y legibilidad. No se exige utilizar violeta: si se utiliza, su significado DEBE quedar explícito en el plan y verificarse en la revisión humana. Se DEBEN evitar colores aleatorios, fondos oscuros dominantes, efectos 3D y elementos decorativos innecesarios. No se DEBE insertar ni recrear el logotipo VQ.
- **FR-006**: Toda la definición DEBE validarse antes de iniciar la generación. Se DEBEN rechazar sintaxis inválida, campos obligatorios ausentes, propiedades desconocidas, versiones y componentes no soportados, tipos incorrectos y los casos inválidos enumerados en Edge Cases. Los errores DEBEN identificar el campo, fila o referencia afectados cuando corresponda, sin producir un reporte ni modificar un destino existente. Verificación: historia 2, escenarios 1 y 2.
- **FR-007**: El YAML DEBE tratarse exclusivamente como datos declarativos. No se DEBE ejecutar código, cargar objetos ejecutables ni convertir texto del usuario en fórmulas de celdas. Esta protección incluye título, encabezados y datos; no impide las referencias internas necesarias del gráfico a su tabla. Verificación: historia 2, escenarios 3 y 5.
- **FR-008**: Se DEBE incluir un ejemplo YAML funcional y documentación con preparación del entorno, comando completo, ubicación del resultado y contenido esperado. El ejemplo DEBE demostrar título y tabla formateados, paleta VQ y gráfico derivado de la tabla. Verificación: historia 1, escenario 5.
- **FR-009**: `GET /health` DEBE conservar HTTP 200 y exactamente `{"status":"ok"}`, sin autenticación y sin depender de definiciones, archivos generados o servicios externos. Verificación: historia 3.
- **FR-010**: La herramienta DEBE crear archivos nuevos; ante errores de lectura o escritura DEBE informar fracaso y la ruta afectada. Un destino existente DEBE rechazarse sin alterarlo. Verificación: historia 2, escenario 4 y Edge Cases.
- **FR-011**: Las pruebas automatizadas DEBEN comprobar, cuando sea viable, los estilos del título, encabezados, alternancia de filas y colores de barras, la existencia de un gráfico de columnas y sus referencias a las columnas y filas correspondientes de la tabla. La validación visual final DEBE realizarla una persona abriendo el XLSX en Excel. Las comprobaciones no automatizables o no ejecutadas DEBEN identificarse explícitamente; no equivalen a una validación satisfactoria. Verificación: historia 1, escenarios 2, 3, 4 y 7.

### Visual Architecture and Ownership Constraints

- La paleta DEBE definirse en un único módulo Python reutilizable. No se DEBEN duplicar códigos HEX entre componentes ni añadir frameworks de diseño o dependencias para gestionar colores.
- El agente B, responsable de generar el XLSX, es el único responsable de aplicar estilos, consumir la paleta y crear el gráfico de columnas mediante XlsxWriter. El agente A NO DEBE implementar lógica de presentación.
- El gráfico DEBE tomar sus categorías y valores de las columnas correspondientes a la tabla generada, conforme a FR-004, sin duplicar datos como fuente independiente del gráfico.
- Se DEBE mantener Minimal Clean Architecture: estas decisiones no autorizan nuevas capas ni acoplar el núcleo a detalles de XlsxWriter. El módulo de paleta y la aplicación de estilos pertenecen a la responsabilidad de generación, fuera del contrato de datos del agente A.
- Al generar el plan y las tareas, se DEBEN trasladar estas restricciones a las responsabilidades de B y definir las verificaciones de FR-011 y la revisión humana final. Esta asignación no inicia ni autoriza implementación en esta actualización documental.

### Scope and Constitutional Constraints

- Alcance final de esta feature: generación local desde YAML de un libro con título, una tabla y un gráfico de barras verticales, con ejemplo y validación. Quedan fuera autenticación, nuevos endpoints públicos, persistencia adicional al archivo de salida solicitado, interfaz gráfica, imágenes, otros gráficos y servicios externos.
- La petición expresa del usuario registra la decisión humana de limitar esta entrega a esos componentes. No modifica la Constitution v1.0.0 ni elimina capacidades del alcance general del experimento. No se incorporan servicios de identidad ni nuevas solicitudes protegidas.
- El plan DEBE cumplir los principios II, III, V, VIII y XII: arquitectura mínima, contratos explícitos, frontera de generación exigida por la Constitution, dependencias reproducibles y ninguna abstracción o dependencia sin necesidad actual. Las tecnologías constitucionalmente obligatorias se concretarán en el plan, sin añadir capacidades funcionales.
- La ejecución local DEBE funcionar sin iniciar el servicio web ni contenedores. La reproducibilidad mediante contenedores exigida por la Constitution permanece vigente y se abordará en el plan, sin crear servicios adicionales.
- Conforme a los principios I, IX y X, la especificación requiere aprobación antes de implementar; después deben existir plan y tareas, verificaciones registradas y revisión antes de integrar en `dev`. La aclaración VQ queda resuelta mediante el contrato visual aprobado por el usuario. Esta actualización documental no acredita funcionamiento del software ni inicia implementación.

### Key Entities *(include if feature involves data)*

- **Definición de reporte**: Documento declarativo versionable que reúne título, tabla y gráfico.
- **Tabla**: Encabezados ordenados y filas de valores; fuente única de las categorías y series del gráfico.
- **Definición de gráfico**: Selección de categorías y series numéricas de la tabla para representarlas como barras verticales.
- **Paleta VQ**: Los seis colores aprobados y sus usos visuales en FR-005, compartidos por tabla y gráfico mediante una única definición reutilizable.
- **Reporte generado**: Archivo XLSX nuevo que presenta los datos y el gráfico con formato VQ.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Siguiendo únicamente las instrucciones incluidas, una persona obtiene el reporte del ejemplo con una sola invocación, sin código adicional, credenciales ni servicios en ejecución.
- **SC-002**: El reporte del ejemplo conserva el 100 % de los encabezados, filas y valores declarados, y todas las categorías y series del gráfico coinciden con los datos seleccionados; cambiar un dato de origen se refleja en el gráfico.
- **SC-003**: El 100 % de los elementos sujetos a FR-005 coincide con los colores y usos VQ aprobados; una revisión humana del libro en Excel confirma título, tabla y gráfico legibles, sin solapamientos, efectos 3D ni decoración innecesaria.
- **SC-004**: Todos los casos inválidos enumerados se rechazan con un mensaje que identifica el problema y sin generar un reporte ni alterar un destino existente.
- **SC-005**: El 100 % de las cadenas de prueba que parecen fórmulas se conserva como texto sin evaluación, y ningún contenido de prueba ejecutable de la entrada se ejecuta.
- **SC-006**: Las tres consultas consecutivas de salud conservan exactamente el resultado acordado antes y después de incorporar la herramienta.

## Assumptions

- El usuario dispone de un entorno local preparado y una aplicación capaz de abrir el archivo generado; la generación no requiere tener Excel instalado.
- El plan puede concretar nombres de campos, versión inicial, argumentos y disposición visual mínima dentro de los requisitos anteriores; debe documentar estas decisiones como contrato antes de implementar. Esta autorización no permite ampliar el alcance ni cambiar los colores y usos VQ aprobados.
- Se admite únicamente la lectura de la definición local y la escritura del archivo solicitado; no se requiere almacenamiento histórico ni modificación de libros existentes.
- La consulta de salud conserva el contrato de [001-health-check](../001-health-check/spec.md).
- No se añaden objetivos de rendimiento, volúmenes arbitrarios, personalización visual ni otros componentes no solicitados.
