"""
gui_skills.py
Interfaz gráfica moderna para el Recomendador de Skills y Prompts.
Implementa navegación sin fricción, health-check de Ollama, 
streaming de respuestas y modo de revelación progresiva.
"""

import threading
import base64
import os
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import ollama

from router_skills import cargar_arbol, avanzar_paso_arbol, MODELO
from decide_skills import decidir_skill

class RecomendadorSkillsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de apariencia
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.title("Recomendador de Skills y Prompts")
        self.geometry("980x720")
        self.minsize(860, 620)

        # Estado del árbol
        self.arbol_raiz = None
        self.historial = []  
        self.nodo_actual = None
        self.camino_actual = []
        self.respuestas_actuales = {}
        self.botones_opciones = []
        
        # Estado del Chat y LLM
        self.chat_system_prompt = ""
        self.chat_titulo_asistente = ""
        self.chat_historial = []
        self.peticion_activa = False
        self.npx_disponible = False
        self.skills_cli_disponible = False
        self.npx_comando = "npx"
        self.mensaje_validacion_skills = "Verificando npx/skills..."

        # Construir estructura gráfica
        self._construir_ui()
        self._configurar_atajos()

        # Iniciar datos y check de sistema
        self._cargar_e_iniciar_arbol()
        self._verificar_ollama()
        self._verificar_herramientas_skills()

    def _construir_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ----------------------------------------------------
        # 1. ENCABEZADO SUPERIOR (Header)
        # ----------------------------------------------------
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray85", "#181b20"))
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.header_frame, text="🧭", font=ctk.CTkFont(size=30)).grid(row=0, column=0, rowspan=2, padx=(20, 10), pady=15)
        
        ctk.CTkLabel(
            self.header_frame, text="Recomendador de Skills y Prompts",
            font=ctk.CTkFont(size=20, weight="bold"), anchor="w"
        ).grid(row=0, column=1, sticky="sw", pady=(15, 0))

        # Indicador de estado de Ollama (Health Check)
        self.lbl_estado_ollama = ctk.CTkLabel(
            self.header_frame, text="⚪ Verificando Ollama...", 
            font=ctk.CTkFont(size=12), text_color=("gray40", "gray60"), anchor="nw"
        )
        self.lbl_estado_ollama.grid(row=1, column=1, sticky="nw", pady=(2, 15))

        # Switch de tema (Oscuro / Claro)
        self.theme_switch = ctk.CTkSwitch(
            self.header_frame, text="Modo Oscuro", command=self._alternar_tema,
            onvalue="Dark", offvalue="Light"
        )
        self.theme_switch.select()
        self.theme_switch.grid(row=0, column=2, rowspan=2, padx=20, pady=15)

        # ----------------------------------------------------
        # 2. CONTENEDOR CENTRAL DE PANTALLAS
        # ----------------------------------------------------
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=25, pady=(15, 10))
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.vista_pregunta = ctk.CTkFrame(self.main_container, corner_radius=12)
        self._construir_vista_pregunta()

        self.vista_cargando = ctk.CTkFrame(self.main_container, corner_radius=12)
        self._construir_vista_cargando()

        self.vista_resultado = ctk.CTkFrame(self.main_container, corner_radius=12)
        self._construir_vista_resultado()

        self.vista_chat = ctk.CTkFrame(self.main_container, corner_radius=12)
        self._construir_vista_chat()

        # ----------------------------------------------------
        # 3. BARRA DE ESTADO INFERIOR
        # ----------------------------------------------------
        self.status_bar = ctk.CTkFrame(self, height=32, corner_radius=0, fg_color=("gray90", "#121417"))
        self.status_bar.grid(row=2, column=0, sticky="ew")
        self.status_bar.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            self.status_bar, text="Listo.", font=ctk.CTkFont(size=13),
            text_color=("gray30", "gray70"), anchor="w"
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=20, pady=4)

    def _configurar_atajos(self):
        # Atajos de teclado para selección rápida (1-9) y retroceder
        for n in range(1, 10):
            self.bind(str(n), lambda event, i=n-1: self._atajo_opcion(i))
        self.bind("<BackSpace>", lambda event: self._atajo_retroceder())

    def _atajo_opcion(self, i):
        if self.vista_pregunta.winfo_ismapped() and i < len(self.botones_opciones):
            self._seleccionar_opcion(i)

    def _atajo_retroceder(self):
        if self.vista_pregunta.winfo_ismapped() and self.historial:
            self._retroceder_paso()

    def _verificar_ollama(self):
        def check():
            try:
                ollama.list()
                self.after(0, lambda: self.lbl_estado_ollama.configure(
                    text=f"🟢 Ollama Activo ({MODELO})", text_color="#10b981"
                ))
            except Exception:
                self.after(0, lambda: self.lbl_estado_ollama.configure(
                    text="🔴 Ollama Desconectado", text_color="#ef4444"
                ))
        threading.Thread(target=check, daemon=True).start()

    def _verificar_herramientas_skills(self):
        def check():
            npx_cmd = self._resolver_npx()
            if not npx_cmd:
                self.after(0, lambda: self._actualizar_estado_herramientas_skills(
                    False,
                    False,
                    "No se encontro npx en PATH."
                ))
                return

            self.npx_comando = npx_cmd

            try:
                probe = self._run_npx(["skills", "--help"], timeout=15)
                if probe.returncode == 0:
                    self.after(0, lambda: self._actualizar_estado_herramientas_skills(
                        True,
                        True,
                        "npx y skills listos."
                    ))
                    return

                detalle = (probe.stderr or probe.stdout or "No se pudo ejecutar npx skills --help.").strip().splitlines()[0]
                self.after(0, lambda: self._actualizar_estado_herramientas_skills(
                    True,
                    False,
                    f"npx OK, pero skills no esta disponible ({detalle})."
                ))
            except Exception as e:
                msg = str(e)  # 1. Guardamos el string en una variable local
                self.after(0, lambda: self.status_label.configure(text=f"No se pudo validar skills: {msg}"))
                self.after(0, lambda: self._actualizar_estado_herramientas_skills(
                    True,
                    False,
                    f"No se pudo validar skills: {msg}"
                ))

        threading.Thread(target=check, daemon=True).start()

    def _resolver_npx(self):
        candidatos = [
            shutil.which("npx"),
            shutil.which("npx.cmd"),
            shutil.which("npx.exe"),
        ]

        # Si la app se lanza fuera de la terminal, PATH puede no traer Node.js.
        if os.name == "nt":
            program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
            program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
            local_app_data = os.environ.get("LOCALAPPDATA", "")
            app_data = os.environ.get("APPDATA", "")

            candidatos.extend([
                os.path.join(program_files, "nodejs", "npx.cmd"),
                os.path.join(program_files_x86, "nodejs", "npx.cmd"),
                os.path.join(local_app_data, "Programs", "nodejs", "npx.cmd"),
                os.path.join(app_data, "npm", "npx.cmd"),
            ])

        for cmd in candidatos:
            if cmd and os.path.exists(cmd):
                return cmd

        return None

    def _run_npx(self, args, timeout=15):
        cmd = self.npx_comando or "npx"
        if os.name == "nt" and cmd.lower().endswith((".cmd", ".bat")):
            comando = f'"{cmd}" ' + " ".join(args)
            return subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                shell=True,
            )

        return subprocess.run(
            [cmd, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

    def _actualizar_estado_herramientas_skills(self, npx_ok, skills_ok, mensaje):
        self.npx_disponible = npx_ok
        self.skills_cli_disponible = skills_ok
        self.mensaje_validacion_skills = mensaje

    def _obtener_instrucciones_setup_skills(self):
        return (
            "No se detecto el entorno para instalar skills automaticamente.\n\n"
            "Pasos sugeridos:\n"
            "1) Instala Node.js LTS: https://nodejs.org\n"
            "2) Cierra y abre una nueva terminal.\n"
            "3) Verifica npx:\n"
            "   npx --version\n"
            "4) Verifica el CLI de skills:\n"
            "   npx skills --help\n\n"
            "Estado detectado por la app:\n"
            f"- {self.mensaje_validacion_skills}\n"
        )

    # --- VISTAS ---
    def _construir_vista_pregunta(self):
        self.vista_pregunta.grid_rowconfigure(2, weight=1)
        self.vista_pregunta.grid_columnconfigure(0, weight=1)

        self.miga_card = ctk.CTkFrame(self.vista_pregunta, fg_color=("gray90", "#242830"), corner_radius=8)
        self.miga_card.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        self.miga_container = ctk.CTkFrame(self.miga_card, fg_color="transparent")
        self.miga_container.pack(fill="x", padx=10, pady=8)

        self.pregunta_card = ctk.CTkFrame(self.vista_pregunta, fg_color=("gray95", "#1e2229"), corner_radius=10)
        self.pregunta_card.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        self.pregunta_card.grid_columnconfigure(0, weight=1)

        self.lbl_pregunta_titulo = ctk.CTkLabel(
            self.pregunta_card, text="Cargando...", font=ctk.CTkFont(size=18, weight="bold"),
            wraplength=760, justify="left", anchor="w"
        )
        self.lbl_pregunta_titulo.grid(row=0, column=0, padx=20, pady=(15, 6), sticky="w")
        
        # Responsive wraplength
        self.pregunta_card.bind("<Configure>", lambda e: self.lbl_pregunta_titulo.configure(wraplength=e.width - 60))

        self.scroll_opciones = ctk.CTkScrollableFrame(self.vista_pregunta, fg_color="transparent")
        self.scroll_opciones.grid(row=2, column=0, sticky="nsew", padx=15, pady=0)
        self.scroll_opciones.grid_columnconfigure(0, weight=1)

        self.footer_pregunta = ctk.CTkFrame(self.vista_pregunta, fg_color="transparent")
        self.footer_pregunta.grid(row=3, column=0, sticky="ew", padx=20, pady=15)
        self.footer_pregunta.grid_columnconfigure(1, weight=1)

        self.btn_atras = ctk.CTkButton(
            self.footer_pregunta, text="← Volver Atrás (Backspace)", width=180,
            fg_color=("gray75", "#374151"), hover_color=("gray65", "#4b5563"),
            command=self._retroceder_paso
        )
        self.btn_atras.grid(row=0, column=0, sticky="w")

        self.btn_reiniciar_arbol = ctk.CTkButton(
            self.footer_pregunta, text="🔄 Nueva Consulta", width=140,
            fg_color="transparent", text_color=("gray30", "gray70"), hover_color=("gray85", "#2a2e39"),
            command=self._reiniciar_todo
        )
        self.btn_reiniciar_arbol.grid(row=0, column=2, sticky="e")

    def _construir_vista_cargando(self):
        self.vista_cargando.grid_rowconfigure((0, 5), weight=1)
        self.vista_cargando.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.vista_cargando, text="🤖", font=ctk.CTkFont(size=56)).grid(row=1, column=0, pady=(0, 10))
        ctk.CTkLabel(self.vista_cargando, text="Analizando respuestas...", font=ctk.CTkFont(size=18, weight="bold")).grid(row=2, column=0, pady=5)
        self.progress_bar = ctk.CTkProgressBar(self.vista_cargando, width=320, mode="indeterminate")
        self.progress_bar.grid(row=3, column=0, pady=10)
        
        self.btn_cancelar_carga = ctk.CTkButton(
            self.vista_cargando, text="Cancelar", fg_color="#ef4444", hover_color="#dc2626",
            command=self._cancelar_peticion
        )
        self.btn_cancelar_carga.grid(row=4, column=0, pady=20)

    def _construir_vista_resultado(self):
        self.vista_resultado.grid_rowconfigure(2, weight=1)
        self.vista_resultado.grid_columnconfigure(0, weight=1)

        self.res_header = ctk.CTkFrame(self.vista_resultado, fg_color=("gray95", "#1e2229"), corner_radius=10)
        self.res_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        self.res_header.grid_columnconfigure(1, weight=1)

        self.lbl_res_badge = ctk.CTkLabel(
            self.res_header, text="🎯 RECOMENDACIÓN", font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#2563eb", "#60a5fa"), fg_color=("gray85", "#2a3447"), corner_radius=6, padx=10, pady=4
        )
        self.lbl_res_badge.grid(row=0, column=0, sticky="w", padx=15, pady=(12, 4))
        self.lbl_res_nombre = ctk.CTkLabel(self.res_header, text="", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_res_nombre.grid(row=1, column=0, columnspan=2, sticky="w", padx=15, pady=(0, 12))

        self.res_content_frame = ctk.CTkFrame(self.vista_resultado, corner_radius=8)
        self.res_content_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.res_content_frame.grid_rowconfigure(1, weight=1)
        self.res_content_frame.grid_columnconfigure(0, weight=1)

        self.lbl_content_title = ctk.CTkLabel(
            self.res_content_frame,
            text="Contenido recomendado:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        self.lbl_content_title.grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))

        self.txt_resultado_contenido = ctk.CTkTextbox(self.res_content_frame, wrap="word", font=ctk.CTkFont(family="Consolas", size=13))
        self.txt_resultado_contenido.grid(row=1, column=0, sticky="nsew", padx=12, pady=(10, 10))

        self.res_footer = ctk.CTkFrame(self.vista_resultado, fg_color="transparent")
        self.res_footer.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 15))
        self.res_footer.grid_columnconfigure(0, weight=1)

        self.btn_copiar = ctk.CTkButton(
            self.res_footer, text="📋 Copiar Comando/Prompt", width=190, 
            fg_color=("gray75", "#374151"), command=self._copiar_resultado
        )
        self.btn_copiar.grid(row=0, column=1, padx=(0, 10), sticky="e")

        self.btn_chatear = ctk.CTkButton(
            self.res_footer, text="💬 Chatear con este Asistente", width=200, 
            font=ctk.CTkFont(weight="bold"), command=self._iniciar_chat_desde_resultado
        )
        self.btn_chatear.grid(row=0, column=2, padx=(0, 10), sticky="e")

        self.btn_nuevo_test = ctk.CTkButton(
            self.res_footer, text="🔄 Nueva Consulta", width=140,
            fg_color="transparent", border_width=1, text_color=("gray30", "gray70"), 
            hover_color=("gray85", "#2a2e39"), border_color=("gray80", "#374151"),
            command=self._reiniciar_todo
        )
        self.btn_nuevo_test.grid(row=0, column=3, sticky="e")

    def _construir_vista_chat(self):
        self.vista_chat.grid_rowconfigure(1, weight=1)
        self.vista_chat.grid_columnconfigure(0, weight=1)

        self.chat_header = ctk.CTkFrame(self.vista_chat, fg_color=("gray95", "#1e2229"), corner_radius=10)
        self.chat_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        self.lbl_chat_titulo = ctk.CTkLabel(self.chat_header, text="", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_chat_titulo.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 10))

        # Textbox con soporte de etiquetas (tags) para diferenciar usuario y asistente
        self.txt_chat = ctk.CTkTextbox(self.vista_chat, wrap="word", font=ctk.CTkFont(size=13))
        self.txt_chat.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.txt_chat.tag_config("usuario", foreground="#3b82f6")
        self.txt_chat.tag_config("asistente", foreground="#10b981")
        self.txt_chat.tag_config("sistema", foreground="#ef4444")
        self.txt_chat.configure(state="disabled")

        self.chat_footer = ctk.CTkFrame(self.vista_chat, fg_color="transparent")
        self.chat_footer.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))
        self.chat_footer.grid_columnconfigure(0, weight=1)

        # Fila 0: Input y botones
        self.entry_chat = ctk.CTkEntry(self.chat_footer, placeholder_text="Escribe tu consulta técnica...")
        self.entry_chat.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_chat.bind("<Return>", lambda e: self._enviar_mensaje_chat())

        self.btn_enviar_chat = ctk.CTkButton(self.chat_footer, text="Enviar", width=110, command=self._enviar_mensaje_chat)
        self.btn_enviar_chat.grid(row=0, column=1, padx=(0, 10))

        ctk.CTkButton(
            self.chat_footer, text="← Volver al Resultado", width=140, 
            fg_color=("gray75", "#374151"), hover_color=("gray65", "#4b5563"),
            command=lambda: self._mostrar_pantalla("resultado")
        ).grid(row=0, column=2, padx=(0, 10))

        ctk.CTkButton(
            self.chat_footer, text="🔄 Nueva Consulta", width=140, 
            fg_color="transparent", border_width=1, text_color=("gray30", "gray70"), 
            hover_color=("gray85", "#2a2e39"), border_color=("gray80", "#374151"),
            command=self._reiniciar_todo
        ).grid(row=0, column=3)

        # Fila 1: Mensaje de advertencia de IA (NUEVO)
        self.lbl_advertencia_ia = ctk.CTkLabel(
            self.chat_footer, 
            text="⚠️ La IA puede cometer errores. Considera verificar la información importante.", 
            font=ctk.CTkFont(size=11), 
            text_color=("gray50", "gray60")
        )
        self.lbl_advertencia_ia.grid(row=1, column=0, columnspan=4, pady=(8, 0))
        
    # --- LÓGICA DE NAVEGACIÓN ---
    def _cargar_e_iniciar_arbol(self):
        try:
            self.arbol_raiz = cargar_arbol()
            self._reiniciar_todo()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar arbol_skills.json:\n{str(e)}")

    def _reiniciar_todo(self):
        if self.vista_chat.winfo_ismapped() and self.chat_historial:
            if not messagebox.askyesno("Confirmar", "¿Deseas borrar esta conversación e iniciar de nuevo?"):
                return
        
        self.historial.clear()
        self.camino_actual = []
        self.respuestas_actuales = {}
        self.nodo_actual = self.arbol_raiz
        self._mostrar_pantalla("pregunta")
        self._renderizar_paso_actual()

    def _renderizar_migas_interactivas(self):
        # Limpiamos la ruta actual
        for widget in self.miga_container.winfo_children():
            widget.destroy()
            
        lbl = ctk.CTkLabel(self.miga_container, text="📍 RUTA:  ", font=ctk.CTkFont(size=12, weight="bold"), text_color="#3a82f6")
        lbl.pack(side="left")

        # Filtramos para mostrar SOLO las respuestas que el usuario selecciono
        pasos_limpios = ["Inicio"] + list(self.respuestas_actuales.values())

        # Funcion para truncar textos largos (ej. "Soy desarrollador y necesito...")
        def truncar(texto, limite=30):
            return texto if len(texto) <= limite else texto[:limite - 3] + "..."

        # Generamos los botones interactivos
        for i, paso in enumerate(pasos_limpios):
            texto_mostrar = truncar(paso)
            btn = ctk.CTkButton(
                self.miga_container, text=texto_mostrar, font=ctk.CTkFont(size=12), width=0, height=24,
                fg_color="transparent", text_color=("gray20", "gray80"), hover_color=("gray85", "#374151"),
                cursor="hand2",
                command=lambda idx=i: self._saltar_a_historial(idx)
            )
            btn.pack(side="left", padx=2)
            
            # Ponemos el separador ">" si no es el último paso
            if i < len(pasos_limpios) - 1:
                ctk.CTkLabel(self.miga_container, text=">", text_color="gray50").pack(side="left")

    def _saltar_a_historial(self, target_idx):
        # target_idx representa el nivel en el árbol al que queremos volver.
        # Mientras nuestro historial sea más profundo que el objetivo, retrocedemos un paso a la vez.
        # Esto asegura que el árbol mantenga coherencia y no se rompa la toma de decisiones.
        while len(self.historial) > target_idx:
            self._retroceder_paso()

    def _renderizar_paso_actual(self):
        nodo, camino, respuestas, es_hoja, tipo_salida, recomendacion = avanzar_paso_arbol(
            self.nodo_actual, self.camino_actual, self.respuestas_actuales
        )
        self.nodo_actual = nodo
        self.camino_actual = camino
        self.respuestas_actuales = respuestas

        if es_hoja:
            self._ejecutar_decision_llm(tipo_salida, recomendacion)
            return

        self._renderizar_migas_interactivas()
        self.lbl_pregunta_titulo.configure(text=self.nodo_actual["valor"])
       
        if len(self.historial) > 0:
            self.btn_atras.grid(row=0, column=0, sticky="w") # Lo muestra si hay historial
        else:
            self.btn_atras.grid_remove() 

        for widget in self.scroll_opciones.winfo_children():
            widget.destroy()
        self.botones_opciones.clear()

        hijos = self.nodo_actual.get("hijos", [])
        for i, hijo in enumerate(hijos):
            texto_opcion = f"[{i+1}]  {hijo['valor']}"
            btn = ctk.CTkButton(
                self.scroll_opciones, text=texto_opcion, anchor="w", font=ctk.CTkFont(size=14),
                height=48, corner_radius=8, fg_color=("gray92", "#242832"), text_color=("gray10", "gray95"),
                hover_color=("#dbeafe", "#313845"), command=lambda idx=i: self._seleccionar_opcion(idx)
            )
            btn.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            self.botones_opciones.append(btn)

        self.status_label.configure(text=f"Paso {len(self.camino_actual)+1}: Selecciona una opción.")

    def _seleccionar_opcion(self, idx):
        hijos = self.nodo_actual.get("hijos", [])
        elegido = hijos[idx]

        self.historial.append({
            "nodo": self.nodo_actual,
            "camino": list(self.camino_actual),
            "respuestas": dict(self.respuestas_actuales)
        })

        clave = self.nodo_actual.get("clave", f"nivel_{len(self.camino_actual)}")
        self.respuestas_actuales[clave] = elegido["valor"]
        self.nodo_actual = elegido
        
        # Feedback visual mínimo antes de avanzar (100ms)
        self.botones_opciones[idx].configure(fg_color=("#2563eb", "#1d4ed8"), text_color="white")
        self.after(100, self._renderizar_paso_actual)

    def _retroceder_paso(self):
        if not self.historial: return
        estado_anterior = self.historial.pop()
        self.nodo_actual = estado_anterior["nodo"]
        self.camino_actual = estado_anterior["camino"]
        self.respuestas_actuales = estado_anterior["respuestas"]
        self._renderizar_paso_actual()

    # --- LÓGICA LLM & RESULTADO ---
    def _cancelar_peticion(self):
        self.peticion_activa = False
        self._retroceder_paso()

    def _ejecutar_decision_llm(self, tipo_salida, recomendacion):
        self._mostrar_pantalla("cargando")
        self.progress_bar.start()
        self.status_label.configure(text="Enrutando con Ollama...")
        self.peticion_activa = True

        def tarea():
            try:
                resultado = decidir_skill(self.respuestas_actuales, tipo_salida, recomendacion, modelo=MODELO)
                if self.peticion_activa:
                    self.after(0, lambda res=resultado, ts=tipo_salida: self._mostrar_resultado_exito(res, ts))
            except Exception as e:
                msg = str(e)
                if self.peticion_activa:
                    self.after(0, lambda m=msg: self._mostrar_resultado_error(m))

        threading.Thread(target=tarea, daemon=True).start()

    def _mostrar_resultado_error(self, mensaje_error):
        self.progress_bar.stop()
        self._retroceder_paso() # Deshace la selección de la hoja
        messagebox.showerror("Error de red", f"Problema con Ollama:\n{mensaje_error}")

    def _mostrar_resultado_exito(self, resultado, tipo_salida):
        self.progress_bar.stop()
        self._mostrar_pantalla("resultado")

        self.lbl_res_nombre.configure(text=resultado["nombre"])
        self.chat_titulo_asistente = resultado["nombre"]
        
        self.txt_resultado_contenido.delete("1.0", "end")
        
        if tipo_salida == "prompt":
            self.lbl_content_title.configure(text="💡 Prompt optimizado (Copia y pega en tu agente de IA):")
            self.chat_system_prompt = resultado.get("contenido", "")
            self.txt_resultado_contenido.insert("1.0", self.chat_system_prompt)
            
        elif tipo_salida == "skill":
            self.chat_system_prompt = resultado.get("contenido", "")
            contenido_b64 = base64.b64encode(self.chat_system_prompt.encode("utf-8")).decode("ascii")
            
            # Determinamos de forma limpia el comando base para npx en Windows o sistemas Unix
            if os.name == "nt" and self.npx_comando and self.npx_comando != "npx":
                comando_npx_ps = f'& "{self.npx_comando}"'
            else:
                comando_npx_ps = "npx"

            # Estructuramos un script de PowerShell ordenado, legible y estético
            comando_instalacion = (
                f"# 1. Definir nombre y ruta local de la skill\n"
                f"$skillName = '{resultado['nombre']}'\n"
                f"$skillDir = Join-Path $PWD \"skills/$skillName\"\n\n"
                f"# 2. Crear la carpeta y el archivo SKILL.md con el contenido técnico\n"
                f"New-Item -ItemType Directory -Path $skillDir -Force | Out-Null\n"
                f"$skillMd = Join-Path $skillDir \"SKILL.md\"\n"
                f"[System.IO.File]::WriteAllBytes($skillMd, [System.Convert]::FromBase64String('{contenido_b64}'))\n\n"
                f"# 3. Registrar la skill en el entorno\n"
                f"{comando_npx_ps} skills add $skillDir"
            )

            if self.npx_disponible and self.skills_cli_disponible:
                self.lbl_content_title.configure(text="🚀 Instalación lista: Copia este script en tu PowerShell")
                self.txt_resultado_contenido.insert("1.0", comando_instalacion)
            else:
                self.lbl_content_title.configure(text="⚠️ Entorno de Node.js / CLI de Skills no detectado automáticamente")
                instrucciones = self._obtener_instrucciones_setup_skills()
                contenido_total = (
                    f"{instrucciones}\n"
                    f"--------------------------------------------------\n"
                    f"UNA VEZ CONFIGURADO EL ENTORNO, EJECUTA ESTE SCRIPT:\n"
                    f"--------------------------------------------------\n\n"
                    f"{comando_instalacion}"
                )
                self.txt_resultado_contenido.insert("1.0", contenido_total)

        self.status_label.configure(text="✅ Diagnóstico completado. Elige tu siguiente acción.")
    def _copiar_resultado(self):
        contenido = self.txt_resultado_contenido.get("1.0", "end-1c")
        if contenido.strip():
            self.clipboard_clear()
            self.clipboard_append(contenido)
            self.update()
            orig = self.btn_copiar.cget("text")
            self.btn_copiar.configure(text="✅ ¡Copiado!")
            self.after(2000, lambda: self.btn_copiar.configure(text=orig))

    def _iniciar_chat_desde_resultado(self):
        self.chat_historial = []
        self.lbl_chat_titulo.configure(text=f"Asistente: {self.chat_titulo_asistente}")
        self.txt_chat.configure(state="normal")
        self.txt_chat.delete("1.0", "end")
        self.txt_chat.configure(state="disabled")
        self._mostrar_pantalla("chat")
        self.entry_chat.focus()
        self.status_label.configure(text="Asistente listo. Escribe tu mensaje.")

    # --- LÓGICA DE CHAT STREAMING ---
    def _enviar_mensaje_chat(self):
        mensaje = self.entry_chat.get().strip()
        if not mensaje: return

        self.entry_chat.delete(0, "end")
        self._escribir_en_chat("Tú", mensaje, tag="usuario")
        self.btn_enviar_chat.configure(state="disabled")
        self.status_label.configure(text="Generando respuesta...")
        self.peticion_activa = True

        historial = [
            {"role": "system", "content": self.chat_system_prompt},
            *self.chat_historial,
            {"role": "user", "content": mensaje}
        ]
        self.chat_historial.append({"role": "user", "content": mensaje})

        def tarea_chat():
            try:
                # Prepara la UI para escribir la respuesta
                self.after(0, lambda: self._escribir_en_chat(self.chat_titulo_asistente, "", tag="asistente", salto_linea=False))
                
                respuesta_completa = ""
                # Streaming token por token
                for chunk in ollama.chat(model=MODELO, messages=historial, stream=True):
                    if not self.peticion_activa: break
                    txt = chunk["message"]["content"]
                    respuesta_completa += txt
                    self.after(0, lambda t=txt: self._escribir_token(t))
                
                if self.peticion_activa:
                    self.after(0, lambda r=respuesta_completa: self._finalizar_chat(r))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda m=msg: self._escribir_en_chat("Sistema", f"Error: {m}", tag="sistema"))
                self.after(0, lambda: self.btn_enviar_chat.configure(state="normal"))

        threading.Thread(target=tarea_chat, daemon=True).start()

    def _escribir_en_chat(self, autor, texto, tag=None, salto_linea=True):
        self.txt_chat.configure(state="normal")
        self.txt_chat.insert("end", f"{autor}:\n", tag)
        self.txt_chat.insert("end", f"{texto}")
        if salto_linea: self.txt_chat.insert("end", "\n\n")
        self.txt_chat.see("end")
        self.txt_chat.configure(state="disabled")

    def _escribir_token(self, token):
        self.txt_chat.configure(state="normal")
        self.txt_chat.insert("end", token)
        self.txt_chat.see("end")
        self.txt_chat.configure(state="disabled")

    def _finalizar_chat(self, respuesta_completa):
        self.chat_historial.append({"role": "assistant", "content": respuesta_completa})
        self.txt_chat.configure(state="normal")
        self.txt_chat.insert("end", "\n\n")
        self.txt_chat.configure(state="disabled")
        self.btn_enviar_chat.configure(state="normal")
        self.status_label.configure(text="Respuesta completada.")

    # --- UTILIDADES ---
    def _mostrar_pantalla(self, pantalla):
        for vista in (self.vista_pregunta, self.vista_cargando, self.vista_resultado, self.vista_chat):
            vista.grid_forget()
        getattr(self, f"vista_{pantalla}").grid(row=0, column=0, sticky="nsew")
        if pantalla == "pregunta": self.entry_chat.focus_set()

    def _alternar_tema(self):
        ctk.set_appearance_mode(self.theme_switch.get())
        self.theme_switch.configure(text="Modo Oscuro" if self.theme_switch.get() == "Dark" else "Modo Claro")

if __name__ == "__main__":
    app = RecomendadorSkillsApp()
    app.mainloop()