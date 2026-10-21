# 🌳 Recomendador de Skills y Prompts

> **Guía paso a paso para Windows**  
> **Proyecto:** `Estructura_2.1corte`  
> **Modelo base:** `llama3.2:1b` · **Modelo derivado:** `arbol-router`

---

## 📚 Índice

- [1. Puesta en marcha desde cero](#1--puesta-en-marcha-desde-cero)
- [2. Cuando modificas algo](#2--cuando-modificas-algo)
- [3. Desactivar el entorno virtual](#3--desactivar-el-entorno-virtual)
- [4. Problemas comunes en Windows](#4--problemas-comunes-en-windows)
- [5. Comparación: modelo original vs. derivado](#5--comparación-modelo-original-vs-derivado)
- [6. Registro de resultados reales](#6--registro-de-resultados-reales)
- [7. Conclusión para el informe](#7--conclusión-para-el-informe)

---

## 1. 🚀 Puesta en marcha desde cero

### Paso 1. Verificar Python

Comprueba que tienes **Python 3.10 o superior** instalado:

```powershell
python --version
```

### Paso 2. Instalar Ollama

Descarga e instala Ollama desde [ollama.com](https://ollama.com).

Verifica la instalación:

```powershell
ollama --version
```

> **Nota:** Si un comando indica que no puede conectarse a Ollama, abre **otra terminal** y déjala abierta ejecutando:

```powershell
ollama serve
```

### Paso 3. Descargar el modelo base

Descarga el modelo de aproximadamente **1,3 GB**. Solo es necesario hacerlo la primera vez:

```powershell
ollama pull llama3.2:1b
```

### Paso 4. Entrar a la carpeta del proyecto

```powershell
cd Estructura_2.1corte
```

Comprueba los archivos:

```powershell
dir
```

Debes encontrar estos **7 archivos**:

- `Modelfile`
- `arbol_skills.json`
- `skills_catalog.json`
- `router_skills.py`
- `decide_skills.py`
- `requirements.txt`
- `README.md`

> **Importante:** `Modelfile` no lleva extensión.

### Paso 5. Crear y activar el entorno virtual

Crea el entorno:

```powershell
python -m venv venv
```

Actívalo:

```powershell
venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la ejecución del script, ejecuta este comando **una sola vez**:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Después, vuelve a activar el entorno. Sabrás que está activo cuando el prompt muestre algo parecido a:

```text
(venv) PS C:\...\Estructura_2.1corte>
```

### Paso 6. Instalar dependencias

Con el entorno virtual activo, ejecuta:

```powershell
pip install -r requirements.txt
```

### Paso 7. Crear el modelo personalizado

Desde la carpeta del proyecto, ejecuta:

```powershell
ollama create arbol-router -f ./Modelfile
```

El proceso debe terminar correctamente, mostrando un mensaje como `success`.

### Paso 8. Verificar los modelos instalados

```powershell
ollama list
```

Debes encontrar ambos modelos:

- `llama3.2:1b`
- `arbol-router`

### Paso 9. (Opcional) Probar los modelos sin Python

Consulta la [Parte 5: comparación entre modelos](#5--comparación-modelo-original-vs-derivado).

### Paso 10. Ejecutar el proyecto

```powershell
python router_skills.py
```

**Flujo de uso:**

1. Selecciona `1` para **SKILL** o `2` para **PROMPT**.
2. Responde el árbol escribiendo el número de cada opción.
3. El sistema consulta al modelo de lenguaje (LLM).
4. Se muestra el elemento recomendado, la razón de la elección y el contenido completo para copiar.

### Paso 11. Casos de prueba sugeridos

| Tipo | Selección | Resultado esperado |
|---|---|---|
| Skill | Frontend → Framework → React | `react-best-practices` |
| Prompt | Frontend → Framework → React | `experto-react` |
| Skill | Backend → Lenguaje → Python | `python-fastapi` |
| Skill | Backend → Lenguaje → Node.js | `node-express-rest` |
| Skill | Base de Datos → Tipo → SQL | `postgres-optimization` |
| Prompt | Seguridad → OWASP | `revisor-seguridad` |

---

## 2. 🔧 Cuando modificas algo

| Cambio realizado | Qué debes ejecutar |
|---|---|
| Modificaste `SYSTEM` o `MESSAGE` en `Modelfile` | Recrear el modelo derivado |
| Modificaste `skills_catalog.json` o `arbol_skills.json` | Volver a ejecutar el programa |
| Quieres borrar y crear de nuevo el modelo derivado | Eliminarlo y recrearlo |

### Si modificaste el `Modelfile`

```powershell
ollama create arbol-router -f ./Modelfile
```

### Si modificaste los archivos JSON

```powershell
python router_skills.py
```

### Si quieres recrear el modelo desde cero

```powershell
ollama rm arbol-router
ollama create arbol-router -f ./Modelfile
```

---

## 3. ⏹️ Desactivar el entorno virtual

Cuando termines de trabajar:

```powershell
deactivate
```

La próxima vez que abras una terminal, entra a la carpeta y activa de nuevo el entorno:

```powershell
cd Estructura_2.1corte
venv\Scripts\Activate.ps1
```

---

## 4. 🧰 Problemas comunes en Windows

### `ModuleNotFoundError: No module named 'ollama'`

Es posible que el entorno virtual no esté activo o que falten dependencias.

```powershell
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### PowerShell bloquea la activación del entorno

Mensaje parecido a:

```text
venv\Scripts\Activate.ps1 no se puede cargar porque la ejecución de scripts está deshabilitada en este sistema
```

Solución —ejecuta una sola vez—:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Después, vuelve a intentar la activación.

### `No se puede conectar a Ollama` / `connection refused`

Abre otra terminal y ejecuta:

```powershell
ollama serve
```

Deja esa terminal abierta mientras trabajas.

### `model 'arbol-router' not found`

El modelo puede no haberse creado o puedes estar en una carpeta distinta.

```powershell
ollama list
ollama create arbol-router -f ./Modelfile
```

Ejecuta el segundo comando desde la carpeta donde está `Modelfile`.

### `El LLM eligió algo que no existe`

El modelo respondió con un nombre que no está en el catálogo.

1. Reintenta la consulta.
2. Si el problema persiste, agrega más ejemplos `MESSAGE` al `Modelfile`.
3. Recrea el modelo:

```powershell
ollama create arbol-router -f ./Modelfile
```

### `JSONDecodeError`

El modelo devolvió texto que no es JSON válido.

- Revisa que la sección `SYSTEM` del `Modelfile` conserve la regla de responder **solo con JSON**.
- Comprueba que la respuesta no incluya explicaciones antes o después del objeto JSON.

### `No such file or directory: 'skills_catalog.json'`

Ejecuta el programa desde dentro de la carpeta del proyecto:

```powershell
cd Estructura_2.1corte
python router_skills.py
```

---

## 5. 🧪 Comparación: modelo original vs. modelo derivado

### Objetivo

Demostrar el efecto de dos técnicas de personalización:

1. **SYSTEM (técnica #1):** define las instrucciones y el comportamiento esperado.
2. **MESSAGE (técnica #2):** proporciona ejemplos que enseñan el patrón de respuesta.

Se enviará **exactamente el mismo prompt** a los dos modelos:

| Modelo | Descripción |
|---|---|
| `llama3.2:1b` | Modelo original, sin personalizar para esta tarea |
| `arbol-router` | Modelo derivado con `SYSTEM` y ejemplos `MESSAGE` |

### Prompt de prueba

Copia el siguiente texto sin modificarlo para que la comparación sea justa:

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

### Opción A. Ejecutar en modo interactivo

Abre una terminal y ejecuta:

```powershell
ollama run llama3.2:1b
```

Pega el prompt de prueba en la sesión. Luego sal con `/bye`.

Repite con el modelo derivado:

```powershell
ollama run arbol-router
```

Pega **el mismo prompt**. Para salir, usa `/bye`; para limpiar la sesión, usa `/clear`.

### Opción B. Ejecutar con un archivo (recomendado)

Esta opción facilita repetir la prueba con exactamente la misma entrada.

**1.** Guarda el prompt anterior en un archivo llamado `prueba.txt`.

**2.** En PowerShell, ejecuta:

```powershell
Get-Content prueba.txt -Raw | ollama run llama3.2:1b
Get-Content prueba.txt -Raw | ollama run arbol-router
```

Compara ambas respuestas.

### Resultado esperado

| Modelo | Comportamiento esperado |
|---|---|
| `llama3.2:1b` (original) | Puede responder en texto libre, no usar JSON o pedir más información. |
| `arbol-router` (derivado) | Se espera un JSON válido con las claves `nombre` y `razon`, y una selección del catálogo. |

> **Importante:** estos son resultados esperados, no garantizados. Registra las respuestas reales que obtengas; un solo ensayo no demuestra que un modelo siempre se comporte de esa manera.

### Ejemplo de respuesta esperada del modelo derivado

```json
{
  "nombre": "python-fastapi",
  "razon": "El usuario diseña endpoints REST en Backend, y python-fastapi cubre exactamente ese caso."
}
```

---

## 6. 📝 Registro de resultados reales

Completa esta tabla después de ejecutar las pruebas. Sirve como evidencia para la entrega o el informe.

| Criterio | `llama3.2:1b` | `arbol-router` |
|---|---|---|
| ¿Responde solo con JSON válido? |  |  |
| ¿Incluye las claves `nombre` y `razon`? |  |  |
| ¿El nombre existe en el catálogo? |  |  |
| ¿Inventa skills o información? |  |  |
| ¿Agrega texto fuera del JSON? |  |  |
| ¿Elige coherentemente entre FastAPI y Express? |  |  |
| Consistencia en 3 intentos (X/3) |  |  |

**Recomendación para la prueba:** ejecuta cada modelo tres veces con el mismo prompt y registra cada resultado. Así podrás comparar la consistencia, además del formato y la selección.

---

## 7. 🎓 Conclusión para el README o informe

El modelo base no está personalizado específicamente para seguir el formato ni para seleccionar elementos del catálogo del proyecto. El modelo derivado incorpora instrucciones mediante `SYSTEM` (técnica #1) y ejemplos mediante `MESSAGE` (técnica #2), con el objetivo de producir respuestas estructuradas y elegir una opción existente en el catálogo.

En este caso no se utiliza **RAG (técnica #3)** porque el catálogo es cerrado, pequeño y puede incluirse completo en el prompt. Esta decisión puede revisarse si el catálogo crece o deja de caber de forma práctica en el contexto del modelo.

---

<div align="center">

**🌳 Fin de la guía**

*Recomendador de Skills y Prompts · `Estructura_2.1corte`*

</div>
