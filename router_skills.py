# router_skills.py
import json
import sys
from decide_skills import decidir_skill

ARBOL_FILE = "arbol_skills.json"    
MODELO = "arbol-router" 

def cargar_arbol(path=ARBOL_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _es_nodo_puente(nodo):
    """Detecta nodos estructurales que solo envuelven una siguiente pregunta."""
    hijos = nodo.get("hijos", [])
    if len(hijos) != 1:
        return False

    unico = hijos[0]
    return bool(unico.get("hijos")) and not unico.get("tipo_salida") and not unico.get("recomendacion")


def _descender_nodos_puente(nodo, camino):
    """Evita pasos redundantes en la interfaz (ej. mostrar una pregunta como única opción)."""
    while _es_nodo_puente(nodo):
        nodo = nodo["hijos"][0]
        camino.append(nodo["valor"])
    return nodo, camino


def _mostrar_encabezado(camino):
    print(f"\n{'=' * 66}")
    print(" Recomendador de Skills y Prompts")

    if len(camino) > 4:
        miga = " > ".join(["...", *camino[-4:]])
    else:
        miga = " > ".join(camino)

    print(f" Ruta: {miga}")
    print("=" * 66)


def _leer_opcion_valida(total_opciones):
    while True:
        idx = input(f"\nNúmero [1-{total_opciones}] > ").strip()
        if idx.isdigit() and 1 <= int(idx) <= total_opciones:
            return int(idx) - 1
        print(f"Opción inválida. Escribe un número entre 1 y {total_opciones}.")


def avanzar_paso_arbol(nodo, camino=None, respuestas=None):
    """
    Función pura y no bloqueante para avanzar en el árbol de decisión.
    Retorna:
      (nodo_actual, camino_actual, respuestas_actuales, es_hoja, tipo_salida, recomendacion)
    """
    camino = list(camino or [])
    if not camino or camino[-1] != nodo["valor"]:
        camino.append(nodo["valor"])
    respuestas = dict(respuestas or {})

    nodo, camino = _descender_nodos_puente(nodo, camino)
    hijos = nodo.get("hijos", [])

    if not hijos:
        clave_final = nodo.get("clave", f"nivel_{len(camino)}")
        respuestas[clave_final] = nodo["valor"]
        return nodo, camino, respuestas, True, nodo.get("tipo_salida"), nodo.get("recomendacion")

    return nodo, camino, respuestas, False, None, None


def explorar_arbol(nodo, camino=None, respuestas=None):
    """Modo interactivo tradicional para la consola (CLI)."""
    nodo, camino, respuestas, es_hoja, tipo_salida, recomendacion = avanzar_paso_arbol(nodo, camino, respuestas)

    if es_hoja:
        return respuestas, tipo_salida, recomendacion

    hijos = nodo.get("hijos", [])
    _mostrar_encabezado(camino)
    print(f"{nodo['valor']}")
    for i, h in enumerate(hijos, 1):
        print(f"{i}. {h['valor']}")

    elegido_idx = _leer_opcion_valida(len(hijos))
    elegido = hijos[elegido_idx]

    clave = nodo.get("clave", f"nivel_{len(camino)}")
    respuestas[clave] = elegido["valor"]

    return explorar_arbol(elegido, camino, respuestas)


def mostrar_resultado(resultado, tipo):
    print("\n" + "=" * 60)
    print(f"🎯 {tipo.upper()} recomendado: {resultado['nombre']}")
    print(f"📋 Razón del LLM: {resultado['razon']}")
    print("=" * 60)

    if tipo == "prompt":
        print("\n💡 Copia y pega este prompt en tu agente:\n")
        print("-" * 60)
        print(resultado["contenido"])
        print("-" * 60)
    elif tipo == "skill":
        nombre_skill = resultado["nombre"]
        comando = f"npx skills add ./skills/{nombre_skill}"

        print("\n🧩 Skill local lista para instalar")
        print(f"Nombre: {nombre_skill}")
        print("\n🚀 Comando de instalación (copia y pega):\n")
        print(comando)
    else:
        print("\n⚠️ Tipo de salida no reconocido.")

    print("\n" + "=" * 60)


def router_skills():
    print("\n🧭  RECOMENDADOR DE SKILLS Y PROMPTS PARA DESARROLLO")
    print("🤖 El sistema identificará tu perfil y necesidad.\n")

    arbol = cargar_arbol()
    respuestas, tipo_salida, recomendacion = explorar_arbol(arbol)

    print("\n" + "=" * 50)
    print(" 🤖 Consultando al LLM para justificar la elección...")
    print("=" * 50)

    resultado = decidir_skill(respuestas, tipo_salida, recomendacion, modelo=MODELO)
    mostrar_resultado(resultado, tipo_salida)


if __name__ == "__main__":
    # Si se pasa el argumento --cli, se ejecuta en la terminal.
    # Por defecto, lanza la interfaz gráfica para una experiencia visual completa.
    if "--cli" in sys.argv:
        router_skills()
    else:
        try:
            from gui_skills import main as iniciar_gui
            iniciar_gui()
        except ImportError:
            print("Iniciando en modo consola (CustomTkinter no detectado o archivo GUI ausente)...")
            router_skills()