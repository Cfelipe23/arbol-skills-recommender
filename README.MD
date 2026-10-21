# 🧭 Recomendador de Skills y Prompts para Desarrollo

Proyecto de la asignatura Estructuras de Datos No Lineales que usa un árbol de preguntas + un LLM local (llama3.2:1b) para recomendar la skill o prompt más adecuado a un desarrollador según su necesidad.

---

## 📌 ¿Qué hace?

1. Pregunta al usuario si quiere una skill o un prompt.
2. Recorre un árbol de decisiones técnicas (Frontend, Backend, DevOps, etc.).
3. Al llegar a una hoja, envía las respuestas + el catálogo de skills/prompts a un LLM local personalizado.
4. El LLM elige el elemento más adecuado del catálogo.
5. El sistema imprime el contenido para que el usuario lo copie y lo use en su agente, chat o proyecto.

---

## 🧠 Técnicas aplicadas del manual

Este proyecto implementa las dos primeras técnicas del manual "Cómo aumentar el conocimiento de un LLM local (llama3.2:1b)".

| Técnica | Descripción | Dónde se aplica |
|---------|-------------|-----------------|
| #1 Modelfile con SYSTEM | Se inyecta el conocimiento base dentro del modelo derivado | `Modelfile` → sección `SYSTEM """..."""` |
| #2 Modelfile con MESSAGE | Se enseñan ejemplos de entrada/salida al modelo | `Modelfile` → secciones `MESSAGE user/assistant` |

No se usa RAG (técnica #3) porque el catálogo es cerrado y pequeño, y entra completo en el prompt.

---

## 📁 Estructura del proyecto

```text
Estructura_2.1corte/
├── Modelfile               # Config del modelo personalizado (sin extensión)
├── arbol_skills.json       # Árbol de decisiones (preguntas al usuario)
├── skills_catalog.json     # Catálogo de skills y prompts disponibles
├── router_skills.py        # Flujo principal: pregunta, recorre árbol, muestra
├── decide_skills.py        # Lógica: filtra catálogo y llama al LLM
├── requirements.txt        # Dependencias de Python
└── README.md               # Este archivo
```

---

## ⚙️ Requisitos

- Python 3.10+
- Ollama instalado → https://ollama.com
- Modelo base descargado:

```bash
ollama pull llama3.2:1b
```

- Librería de Python:

```bash
pip install -r requirements.txt
```

---

## 🚀 Cómo se crea el modelo personalizado

El proyecto no usa llama3.2:1b directamente. Se crea un modelo derivado llamado arbol-router que ya tiene grabadas las reglas del sistema y los ejemplos de decisión.

### Paso 1: Crear el modelo derivado

```bash
cd Estructura_2.1corte
ollama create arbol-router -f ./Modelfile
```

Debe aparecer `success` al final.

### Paso 2: Verificar que existe

```bash
ollama list
```

Salida esperada:

```text
NAME              ID              SIZE      MODIFIED
arbol-router      xxxxxxxx        1.3 GB    hace unos segundos
llama3.2:1b       yyyyyyyy        1.3 GB    hace X días
```

### Paso 3: Probar el modelo directamente (sin Python)

```bash
ollama run arbol-router
```

Prompt de prueba:

```text
TIPO SOLICITADO: skill

RESPUESTAS DEL USUARIO:
- nivel_1: Backend
- nivel_2: Tipo de API
- nivel_3: REST
- nivel_4: Diseñar endpoints

CATÁLOGO DE SKILLS DISPONIBLES:
1. python-fastapi
   Descripción: APIs REST con Python y FastAPI.
   Tags: python, rest, diseñar endpoints, backend
2. node-express-rest
   Descripción: APIs REST con Node.js y Express.
   Tags: node.js, rest, diseñar endpoints, backend

Elige la mejor y responde solo con el JSON.
```

Salida esperada:

```json
{"nombre": "python-fastapi", "razon": "El usuario diseña endpoints REST en Backend, y python-fastapi cubre exactamente ese caso."}
```

Para salir: `/bye`

---

## 🔬 Comparación con el modelo original

Para demostrar el efecto del SYSTEM + MESSAGE, se compara el modelo derivado con el original. La diferencia es la evidencia clave de que el conocimiento fue inyectado correctamente.

### Prueba con el modelo SIN personalizar

```bash
ollama run llama3.2:1b
```

Pega exactamente el mismo prompt de la sección anterior.

| Modelo | Respuesta esperada |
|--------|--------------------|
| llama3.2:1b (original) | Texto libre, no JSON, posiblemente inventa skills o pide más info |
| arbol-router (derivado) | JSON válido con nombre y razon, sin inventar |

**Conclusión:** El modelo base no conoce el formato ni el catálogo; el modelo derivado sí, porque las reglas viven dentro de él (en el SYSTEM) y los ejemplos le enseñaron el patrón (en los MESSAGE).

---

## ▶️ Cómo se corre el proyecto

Una vez creado el modelo arbol-router:

```bash
python router_skills.py
```

Salida de ejemplo:

```text
🧭  RECOMENDADOR DE SKILLS Y PROMPTS PARA DESARROLLO

==================================================
 ¿Qué quieres obtener?
==================================================
1. Una SKILL  (contenido para guardar como SKILL.md)
2. Un PROMPT  (texto para pegar en tu agente/chat)

Número > 1

Ahora responde el árbol de preguntas:

==================================================
 Desarrollo de Software
==================================================
1. Frontend
2. Backend
3. Base de Datos
...

Número > 2

==================================================
 🤖 Consultando al LLM...
==================================================

==================================================
 🎯 SKILL recomendado: python-fastapi
 📋 Por qué: El usuario diseña endpoints REST en Backend.
==================================================

💡 Guarda el siguiente contenido como SKILL.md
   dentro de la carpeta de skills de tu agente.

────────────────────────────────────────────────────────────
    # FastAPI Best Practices

    ## Cuándo usar
    Al diseñar o implementar APIs REST en Python con FastAPI.

    ## Reglas
    - Usa Pydantic para validación de entrada.
    - Separa routers por dominio.
    - Inyecta dependencias con Depends.
    - Maneja errores con HTTPException y handlers globales.
────────────────────────────────────────────────────────────
```

---

## 🧪 Casos de prueba sugeridos

| # | Tipo | Respuestas | Resultado esperado |
|---|------|------------|--------------------|
| 1 | skill | Frontend → Crear componentes → React | react-best-practices |
| 2 | prompt | Experto técnico → Frontend → Conciso | experto-react |
| 3 | skill | Backend → REST → Diseñar endpoints | python-fastapi o node-express-rest |
| 4 | skill | Base de Datos → Optimizar queries → SQL | postgres-optimization |
| 5 | prompt | Revisor de código → Seguridad | revisor-seguridad |

---

## 🛠️ Personalización

### Agregar una nueva skill

Edita `skills_catalog.json` y agrega una entrada:

```json
{
  "nombre": "mi-nueva-skill",
  "tipo": "skill",
  "descripcion": "Descripción corta.",
  "tags": ["react", "crear componentes"],
  "contenido": "# Mi Skill\n\nContenido en markdown..."
}
```

### Agregar una nueva pregunta al árbol

Edita `arbol_skills.json` y agrega un nodo:

```json
{
  "valor": "Nueva pregunta",
  "hijos": [
    { "valor": "Opción A" },
    { "valor": "Opción B" }
  ]
}
```

### Cambiar las reglas del modelo

Edita `Modelfile` (sección SYSTEM o MESSAGE) y vuelve a crear el modelo:

```bash
ollama create arbol-router -f ./Modelfile
```

---

## 📚 Referencias

- Manual del curso: "Cómo aumentar el conocimiento de un LLM local (llama3.2:1b)"
- Ollama: https://ollama.com
- Documentación de Modelfile: https://github.com/ollama/ollama/blob/main/docs/modelfile.md

---