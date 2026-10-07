# Constitución — sdd-multiagent-reporting-experiment

Estado: RATIFICADA

## Principios

### I. Desarrollo guiado por especificaciones como fuente de verdad

Toda funcionalidad DEBE estar definida mediante una especificación
antes de que comience su implementación.

La especificación DEBE describir comportamiento esperado, criterios
de aceptación y restricciones relevantes.

Los agentes NO DEBEN implementar comportamiento que no pueda
rastrearse hacia una especificación, plan o tarea aprobada.

Si durante la implementación se identifica una necesidad que modifica
el comportamiento esperado, la especificación DEBE actualizarse antes
de continuar con ese cambio.

Ningún agente PUEDE modificar silenciosamente el alcance funcional.

### II. Arquitectura limpia mínima

La solución DEBE seguir un enfoque de arquitectura limpia mínima.

El objetivo es mantener separación de responsabilidades y dirección
correcta de dependencias sin reproducir capas, abstracciones o patrones
que no resuelvan una necesidad concreta.

La lógica de generación de reportes NO DEBE depender de FastAPI,
HTTP, Docker ni de mecanismos de autenticación.

Los detalles externos DEBEN depender del núcleo de la aplicación y no
al contrario.

Las abstracciones, interfaces, fábricas, repositorios, adaptadores u otras
capas solamente DEBEN existir cuando exista una necesidad concreta
identificada en la especificación o en el plan.

No se DEBEN introducir abstracciones para necesidades hipotéticas.

La Constitución NO prescribe nombres de carpetas, número fijo de capas
ni una implementación clásica completa de arquitectura limpia.

Una nueva capa o abstracción DEBE justificar explícitamente qué problema
actual resuelve.

### III. Contratos explícitos entre componentes

Las fronteras entre API, aplicación, generación de reportes,
infraestructura y autenticación DEBEN tener contratos explícitos.

Los agentes NO DEBEN inferir contratos incompatibles de manera
independiente.

Los cambios en contratos compartidos DEBEN identificarse antes de que
las tareas dependientes continúen.

Cuando dos agentes trabajen en paralelo, ambos DEBEN partir de los mismos
artefactos aprobados de desarrollo guiado por especificaciones.

### IV. Configuración declarativa mediante YAML

La estructura de los reportes DEBE definirse de forma declarativa mediante
archivos YAML.

El YAML representa la definición del reporte y NO DEBE contener código
ejecutable.

Toda definición YAML DEBE validarse antes de iniciar la generación del
archivo Excel.

Las propiedades desconocidas, tipos de componentes no soportados o
configuraciones inválidas DEBEN producir un error explícito.

El esquema YAML DEBE ser versionable para permitir evolución controlada.

Los cambios incompatibles en el esquema DEBEN tratarse como cambios
explícitos de contrato.

### V. Generación de Excel controlada

La generación de archivos Excel DEBE realizarse mediante XlsxWriter.

El núcleo de la aplicación NO DEBE acoplar su modelo de reportes
directamente a detalles internos de XlsxWriter.

La integración con XlsxWriter DEBE permanecer detrás de una frontera
claramente identificable dentro de la solución.

El sistema genera archivos XLSX nuevos a partir de la definición del
reporte. La modificación de archivos XLSX existentes queda fuera del
alcance inicial.

### VI. Seguridad por diseño

El API de reportes DEBE utilizar tokens de acceso portador de OAuth2 para autorizar
las solicitudes protegidas.

La autenticación del usuario DEBE realizarse mediante OpenID Connect.

La responsabilidad de autenticación DEBE permanecer fuera del API de reportes.

DEBE existir un servicio de identidad/autenticación separado encargado
del flujo de autenticación y de la emisión o intermediación de los tokens
utilizados por el API de reportes.

Los JWT utilizados por el API DEBEN emplear firma asimétrica RSA.

La clave privada NO DEBE estar disponible para el API de reportes.

El API únicamente DEBE disponer de la información pública necesaria para
validar los tokens.

La validación DEBE comprobar como mínimo:

- firma;
- algoritmo esperado;
- emisor;
- audiencia;
- expiración;
- vigencia temporal del token.

No se DEBE implementar criptografía propia.

Credenciales, claves privadas y secretos NO DEBEN almacenarse en el
repositorio.

### VII. Fuentes de imágenes controladas por servidor

Las imágenes incorporadas a los reportes DEBEN provenir de fuentes
controladas por el servidor.

El cliente NO DEBE poder enviar imágenes binarias dentro de la solicitud.

El cliente NO DEBE proporcionar URLs arbitrarias que el servidor descargue
directamente.

Las definiciones de reporte únicamente PODRÁN hacer referencia a imágenes
mediante identificadores o referencias aceptadas por el sistema.

La resolución de esas referencias DEBE realizarse contra fuentes
configuradas y permitidas por el servidor.

### VIII. Contenedores y reproducibilidad

Todos los servicios ejecutables del experimento DEBEN poder ejecutarse
mediante contenedores Docker.

Los servicios NO DEBEN depender de configuración específica de la máquina
del desarrollador.

Configuración, secretos y valores dependientes del ambiente DEBEN
externalizarse.

Las dependencias Python DEBEN estar declaradas y versionadas de manera
reproducible.

Una ejecución obtenida desde el repositorio y su configuración documentada
DEBE poder reproducirse en otro entorno compatible con Docker.

### IX. Verificación antes de considerar trabajo terminado

Una tarea NO DEBE considerarse terminada únicamente porque el agente haya
generado código.

Los criterios de aceptación asociados DEBEN verificarse.

Cuando sea razonable, la verificación DEBE realizarse mediante pruebas
automatizadas.

Los cambios en contratos compartidos DEBEN incluir pruebas de integración
entre productor y consumidor.

Las pruebas fallidas, omitidas o imposibles de ejecutar DEBEN reportarse
explícitamente.

Un comportamiento no verificado NO DEBE presentarse como comportamiento
validado.

### X. No asumir decisiones ausentes

Cuando una decisión que afecte comportamiento, arquitectura, contratos,
seguridad o criterios de aceptación no pueda derivarse de la
especificación, plan, tareas o Constitución, el agente NO DEBE inventar
una respuesta.

La ambigüedad DEBE ser escalada al humano en el circuito.

Una suposición solamente PUEDE convertirse en decisión cuando haya sido
aprobada explícitamente o cuando la especificación autorice esa libertad.

Las intervenciones humanas derivadas de este proceso DEBEN poder
registrarse como parte de las métricas del experimento.

### XI. Responsabilidad y aislamiento multiagente

Cada agente DEBE conocer claramente la responsabilidad que tiene asignada.

Cuando dos agentes trabajen de forma paralela, DEBEN operar sobre
árboles de trabajo independientes.

Dos agentes NO DEBEN modificar simultáneamente los mismos archivos salvo
que exista una coordinación explícita aprobada previamente.

Un agente NO DEBE modificar artefactos cuya responsabilidad pertenezca
a otro agente sin reportar primero el conflicto.

Los traspasos de trabajo DEBEN indicar como mínimo:

- trabajo realizado;
- archivos afectados;
- validaciones ejecutadas;
- decisiones tomadas;
- bloqueantes o ambigüedades pendientes.

### XII. Simplicidad y disciplina de dependencias

DEBE preferirse la solución más simple que satisfaga correctamente la
especificación actual.

No se DEBE diseñar arquitectura para requerimientos hipotéticos.

Una nueva dependencia de producción DEBE justificar qué requisito o
problema concreto resuelve.

Los agentes NO DEBEN agregar marcos de trabajo, bibliotecas, servicios o patrones
simplemente porque representen una práctica común.

La reducción de complejidad accidental tiene prioridad sobre la
generalización prematura.

## Restricciones funcionales iniciales del experimento

La primera versión del motor de reportes utilizará Python y FastAPI.

La definición estructural del reporte será suministrada mediante YAML.

La salida será un archivo XLSX generado mediante XlsxWriter.

Los componentes configurables mínimos soportados inicialmente serán:

- títulos;
- tablas;
- imágenes provenientes de fuentes controladas por el servidor;
- gráficos de líneas;
- gráficos de barras;
- gráficos circulares;
- gráficos dona.

Agregar nuevos tipos de componentes requiere una modificación explícita de
la especificación correspondiente.

Eliminar uno de estos componentes del alcance inicial requiere una decisión
explícita del humano en el circuito.

## Restricciones de despliegue iniciales

El API de reportes DEBE poder ejecutarse como contenedor independiente.

El servicio de identidad/autenticación DEBE poder ejecutarse como
contenedor independiente.

Ninguno de los dos servicios DEBE compartir estado local obligatorio
para funcionar correctamente.

La infraestructura de desarrollo DEBE permitir levantar el sistema de
manera reproducible.

## Flujo obligatorio de desarrollo

Para cada funcionalidad:

1. DEBE existir una especificación aprobada.
2. Las ambigüedades relevantes DEBEN resolverse.
3. DEBE generarse un plan compatible con esta Constitución.
4. DEBEN definirse tareas y responsabilidades.
5. Los agentes PUEDEN comenzar la implementación.
6. DEBEN ejecutarse las validaciones correspondientes.
7. DEBE revisarse el resultado antes de integrarlo.
8. Los cambios aceptados se integran sobre `dev`.
9. `main` solamente recibe cambios mediante solicitud de incorporación de cambios y aprobación humana.

## Gobernanza

Esta Constitución tiene precedencia sobre decisiones generadas por los
agentes.

Ningún agente PUEDE modificarla por iniciativa propia.

Toda modificación requiere revisión y aprobación explícita del
humano en el circuito.

Un cambio en una regla existente DEBE indicar:

- regla afectada;
- motivo del cambio;
- impacto esperado;
- funcionalidades afectadas.

Las modificaciones a la Constitución DEBEN versionarse.

Cambios incompatibles en principios fundamentales requieren incremento
MAYOR.

Nuevos principios o ampliaciones sustanciales requieren incremento MENOR.

Aclaraciones que no cambien obligaciones requieren incremento PARCHE.

La primera versión aprobada de este documento será Constitución 1.0.0.

**Versión**: 1.0.0 | **Ratificada**: 2026-10-06 | **Última modificación**: 2026-10-06
