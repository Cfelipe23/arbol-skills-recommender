# decide_skills.py
import json
import ollama

CATALOGO_FILE = "skills_catalog.json"
MODELO = "arbol-router"

def cargar_catalogo(path=CATALOGO_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def construir_user(respuestas, catalogo, tipo, recomendacion):
    respuestas_texto = "\n".join(f"- {k}: {v}" for k, v in respuestas.items())
    catalogo_texto = "\n\n".join(
        f"{i+1}. {s['nombre']}\n"
        f"   Descripción: {s['descripcion']}\n"
        f"   Tags: {', '.join(s.get('tags', []))}"
        for i, s in enumerate(catalogo)
    )
    return (
        f"TIPO SOLICITADO: {tipo}\n\n"
        f"RESPUESTAS DEL USUARIO:\n{respuestas_texto}\n\n"
        f"RECOMENDACIÓN SUGERIDA POR EL ÁRBOL DE DECISIÓN: {recomendacion}\n\n"
        f"CATÁLOGO DE {tipo.upper()}S DISPONIBLES:\n{catalogo_texto}\n\n"
        f"Elige la mejor opción del catálogo (idealmente la recomendación sugerida) y responde solo con el JSON."
    )

def decidir_skill(respuestas, tipo_salida, recomendacion, modelo=MODELO):
    catalogo_completo = cargar_catalogo()
    
    # 1. Filtrar estrictamente por el tipo_salida que dictó el árbol
    pool = [s for s in catalogo_completo if s.get("tipo") == tipo_salida]

    if not pool:
        raise ValueError(f"No hay {tipo_salida}s en el catálogo para esas respuestas.")

    user = construir_user(respuestas, pool, tipo_salida, recomendacion)

    response = ollama.chat(
        model=modelo,
        messages=[{"role": "user", "content": user}],
        format="json",
    )

    parsed = json.loads(response["message"]["content"])
    
    # 2. Buscar lo que el LLM eligió
    skill = next((s for s in pool if s["nombre"] == parsed["nombre"]), None)
    
    # 3. Fallback: si el LLM se equivoca, forzamos la recomendación del árbol
    if not skill and recomendacion:
        skill = next((s for s in catalogo_completo if s["nombre"] == recomendacion), None)
        
    if not skill:
        raise ValueError(f"El LLM eligió algo que no existe y el árbol no pudo salvarlo: {parsed.get('nombre')}")

    return {
        "nombre": skill["nombre"],
        "razon": parsed.get("razon", "El árbol de decisión determinó que esta es la mejor opción para tu perfil."),
        "contenido": skill["contenido"],
        "ruta": skill.get("ruta", f"./skills/{skill['nombre']}/SKILL.md")
    }