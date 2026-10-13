# mostaza-phase1-foundation

[$sdd](/Users/diego/.codex/skills/sdd/SKILL.md) # PROYECTO: MOSTAZA HARNESS\
\# FASE 1: FOUNDATION, HYBRID RETRIEVAL & FIRST BENCHMARK\
\
\## 1. CONTEXTO\
\
Estamos desarrollando Mostaza Harness, un proyecto open source de\
investigación aplicada en ingeniería de agentes de inteligencia\
artificial.\
\
El proyecto nace como una participación en la competencia:\
\
Google DeepMind — Gemma 4 Developer Agent Competition\
https\://www\.kaggle.com/competitions/gemma-4-developer-agent/overview\
\
Sin embargo, nuestra visión es construir una metodología reutilizable\
para mejorar la capacidad de los modelos de lenguaje relativamente\
pequeños de resolver problemas reales de ingeniería de software.\
\
Nombre del proyecto: Mostaza\
Repositorio: mostaza-harness\
Metodología: Graph-SDD\
Licencia propuesta: Apache 2.0\
\
La investigación se concentrará inicialmente en tres capacidades:\
\
1\. Exploración eficiente de repositorios mediante búsqueda híbrida.\
2\. Resolución estructurada de problemas de ingeniería de software.\
3\. Validación automática y mejora iterativa de soluciones.\
\
El proyecto debe diseñarse para producir resultados académicos\
reproducibles, además de participar en Kaggle.\
\
IMPORTANTE:\
\
No debemos construir un framework alternativo a Google ADK.\
\
Debemos aprovechar el harness proporcionado por Kaggle y desarrollar\
una estrategia de exploración, razonamiento e implementación que mejore\
sus resultados.\
\
La primera implementación debe ser sencilla, medible y compatible\
con las restricciones oficiales del concurso.\
\
\
\## 2. OBJETIVO GENERAL\
\
Diseñar, implementar y evaluar una primera versión de Mostaza Harness\
capaz de resolver problemas de ingeniería de software utilizando\
Gemma 4 y una estrategia híbrida de recuperación de contexto.\
\
La estrategia combinará:\
\
\- Lexical Search.\
\- Vector Similarity Search.\
\- Graph Traversal.\
\- Context Ranking.\
\- Context Budget Optimization.\
\- Structured Problem Solving.\
\- Automated Verification.\
\
La hipótesis inicial de investigación es:\
\
"Una estrategia adaptativa de recuperación híbrida, combinando\
búsqueda léxica, similitud vectorial y relaciones estructurales\
del código, puede mejorar la eficiencia de localización y la\
capacidad de resolución de problemas de modelos de lenguaje\
relativamente pequeños".\
\
Esta hipótesis debe evaluarse experimentalmente.\
\
No se asumirá que la arquitectura propuesta es superior hasta\
obtener evidencia cuantitativa.\
\
\
\## 3. OBJETIVOS DE LA PRIMERA FASE\
\
La primera fase debe producir:\
\
1\. Un repositorio funcional y documentado.\
2\. Un entorno de desarrollo local reproducible.\
3\. Compatibilidad con el harness oficial de Kaggle.\
4\. Un agente baseline sin optimizaciones.\
5\. Un agente experimental con recuperación híbrida.\
6\. Un mecanismo básico de ejecución de benchmarks.\
7\. Una comparación inicial entre ambas configuraciones.\
8\. Un registro reproducible de resultados experimentales.\
\
Al finalizar debemos poder responder:\
\
\- ¿El agente baseline funciona?\
\- ¿Puede generar un parche válido?\
\- ¿Puede resolver al menos un problema real?\
\- ¿La estrategia híbrida encuentra código relevante?\
\- ¿Reduce las operaciones de exploración?\
\- ¿Cómo afecta el tiempo y los tokens?\
\- ¿Qué debemos mejorar en la siguiente iteración?\
\
\
\## 4. RESTRICCIONES DEL CONCURSO\
\
Consultar antes de implementar:\
\
Competition:\
https\://www\.kaggle.com/competitions/gemma-4-developer-agent/overview\
\
Getting Started:\
https\://www\.kaggle.com/code/ryanholbrook/getting-started-gemma-4-developer-agent\
\
Documentación oficial del harness:\
HARNESS_README.md incluido en los recursos del concurso.\
\
Modelo obligatorio:\
\
gemma-4-31b-it-qat-w4a16-ct\
\
Todos los agentes y subagentes utilizados durante la evaluación\
oficial deberán respetar esta restricción.\
\
La arquitectura debe:\
\
\- Utilizar Google ADK.\
\- Respetar el formato declarativo de submission.\
\- Ejecutarse sin depender de servicios externos.\
\- Utilizar únicamente herramientas autorizadas.\
\- Respetar los presupuestos de ejecución.\
\- Producir parches de código verificables.\
\- Ser compatible con la evaluación oficial de Kaggle.\
\
No utilizar Claude, GPT ni Gemini durante la resolución de tareas\
evaluadas oficialmente.\
\
Estas herramientas sí pueden utilizarse durante el desarrollo\
del proyecto.\
\
No asumir que Kaggle permite ejecutar código Python arbitrario\
como componente del agente enviado.\
\
Verificar las capacidades declarativas, herramientas y scripts\
autorizados antes de diseñar extensiones.\
\
Cualquier implementación experimental que no sea compatible con\
las restricciones oficiales deberá permanecer fuera de\
la entrega del concurso.\
\
\
\## 5. ENTORNO TECNOLÓGICO\
\
\### Desarrollo local\
\
Equipo principal:\
\
MacBook Pro Apple M4\
24 GB de memoria unificada\
macOS\
\
Stack preferido:\
\
\- Python 3.13, si es compatible con el harness oficial.\
\- uv para dependencias.\
\- Google ADK.\
\- Git.\
\- GitHub.\
\- Docker.\
\- Colima.\
\- pytest.\
\- Ruff.\
\- YAML.\
\- JSON / JSONL.\
\
Colima ya se utiliza en el equipo y tiene aproximadamente\
8 GB de memoria asignada.\
\
No modificar globalmente esta configuración salvo que sea\
estrictamente necesario.\
\
No descargar modelos grandes innecesariamente.\
\
\### Evaluación\
\
Utilizar el entorno oficial de Kaggle con:\
\
\- GPU NVIDIA L4 x4.\
\- Gemma 4 31B.\
\- Dataset del concurso.\
\- Harness oficial.\
\- Herramientas de grafos y embeddings precalculados.\
\
La ejecución local debe utilizarse inicialmente para:\
\
\- Desarrollo.\
\- Validación de configuraciones.\
\- Pruebas unitarias.\
\- Pruebas de herramientas.\
\- Análisis de datasets.\
\- Evaluación offline cuando sea viable.\
\
La evaluación real de Gemma 4 debe ejecutarse principalmente\
en Kaggle.\
\
No asumir que una prueba con mocks equivale a una prueba real.\
\
\
\## 6. ARQUITECTURA CONCEPTUAL\
\
Mostaza Harness estará dividido conceptualmente en:\
\
A. Agent Orchestration\
B. Hybrid Code Retrieval\
C. Context Optimization\
D. Graph-SDD\
E. Verification\
F. Evaluation & Research\
\
Flujo principal:\
\
&#x20;                   ISSUE\
&#x20;                     |\
&#x20;                     v\
&#x20;               Issue Analyzer\
&#x20;                     |\
&#x20;                     v\
&#x20;             Hybrid Retrieval\
&#x20;                     |\
&#x20;         +-----------+-----------+\
&#x20;         \|           |           |\
&#x20;         v           v           v\
&#x20;      Lexical      Vector      Graph\
&#x20;      Search       Search     Traversal\
&#x20;         \|           |           |\
&#x20;         +-----------+-----------+\
&#x20;                     |\
&#x20;                     v\
&#x20;              Result Ranking\
&#x20;                     |\
&#x20;                     v\
&#x20;            Context Optimization\
&#x20;                     |\
&#x20;                     v\
&#x20;               Graph-SDD\
&#x20;                     |\
&#x20;             +-------+-------+\
&#x20;             \|       |       |\
&#x20;             v       v       v\
&#x20;           Plan    Implement Verify\
&#x20;                     |\
&#x20;                     v\
&#x20;                 Code Patch\
&#x20;                     |\
&#x20;                     v\
&#x20;                Evaluation\
\
Esta arquitectura es conceptual.\
\
No crear múltiples agentes independientes para cada componente\
sin justificar su necesidad.\
\
En el MVP se prefiere un único LlmAgent con herramientas,\
instrucciones estructuradas y presupuesto limitado.\
\
\
\## 7. HYBRID CODE RETRIEVAL\
\
Esta será la principal capacidad experimental de Mostaza.\
\
El objetivo es identificar rápidamente los símbolos y fragmentos\
de código relevantes para resolver un problema.\
\
\### 7.1 Lexical Search\
\
Identificar:\
\
\- Nombres de archivos.\
\- Funciones.\
\- Clases.\
\- Métodos.\
\- Excepciones.\
\- Mensajes de error.\
\- Referencias a módulos.\
\- Símbolos mencionados en el issue.\
\
Utilizar herramientas disponibles en el sandbox:\
\
\- grep.\
\- find.\
\- git grep.\
\- Búsquedas textuales equivalentes.\
\
No asumir que ripgrep está instalado.\
\
Priorizar coincidencias exactas cuando existan identificadores\
específicos en el problema.\
\
\### 7.2 Vector Similarity Search\
\
Aprovechar los embeddings precalculados proporcionados\
por el concurso.\
\
Herramienta oficial:\
\
search_similar_code(query, k)\
\
IMPORTANTE:\
\
Verificar cómo se resuelve el parámetro query.\
\
El harness oficial utiliza embeddings asociados a símbolos\
del repositorio y no necesariamente proporciona un encoder\
de texto libre.\
\
La primera implementación deberá utilizar símbolos existentes\
como puntos de partida para la recuperación vectorial.\
\
No implementar un servicio de embeddings externo.\
\
No incorporar Qdrant, Chroma ni FAISS salvo que los experimentos\
demuestren su necesidad y sean compatibles con Kaggle.\
\
\### 7.3 Graph Traversal\
\
Utilizar los grafos estructurales proporcionados por Kaggle.\
\
Herramientas oficiales:\
\
get_code_neighbors(node)\
get_code_subgraph(nodes)\
\
Explorar relaciones como:\
\
\- Funciones que llaman a otras funciones.\
\- Funciones llamadas por el símbolo encontrado.\
\- Relaciones de clases.\
\- Dependencias.\
\- Referencias estructurales disponibles en el grafo.\
\
La profundidad inicial de exploración deberá ser conservadora.\
\
Por defecto:\
\
\- Priorizar expansión de un salto.\
\- Expandir a dos saltos solo cuando exista evidencia.\
\- Limitar la cantidad de vecinos.\
\- Evitar recuperar subgrafos completos innecesariamente.\
\
\### 7.4 Adaptive Retrieval Strategy\
\
No ejecutar siempre todas las herramientas.\
\
La estrategia inicial será:\
\
1\. Analizar el issue.\
2\. Extraer símbolos y palabras clave.\
3\. Realizar una búsqueda léxica dirigida.\
4\. Identificar símbolos candidatos.\
5\. Consultar relaciones estructurales relevantes.\
6\. Utilizar similitud vectorial cuando existan símbolos\
&#x20;  candidatos apropiados.\
7\. Combinar resultados.\
8\. Seleccionar el contexto necesario.\
9\. Detener la exploración cuando exista evidencia suficiente.\
\
Evitar exploración repetitiva.\
\
Mantener un registro conceptual de los símbolos ya visitados.\
\
No solicitar nuevamente información que ya se encuentre\
en el contexto disponible.\
\
\
\## 8. CONTEXT RANKING\
\
Diseñar una política inicial de priorización de resultados.\
\
Considerar las siguientes señales:\
\
Lexical relevance:\
Coincidencia con términos del issue.\
\
Semantic relevance:\
Similitud vectorial.\
\
Structural relevance:\
Distancia y relaciones en el grafo.\
\
Evidence relevance:\
Relación con errores, stack traces o pruebas.\
\
Context cost:\
Cantidad de tokens necesarios para incluir el código.\
\
La política puede comenzar como una heurística sencilla,\
sin entrenar un modelo adicional.\
\
Una posible formulación conceptual es:\
\
Score(node) =\
&#x20;   w1 \* lexical_score\
&#x20; \+ w2 \* vector_score\
&#x20; \+ w3 \* graph_score\
&#x20; \+ w4 \* evidence_score\
&#x20; \- w5 \* context_cost\
\
Los pesos no deben escogerse arbitrariamente y presentarse\
como óptimos.\
\
Si esta fórmula no puede implementarse dentro de las\
capacidades permitidas por Kaggle, representarla inicialmente\
mediante reglas de priorización en las instrucciones del agente.\
\
Registrar las decisiones de diseño.\
\
Evitar añadir complejidad matemática sin evidencia de beneficio.\
\
\
\## 9. GRAPH-SDD\
\
Graph-SDD será la metodología de resolución de problemas.\
\
Inicialmente tendrá cuatro fases:\
\
\### Phase A: Understand\
\
\- Interpretar el problema.\
\- Identificar el comportamiento esperado.\
\- Extraer pistas técnicas.\
\- Identificar restricciones.\
\- Determinar qué información falta.\
\
\### Phase B: Explore\
\
\- Ejecutar Hybrid Code Retrieval.\
\- Localizar símbolos relevantes.\
\- Explorar dependencias.\
\- Seleccionar el contexto mínimo.\
\- Formular una hipótesis sobre la causa del problema.\
\
\### Phase C: Implement\
\
\- Definir un plan mínimo.\
\- Modificar únicamente el código necesario.\
\- Respetar convenciones del repositorio.\
\- Evitar cambios no relacionados.\
\- Preservar compatibilidad.\
\
\### Phase D: Verify\
\
\- Ejecutar pruebas dirigidas.\
\- Interpretar errores.\
\- Realizar correcciones justificadas.\
\- Verificar el diff.\
\- Entregar el parche.\
\
No crear agentes separados para estas fases durante el MVP.\
\
Implementarlas inicialmente como un protocolo de trabajo\
dentro de un único agente.\
\
Una futura versión podrá experimentar con planificación,\
implementación y auditoría mediante subagentes especializados.\
\
\
\## 10. BUDGET-AWARE EXECUTION\
\
El concurso dispone de un presupuesto global de ejecución.\
\
El agente debe ser consciente de sus límites.\
\
Diseñar una política sencilla para controlar:\
\
\- Llamadas al modelo.\
\- Llamadas a herramientas.\
\- Tiempo de ejecución.\
\- Lecturas de archivos.\
\- Expansiones del grafo.\
\- Intentos de reparación.\
\
La estrategia debe priorizar:\
\
1\. Encontrar el código relevante.\
2\. Implementar el parche.\
3\. Ejecutar pruebas.\
4\. Finalizar correctamente.\
\
No consumir todo el presupuesto explorando.\
\
Utilizar get_status() cuando resulte apropiado.\
\
El agente debe reconocer cuándo detener una búsqueda\
que no está proporcionando información útil.\
\
No establecer límites definitivos sin medir primero\
el comportamiento del baseline.\
\
\
\## 11. ESTRUCTURA DEL REPOSITORIO\
\
Crear una estructura sencilla y extensible:\
\
mostaza-harness/\
│\
├── README.md\
├── LICENSE\
├── pyproject.toml\
├── uv.lock\
├── .gitignore\
│\
├── docs/\
│   ├── architecture.md\
│   ├── research-proposal.md\
│   ├── kaggle-setup.md\
│   └── experiments.md\
│\
├── submission/\
│   ├── agent.yaml\
│   ├── eval_config.yaml\
│   ├── prompts/\
│   │   ├── baseline.md\
│   │   └── hybrid-retrieval.md\
│   └── skills/\
│\
├── experiments/\
│   ├── E0-baseline/\
│   └── E1-hybrid-retrieval/\
│\
├── src/\
│   └── mostaza/\
│       ├── \_\_init\_\_.py\
│       ├── evaluation/\
│       └── research/\
│\
├── tests/\
│   ├── unit/\
│   └── integration/\
│\
├── scripts/\
│   ├── setup.sh\
│   ├── validate.sh\
│   ├── package.sh\
│   └── run_experiment.sh\
│\
└── results/\
&#x20;   └── .gitkeep\
\
NOTAS:\
\
La carpeta submission/ debe contener únicamente los\
archivos autorizados por la competencia.\
\
El código Python de src/ corresponde inicialmente a\
herramientas de desarrollo, experimentación y análisis.\
\
No asumir que estas herramientas pueden ejecutarse como parte\
del agente enviado a Kaggle.\
\
Los directorios de experimentos pueden contener manifiestos\
y configuraciones, pero la construcción de submission.zip\
debe seleccionar explícitamente una configuración.\
\
No incluir datasets completos, pesos del modelo, entornos\
virtuales ni resultados voluminosos en Git.\
\
Si existe un scaffold previo del proyecto, inspeccionarlo,\
reutilizar lo válido y migrarlo sin destruir cambios existentes.\
\
\
\## 12. IMPLEMENTACIÓN DEL BASELINE\
\
Experimento:\
\
E0 — Official Baseline\
\
Objetivo:\
\
Reproducir el comportamiento de referencia utilizando\
Gemma 4 y las herramientas básicas del concurso.\
\
Procedimiento:\
\
1\. Descargar o localizar los recursos oficiales.\
2\. Examinar HARNESS_README.md.\
3\. Examinar sample_submission/.\
4\. Identificar versiones compatibles.\
5\. Validar el formato agent.yaml.\
6\. Configurar un agente básico.\
7\. Preparar el empaquetado oficial.\
8\. Ejecutar pruebas estructurales locales.\
9\. Ejecutar una evaluación real en Kaggle.\
10\. Guardar los resultados.\
\
No introducir optimizaciones Graph-SDD en E0.\
\
Preferir la configuración oficial sin modificar para que\
sirva como referencia experimental válida.\
\
Registrar:\
\
\- Identificador de tarea.\
\- Resultado PASS/FAIL.\
\- Tiempo de ejecución.\
\- Llamadas a herramientas.\
\- Tokens utilizados, cuando estén disponibles.\
\- Existencia y validez del parche.\
\- Errores de ejecución.\
\
Guardar el manifiesto de configuración y los resultados.\
\
\
\## 13. IMPLEMENTACIÓN DE HYBRID RETRIEVAL\
\
Experimento:\
\
E1 — Adaptive Hybrid Retrieval\
\
Objetivo:\
\
Evaluar el impacto de combinar búsqueda léxica,\
recuperación vectorial y navegación por grafos.\
\
Partir del baseline E0.\
\
Modificar únicamente lo necesario para implementar\
la estrategia de exploración.\
\
No cambiar simultáneamente:\
\
\- Modelo.\
\- Presupuesto.\
\- Sampling.\
\- Arquitectura multiagente.\
\- Estrategia de reparación.\
\
Mantener las condiciones comparables.\
\
La implementación inicial puede utilizar:\
\
\- Instrucciones especializadas.\
\- Herramientas de Kaggle.\
\- Reglas de selección de contexto.\
\- Skills compatibles con el harness, si están permitidas.\
\
No crear infraestructura adicional antes de verificar\
que las capacidades nativas son suficientes.\
\
\
\## 14. PRIMERA PRUEBA FUNCIONAL\
\
Debemos ejecutar una primera prueba real sobre problemas\
del dataset público del concurso.\
\
Seleccionar un conjunto pequeño de tareas.\
\
Propuesta inicial:\
\
\- Una tarea de Requests.\
\- Una tarea de FastAPI.\
\- Una tarea de Rich o HTTPX.\
\
Elegir tareas existentes en el dataset y registrar\
sus instance_id exactos.\
\
No seleccionar únicamente problemas triviales.\
\
El objetivo inicial es validar el funcionamiento,\
no maximizar artificialmente el score.\
\
\### Ejecución\
\
Para cada tarea:\
\
1\. Preparar el snapshot correspondiente.\
2\. Entregar al agente el problem_statement.\
3\. Ejecutar la estrategia de exploración.\
4\. Identificar el código relevante.\
5\. Producir un parche.\
6\. Ejecutar las pruebas permitidas.\
7\. Registrar el resultado.\
\
Realizar E0 y E1 sobre exactamente las mismas tareas.\
\
Mantener iguales:\
\
\- Modelo.\
\- Parámetros de generación.\
\- Presupuestos.\
\- Configuración del entorno.\
\- Criterios de validación.\
\
No mostrar al agente el parche de referencia ni las\
pruebas ocultas de verificación.\
\
No utilizar información del resultado esperado para\
orientar la generación de soluciones.\
\
Las referencias del dataset público pueden utilizarse\
exclusivamente para evaluación y análisis posterior.\
\
Si no hay acceso a GPU o autenticación de Kaggle,\
ejecutar pruebas locales de configuración y herramientas,\
pero registrar que la evaluación real sigue pendiente.\
\
\
\## 15. MÉTRICAS DE INVESTIGACIÓN\
\
Registrar como mínimo:\
\
\### Code Localization\
\
\- Recall@K de símbolos relevantes, cuando pueda medirse.\
\- Cantidad de archivos inspeccionados.\
\- Cantidad de símbolos explorados.\
\- Cantidad de llamadas de búsqueda.\
\- Tiempo dedicado a localizar el problema.\
\
\### Context Efficiency\
\
\- Tokens consumidos.\
\- Cantidad de código recuperado.\
\- Número de expansiones del grafo.\
\- Repetición de información.\
\- Proporción de contexto relevante, cuando pueda estimarse.\
\
\### Software Engineering\
\
\- Patch validity.\
\- Tests passed.\
\- Issue resolved: PASS/FAIL.\
\- Tiempo total de resolución.\
\- Intentos de reparación.\
\
\### Comparación\
\
Calcular:\
\
E1 - E0\
\
Para las métricas relevantes.\
\
No afirmar mejoras estadísticamente significativas\
con muestras pequeñas.\
\
La primera prueba será exploratoria.\
\
Guardar suficientes datos para posteriormente ampliar\
el benchmark y realizar análisis estadísticos.\
\
\
\## 16. REPRODUCIBILIDAD\
\
Cada experimento debe registrar:\
\
\- ID del experimento.\
\- Fecha y hora.\
\- Commit del código.\
\- Configuración del agente.\
\- Versión del harness.\
\- Modelo utilizado.\
\- Dataset.\
\- Tareas evaluadas.\
\- Parámetros de inferencia.\
\- Presupuestos.\
\- Resultados.\
\- Limitaciones conocidas.\
\
Utilizar JSON o JSONL para los resultados estructurados.\
\
Mantener los resultados grandes fuera del repositorio.\
\
No modificar manualmente las métricas.\
\
No confundir pruebas simuladas con evaluaciones reales.\
\
\
\## 17. CRITERIOS DE ACEPTACIÓN\
\
La primera fase estará completa cuando:\
\
[ ] El repositorio esté estructurado.\
[ ] El entorno local pueda instalarse de forma reproducible.\
[ ] Las pruebas unitarias pasen.\
[ ] Exista una configuración baseline válida.\
[ ] Exista una configuración experimental E1.\
[ ] La configuración sea compatible con el harness oficial.\
[ ] El proyecto pueda generar submission.zip.\
[ ] Exista un procedimiento documentado para ejecutar Kaggle.\
[ ] Se haya realizado al menos una ejecución real con Gemma 4.\
[ ] Se hayan ejecutado E0 y E1 sobre las mismas tareas.\
[ ] Los resultados estén almacenados de forma reproducible.\
[ ] Exista un informe comparativo preliminar.\
\
La generación correcta de submission.zip no implica que\
la entrega haya sido validada oficialmente.\
\
La prueba con Gemma 4 y la compatibilidad real deben\
verificarse utilizando el entorno del concurso.\
\
\
\## 18. FUERA DEL ALCANCE INICIAL\
\
No implementar todavía:\
\
\- Fine-tuning LoRA.\
\- Reinforcement Learning.\
\- Múltiples agentes especializados.\
\- Bases de datos vectoriales externas.\
\- Bases de datos de grafos independientes.\
\- Interfaces gráficas.\
\- Paneles web.\
\- APIs públicas.\
\- Sistemas distribuidos.\
\- Compatibilidad completa con todos los LLM locales.\
\- Despliegue en producción.\
\- Optimización exhaustiva de hiperparámetros.\
\
Estas capacidades podrán evaluarse posteriormente\
si los resultados experimentales lo justifican.\
\
\
\## 19. METODOLOGÍA DE IMPLEMENTACIÓN\
\
Utilizar nuestro flujo SDD.\
\
Orden de ejecución:\
\
FASE A — INVESTIGACIÓN\
\
\- Revisar documentación oficial.\
\- Identificar restricciones.\
\- Analizar el harness.\
\- Inspeccionar recursos disponibles.\
\- Documentar decisiones.\
\
FASE B — PLANIFICACIÓN\
\
\- Crear plan de implementación.\
\- Definir arquitectura mínima.\
\- Identificar dependencias.\
\- Definir pruebas.\
\- Identificar riesgos.\
\
FASE C — IMPLEMENTACIÓN\
\
\- Crear o adaptar repositorio.\
\- Configurar herramientas.\
\- Implementar baseline.\
\- Implementar recuperación híbrida.\
\- Configurar experimentos.\
\
FASE D — VERIFICACIÓN\
\
\- Ejecutar pruebas.\
\- Validar YAML.\
\- Validar empaquetado.\
\- Comprobar compatibilidad.\
\- Ejecutar benchmark.\
\- Revisar resultados.\
\
FASE E — AUDITORÍA\
\
\- Revisar calidad del código.\
\- Revisar cumplimiento de reglas.\
\- Verificar reproducibilidad.\
\- Detectar complejidad innecesaria.\
\- Identificar problemas pendientes.\
\
Corregir los hallazgos que impidan completar\
los criterios de aceptación.\
\
\
\## 20. INSTRUCCIONES FINALES\
\
No detenerse en la planificación.\
\
Implementar el proyecto y ejecutar todas las verificaciones\
que permita el entorno disponible.\
\
Priorizar código funcional sobre documentación extensa.\
\
Mantener la arquitectura simple.\
\
No instalar herramientas innecesarias.\
\
No inventar interfaces del harness.\
\
Cuando exista incertidumbre sobre la API, consultar\
el código o la documentación oficial.\
\
No afirmar que una prueba pasó si no fue ejecutada.\
\
No presentar resultados simulados como benchmarks reales.\
\
Si alguna tarea requiere credenciales, acceso a Kaggle\
o infraestructura no disponible:\
\
\- Completar primero todas las tareas independientes.\
\- Documentar el bloqueo concreto.\
\- Proporcionar los comandos para finalizar esa tarea.\
\- Continuar con el resto de actividades posibles.\
\
Al finalizar entregar:\
\
1\. Resumen de la implementación.\
2\. Estructura final del repositorio.\
3\. Dependencias instaladas.\
4\. Comandos de instalación y ejecución.\
5\. Resultado de las pruebas locales.\
6\. Resultado del baseline E0.\
7\. Resultado del experimento E1.\
8\. Comparación preliminar de métricas.\
9\. Problemas encontrados.\
10\. Próximas tareas recomendadas.\
\
OBJETIVO FINAL DE ESTA ITERACIÓN:\
\
Conseguir una primera implementación funcional de\
Mostaza Harness, compatible con Kaggle, y producir\
la primera evidencia experimental sobre el impacto\
de Hybrid Graph-Vector Retrieval en la resolución\
autónoma de problemas de software.


Bootstrap decision: The user authorized a new repository, an initial empty commit and develop, then provided origin git@github.com:diego-escobar-git/mostaza-harness.git and requested initial publication on main. Local develop is retained at the same initial commit for SDD. Research and planning are requested now; implementation awaits required plan/gate approval.

## Planning record (2026-10-13)

The complete original requirement above remains authoritative. This plan implements the whole first phase; the current handoff stops at plan approval. No product code has been implemented and no validation success or real model result is claimed.

### Research and verified facts

The empty branch starts at ceb055d21c20b5274bb49b24e02e79656482a81f. No repository-specific code, tests, instructions or alternate spec root existed. The parent source checkout remains on main. Runtime evidence and approvals live only in this plan.

Official sources inspected on 2026-10-13:

- [Competition overview](https://www.kaggle.com/competitions/gemma-4-developer-agent/overview): declarative ADK ZIP with root agent.yaml, native workspace/patch/status/graph tools, sandboxed skill scripts, offline L4x4 and a 12-hour aggregate patch-generation budget including setup. Direct HTML has no text; indexed official content was used. Its single-model statement is older than current notebook/code; Mostaza keeps the specifically requested 31B model regardless.
- [Official starter notebook](https://www.kaggle.com/code/ryanholbrook/getting-started-gemma-4-developer-agent), retrieved through the official `/api/v1/kernels/pull/ryanholbrook/getting-started-gemma-4-developer-agent` endpoint: version 3, Python metadata 3.12.13. It demonstrates `swegemma.models.load_tasks`, graph helpers, `adk_submission.VllmServer`, `swegemma.config.EvalConfig`, `Evaluator.evaluate_task`, `validate_directory` and packaging. Its default demonstration now selects 12B; that is not copied into this project. The notebook shows sample subagents/dummy LoRA, which explains the explicit baseline derivation decision.
- [Organizer wheelhouse](https://www.kaggle.com/datasets/metric/gemma-4-developer-agent-wheelhouse), official API metadata and complete relevant file listings: current version 31, updated 2026-10-12. Inspected small official wheel source, without installing it: swegemma 0.2.11 (Python >=3.12), adk-submission 0.2.13 (>=3.11), adk-eval-core 0.1.0 (>=3.11); listing contains google-adk 1.36.1. GPU wheels include Linux CPython 3.12 artifacts; do not copy this GPU stack into the Mac environment.
- `swegemma/graph/embedding_utils.py` in that wheel resolves exact stored symbols and deterministic suffix/case matches; it does not run a neural free-text encoder. Prefer fully qualified symbols and handle missing/ambiguous seeds explicitly. The current compiler accepts organizer registries and constraints; public ADK schema alone is insufficient.
- [Official notebook input description](https://www.kaggle.com/code/ryanholbrook/getting-started-gemma-4-developer-agent/input) identifies public task JSONL, snapshots, graph/embedding assets, sample submission and HARNESS_README. Actual task bytes and starter files have not yet been obtained. Do not convert illustrative IDs into the cohort.

Official wheel SHA-256 pins for reproduction:

| Wheel | SHA-256 |
| --- | --- |
| swegemma-0.2.11-py3-none-any.whl | 9ad876581f3acde8ec3c369858f0834e2b9f41a3cffce3ca42f09cb090aea9d3 |
| adk_submission-0.2.13-py3-none-any.whl | f156f0bd84580ccb9334726d114d7a5481f16d3a6e2887cc4d276ced0ef8d99d |
| adk_eval_core-0.1.0-py3-none-any.whl | e614e1b2fe8d886a634871e4c57f9887e1cc66e8c27300f8503a43c6e3ca82f3 |

### Prerequisites and blockers

Authenticated official competition data listing returned HTTP 401 without credentials. Direct README download attempts returned HTTP 404; neither proves the README is absent. HARNESS_README, actual sample_submission, task/snapshot/graph/embedding files remain unavailable. Parent verified no Kaggle credential configuration, no uv/kaggle executables, and no active Python harness/test packages. Python 3.13.15, Docker and Colima are present. Official network escalation succeeded for small public notebook/wheel downloads; this is not a continuing generic permission denial.

Implementation may complete independent foundation and record/analysis tooling after approval. Stage baseline must acquire and review the official README and starter before implementing the agent config; stage real benchmark must obtain Kaggle authentication, accepted competition/model access and L4x4 quota. Never request secrets in chat. Retrieve only needed assets; no complete 23 GB dataset or local model download. Prefer official UI download or an installed Kaggle CLI with credentials configured by the user. Exact official evaluation commands will be documented from the inspected pinned resources; do not substitute guessed CLI syntax. The now-verified notebook APIs provide the initial supported integration route.

A resource/API contradiction that changes behavior, stages' acceptance, gate commands or provenance pins returns to Planner and fresh approval. A newer wheelhouse is not silently substituted during E0/E1. Missing external resources do not permit skipped required integration checks, synthetic evidence, an empty cohort or phase completion. The full gate and audit remain blocked until the real evidence exists.

## Specification changes

Files added: docs/specs/README.md, docs/specs/foundation.md, docs/specs/agent-retrieval.md, docs/specs/evaluation.md. No modified, removed or restored ACs. Product decisions are recorded in the three normative files: Python/host separation and Apache-2.0; explicit minimal single-agent baseline derivation; exploration-only E1 native-tool instructions; preselected matched cohort and honest pending/missing evidence.

Added acceptance criteria (exact text):

- `foundation:AC-1` — A fresh macOS development environment installs the locked Python 3.13 tooling with uv; setup validates the interpreter and never installs GPU model weights or changes global Colima configuration. Kaggle GPU execution follows the official notebook environment separately.
- `foundation:AC-2` — The repository has the requested source, tests, submission, experiments, scripts, results and documentation structure, Apache-2.0 license, and ignore rules excluding credentials, virtual environments, weights, datasets, archives and bulky run outputs.
- `foundation:AC-3` — The resource inventory records official URLs, retrieval date, notebook and wheelhouse versions, wheel SHA-256 and Python requirements; HARNESS_README, sample submission and selected task resources are reviewed from official authenticated downloads before integration. Missing resources cause an explicit prerequisite failure, never invented API behavior.
- `foundation:AC-4` — Local unit, integration, lint, formatting, type and package-build checks execute reproducibly; simulation, compiler-only validation and actual Gemma/Kaggle evaluation are distinguishable in documentation and results.
- `agent-retrieval:AC-1` — E0 is a single Google ADK LlmAgent derived minimally from the official starter, using gemma-4-31b-it-qat-w4a16-ct, authorized tools, no LoRA and no Graph-SDD retrieval optimization; every removal or adjustment from the official sample is documented and its source hashed.
- `agent-retrieval:AC-2` — E1 preserves E0 model, generation parameters, tool availability, repair policy, budgets and environment; only exploration instructions change. It prioritizes exact lexical clues, then relevant one-hop graph neighbors and symbol-seeded similarity when useful; two-hop expansion needs explicit evidence, neighbors are bounded, visited symbols are reused and unproductive searches stop.
- `agent-retrieval:AC-3` — E1 applies understandable context priorities: issue/test/stack-trace evidence and exact matches first, structural proximity and similarity next, then minimum sufficient code and low context cost; no learned ranker or claim of optimal weights. Understand, Explore, Implement and Verify remain phases of one agent, with E0-equivalent implementation and repair behavior.
- `agent-retrieval:AC-4` — Both configurations use official budget enforcement, check get_status at meaningful transitions, preserve time for patching and verification, and record observed model/tool calls, time, reads, graph expansions and repairs when exposed; starting numeric limits are copied from the inspected official baseline, shared across arms and labeled provisional until measured.
- `agent-retrieval:AC-5` — Packaging requires an explicit E0 or E1 selection, produces a deterministic submission.zip with root agent.yaml and only its allowed dependency closure, and fails on traversal, symlinks, unknown tools/models, forbidden files or missing includes. Both archives pass current official directory/schema/compiler validation; archive creation alone never establishes official evaluation compatibility.
- `agent-retrieval:AC-6` — Official graph/embedding fixtures and source-based contract tests verify symbol lookup, missing/ambiguous symbols, unavailable graph data and bounded retrieval behavior without external encoders or databases; prompt-policy tests are never represented as proof that a real agent followed those policies.
- `evaluation:AC-1` — The benchmark cohort freezes exact existing public instance_id values, base commits and resource hashes before either arm runs, selecting one Requests, one FastAPI and one Rich or HTTPX task with a documented difficulty rationale; selection does not use successful outcomes or expose reference patches/tests to the agent. If those resources are unavailable the cohort remains pending, without invented IDs.
- `evaluation:AC-2` — Agent-visible task inputs contain only an allowlisted issue and snapshot context; reference patch and test_patch stay exclusively in isolated post-generation verification/analysis. Tests cover leakage through serialized inputs, logs, filesystem packaging and future repository history.
- `evaluation:AC-3` — Each immutable run record includes experiment/run ID, UTC timestamp, code commit plus working-tree/config/archive digest, model, harness/wheelhouse/dataset versions, exact cohort, inference parameters, budgets, environment and limitations. Per-task JSONL records distinguish PASS, FAIL, ERROR and NOT_RUN, patch presence/validity, test outcomes and sourced metrics; absent measurements are null with reasons, never zero or fabricated.
- `evaluation:AC-4` — At least one actual Gemma 4 execution and complete paired E0/E1 evaluation on the same frozen cohort take place in the official Kaggle environment. Both arms use the same fixed non-treatment conditions and official verification, with durable source run identifiers, trace/result and patch hashes. Missing authentication, resources or GPU leaves this criterion pending and prevents phase completion.
- `evaluation:AC-5` — A reproducible preliminary report computes matched E1-minus-E0 metrics for localization, context efficiency and engineering outcomes; it separates unavailable/estimated metrics, failures and simulation, reports denominators and provenance, and makes no significance or superiority claim from the small exploratory sample. Recall@K and relevant-context ratio are reported only with explicit post-run ground-truth mapping and definitions.
- `evaluation:AC-6` — Documentation provides exact verified setup, package, Kaggle execution, result import and report commands, obtained from the pinned official resources; it states observed baseline/hybrid outcomes, remaining blockers and next research steps. A local-only checkpoint never satisfies real compatibility or full phase completion.

## Implementation stages

The executable definition below owns exact paths, IDs, levels and dependencies. The following checkpoints explain each item. Normative specifications and index are Planner-owned and frozen after approval; Implementers never edit them.

### Stage 1 [stage-foundation] Reproducible foundation — MEDIUM

F-ENV: Establish a small locked uv environment with Python 3.13, pytest, Ruff, mypy and package build tooling; isolate official compiler dependencies from optional GPU runtime. Resolve actual compatible versions and hashes. F-SCAFFOLD: Add package/shell entry points, Apache license, ignore rules and concise architecture/research documentation. The interacting contract is setup → locked tool environment → package import/build and checks. Test fresh installation/package build in a temporary directory without changing global tools or Colima. No model download.

### Stage 2 [stage-baseline] Official baseline and archive boundary — HIGH

B-RESOURCES: Acquire authentic README/starter/task metadata as prerequisites, verify pinned wheel hashes, inventory licensing and review actual declarations. Implement a bounded explicit resource-fetch utility and source manifest. B-CONFIG: Derive the minimum single-agent/no-LoRA E0 from the actual starter; record exact differences and retain official generation/budget defaults provisionally. B-PACKAGE: Implement explicit experiment selection and transitive include allowlisting, deterministic archives, current official validation/compilation and rejection tests. Risk: sandbox/path boundary and official compiler compatibility. Resource review cannot be replaced with third-party copies. Compiler-only tests may bind inert registry objects for no-inference compilation, labeled accurately; native tool behavior must also be exercised against the official modules.

### Stage 3 [stage-hybrid] Controlled retrieval treatment — MEDIUM

H-POLICY: Write the exploration-only E1 prompt and manifest; preserve the frozen E0 settings. Choose a documented conservative initial neighbor count (10) and vector k (5) as pilot values, not learned optima; keep graph depth one by default. These affect retrieval policy, not shared global execution budgets. H-CONTRACT: Test treatment isolation and verified graph/embedding semantics including exact symbols, deterministic suffix handling, no matches and missing resources. Native retrieval → bounded context → prompt protocol is the interacting contract. Unit fixtures prove policy/config invariants; real behavior is measured later.

### Stage 4 [stage-evaluation] Safe benchmark and research tooling — HIGH

E-ISOLATION: Load task metadata and build strict agent-visible allowlists; reference solutions remain in post-generation verification. E-RECORDS: Validate versioned run manifests and per-task immutable records with explicit missing/error states. E-COMPARE: Compute paired differences from raw metrics, reject mismatched configurations/cohorts and generate deterministic JSON/Markdown reports. E-RUNNER: Provide thin official-run orchestration/import wrappers, never a replacement harness. Risk: reference leakage and false experimental claims. Local fixture work is independent of stage baseline and should proceed when external data is blocked. Actual official runner integration waits for the stage-baseline resource review even though local schema/analysis work does not.

### Stage 5 [stage-real-benchmark] Actual paired Kaggle evidence — HIGH

R-COHORT: Freeze three verified public tasks and selection rationale before outcome inspection; render the official notebook route with the pinned 31B model and explicit arm selection. R-PAIRED: Execute each arm on the same cohort, retain native validation/trace/patch provenance and import compact authentic measurements. R-REPORT: Recompute paired metrics and explain successes, failures, missing telemetry and limitations. Risk: experimental confounding and invalid equivalence of mock/local evidence to Kaggle execution. External execution is an implementation activity; the deterministic gate only reads and verifies its declared evidence. It does not launch a new costly benchmark on every rerun. Failed issue resolution is a measured outcome, not a fabricated success. No superiority claim or minimum score is imposed beyond the user's functional/evidence criteria.

## Validation and evidence

Exact gate argv is in definition.checks. All checks run at the resolved repository root. `uv run --frozen --no-sync` uses the already-installed locked environment and must not resolve/update dependencies in the gate. Tests use temporary directories and disable pytest cache; build/archive checks produce temporary artifacts outside product paths and compare their contents. The scripts are planned project interfaces, not claims that pre-existing commands already exist. Required external resources and evidence are fail-closed prerequisites, never skip/xfail paths. Source and scripts are fully type checked; notebooks are validated structurally and through actual execution provenance. No UI, database, generated API contract, migration or model catalog is built, so those unrelated gates are omitted. The real model name is asserted in every configuration.

- `format` (stage-foundation, timeout 600s): `uv run --frozen --no-sync ruff format --check .`
- `lint` (stage-foundation, timeout 600s): `uv run --frozen --no-sync ruff check .`
- `types` (stage-foundation, timeout 600s): `uv run --frozen --no-sync mypy src scripts`
- `unit` (stage-evaluation, timeout 600s): `uv run --frozen --no-sync pytest -q -p no:cacheprovider tests/unit`
- `integration` (stage-hybrid, timeout 1200s): `uv run --frozen --no-sync pytest -q -p no:cacheprovider tests/integration`
- `official` (stage-baseline, timeout 1200s): `uv run --frozen --no-sync python scripts/check_official.py --check --experiments E0 E1`
- `real-evidence` (stage-real-benchmark, timeout 600s): `uv run --frozen --no-sync python scripts/check_evidence.py --require-real-paired --cohort experiments/cohort.json --evidence-dir docs/implementation/evidence/mostaza-phase1-foundation`

The runtime additionally runs `git diff --check HEAD -- <each stage's exact owned paths>` for every stage and verifies the approved specification digests. There are no passed checks yet.

Declared compact evidence (all owned by stage-real-benchmark):

- `docs/implementation/evidence/mostaza-phase1-foundation/resource-review.json` — official resource versions, hashes, baseline derivation and remaining constraints.
- `docs/implementation/evidence/mostaza-phase1-foundation/official-validation.json` — official compiler and actual Kaggle execution validation receipts with source run IDs.
- `docs/implementation/evidence/mostaza-phase1-foundation/paired-results.jsonl` — compact per-task real E0/E1 measurements and provenance.
- `docs/implementation/evidence/mostaza-phase1-foundation/comparison.json` — deterministically recomputed paired metrics with missingness and denominators.
- `docs/implementation/evidence/mostaza-phase1-foundation/report.md` — preliminary narrative, observed outcomes and limitations.

Evidence is generated/imported during implementation, not manually filled with estimates. Final read-only checks must recalculate summaries and bind source run IDs/hashes, config identity, matched task sets, actual model/runtime and patch/test receipts. Immutable source bundles remain outside Git with reproducible locator/hash records; no secrets or bulky traces are committed. Missing source evidence fails verification. The reports contain results only; workflow decisions and status remain in this plan.

## Approval and publication scope

Approve the specification delta, exact gate, stages and declared evidence together. Approval includes eventual Versioner commit, push of sdd/mostaza-phase1-foundation to origin and publication of a PR targeting develop in the already-public diego-escobar-git/mostaza-harness repository. Remote currently contains main only: before feature/PR publication, Versioner must publish develop at verified initial base ceb055d21c20b5274bb49b24e02e79656482a81f without overwriting any newly existing remote develop. If the Versioner runtime requires develop to preexist or cannot publish the base, report that prerequisite to Orchestrator before closure; do not change PR target or rewrite history. No merge, force push or deployment is authorized. No implementation until the current approval digest is recorded.

The whole phase remains incomplete until the real paired evaluation criterion, full gate, independent zero-finding audit and approved versioning closure succeed. An approved local-only checkpoint may report useful progress but cannot close this plan or weaken the original criteria.

<!-- SDD-CONTINUITY:START -->

```sdd-execution
{
  "version": 3,
  "id": "mostaza-phase1-foundation",
  "project": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness",
  "plan_path": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/docs/specs/plans/open/mostaza-phase1-foundation.md",
  "branch": "sdd/mostaza-phase1-foundation",
  "head": "ceb055d21c20b5274bb49b24e02e79656482a81f",
  "definition": {
    "scope": "Implement complete Phase 1 under docs/specs/foundation.md, agent-retrieval.md and evaluation.md; preserve real Kaggle paired evaluation as mandatory acceptance.",
    "stages": [
      {
        "id": "stage-foundation",
        "level": "MEDIUM",
        "depends": [],
        "items": [
          "F-ENV",
          "F-SCAFFOLD"
        ],
        "paths": [
          "README.md",
          "LICENSE",
          ".gitignore",
          "pyproject.toml",
          "uv.lock",
          ".python-version",
          "src/mostaza/__init__.py",
          "scripts/setup.sh",
          "scripts/validate.sh",
          "tests/unit/test_foundation.py",
          "docs/architecture.md",
          "docs/research-proposal.md",
          "results/.gitkeep"
        ],
        "satisfies": [
          "foundation:AC-1",
          "foundation:AC-2",
          "foundation:AC-4"
        ]
      },
      {
        "id": "stage-baseline",
        "level": "HIGH",
        "depends": [
          "stage-foundation"
        ],
        "items": [
          "B-RESOURCES",
          "B-CONFIG",
          "B-PACKAGE"
        ],
        "paths": [
          "resources/manifest.json",
          "submission/agent.yaml",
          "submission/eval_config.yaml",
          "submission/prompts/baseline.md",
          "experiments/E0-baseline/manifest.json",
          "src/mostaza/packaging.py",
          "src/mostaza/resources.py",
          "scripts/package.sh",
          "scripts/fetch_resources.py",
          "scripts/check_official.py",
          "tests/unit/test_packaging.py",
          "tests/integration/test_official_contract.py"
        ],
        "satisfies": [
          "foundation:AC-3",
          "agent-retrieval:AC-1",
          "agent-retrieval:AC-5"
        ]
      },
      {
        "id": "stage-hybrid",
        "level": "MEDIUM",
        "depends": [
          "stage-foundation"
        ],
        "items": [
          "H-POLICY",
          "H-CONTRACT"
        ],
        "paths": [
          "submission/prompts/hybrid-retrieval.md",
          "experiments/E1-hybrid-retrieval/manifest.json",
          "tests/unit/test_retrieval_policy.py",
          "tests/integration/test_retrieval_contract.py"
        ],
        "satisfies": [
          "agent-retrieval:AC-2",
          "agent-retrieval:AC-3",
          "agent-retrieval:AC-4",
          "agent-retrieval:AC-6"
        ]
      },
      {
        "id": "stage-evaluation",
        "level": "HIGH",
        "depends": [
          "stage-foundation"
        ],
        "items": [
          "E-ISOLATION",
          "E-RECORDS",
          "E-COMPARE",
          "E-RUNNER"
        ],
        "paths": [
          "src/mostaza/evaluation/__init__.py",
          "src/mostaza/evaluation/contracts.py",
          "src/mostaza/evaluation/tasks.py",
          "src/mostaza/evaluation/runner.py",
          "src/mostaza/evaluation/import_results.py",
          "src/mostaza/research/__init__.py",
          "src/mostaza/research/metrics.py",
          "src/mostaza/research/report.py",
          "scripts/run_experiment.sh",
          "scripts/check_evidence.py",
          "tests/unit/test_task_isolation.py",
          "tests/unit/test_results.py",
          "tests/unit/test_metrics.py",
          "tests/integration/test_pipeline.py",
          "docs/experiments.md",
          "docs/kaggle-setup.md"
        ],
        "satisfies": [
          "evaluation:AC-2",
          "evaluation:AC-3",
          "evaluation:AC-5"
        ]
      },
      {
        "id": "stage-real-benchmark",
        "level": "HIGH",
        "depends": [
          "stage-foundation"
        ],
        "items": [
          "R-COHORT",
          "R-PAIRED",
          "R-REPORT"
        ],
        "paths": [
          "experiments/cohort.json",
          "experiments/kaggle-run.ipynb"
        ],
        "satisfies": [
          "evaluation:AC-1",
          "evaluation:AC-4",
          "evaluation:AC-6"
        ]
      }
    ],
    "checks": [
      {
        "id": "format",
        "stage": "stage-foundation",
        "argv": [
          "uv",
          "run",
          "--frozen",
          "--no-sync",
          "ruff",
          "format",
          "--check",
          "."
        ],
        "timeout": 600,
        "basis": "foundation:AC-4; English Python style"
      },
      {
        "id": "lint",
        "stage": "stage-foundation",
        "argv": [
          "uv",
          "run",
          "--frozen",
          "--no-sync",
          "ruff",
          "check",
          "."
        ],
        "timeout": 600,
        "basis": "foundation:AC-4; static defects"
      },
      {
        "id": "types",
        "stage": "stage-foundation",
        "argv": [
          "uv",
          "run",
          "--frozen",
          "--no-sync",
          "mypy",
          "src",
          "scripts"
        ],
        "timeout": 600,
        "basis": "foundation:AC-4; record and API typing"
      },
      {
        "id": "unit",
        "stage": "stage-evaluation",
        "argv": [
          "uv",
          "run",
          "--frozen",
          "--no-sync",
          "pytest",
          "-q",
          "-p",
          "no:cacheprovider",
          "tests/unit"
        ],
        "timeout": 600,
        "basis": "foundation:AC-1,AC-2,AC-4; agent-retrieval:AC-2..AC-5; evaluation:AC-2,AC-3,AC-5"
      },
      {
        "id": "integration",
        "stage": "stage-hybrid",
        "argv": [
          "uv",
          "run",
          "--frozen",
          "--no-sync",
          "pytest",
          "-q",
          "-p",
          "no:cacheprovider",
          "tests/integration"
        ],
        "timeout": 1200,
        "basis": "agent-retrieval:AC-1,AC-5,AC-6; evaluation:AC-2,AC-3; current official compiler and fixture contracts"
      },
      {
        "id": "official",
        "stage": "stage-baseline",
        "argv": [
          "uv",
          "run",
          "--frozen",
          "--no-sync",
          "python",
          "scripts/check_official.py",
          "--check",
          "--experiments",
          "E0",
          "E1"
        ],
        "timeout": 1200,
        "basis": "foundation:AC-3; agent-retrieval:AC-1,AC-5; read-only official provenance, config compilation and reproducible package/build verification"
      },
      {
        "id": "real-evidence",
        "stage": "stage-real-benchmark",
        "argv": [
          "uv",
          "run",
          "--frozen",
          "--no-sync",
          "python",
          "scripts/check_evidence.py",
          "--require-real-paired",
          "--cohort",
          "experiments/cohort.json",
          "--evidence-dir",
          "docs/implementation/evidence/mostaza-phase1-foundation"
        ],
        "timeout": 600,
        "basis": "evaluation:AC-1..AC-6; require sourced actual Kaggle results and recompute paired report"
      }
    ],
    "spec_changes": {
      "files": [
        "docs/specs/README.md",
        "docs/specs/foundation.md",
        "docs/specs/agent-retrieval.md",
        "docs/specs/evaluation.md"
      ],
      "added": [
        "foundation:AC-1",
        "foundation:AC-2",
        "foundation:AC-3",
        "foundation:AC-4",
        "agent-retrieval:AC-1",
        "agent-retrieval:AC-2",
        "agent-retrieval:AC-3",
        "agent-retrieval:AC-4",
        "agent-retrieval:AC-5",
        "agent-retrieval:AC-6",
        "evaluation:AC-1",
        "evaluation:AC-2",
        "evaluation:AC-3",
        "evaluation:AC-4",
        "evaluation:AC-5",
        "evaluation:AC-6"
      ],
      "modified": [],
      "removed": [],
      "restores": [],
      "justification": null
    },
    "evidence": [
      {
        "path": "docs/implementation/evidence/mostaza-phase1-foundation/resource-review.json",
        "stage": "stage-real-benchmark",
        "purpose": "official resource versions, hashes, baseline derivation and remaining constraints"
      },
      {
        "path": "docs/implementation/evidence/mostaza-phase1-foundation/official-validation.json",
        "stage": "stage-real-benchmark",
        "purpose": "official compiler and actual Kaggle execution validation receipts with source run IDs"
      },
      {
        "path": "docs/implementation/evidence/mostaza-phase1-foundation/paired-results.jsonl",
        "stage": "stage-real-benchmark",
        "purpose": "compact per-task real E0/E1 measurements and provenance"
      },
      {
        "path": "docs/implementation/evidence/mostaza-phase1-foundation/comparison.json",
        "stage": "stage-real-benchmark",
        "purpose": "deterministically recomputed paired metrics with missingness and denominators"
      },
      {
        "path": "docs/implementation/evidence/mostaza-phase1-foundation/report.md",
        "stage": "stage-real-benchmark",
        "purpose": "preliminary narrative, observed outcomes and limitations"
      }
    ]
  },
  "baseline": {},
  "approval": {
    "digest": "b5f4a7b8074aba0a10d11fae042a858dc6b06d3d2f39415abb4dbcbe74bbd9b2",
    "gate_digest": "1a18a2ca4e0683c8bd770a13ec5d39b791960d74ac759ebf614df063d3bc3591",
    "evidence": "User explicitly approved specifications, plan, gate and PR publication to develop on 2026-10-13; requested all possible implementation and verification with honest Kaggle blockers.",
    "publish": {
      "remote": "origin",
      "base": "develop"
    },
    "technical_revision": 19
  },
  "approvals": [
    {
      "digest": "15e40e9a68ad226ccbf754448e0ec4a2042c84f190a83ad236cfbfe56ef5191e",
      "gate_digest": "1a18a2ca4e0683c8bd770a13ec5d39b791960d74ac759ebf614df063d3bc3591",
      "evidence": "User explicitly approved specifications, plan, gate and PR publication to develop on 2026-10-13; requested all possible implementation and verification with honest Kaggle blockers.",
      "publish": {
        "remote": "origin",
        "base": "develop"
      }
    },
    {
      "technical_revision": 5,
      "reason": "Technical work-readiness reorganization only. Current approved foundation is complete; evaluation E-ISOLATION/E-RECORDS/E-COMPARE are complete and repository contracts/runner exist. Pinned public wheel/native API source and notebook are available while authenticated README/sample/tasks remain pending. Removing coarse whole-stage prerequisites allows existing hybrid native-contract tests/policy draft and existing notebook/pending-cohort/evidence preparation. H-POLICY remains pending until actual E0 treatment invariants are verified; R-COHORT/R-PAIRED/R-REPORT remain pending until authentic tasks, complete E0/E1 integration and real paired evidence satisfy unchanged prose/ACs. No fake defaults, IDs or results; no weakened gate or completion condition. Only two depends arrays change; all approved prose/specs, paths, items, stage IDs, checks, evidence and history are preserved.",
      "digest": "e0bc97b00b4f37fa93fed9780dec31f8f09bceeadd52f4000c3971e6315519b1"
    },
    {
      "technical_revision": 19,
      "reason": "AUD-001: evaluation owner repairs scripts/check_evidence.py and existing import_results/metrics helpers so unchanged real-evidence gate safely resolves retained source root, verifies source inventory/native manifest/result/trace hashes and executed notebook/archive/config/model/runtime/run provenance, recomputes normalized records and source analysis from authentic bytes and compares declared records/receipts/report. Reuse existing derivation semantics, preserve original executed-source hashes separately from current host postprocessing. Missing, changed, escaped or mismatched native sources fail closed. Add negative tests in existing tests/unit/test_results.py and tests/integration/test_pipeline.py for nonexistent source root, changed native bytes/inventory, forged token metrics with regenerated summaries, mismatched manifest/config/archive/provenance and mismatched analysis; authentic retained six-task data must still pass. AUD-002: evaluation owner updates docs/experiments.md and reassigned docs/kaggle-setup.md to distinguish completed six real31B L4x4 executions from prerequisites for a future rerun: each arm PASS0 FAIL1 ERROR2, all timeout, E1 no vector/graph attempts, no retrieval-benefit conclusion. Reopen existing evaluation items for these corrections. Benchmark owner refreshes only already-declared evidence metadata/derived outputs as required by host-source hashes, using existing authentic results; no numeric manual edits or GPU reruns. Reopen R-REPORT for that bounded regeneration and self-check. Only one existing documentation path changes owning stage; all scope, prose/specs/AC coverage/check semantics/evidence declarations/IDs/history remain unchanged. Findings stay open for independent Auditor after full unchanged gate.",
      "digest": "b5f4a7b8074aba0a10d11fae042a858dc6b06d3d2f39415abb4dbcbe74bbd9b2"
    }
  ],
  "normative_digest": "4f54c83602edb415ff4db7b245f3afbda970d57932912b9f73d24a2a442e99de",
  "normative_material_digest": "056b9050c7a2feafd10c7e37eeddb7ef24a2a83dd26c9e3c955347f172ebe706",
  "planner_pending": false,
  "dispatches": [
    {
      "id": 1,
      "role": "planner",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 2,
      "role": "implementer-medium",
      "stage": "stage-foundation",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 3,
      "role": "implementer-high",
      "stage": "stage-evaluation",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 4,
      "role": "implementer-high",
      "stage": "stage-baseline",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 5,
      "role": "planner",
      "stage": "stage-baseline",
      "status": "DONE",
      "review": 1
    },
    {
      "id": 6,
      "role": "implementer-medium",
      "stage": "stage-hybrid",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 7,
      "role": "implementer-high",
      "stage": "stage-real-benchmark",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 8,
      "role": "implementer-high",
      "stage": "stage-baseline",
      "status": "DONE",
      "review": 1
    },
    {
      "id": 9,
      "role": "implementer-high",
      "stage": "stage-baseline",
      "status": "DONE",
      "review": 1
    },
    {
      "id": 10,
      "role": "implementer-high",
      "stage": "stage-evaluation",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 11,
      "role": "implementer-high",
      "stage": "stage-baseline",
      "status": "DONE",
      "review": 1
    },
    {
      "id": 12,
      "role": "implementer-high",
      "stage": "stage-real-benchmark",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 13,
      "role": "implementer-medium",
      "stage": "stage-hybrid",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 14,
      "role": "implementer-high",
      "stage": "stage-evaluation",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 15,
      "role": "implementer-high",
      "stage": "stage-real-benchmark",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 16,
      "role": "implementer-high",
      "stage": "stage-real-benchmark",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 17,
      "role": "implementer-high",
      "stage": "stage-evaluation",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 18,
      "role": "auditor",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 19,
      "role": "planner",
      "stage": "stage-evaluation",
      "status": "DONE",
      "review": 1
    },
    {
      "id": 20,
      "role": "implementer-high",
      "stage": "stage-evaluation",
      "status": "DONE",
      "review": 1
    },
    {
      "id": 21,
      "role": "implementer-high",
      "stage": "stage-real-benchmark",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 22,
      "role": "auditor",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 23,
      "role": "versioner",
      "stage": null,
      "status": "INTERRUPTED",
      "review": null
    },
    {
      "id": 24,
      "role": "versioner",
      "stage": null,
      "status": "DONE",
      "review": null
    }
  ],
  "legacy_dispatches": 0,
  "audits": [
    {
      "round": 1,
      "verdict": "FIX_REQUIRED",
      "candidate": {
        "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
        "value": "c01446e8fedcb49e7f0f0f226db71abd0820382a06413b42deb2824ebdf61d22"
      },
      "approval_digest": "e0bc97b00b4f37fa93fed9780dec31f8f09bceeadd52f4000c3971e6315519b1",
      "dispatch": 18,
      "acceptance": [
        {
          "id": "foundation:AC-1",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/scripts/setup.sh; Python 3.13 lock, scoped setup and retained fresh-install self-check."
        },
        {
          "id": "foundation:AC-2",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/.gitignore; complete scaffold and Apache-2.0 license."
        },
        {
          "id": "foundation:AC-3",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/resources/manifest.json; authentic pinned resources, source review and fail-closed resource loader."
        },
        {
          "id": "foundation:AC-4",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/docs/specs/plans/active/mostaza-phase1-foundation.md; successful current-candidate format, lint, types, unit, integration and official/package checks; evidence levels remain distinct."
        },
        {
          "id": "agent-retrieval:AC-1",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/experiments/E0-baseline/manifest.json; minimal authenticated single-agent/no-LoRA derivation and source-preserving contract tests."
        },
        {
          "id": "agent-retrieval:AC-2",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/submission/prompts/hybrid-retrieval.md; exploration-only treatment, bounded retrieval and identical shared conditions verified against executed archive contents."
        },
        {
          "id": "agent-retrieval:AC-3",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/submission/prompts/hybrid-retrieval.md; qualitative context priorities and byte-preserved implementation/verification policy."
        },
        {
          "id": "agent-retrieval:AC-4",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/submission/eval_config.yaml; authentic shared provisional limits, budget checkpoints and source-derived attempted/charged tool counts."
        },
        {
          "id": "agent-retrieval:AC-5",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/src/mostaza/packaging.py; deterministic selected closure, boundary rejection tests and real official compiler receipts."
        },
        {
          "id": "agent-retrieval:AC-6",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/tests/integration/test_retrieval_contract.py; pinned native symbol/embedding/graph contracts, bounded traversal and unavailable-resource behavior."
        },
        {
          "id": "evaluation:AC-1",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/experiments/cohort.json; three existing tasks, difficulty rationale, frozen before execution and identical to notebook inputs/native manifests."
        },
        {
          "id": "evaluation:AC-2",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/src/mostaza/evaluation/tasks.py; allowlisted serialization, snapshot/history leakage tests and inspected official generation/verification separation."
        },
        {
          "id": "evaluation:AC-3",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/docs/implementation/evidence/mostaza-phase1-foundation/paired-results.jsonl; six records independently recomputed from native results/traces; immutable manifests, missingness and source identities preserved."
        },
        {
          "id": "evaluation:AC-4",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/results/kaggle-v2-358139443/private-run-evidence/99c637be-d945-4dd7-85d8-4042cfcc2bad; original ZIP, 32 inventory entries and 16 embedded inputs verified; actual 31B responses, local TP4 server and six paired results inspected."
        },
        {
          "id": "evaluation:AC-5",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/docs/implementation/evidence/mostaza-phase1-foundation/report.md; byte-for-byte native-derived comparison/report, failures, denominators, missingness and absent E1 graph/vector engagement."
        },
        {
          "id": "evaluation:AC-6",
          "status": "UNMET",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/docs/experiments.md:196; procedures and outcomes provided but contradictory obsolete status remains (AUD-002)."
        }
      ]
    },
    {
      "round": 2,
      "verdict": "PASS",
      "candidate": {
        "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
        "value": "3b0cb3e5ce0dfb455706bb61d951fe852b27e5ab4ee5e211e89f7ed9c2b8f1e7"
      },
      "approval_digest": "b5f4a7b8074aba0a10d11fae042a858dc6b06d3d2f39415abb4dbcbe74bbd9b2",
      "dispatch": 22,
      "files": {
        ".gitignore": [
          "file",
          420,
          "45ec570e7165a958655f7a3a955fb206e5c6478b48d4c0320cc7cb363ac3a0a2"
        ],
        ".python-version": [
          "file",
          420,
          "861b3dd8083d28f336ef70f6755bc399538ddad627b1d095820ca34cb953cf14"
        ],
        "LICENSE": [
          "file",
          420,
          "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
        ],
        "README.md": [
          "file",
          420,
          "f76bcb473b8b0846c7cbd69cbd4b820790e73b9e14d20b368237dc9d2a76e6ca"
        ],
        "docs/architecture.md": [
          "file",
          420,
          "36f098ef8c753f57fd722d260806542ae2e92151948f166a82090b0521f0ff0c"
        ],
        "docs/experiments.md": [
          "file",
          420,
          "53c73e205c640b98e5327e26d7c2fbb47f6a41eb20a33af14fe2529d3fbf2bcc"
        ],
        "docs/implementation/evidence/mostaza-phase1-foundation/comparison.json": [
          "file",
          420,
          "ab87b9880311dc4815af8362712f031505aa9ba7566f60b5d37f0716a808aa7a"
        ],
        "docs/implementation/evidence/mostaza-phase1-foundation/official-validation.json": [
          "file",
          420,
          "6b083bfbbc9d9bab4dd22a5fa02666b9682e4cdf659db7628804c1b919f24756"
        ],
        "docs/implementation/evidence/mostaza-phase1-foundation/paired-results.jsonl": [
          "file",
          420,
          "05096901634f8770de3d8e2d1720a1fa3831ae71caaf6ce4fe216eecbf45ab5d"
        ],
        "docs/implementation/evidence/mostaza-phase1-foundation/report.md": [
          "file",
          420,
          "b15aef99c3aae5d779fd60adc7965e9848a2275e4423525cb35da58af092f403"
        ],
        "docs/implementation/evidence/mostaza-phase1-foundation/resource-review.json": [
          "file",
          420,
          "57f5980b4c4a1b23f86af1c14846bb26a2908796ec4296a71dca820219d40bcc"
        ],
        "docs/kaggle-setup.md": [
          "file",
          420,
          "eb27f79059a79b10a9a44f51362103b8c3fcc150faf0847d00d5bb1a86984987"
        ],
        "docs/research-proposal.md": [
          "file",
          420,
          "294162495da1ab44315c1b3da88296298947f9a479628144fa6de6601a881700"
        ],
        "docs/specs/README.md": [
          "file",
          420,
          "db51917d8d8466f7eea45aa065c98f8484ca07e0b09def27b7533ba74a7ef28e"
        ],
        "docs/specs/agent-retrieval.md": [
          "file",
          420,
          "0c17913fe07e776b1991e08b62781dab4d66ce727360ae5bcc684dbf7fc1dc20"
        ],
        "docs/specs/evaluation.md": [
          "file",
          420,
          "91b7b07765f7c26f3d09ad2dac95ddf0fba96c448fa48cc68eee10aa40ebb799"
        ],
        "docs/specs/foundation.md": [
          "file",
          420,
          "da4e829be5a736c94b675215d927cb7b54945d23096d91a2a09b0e2196bd817f"
        ],
        "experiments/E0-baseline/manifest.json": [
          "file",
          420,
          "69d25543cdca0dd803f05a8658b32797e8a78c979a0e9c7c42dd303d3e9610b5"
        ],
        "experiments/E1-hybrid-retrieval/manifest.json": [
          "file",
          420,
          "8cba982f0f4e47049df09dee57d4e95bb0a3ce78ed511906228e9375251038db"
        ],
        "experiments/cohort.json": [
          "file",
          420,
          "1ee1eef565392ee98efb2a4aa6398c79611a6e95d61def165410f2aaee918a09"
        ],
        "experiments/kaggle-run.ipynb": [
          "file",
          420,
          "38d858f9bafddaf7df8d3653a56d95ed85ab3a596b8157702e67964fea7c74c0"
        ],
        "pyproject.toml": [
          "file",
          420,
          "f918c4674467ca9472dff0f2be3f16c5472244e641a9511aca9359c5d1e591a7"
        ],
        "resources/manifest.json": [
          "file",
          420,
          "d6e6e7671d63c21ec4d7fc7c97e56ec32733a3aeb6070cf483c22b5dc79cd5e9"
        ],
        "results/.gitkeep": [
          "file",
          420,
          "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ],
        "scripts/check_evidence.py": [
          "file",
          420,
          "bf1354aea7853263d77855f0a388a769ad2ed1e4e3301cedf35e38605f60be80"
        ],
        "scripts/check_official.py": [
          "file",
          420,
          "001045273dc32f2363a3cbb72be08a317a28ad3597f2453fa7f5e1c8f4104b8c"
        ],
        "scripts/fetch_resources.py": [
          "file",
          420,
          "7f4dfc8254fd4e289bcdea9c9fa30078d0e912a1c4e248366abf4786f2eaa341"
        ],
        "scripts/package.sh": [
          "file",
          493,
          "62a83029a7c8c4419382fd6eb1497a39b4f2863089a2527c3fea034d6df93907"
        ],
        "scripts/run_experiment.sh": [
          "file",
          493,
          "c0a58bc5eedfd8c843b984a429a5ded08a933799b8617f9fa083250f6444f77f"
        ],
        "scripts/setup.sh": [
          "file",
          493,
          "40537deb14ca5cf30e56e9c080fab2d30eb55cc0a96ef59169e8e3013d49f181"
        ],
        "scripts/validate.sh": [
          "file",
          493,
          "346a3669a40627a0d80bc309c2ed1dc8bb8a7c6212a37faac3ca62e8c3ddac62"
        ],
        "src/mostaza/__init__.py": [
          "file",
          420,
          "e6e7452e239f7a03d6645be265792ed103fcc93b27da4e1f2b982aa8af018d3c"
        ],
        "src/mostaza/evaluation/__init__.py": [
          "file",
          420,
          "2106119b057d082ec60e8a8e21aef6fcc3f7d63a3ff4d0e177ddbac3db9efcac"
        ],
        "src/mostaza/evaluation/contracts.py": [
          "file",
          420,
          "b8500c062a3e81b7bc0fb6051e72cc4af07689fc1cf2f8dc60f8c58a8c87e7d3"
        ],
        "src/mostaza/evaluation/import_results.py": [
          "file",
          420,
          "9205c08f6db52ae6b178923e72753b2d0ad4f93b0fecd2ef5ec84390c518bfb6"
        ],
        "src/mostaza/evaluation/runner.py": [
          "file",
          420,
          "5f56dfd22e339ac72ae6c93b0b43c4229f92959b5fc28cda1f531d952b229770"
        ],
        "src/mostaza/evaluation/tasks.py": [
          "file",
          420,
          "eab3240c3ddc78114b849b81b8944a74daadd6da7e1859e7bfa99455e6a8dc91"
        ],
        "src/mostaza/packaging.py": [
          "file",
          420,
          "0d391b6c2aecff94f00586d0bc62cbe95b4e8d6a7cd7ddb3b7e8987f9481f725"
        ],
        "src/mostaza/research/__init__.py": [
          "file",
          420,
          "f9bbf774dea93e1ddfc7a00710fbe737cfb2e1404fbb7b83857cbb24e0051059"
        ],
        "src/mostaza/research/metrics.py": [
          "file",
          420,
          "6c98c1523c905cd3646b4ac6dd9d198d1abe58e0c5cbf75c57d1f156f76865dc"
        ],
        "src/mostaza/research/report.py": [
          "file",
          420,
          "5dde63e31be85222c8191f3b150fc7d9a4d6969da4d255f4e2b453251283d9cd"
        ],
        "src/mostaza/resources.py": [
          "file",
          420,
          "b3b628f0b40e5303d18b412664fc2f542088983838ed003960cb0886ef41530c"
        ],
        "submission/agent.yaml": [
          "file",
          420,
          "63231bec8724cb68d0a3d139403cfe2c8c80cddf3edfcb0e971dc38110ae2afc"
        ],
        "submission/eval_config.yaml": [
          "file",
          420,
          "adb486b67535fa59b427b79d44dafc131176f1f1964d184e16046ed520ede02d"
        ],
        "submission/prompts/baseline.md": [
          "file",
          420,
          "4841635e2176986bef18dd6fca44c4757795894506a1db88c30975057884e140"
        ],
        "submission/prompts/hybrid-retrieval.md": [
          "file",
          420,
          "c6ecb762f46ae76ad4cc18a6559706822c559fc110152acc88539a48d7b5be0e"
        ],
        "tests/integration/test_official_contract.py": [
          "file",
          420,
          "f60471ab0deb53dbe1a6bba0cfaf535f9ff3a309c84592b89de7b02cf610d5c7"
        ],
        "tests/integration/test_pipeline.py": [
          "file",
          420,
          "70712ecd1571b3f26535db1c8eb822928fb5d0bc6224c826b1d0319e03683108"
        ],
        "tests/integration/test_retrieval_contract.py": [
          "file",
          420,
          "0d309a3ed50167b05cb3a22da627b9b501e54d2e0e29a5afa3f52c12ee656819"
        ],
        "tests/unit/test_foundation.py": [
          "file",
          420,
          "27b2ada7e9f1d730eede8a0c7ce53be53e92f3c902baa8261ab13f67bd3b6c97"
        ],
        "tests/unit/test_metrics.py": [
          "file",
          420,
          "7564c8f8ef25fbc997bf60c7865c7ce002c6703bfab6757c26ac4c273136d31e"
        ],
        "tests/unit/test_packaging.py": [
          "file",
          420,
          "be76000873bada6903b7ce1bae544a25fc6d8eec850c36778514538845a3fdc7"
        ],
        "tests/unit/test_results.py": [
          "file",
          420,
          "99e64500c2072d86b64923ba9d70e9b8e72194e32b4198531d0aab62d9e2a097"
        ],
        "tests/unit/test_retrieval_policy.py": [
          "file",
          420,
          "591adb161368e76ccae35c20b1f700c88419529d32731d743e43b55f6354f3cd"
        ],
        "tests/unit/test_task_isolation.py": [
          "file",
          420,
          "2874980848dd6f5a3407360eaa2c7cefb3427a6b87b16ae384b970e3ee8292bd"
        ],
        "uv.lock": [
          "file",
          420,
          "83aad5c31df4ede0c8abfd34ee61e4e1f7396f7cdad754ccfe1ad9856daa4e4e"
        ]
      },
      "git_entries": {
        ".gitignore": [
          "100644",
          "3b1214d5f9700304268f2bfaaa61bd8f8ed881fc"
        ],
        ".python-version": [
          "100644",
          "4de75f8d77a3e872d8883636a5d65deefb47fbe6"
        ],
        "LICENSE": [
          "100644",
          "d645695673349e3947e8e5ae42332d0ac3164cd7"
        ],
        "README.md": [
          "100644",
          "5b6129ffe186a4cbde6dbd50ba1720af94d7a816"
        ],
        "docs/architecture.md": [
          "100644",
          "52291b46d395144bc0276e98a13e71b2b78c01bb"
        ],
        "docs/experiments.md": [
          "100644",
          "37385ffe72fa8f8b87339d0cca10ba3ffa035bc3"
        ],
        "docs/implementation/evidence/mostaza-phase1-foundation/comparison.json": [
          "100644",
          "6de13c4e7be99dacd62d75e98630d4dde768a9c2"
        ],
        "docs/implementation/evidence/mostaza-phase1-foundation/official-validation.json": [
          "100644",
          "c27a2fb8cb744cf515b8a10489d480099ddac4e4"
        ],
        "docs/implementation/evidence/mostaza-phase1-foundation/paired-results.jsonl": [
          "100644",
          "eb059b3709e8577b17e68d7ed46094a82ab82f06"
        ],
        "docs/implementation/evidence/mostaza-phase1-foundation/report.md": [
          "100644",
          "4ad5865e186fc17f01549ef19c884d75d95c752b"
        ],
        "docs/implementation/evidence/mostaza-phase1-foundation/resource-review.json": [
          "100644",
          "37ad97f71e7bcd552ca37bd790eb16252ba179cb"
        ],
        "docs/kaggle-setup.md": [
          "100644",
          "321b0de6a277297a9e8ae559ce83db8909b44f3b"
        ],
        "docs/research-proposal.md": [
          "100644",
          "dcc338e0ec7f3e7095e3f8522a08b6c1de9f356a"
        ],
        "docs/specs/README.md": [
          "100644",
          "661f5d9f3426b3c8e95a1588419620fd1959ea00"
        ],
        "docs/specs/agent-retrieval.md": [
          "100644",
          "c7b1cc05d7ede5eafd2cc5effe4310319590d87f"
        ],
        "docs/specs/evaluation.md": [
          "100644",
          "3184fa575b3db1e05e89fff4ef7f5b1b9163b03a"
        ],
        "docs/specs/foundation.md": [
          "100644",
          "2ab7b18e6c4f3f44e472bbff5167871e140aad58"
        ],
        "experiments/E0-baseline/manifest.json": [
          "100644",
          "7b38d81488b5a6c4d7f1c6882dc944222e6a101a"
        ],
        "experiments/E1-hybrid-retrieval/manifest.json": [
          "100644",
          "3f8a1dececd801aa8db3437f545aaabdff0eb1a0"
        ],
        "experiments/cohort.json": [
          "100644",
          "02bb6c42c66846ec743329ee56ac745196825c35"
        ],
        "experiments/kaggle-run.ipynb": [
          "100644",
          "420803bdf585545dfd8696d5c3e9e66efa3bfd04"
        ],
        "pyproject.toml": [
          "100644",
          "8efa24184a22b876572a0f942297a67e0e2c8edd"
        ],
        "resources/manifest.json": [
          "100644",
          "233ae99cf2aa764623bfbe444752e7aeda454184"
        ],
        "results/.gitkeep": [
          "100644",
          "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
        ],
        "scripts/check_evidence.py": [
          "100644",
          "52676d54827562d49399c42664c53e773f52c1d2"
        ],
        "scripts/check_official.py": [
          "100644",
          "0f680e01c5afda541615908b744d7eb8d0e2cc1e"
        ],
        "scripts/fetch_resources.py": [
          "100644",
          "f4c5251423c3e5c4e09faf72f57ceed31d874050"
        ],
        "scripts/package.sh": [
          "100755",
          "60f6c910f0a4f9683e60e823b751d8365b8481c6"
        ],
        "scripts/run_experiment.sh": [
          "100755",
          "ce5ffb2a7205f8f020093480328d21e17100d8e3"
        ],
        "scripts/setup.sh": [
          "100755",
          "c1980d35c4a3e4c814c5404ea293bd52ba3e3296"
        ],
        "scripts/validate.sh": [
          "100755",
          "1f546bcb4ccf978a0f715cebffc8bbc1198ad097"
        ],
        "src/mostaza/__init__.py": [
          "100644",
          "898742420540909b65a0494e225c6ea27a80e70f"
        ],
        "src/mostaza/evaluation/__init__.py": [
          "100644",
          "ba16aef79fa7f856e35b9250ab57e0a860a2748a"
        ],
        "src/mostaza/evaluation/contracts.py": [
          "100644",
          "3d6c2be1e0983cbe929af4b4ce9c74053b8c79a3"
        ],
        "src/mostaza/evaluation/import_results.py": [
          "100644",
          "0940d5745d5d0580521b00698e2aef5a94d414e3"
        ],
        "src/mostaza/evaluation/runner.py": [
          "100644",
          "f7efe25463542853f4e27cb2c707fd9395fe403f"
        ],
        "src/mostaza/evaluation/tasks.py": [
          "100644",
          "9daf86fa1800f230ba9c5a6872071a420634ed36"
        ],
        "src/mostaza/packaging.py": [
          "100644",
          "b83f6cc7610e6fccd12db113f980a28f6642765e"
        ],
        "src/mostaza/research/__init__.py": [
          "100644",
          "cf361cc0bceb22491dc296d9447c98036e03f72d"
        ],
        "src/mostaza/research/metrics.py": [
          "100644",
          "4f10e9da8063a29e49f91abdface214fd6a968fd"
        ],
        "src/mostaza/research/report.py": [
          "100644",
          "d927f7f8f52ad66f43ccbfe7f7a6371ad9a68df6"
        ],
        "src/mostaza/resources.py": [
          "100644",
          "0a87de1fa90309351db3a54ae021a18bd2234cdf"
        ],
        "submission/agent.yaml": [
          "100644",
          "6ad11b950460281b150d4418d2a68335d15e08f4"
        ],
        "submission/eval_config.yaml": [
          "100644",
          "ac12c2901126852890a7438fb9baa3d64424be3a"
        ],
        "submission/prompts/baseline.md": [
          "100644",
          "909d9dbd7a676529e648ff26d73101176ed6afc9"
        ],
        "submission/prompts/hybrid-retrieval.md": [
          "100644",
          "c57ac90a5d1651371fd6f178d56cf9b8df68c517"
        ],
        "tests/integration/test_official_contract.py": [
          "100644",
          "2fdb32c4eca3c82c1f9bfbfddc1884f59f8872d2"
        ],
        "tests/integration/test_pipeline.py": [
          "100644",
          "d49f10ddfe42780a14be88a052a67fa1cd960220"
        ],
        "tests/integration/test_retrieval_contract.py": [
          "100644",
          "881a6ca2f23ed7a0f4bf5817384af43bc820890d"
        ],
        "tests/unit/test_foundation.py": [
          "100644",
          "82ab5f1e09e9f69f6063f1f8822fccc302448d01"
        ],
        "tests/unit/test_metrics.py": [
          "100644",
          "31e4f80e528ae4030b48b4b33a909be4974e997e"
        ],
        "tests/unit/test_packaging.py": [
          "100644",
          "395a77aafc05c15b1d951a52ddd947d762ff24b2"
        ],
        "tests/unit/test_results.py": [
          "100644",
          "fe73999c300e22fe24ca9ee3193c9e34e4353209"
        ],
        "tests/unit/test_retrieval_policy.py": [
          "100644",
          "4ac47c5e41ec4efcabe2905c209a8da74fd10d46"
        ],
        "tests/unit/test_task_isolation.py": [
          "100644",
          "5be718e64f4ac7627469d933f8ea82e7199ddece"
        ],
        "uv.lock": [
          "100644",
          "a17da4733c9361331502c81056d15f6bb2cbe7d4"
        ]
      },
      "acceptance": [
        {
          "id": "foundation:AC-1",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/scripts/setup.sh: scoped locked Python3.13 setup and fresh-install validation; no model download or Colima change."
        },
        {
          "id": "foundation:AC-2",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/.gitignore: complete scaffold, Apache-2.0 and credential/environment/dataset/weight/bulky-output exclusions."
        },
        {
          "id": "foundation:AC-3",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/resources/manifest.json: authentic official resource pins/provenance/versions; missing or changed resources fail closed."
        },
        {
          "id": "foundation:AC-4",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/docs/specs/plans/active/mostaza-phase1-foundation.md: current full gate passed; independent correction tests12/12."
        },
        {
          "id": "agent-retrieval:AC-1",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/experiments/E0-baseline/manifest.json: source-bound minimal single-agent31B/no-LoRA derivation and tested adjustments."
        },
        {
          "id": "agent-retrieval:AC-2",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/submission/prompts/hybrid-retrieval.md: exploration-only treatment, symbol-seeded bounded retrieval and shared conditions/archive identity verified."
        },
        {
          "id": "agent-retrieval:AC-3",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/submission/prompts/hybrid-retrieval.md: qualitative context priorities, single-agent phases and preserved E0 implementation/verification."
        },
        {
          "id": "agent-retrieval:AC-4",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/submission/eval_config.yaml: shared authentic limits/enforcement/checkpoints and honest native attempted/charged usage."
        },
        {
          "id": "agent-retrieval:AC-5",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/src/mostaza/packaging.py: explicit deterministic closure and boundary rejection; current official directory/schema/compiler validation."
        },
        {
          "id": "agent-retrieval:AC-6",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/tests/integration/test_retrieval_contract.py: native graph/embedding exact/ambiguous/missing/unavailable/bounded cases; fixtures distinct from agent behavior."
        },
        {
          "id": "evaluation:AC-1",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/experiments/cohort.json: pre-execution frozen Requests/FastAPI/Rich IDs/commits/hashes/rationale matched executed inputs."
        },
        {
          "id": "evaluation:AC-2",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/src/mostaza/evaluation/tasks.py: allowlisted input and snapshot/history isolation, official generation/verification separation."
        },
        {
          "id": "evaluation:AC-3",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/docs/implementation/evidence/mostaza-phase1-foundation/official-validation.json: source-bound immutable manifests; six native recomputations; independent missing-source/forged-token probes reject."
        },
        {
          "id": "evaluation:AC-4",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/results/kaggle-v2-358139443/private-run-evidence/99c637be-d945-4dd7-85d8-4042cfcc2bad: six real31B paired executions and TP4 provenance, originalZIP/32inventory/16notebook-input pins verified."
        },
        {
          "id": "evaluation:AC-5",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/docs/implementation/evidence/mostaza-phase1-foundation/report.md: deterministic native-derived report; zero resolved both arms, no E1graph/vector engagement or superiority claim."
        },
        {
          "id": "evaluation:AC-6",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/docs/experiments.md: verified procedures/current outcomes/limitations/next steps; obsolete pending wording corrected."
        }
      ]
    }
  ],
  "findings": {
    "AUD-001": {
      "id": "AUD-001",
      "severity": "MEDIUM",
      "location": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/scripts/check_evidence.py:43",
      "issue": "The real-evidence gate validates compact records against their summaries without verifying retained native sources. Auditor isolated-copy probes accepted a nonexistent retained_source_root and changing Requests E0 tokens from 38523 to 1038522 with regenerated summaries and the original trace digest. Current measurements independently match authentic sources, but approved fail-closed verification is not implemented.",
      "expected": "Missing or changed native evidence and measurements inconsistent with that evidence must fail the unchanged approved gate.",
      "correction": "Resolve retained source bundle safely; verify inventory and native manifest/result/trace hashes; recompute normalized records and source analysis and compare declared evidence. Bind executed archives/configuration and execution provenance. Regression tests for missing sources and altered measurements.",
      "open": false,
      "stage": "stage-evaluation"
    },
    "AUD-002": {
      "id": "AUD-002",
      "severity": "LOW",
      "location": "/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/docs/experiments.md:196",
      "acceptance_id": "evaluation:AC-6",
      "issue": "Closing paragraph says no E0/E1 outcome observed, contradicting completed executions and measured failures. Pending-integration heading and Kaggle setup remaining-prerequisite wording retain obsolete execution status.",
      "expected": "Documentation consistently states observed outcomes, current prerequisites and remaining research limitations.",
      "correction": "Replace obsolete pending/no-outcome wording with verified six executions, zero resolved tasks and absence of evidence for retrieval improvement.",
      "open": false,
      "stage": "stage-evaluation"
    }
  },
  "stages": {
    "stage-foundation": {
      "done": [
        "F-ENV",
        "F-SCAFFOLD"
      ],
      "reviews": 0,
      "failures": 0,
      "review": null,
      "blocked": null,
      "checkpoint": {
        "item": "F-SCAFFOLD",
        "evidence": "Added scoped setup/full validation shell entrypoints, Apache2 license, credential/asset ignore rules, host package, README, architecture and proposal docs. Self-review preserves local/compiler/real evidence boundaries. Ruff format/check passed; foundation pytest3/3, mypy src, bash syntax and fresh temporary locked install/sdist/wheel/clean wheel import passed. Exact mypy src scripts awaits stage-owned Python scripts; no claim of full phase gate or Kaggle pass.",
        "candidate": {
          "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
          "value": "71f887734a18aac8fbcff9b8a67ff19c24a9724c7fd3ddc15a7dc72f2324a17a"
        }
      },
      "gate_history": [
        0,
        0
      ]
    },
    "stage-baseline": {
      "done": [
        "B-RESOURCES",
        "B-CONFIG",
        "B-PACKAGE"
      ],
      "reviews": 1,
      "failures": 0,
      "review": null,
      "blocked": null,
      "gate_history": [
        0,
        0,
        0
      ],
      "checkpoint": {
        "item": "B-PACKAGE",
        "evidence": "Self-review high-risk path/closure boundary complete: explicit ready E0/E1, known31B/native9tools, only selected transitive includes, nofollow component reads/nonregular rejection, traversal/symlink/FIFO/forbidden/missing/cyclic tests.46 scoped baseline tests passed plus Ruff/types/format/diff clean. Exact approved official argv executed exit0: both actual derived configs current pinned directory/schema/compiler PASS, two byteidentical deterministic archives each, host sdist+wheel built. E0 ZIP SHA aa40c075b2bf77c62cca80b9a9b1ec8fd5f28131295c9bf03926fce241464fe4; E1 be8ebd8e660c75b6a7e467b6590e0ff4f093077055e7aeee0db6fa6a0ddd375e. Canonicalize macOS temp root to preserve unchanged official no-symlink checks. Compiler-only; no model execution.",
        "candidate": {
          "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
          "value": "e31f10943935ffebe5041d86992c8ad23b7b9a4c9ea30b1ff7123953c6dfe7ef"
        }
      }
    },
    "stage-hybrid": {
      "done": [
        "H-CONTRACT",
        "H-POLICY"
      ],
      "reviews": 0,
      "failures": 0,
      "review": null,
      "blocked": null,
      "checkpoint": {
        "item": "H-POLICY",
        "evidence": "E1 finalized against authenticated frozen E0: section1 exploration replacement only; byteexact surrounding prompt incl shared AC4 suffix. Actual isolation tests verify model/sampling/tool order/eval/budgets/repair/environment/source hashes/shared conditions equality and prompt hashes. max_neighbors10/k5/one-hop evidencebased two-hop native policy. True E1 directory/schema/compiler PASS twice through build_submission; deterministic ZIP exact selected closure. Scoped ruff check/format passed; targeted7/7; approved integration16/16 and units82/82. Ready manifest is compiler/config readiness only; real Gemma NOT_RUN/compatibility unverified. Self-review preserves unchanged E0 settings and honest inference boundary.",
        "candidate": {
          "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
          "value": "5d47e87b8d59d42cb4fcaf8f003b1199dc70718f5a8a134f226023a8d4c145c0"
        }
      },
      "gate_history": [
        0,
        0
      ]
    },
    "stage-evaluation": {
      "done": [
        "E-ISOLATION",
        "E-RECORDS",
        "E-COMPARE",
        "E-RUNNER"
      ],
      "reviews": 1,
      "failures": 0,
      "review": null,
      "blocked": null,
      "checkpoint": {
        "item": "E-RUNNER",
        "evidence": "AUD002 docs experiments/setup obsolete pending/nooutcome text replaced by actual v2run358139443 six31B L4x4 executions: eacharm PASS0 FAIL1 ERROR2, alltimeout, noresolvedtask/E1graphvectorcall. Future rerun prerequisites separated. AUD001 source guard binds actual executed notebook/input archives/model traces/local vLLM serving and original57c runtime overlay separately from current9205c host helper; never currentHEAD. Authentic complete gate clone passes + negative provenance regressions.65 scoped tests/lint/types pass; no GPU/model rerun or evidence/spec/Git write. Actualgate awaits21 metadata refresh.",
        "candidate": {
          "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
          "value": "22bb0ac1c4edfb6ab8bbb2c1dd15dbbe89835c513d133c882a1cb5598c2a0c23"
        }
      },
      "gate_history": [
        0,
        0,
        0
      ]
    },
    "stage-real-benchmark": {
      "done": [
        "R-COHORT",
        "R-PAIRED",
        "R-REPORT"
      ],
      "reviews": 0,
      "failures": 0,
      "review": null,
      "blocked": null,
      "decisions": [
        {
          "cause": "EXTERNAL",
          "block": {
            "scope": {
              "decision_id": "kaggle-authenticated-cohort-resources",
              "item": "R-COHORT",
              "paths": [
                "experiments/cohort.json"
              ],
              "policy": "authenticated-official-resources-v1",
              "semantics": "User must personally complete Kaggle competition entry and rules acceptance in the current signed-in session, then authentic official resource acquisition and review must succeed before pre-outcome frozen cohort selection. Browser sign-in is observed but the Data page still requires joining to view data; authenticated API access and resource bytes remain unverified.",
              "limits": [
                "No credentials in Git or chat",
                "No competition rule acceptance by an agent",
                "Official sources only",
                "Acquire selected needed assets only; no full dataset or model downloads on the Mac",
                "No fabricated task IDs, model runs, configs or results",
                "Approved gate and acceptance criteria remain unchanged"
              ]
            },
            "scope_digest": "c7837c7572aac1bf836c572d4b8ece78547d6ed93c3163cb02fc1199a3252641"
          }
        },
        {
          "cause": "EXTERNAL",
          "authorization": 1,
          "scope_digest": "c7837c7572aac1bf836c572d4b8ece78547d6ed93c3163cb02fc1199a3252641",
          "evidence": "User stated Ya terminé y estoy inscrito en el challenge. Authenticated Kaggle Data UI now displays full HARNESS_README and Submit Prediction; official individual download produced /Users/diego/Downloads/HARNESS_README.md (55940 bytes). Original approved bounded acquisition limits remain unchanged."
        }
      ],
      "external_block": {
        "scope": {
          "decision_id": "kaggle-authenticated-cohort-resources",
          "item": "R-COHORT",
          "paths": [
            "experiments/cohort.json"
          ],
          "policy": "authenticated-official-resources-v1",
          "semantics": "User must personally complete Kaggle competition entry and rules acceptance in the current signed-in session, then authentic official resource acquisition and review must succeed before pre-outcome frozen cohort selection. Browser sign-in is observed but the Data page still requires joining to view data; authenticated API access and resource bytes remain unverified.",
          "limits": [
            "No credentials in Git or chat",
            "No competition rule acceptance by an agent",
            "Official sources only",
            "Acquire selected needed assets only; no full dataset or model downloads on the Mac",
            "No fabricated task IDs, model runs, configs or results",
            "Approved gate and acceptance criteria remain unchanged"
          ]
        },
        "scope_digest": "c7837c7572aac1bf836c572d4b8ece78547d6ed93c3163cb02fc1199a3252641"
      },
      "checkpoint": {
        "item": "R-REPORT",
        "evidence": "Planner19 bounded regeneration complete: create-only ignored retention copies of authentic ZIP a654d3f and executed notebook b615bed byte-identical to originals; acquisition now records project-relative source paths and actual executed input root. Current9205c host normalizer/bf1354 checker digests refreshed via native evidence generator; original57c executed source, native inventory/manifests, outcomes and all numeric metrics unchanged. Exact approved real-evidence command exit0 verifies retained sources and deterministic derivation. Fresh immutable-bundle report CLI reproduces comparison/report byte-for-byte; stage-scoped git diff --check HEAD exit0. Auditor findings remain for independent re-audit; no GPU rerun.",
        "candidate": {
          "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
          "value": "3b0cb3e5ce0dfb455706bb61d951fe852b27e5ab4ee5e211e89f7ed9c2b8f1e7"
        }
      },
      "gate_history": [
        0,
        0
      ]
    }
  },
  "gate": {
    "candidate": {
      "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
      "value": "3b0cb3e5ce0dfb455706bb61d951fe852b27e5ab4ee5e211e89f7ed9c2b8f1e7"
    },
    "digest": "d405fb1c66ac0fa0245679bff64d6f847d738222681f1bbfb783643540636c4a",
    "results": [
      {
        "id": "spec-frozen",
        "stage": null,
        "code": 0,
        "spec_digest": "e7a2f60f70b805fe54dde5c911e2c1441499a0d391afcccfcff22bc8a8da82a6"
      },
      {
        "id": "git-diff-check-stage-foundation",
        "stage": "stage-foundation",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-baseline",
        "stage": "stage-baseline",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-hybrid",
        "stage": "stage-hybrid",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-evaluation",
        "stage": "stage-evaluation",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-real-benchmark",
        "stage": "stage-real-benchmark",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "format",
        "stage": "stage-foundation",
        "code": 0,
        "output_digest": "00130a4c8959aba48d3edd55439cc0023d306b510d8ec56f7d1dd97cd7bf3fb2"
      },
      {
        "id": "lint",
        "stage": "stage-foundation",
        "code": 0,
        "output_digest": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"
      },
      {
        "id": "types",
        "stage": "stage-foundation",
        "code": 0,
        "output_digest": "fe22d95914d7fdd98483ace256b7f2708db4be1255737e5d7cca4d16703ca242"
      },
      {
        "id": "unit",
        "stage": "stage-evaluation",
        "code": 0,
        "output_digest": "6f5988fa89bdc5197d785a9175802eb386aa49128de92734303e7f45f8eccae4"
      },
      {
        "id": "integration",
        "stage": "stage-hybrid",
        "code": 0,
        "output_digest": "b501d6ff0a0b3260352519d8336fdd02faed5b86e60b2ca7c6c3f5e88227660f"
      },
      {
        "id": "official",
        "stage": "stage-baseline",
        "code": 0,
        "output_digest": "bd0e66ae4a774f61c655faf9d5404403a5c643b79e5df583b5fe14d7926be0ce"
      },
      {
        "id": "real-evidence",
        "stage": "stage-real-benchmark",
        "code": 0,
        "output_digest": "4d9a7a3ed3b5a16c54dce71a5ec514a6312ffd1431f4088f757115d9e931998b"
      }
    ]
  },
  "versioning": {
    "candidate": {
      "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
      "value": "3b0cb3e5ce0dfb455706bb61d951fe852b27e5ab4ee5e211e89f7ed9c2b8f1e7"
    },
    "status": "CLOSED_FOR_COMMIT",
    "paths": [
      ".gitignore",
      ".python-version",
      "LICENSE",
      "README.md",
      "docs/architecture.md",
      "docs/experiments.md",
      "docs/implementation/evidence/mostaza-phase1-foundation/comparison.json",
      "docs/implementation/evidence/mostaza-phase1-foundation/official-validation.json",
      "docs/implementation/evidence/mostaza-phase1-foundation/paired-results.jsonl",
      "docs/implementation/evidence/mostaza-phase1-foundation/report.md",
      "docs/implementation/evidence/mostaza-phase1-foundation/resource-review.json",
      "docs/kaggle-setup.md",
      "docs/research-proposal.md",
      "docs/specs/README.md",
      "docs/specs/agent-retrieval.md",
      "docs/specs/evaluation.md",
      "docs/specs/foundation.md",
      "experiments/E0-baseline/manifest.json",
      "experiments/E1-hybrid-retrieval/manifest.json",
      "experiments/cohort.json",
      "experiments/kaggle-run.ipynb",
      "pyproject.toml",
      "resources/manifest.json",
      "results/.gitkeep",
      "scripts/check_evidence.py",
      "scripts/check_official.py",
      "scripts/fetch_resources.py",
      "scripts/package.sh",
      "scripts/run_experiment.sh",
      "scripts/setup.sh",
      "scripts/validate.sh",
      "src/mostaza/__init__.py",
      "src/mostaza/evaluation/__init__.py",
      "src/mostaza/evaluation/contracts.py",
      "src/mostaza/evaluation/import_results.py",
      "src/mostaza/evaluation/runner.py",
      "src/mostaza/evaluation/tasks.py",
      "src/mostaza/packaging.py",
      "src/mostaza/research/__init__.py",
      "src/mostaza/research/metrics.py",
      "src/mostaza/research/report.py",
      "src/mostaza/resources.py",
      "submission/agent.yaml",
      "submission/eval_config.yaml",
      "submission/prompts/baseline.md",
      "submission/prompts/hybrid-retrieval.md",
      "tests/integration/test_official_contract.py",
      "tests/integration/test_pipeline.py",
      "tests/integration/test_retrieval_contract.py",
      "tests/unit/test_foundation.py",
      "tests/unit/test_metrics.py",
      "tests/unit/test_packaging.py",
      "tests/unit/test_results.py",
      "tests/unit/test_retrieval_policy.py",
      "tests/unit/test_task_isolation.py",
      "uv.lock",
      "docs/specs/plans/closed/mostaza-phase1-foundation.md"
    ],
    "files": {
      "scripts/run_experiment.sh": [
        "file",
        493,
        "c0a58bc5eedfd8c843b984a429a5ded08a933799b8617f9fa083250f6444f77f"
      ],
      "src/mostaza/evaluation/runner.py": [
        "file",
        420,
        "5f56dfd22e339ac72ae6c93b0b43c4229f92959b5fc28cda1f531d952b229770"
      ],
      "tests/integration/test_retrieval_contract.py": [
        "file",
        420,
        "0d309a3ed50167b05cb3a22da627b9b501e54d2e0e29a5afa3f52c12ee656819"
      ],
      "LICENSE": [
        "file",
        420,
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
      ],
      "docs/implementation/evidence/mostaza-phase1-foundation/official-validation.json": [
        "file",
        420,
        "6b083bfbbc9d9bab4dd22a5fa02666b9682e4cdf659db7628804c1b919f24756"
      ],
      "tests/unit/test_results.py": [
        "file",
        420,
        "99e64500c2072d86b64923ba9d70e9b8e72194e32b4198531d0aab62d9e2a097"
      ],
      "scripts/setup.sh": [
        "file",
        493,
        "40537deb14ca5cf30e56e9c080fab2d30eb55cc0a96ef59169e8e3013d49f181"
      ],
      "docs/specs/README.md": [
        "file",
        420,
        "db51917d8d8466f7eea45aa065c98f8484ca07e0b09def27b7533ba74a7ef28e"
      ],
      "submission/eval_config.yaml": [
        "file",
        420,
        "adb486b67535fa59b427b79d44dafc131176f1f1964d184e16046ed520ede02d"
      ],
      "experiments/kaggle-run.ipynb": [
        "file",
        420,
        "38d858f9bafddaf7df8d3653a56d95ed85ab3a596b8157702e67964fea7c74c0"
      ],
      "docs/implementation/evidence/mostaza-phase1-foundation/comparison.json": [
        "file",
        420,
        "ab87b9880311dc4815af8362712f031505aa9ba7566f60b5d37f0716a808aa7a"
      ],
      "docs/specs/foundation.md": [
        "file",
        420,
        "da4e829be5a736c94b675215d927cb7b54945d23096d91a2a09b0e2196bd817f"
      ],
      "docs/kaggle-setup.md": [
        "file",
        420,
        "eb27f79059a79b10a9a44f51362103b8c3fcc150faf0847d00d5bb1a86984987"
      ],
      "src/mostaza/research/metrics.py": [
        "file",
        420,
        "6c98c1523c905cd3646b4ac6dd9d198d1abe58e0c5cbf75c57d1f156f76865dc"
      ],
      "submission/agent.yaml": [
        "file",
        420,
        "63231bec8724cb68d0a3d139403cfe2c8c80cddf3edfcb0e971dc38110ae2afc"
      ],
      "docs/research-proposal.md": [
        "file",
        420,
        "294162495da1ab44315c1b3da88296298947f9a479628144fa6de6601a881700"
      ],
      "submission/prompts/hybrid-retrieval.md": [
        "file",
        420,
        "c6ecb762f46ae76ad4cc18a6559706822c559fc110152acc88539a48d7b5be0e"
      ],
      "tests/unit/test_retrieval_policy.py": [
        "file",
        420,
        "591adb161368e76ccae35c20b1f700c88419529d32731d743e43b55f6354f3cd"
      ],
      "src/mostaza/evaluation/tasks.py": [
        "file",
        420,
        "eab3240c3ddc78114b849b81b8944a74daadd6da7e1859e7bfa99455e6a8dc91"
      ],
      "tests/unit/test_task_isolation.py": [
        "file",
        420,
        "2874980848dd6f5a3407360eaa2c7cefb3427a6b87b16ae384b970e3ee8292bd"
      ],
      "docs/implementation/evidence/mostaza-phase1-foundation/paired-results.jsonl": [
        "file",
        420,
        "05096901634f8770de3d8e2d1720a1fa3831ae71caaf6ce4fe216eecbf45ab5d"
      ],
      "src/mostaza/resources.py": [
        "file",
        420,
        "b3b628f0b40e5303d18b412664fc2f542088983838ed003960cb0886ef41530c"
      ],
      "resources/manifest.json": [
        "file",
        420,
        "d6e6e7671d63c21ec4d7fc7c97e56ec32733a3aeb6070cf483c22b5dc79cd5e9"
      ],
      "pyproject.toml": [
        "file",
        420,
        "f918c4674467ca9472dff0f2be3f16c5472244e641a9511aca9359c5d1e591a7"
      ],
      "src/mostaza/packaging.py": [
        "file",
        420,
        "0d391b6c2aecff94f00586d0bc62cbe95b4e8d6a7cd7ddb3b7e8987f9481f725"
      ],
      "scripts/check_official.py": [
        "file",
        420,
        "001045273dc32f2363a3cbb72be08a317a28ad3597f2453fa7f5e1c8f4104b8c"
      ],
      ".gitignore": [
        "file",
        420,
        "45ec570e7165a958655f7a3a955fb206e5c6478b48d4c0320cc7cb363ac3a0a2"
      ],
      "tests/integration/test_official_contract.py": [
        "file",
        420,
        "f60471ab0deb53dbe1a6bba0cfaf535f9ff3a309c84592b89de7b02cf610d5c7"
      ],
      "tests/integration/test_pipeline.py": [
        "file",
        420,
        "70712ecd1571b3f26535db1c8eb822928fb5d0bc6224c826b1d0319e03683108"
      ],
      "docs/architecture.md": [
        "file",
        420,
        "36f098ef8c753f57fd722d260806542ae2e92151948f166a82090b0521f0ff0c"
      ],
      "scripts/fetch_resources.py": [
        "file",
        420,
        "7f4dfc8254fd4e289bcdea9c9fa30078d0e912a1c4e248366abf4786f2eaa341"
      ],
      "scripts/package.sh": [
        "file",
        493,
        "62a83029a7c8c4419382fd6eb1497a39b4f2863089a2527c3fea034d6df93907"
      ],
      "scripts/validate.sh": [
        "file",
        493,
        "346a3669a40627a0d80bc309c2ed1dc8bb8a7c6212a37faac3ca62e8c3ddac62"
      ],
      "src/mostaza/research/__init__.py": [
        "file",
        420,
        "f9bbf774dea93e1ddfc7a00710fbe737cfb2e1404fbb7b83857cbb24e0051059"
      ],
      "docs/experiments.md": [
        "file",
        420,
        "53c73e205c640b98e5327e26d7c2fbb47f6a41eb20a33af14fe2529d3fbf2bcc"
      ],
      "src/mostaza/evaluation/contracts.py": [
        "file",
        420,
        "b8500c062a3e81b7bc0fb6051e72cc4af07689fc1cf2f8dc60f8c58a8c87e7d3"
      ],
      "tests/unit/test_foundation.py": [
        "file",
        420,
        "27b2ada7e9f1d730eede8a0c7ce53be53e92f3c902baa8261ab13f67bd3b6c97"
      ],
      "scripts/check_evidence.py": [
        "file",
        420,
        "bf1354aea7853263d77855f0a388a769ad2ed1e4e3301cedf35e38605f60be80"
      ],
      "submission/prompts/baseline.md": [
        "file",
        420,
        "4841635e2176986bef18dd6fca44c4757795894506a1db88c30975057884e140"
      ],
      "experiments/cohort.json": [
        "file",
        420,
        "1ee1eef565392ee98efb2a4aa6398c79611a6e95d61def165410f2aaee918a09"
      ],
      "results/.gitkeep": [
        "file",
        420,
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      ],
      "docs/implementation/evidence/mostaza-phase1-foundation/resource-review.json": [
        "file",
        420,
        "57f5980b4c4a1b23f86af1c14846bb26a2908796ec4296a71dca820219d40bcc"
      ],
      "tests/unit/test_packaging.py": [
        "file",
        420,
        "be76000873bada6903b7ce1bae544a25fc6d8eec850c36778514538845a3fdc7"
      ],
      "docs/specs/agent-retrieval.md": [
        "file",
        420,
        "0c17913fe07e776b1991e08b62781dab4d66ce727360ae5bcc684dbf7fc1dc20"
      ],
      "tests/unit/test_metrics.py": [
        "file",
        420,
        "7564c8f8ef25fbc997bf60c7865c7ce002c6703bfab6757c26ac4c273136d31e"
      ],
      "src/mostaza/evaluation/import_results.py": [
        "file",
        420,
        "9205c08f6db52ae6b178923e72753b2d0ad4f93b0fecd2ef5ec84390c518bfb6"
      ],
      "docs/implementation/evidence/mostaza-phase1-foundation/report.md": [
        "file",
        420,
        "b15aef99c3aae5d779fd60adc7965e9848a2275e4423525cb35da58af092f403"
      ],
      ".python-version": [
        "file",
        420,
        "861b3dd8083d28f336ef70f6755bc399538ddad627b1d095820ca34cb953cf14"
      ],
      "docs/specs/evaluation.md": [
        "file",
        420,
        "91b7b07765f7c26f3d09ad2dac95ddf0fba96c448fa48cc68eee10aa40ebb799"
      ],
      "src/mostaza/__init__.py": [
        "file",
        420,
        "e6e7452e239f7a03d6645be265792ed103fcc93b27da4e1f2b982aa8af018d3c"
      ],
      "src/mostaza/evaluation/__init__.py": [
        "file",
        420,
        "2106119b057d082ec60e8a8e21aef6fcc3f7d63a3ff4d0e177ddbac3db9efcac"
      ],
      "README.md": [
        "file",
        420,
        "f76bcb473b8b0846c7cbd69cbd4b820790e73b9e14d20b368237dc9d2a76e6ca"
      ],
      "experiments/E1-hybrid-retrieval/manifest.json": [
        "file",
        420,
        "8cba982f0f4e47049df09dee57d4e95bb0a3ce78ed511906228e9375251038db"
      ],
      "src/mostaza/research/report.py": [
        "file",
        420,
        "5dde63e31be85222c8191f3b150fc7d9a4d6969da4d255f4e2b453251283d9cd"
      ],
      "experiments/E0-baseline/manifest.json": [
        "file",
        420,
        "69d25543cdca0dd803f05a8658b32797e8a78c979a0e9c7c42dd303d3e9610b5"
      ],
      "uv.lock": [
        "file",
        420,
        "83aad5c31df4ede0c8abfd34ee61e4e1f7396f7cdad754ccfe1ad9856daa4e4e"
      ]
    }
  },
  "legacy": null,
  "autonomy": {
    "policy": "audit-only-v1",
    "authorizations": []
  },
  "specification_policy": "planner-first-v1",
  "work_branch": {
    "name": "sdd/mostaza-phase1-foundation",
    "base": "develop",
    "base_head": "ceb055d21c20b5274bb49b24e02e79656482a81f",
    "initial_head": "ceb055d21c20b5274bb49b24e02e79656482a81f",
    "remote": "origin",
    "target": "develop",
    "push_url": "git@github.com:diego-escobar-git/mostaza-harness.git"
  },
  "spec_file_digest": "e7a2f60f70b805fe54dde5c911e2c1441499a0d391afcccfcff22bc8a8da82a6",
  "external_authorizations": [
    {
      "id": 1,
      "decision_id": "kaggle-authenticated-cohort-resources",
      "stage": "stage-real-benchmark",
      "item": "R-COHORT",
      "scope": {
        "decision_id": "kaggle-authenticated-cohort-resources",
        "item": "R-COHORT",
        "paths": [
          "experiments/cohort.json"
        ],
        "policy": "authenticated-official-resources-v1",
        "semantics": "User must personally complete Kaggle competition entry and rules acceptance in the current signed-in session, then authentic official resource acquisition and review must succeed before pre-outcome frozen cohort selection. Browser sign-in is observed but the Data page still requires joining to view data; authenticated API access and resource bytes remain unverified.",
        "limits": [
          "No credentials in Git or chat",
          "No competition rule acceptance by an agent",
          "Official sources only",
          "Acquire selected needed assets only; no full dataset or model downloads on the Mac",
          "No fabricated task IDs, model runs, configs or results",
          "Approved gate and acceptance criteria remain unchanged"
        ]
      },
      "scope_digest": "c7837c7572aac1bf836c572d4b8ece78547d6ed93c3163cb02fc1199a3252641",
      "source": "user",
      "evidence": "User stated Ya terminé y estoy inscrito en el challenge. Authenticated Kaggle Data UI now displays full HARNESS_README and Submit Prediction; official individual download produced /Users/diego/Downloads/HARNESS_README.md (55940 bytes). Original approved bounded acquisition limits remain unchanged.",
      "status": "CONSUMED"
    }
  ],
  "gate_sequence": 2,
  "last_gate": {
    "results": [
      {
        "id": "spec-frozen",
        "stage": null,
        "code": 0,
        "spec_digest": "e7a2f60f70b805fe54dde5c911e2c1441499a0d391afcccfcff22bc8a8da82a6"
      },
      {
        "id": "git-diff-check-stage-foundation",
        "stage": "stage-foundation",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-baseline",
        "stage": "stage-baseline",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-hybrid",
        "stage": "stage-hybrid",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-evaluation",
        "stage": "stage-evaluation",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-real-benchmark",
        "stage": "stage-real-benchmark",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "format",
        "stage": "stage-foundation",
        "code": 0,
        "output_digest": "00130a4c8959aba48d3edd55439cc0023d306b510d8ec56f7d1dd97cd7bf3fb2"
      },
      {
        "id": "lint",
        "stage": "stage-foundation",
        "code": 0,
        "output_digest": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"
      },
      {
        "id": "types",
        "stage": "stage-foundation",
        "code": 0,
        "output_digest": "fe22d95914d7fdd98483ace256b7f2708db4be1255737e5d7cca4d16703ca242"
      },
      {
        "id": "unit",
        "stage": "stage-evaluation",
        "code": 0,
        "output_digest": "6f5988fa89bdc5197d785a9175802eb386aa49128de92734303e7f45f8eccae4"
      },
      {
        "id": "integration",
        "stage": "stage-hybrid",
        "code": 0,
        "output_digest": "b501d6ff0a0b3260352519d8336fdd02faed5b86e60b2ca7c6c3f5e88227660f"
      },
      {
        "id": "official",
        "stage": "stage-baseline",
        "code": 0,
        "output_digest": "bd0e66ae4a774f61c655faf9d5404403a5c643b79e5df583b5fe14d7926be0ce"
      },
      {
        "id": "real-evidence",
        "stage": "stage-real-benchmark",
        "code": 0,
        "output_digest": "4d9a7a3ed3b5a16c54dce71a5ec514a6312ffd1431f4088f757115d9e931998b"
      }
    ],
    "candidate": {
      "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
      "value": "3b0cb3e5ce0dfb455706bb61d951fe852b27e5ab4ee5e211e89f7ed9c2b8f1e7"
    },
    "definition_digest": "d405fb1c66ac0fa0245679bff64d6f847d738222681f1bbfb783643540636c4a"
  }
}
```

<!-- SDD-CONTINUITY:END -->
