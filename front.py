import streamlit as st
import re
import requests
from authenticator.controller.authentication_controller import AuthenticationController
from authenticator.controller.cookie_controller import CookieController
import  authenticator.params as params
from typing import Generator
from backend.Scrum_AI import Agente_AI
from backend.UserHist_AI import Agente_UH_AI
from PIL import Image
from docx import Document
from PyPDF2 import PdfReader
import extra_streamlit_components as stx
from Crear_pptx import extract_text_from_pptx
from Crear_Excel import leer_excel_como_texto
from  MongoDB import Obtener_Nombres_ChatDB,Cargar_HistorialDB,guardar_nuevo_chatDB,borrar_chatDB, guardar_historial_chatDB,obtener_archivo_gridfs,obtener_archivo_excel_gridfs
import time
# Página 1: User History
def user_history_page(user:str,logo):
    st.title("User History 🤖")
    AI="U_History"
    mensajeinicial="""🎉 ¡Bienvenido a la ventana del agente para la creación de historias de usuario!  
El objetivo de esta herramienta es ayudarte a elaborar un documento **Excel** con historias de usuario para tu proyecto, basado en la metodología **Scrum**. Este proceso es interactivo y está diseñado para recopilar toda la información necesaria paso a paso.  

### 🛠️ **¿Cómo funciona?**  
El chat te guiará a través de los siguientes pasos para estructurar las historias de usuario de tu proyecto:

📌 **Paso 1: Recopilación de Épicas**  
- Recopila las **épicas** del proyecto, asegurando que no falte ninguna. Te asignaremos un código único para cada una.  

📌 **Paso 2: Sugerencia de Historias de Usuario**  
- Por cada épica proporcionada, te sugeriremos **historias de usuario** relevantes. Validaremos contigo la codificación y contenido.  

📌 **Paso 3: Definición de Criterios de Aceptación**  
- Te ayudaremos a definir los **criterios de aceptación** para cada historia de usuario, asegurando que todas las condiciones sean claras para completarlas.  

📌 **Paso 4: Prioridad, Estimación de Esfuerzo y Responsable**  
- Estableceremos la **prioridad** y la **estimación de esfuerzo** para cada historia de usuario. También asignaremos a los **responsables** de cada tarea.  

📌 **Paso 5: Validación Final de la Información**  
- Verificaremos que toda la información esté completa y correcta antes de generar el documento final.  

📌 **Paso 6: Propuesta Preliminar**  
- Te presentaremos una versión preliminar del documento, que incluirá todos los detalles recopilados hasta el momento.  

📌 **Paso 7: Generación del Documento**  
- **Solo si apruebas la propuesta preliminar**, procederemos a generar el documento en formato Excel.  

---

### ❗ **Mensajes importantes:**  
🔴 **Campos faltantes:** Si intentamos generar el documento y aparece un mensaje en rojo indicando que falta información, utiliza frases como:  
- "¿ qué información hace falta?" 
- "¿En qué paso nos quedamos?"  
- "Genera el documento,  obteniendo toda la información proporcionada."  
- "quiero la propuesta preliminar"   

🔄 **Uso de términos adecuados:**  
- Durante los pasos intermedios, usa términos como **"continúa"** o **"continuar al siguiente paso"** para avanzar.  
- Evita palabras como **"aprobado"** o **"confirmo"** hasta la etapa final, cuando se te solicite explícitamente tu **aprobación final** para generar el documento.  
- siempre antes de generar el documento es recomendable preguntar *"quiero la propuesta preliminar"* si no se la ha brindado, para recopilar toda la información.

🔚 **Finalización de la interacción:**  
- Toda la interacción termina una vez has obtenido el **botón para descargar el archivo**.  

---

### 🚀 **¿Qué sigue?**  
📤 **Cargar un archivo:** Si tienes información previa o documentación del proyecto, puedes cargarla para darle contexto a la IA.  
💡 **Compartir tu idea:** Describe brevemente la idea que tienes para el proyecto, y el sistema te ayudará a desarrollarla.  

---

**¡Comencemos estructurando las historias de usuario y avanzando juntos!** 🎯✨  
    """
    st.write(mensajeinicial)
    st.sidebar.image(logo, caption="PENTALAB",use_container_width=True)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    #chats= Obtener_Chat(ruta)
    print("el usuario es"+user)  
    chats=Obtener_Nombres_ChatDB(user,AI)
    print(chats)

    if "nuevo_HU" not in st.session_state:
            st.session_state.nuevo_HU = False
    if not chats :
        print("entro2")
        st.session_state.nuevo_HU=True

    if st.session_state.nuevo_HU==False:
        parModelo = st.sidebar.selectbox('Chats', options=chats, index=0,disabled= st.session_state.nuevo_HU )
    else:
        parModelo="nuevo_chat"

    if "last_model" not in st.session_state :
        try:
            st.session_state.messages = Cargar_HistorialDB(user, parModelo,AI)
            st.session_state.nuevo_HU = False
            st.session_state.last_model = parModelo
        except FileNotFoundError:
            st.session_state.messages = []
            st.session_state.last_model = parModelo
            st.session_state.nuevo_HU = False
            st.session_state.last_model = parModelo

    if st.session_state.last_model != parModelo and parModelo!="nuevo_chat" :
        try:
            st.session_state.messages = Cargar_HistorialDB(user, parModelo,AI)
            st.session_state.last_model = parModelo
            st.session_state.nuevo_HU = False
        except FileNotFoundError:
            st.session_state.messages = []
            st.session_state.last_model = parModelo

    if st.query_params.last_AI=='True'and parModelo!= "nuevo_chat" :
        st.session_state.messages = Cargar_HistorialDB(user, parModelo,AI)
        st.session_state.last_model = parModelo
        st.session_state.nuevo_HU = False
        st.query_params.last_AI=False

    if  st.session_state.nuevo_HU==False:
        if st.sidebar.button("🗑️Borrar chat"):
            #borrar_chat(parModelo, ruta)  # Borrar el archivo correspondiente      # Muestra mensajes de chat desde la historia en la aplicación
            borrar_chatDB(user, parModelo,AI)
            st.rerun() 
        
        if st.sidebar.button("💾Nuevo_Proyecto"):
            #borrar_chat(parModelo, ruta)  # Borrar el archivo correspondiente      # Muestra mensajes de chat desde la historia en la aplicación
            st.session_state.nuevo_HU = True
            st.session_state.messages = []

            st.rerun() 
    if  st.session_state.nuevo_HU==True:
        print("entro ")
        nombre_archivo=st.sidebar.text_input(" Para guardar este  chat,ingresa un nombre:",key=1)
        # Si el usuario ha ingresado un nombre, guardar el chat
        if nombre_archivo:
            if st.sidebar.button("💾Guardar chat"):
                if " " in nombre_archivo:
                    st.sidebar.error("El nombre no puede contener espacios")
                else:
                    # Guardar el chat con el nombre proporcionado
                    respuesta=guardar_nuevo_chatDB(user, nombre_archivo, st.session_state.messages,AI)
                    st.session_state.last_model = nombre_archivo
                    st.session_state.nuevo_HU=False
                    st.sidebar.success(respuesta)  
                    st.rerun()   
         
    with st.container():
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Mostramos el campo para el prompt del usuario
    prompt = st.chat_input("Como te puedo ayudar?")
    
    if st.session_state.messages == [] :
        uploaded_file= st.file_uploader("Podemos iniciar la conversación,cargando la información.")
        if uploaded_file is not None:
            nombre_archivo = uploaded_file.name
            if   nombre_archivo.endswith('.pptx'):
                text=extract_text_from_pptx(uploaded_file)
                uploaded_file=None
                text=text+"En base a esta información de mi proyecto,usalo como contexto del proyecto y empieza sugiriendome las epicas y hisotrias de usuario  respectivas."
                prompt=text
            elif   nombre_archivo.endswith('.xlsx'):
                text=leer_excel_como_texto(uploaded_file)
                uploaded_file=None
                text=text+"En base a esta información de mi proyecto,analiza la información y usalo como contexto para seguir desarrollando el proyecto."
                prompt=text
            elif  nombre_archivo.endswith('.pdf'):
                text=leer_archivo_pdf(uploaded_file)
                uploaded_file=None
                text=text+"En base a esta información de mi proyecto,analiza la información y empieza sugiriendome las epicas  y hisotrias de usuario respectivas."
                prompt=text
            elif nombre_archivo.endswith('.docx'):
                text=leer_archivo_word(uploaded_file)
                uploaded_file=None
                text=text+"En base a esta información de mi proyecto,analiza la información  y empieza sugiriendome las epicas y hisotrias de usuario  respectivas."
                prompt=text
            else:
                st.error(f"el formato del archivo no es compatible")
         
                
    if prompt:
        print(parModelo)
        print(st.session_state.nuevo_HU)
        # Mostrar mensaje de usuario en el contenedor de mensajes de chat
        st.chat_message("user").markdown(prompt)
        # Agregar mensaje de usuario al historial de chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        if st.session_state.nuevo_HU==False:
            guardar_historial_chatDB([{"role": "user", "content": prompt}], parModelo, user,AI)
            #guardar_historial_chat([{"role": "user", "content": prompt}], archivo_id=parModelo,AI=ruta)
        try:
            # Mostrar respuesta del asistente en el contenedor de mensajes de chat
            with st.chat_message("assistant"):
                #respuesta = Agente_UH_AI(prompt,parModelo,"/"+ruta+"/",st.session_state.messages) #Agente_AI(prompt,parModelo) 
                respuesta = Agente_UH_AI(prompt,parModelo,st.session_state.messages,user)
                chat_responses_generator = generate_chat_responses(respuesta)
                full_response = st.write_stream(chat_responses_generator)
                if ".xlsx" in full_response:
                    frase_clave = ":"
                    # Extraer el nombre del archivo
                    if frase_clave in full_response :
                        nombre_archivo = full_response .split(frase_clave)[1].strip()
                        nombre_archivo=extraer_nombre_archivo(full_response, frase_clave,1)
                        print(" el nombre es"+nombre_archivo)
                        archivo_binario, archivo_nombre = obtener_archivo_excel_gridfs( nombre_archivo)
                # Descargar el archivo
                        st.download_button(
                            label="📥 Haz clic aquí para descargar el archivo",
                            data=archivo_binario,
                            file_name=archivo_nombre,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )              
                elif "se ha creado y guardado como:" in full_response:
                    frase_clave = "como:"
                    if full_response.endswith("."):
                        # Elimina el último carácter
                        full_response = full_response[:-1]
                    full_response=full_response+'.xlsx'
                    # Extraer el nombre del archivo
                    if frase_clave in full_response :
                        nombre_archivo = full_response .split(frase_clave)[1].strip()
                        nombre_archivo=extraer_nombre_archivo(full_response, frase_clave,1)
                        print(" el nombre es"+nombre_archivo)
                        archivo_binario, archivo_nombre = obtener_archivo_excel_gridfs( nombre_archivo)
                # Descargar el archivo
                        st.download_button(
                            label="📥 Haz clic aquí para descargar el archivo",
                            data=archivo_binario,
                            file_name=archivo_nombre,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )                        
            # Agregar respuesta de asistente al historial de chat
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            if st.session_state.nuevo_HU==False:
                print(parModelo)
                guardar_historial_chatDB([{"role": "assistant", "content": full_response}], parModelo, user,AI)
                #guardar_historial_chat([{"role": "assistant", "content": full_response}], archivo_id=parModelo,AI=ruta)
        except Exception as e:
            try:
                for error  in e.errors():
                    if  error.get("loc", ["Desconocido"])[0]=="nombre_archivo":
                        field = error.get("loc", ["Desconocido"])[0]  # Campo con el error
                        st.error(f"No se pudo crear el documento la IA no esta enviando la información de '{field}' ,asegurate de pedirle a la AI que envie esa información.")
                    else:
                        field = error.get("loc", ["Desconocido"])[1]  # Campo con el error
                        st.error(f"No se pudo crear el documento la IA no esta enviando la información de '{field}' ,asegurate de pedirle a la AI que envie esa información.")
                
            except:
                st.error(e)




# Página 2: Levantamiento de Proyectos
def levantamiento_proyectos_page(user:str,logo):
    st.title("Levantamiento de Proyectos 📂")
    mensajeinicial="""🎉 ¡Bienvenido a la ventana del agente para el levantamiento de proyectos!  

El objetivo de esta herramienta es ayudarte a generar un documento estructurado en formato **PowerPoint** para tu proyecto, basado en la metodología **Scrum**. Este proceso es interactivo y está diseñado para recopilar toda la información necesaria paso a paso.  

### 🛠️ **¿Cómo funciona?**  
El chat te guiará a través de los siguientes puntos para estructurar tu proyecto:  

📌 **Información General:**  
- 📄 Nombre del Proyecto  
- 👤 Encargado  
- 📂 Clúster / Área  

📌 **Detalles del Proyecto:**  
- 🎯 Objetivos  

📌 **Detalles Específicos:**  
- 📝 Justificación  
- ⚠️ Riesgos y Consideraciones  
- 📊 Especificaciones  
   - 📌 Alcance  
   - ✅ Beneficios  
   - 📈 Indicadores de Éxito  
- ⏳ Cronograma de Ejecución  

📌 **Recursos:**  
- 💻 Tecnológicos  
- 🧑‍🤝‍🧑 Humanos  
- 💰 Financieros  

Durante el proceso, podrás interactuar con la IA para **ajustar detalles**, recibir **sugerencias**, o avanzar al **siguiente paso** según sea necesario.  

---

### ❗ **Mensajes importantes:**  
🔴 **Campos faltantes:** Si intentamos generar el documento y aparece un mensaje en rojo indicando que falta información, utiliza frases como:  
- "¿ qué información hace falta?"  
- "Genera el documento,  obteniendo toda la información proporcionada."  
- "¿En qué paso nos quedamos?"  

🔄 **Uso de términos adecuados:**  
- Durante los pasos intermedios, usa términos como **"continúa"** o **"continuar al siguiente paso"** para avanzar.  
- Evita palabras como **"aprobado"** o **"confirmo"** hasta la etapa final, cuando se te solicite explícitamente tu **aprobación final** para generar el documento.  

🔚 **Finalización de la interacción:**  
- Toda la interacción termina una vez has obtenido el **botón para descargar el archivo**.  

---

### 🚀 **¿Qué sigue?**  
📤 **Cargar un archivo:** Si tienes información previa o documentación del proyecto, puedes cargarla para darle contexto a la IA.  
💡 **Compartir tu idea:** Describe brevemente la idea que tienes para el proyecto, y el sistema te ayudará a desarrollarla.  

---

**¡Comencemos estructurando tu proyecto y avanzando juntos!** 🎯✨  
"""
    st.write(mensajeinicial)
    st.sidebar.image(logo, caption="PENTALAB",use_container_width=True)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "nuevo_p"not in st.session_state:
        st.session_state.nuevo_p = False
    AI="L_Proyectos"
    chats=Obtener_Nombres_ChatDB(user,AI)
    if not chats :
        st.session_state.nuevo_p=True
    if st.session_state.nuevo_p==False:
        parModelo = st.sidebar.selectbox('Chats', options=chats, index=0,disabled= st.session_state.nuevo_p )
    else:
        parModelo="nuevo_chat"
    if "last_model" not in st.session_state:
        try:
            st.session_state.messages = Cargar_HistorialDB(user, parModelo,AI)
            st.session_state.nuevo_p = False
            st.session_state.last_model = parModelo
        except FileNotFoundError:
            st.session_state.messages = []
            st.session_state.last_model = parModelo
            st.session_state.nuevo_p = False
            st.session_state.last_model = parModelo
    if st.session_state.last_model != parModelo and parModelo!="nuevo_chat" :
        try:
            st.session_state.messages = Cargar_HistorialDB(user, parModelo,AI)
            st.session_state.last_model = parModelo
            st.session_state.nuevo_p = False
        except FileNotFoundError:
            st.session_state.messages = []
            st.session_state.last_model = parModelo
    if st.query_params.last_AI=='True'and parModelo!= "nuevo_chat" :
        st.session_state.messages = Cargar_HistorialDB(user, parModelo,AI)
        st.session_state.last_model = parModelo
        st.session_state.nuevo_p = False
        st.query_params.last_AI=False
   
    if  st.session_state.nuevo_p==False:
        if st.sidebar.button("🗑️Borrar chat"):
            #borrar_chat(parModelo, ruta)  # Borrar el archivo correspondiente      # Muestra mensajes de chat desde la historia en la aplicación
            borrar_chatDB(user, parModelo,AI)
            st.rerun() 
        
        if st.sidebar.button("💾Nuevo_Proyecto"):
            #borrar_chat(parModelo, ruta)  # Borrar el archivo correspondiente      # Muestra mensajes de chat desde la historia en la aplicación
            st.session_state.nuevo_p = True
            st.session_state.messages = []
            st.rerun() 
    print(st.session_state.nuevo_p) 
    if  st.session_state.nuevo_p==True:
        nombre_archivo=st.sidebar.text_input(" Para guardar este  chat,ingresa un nombre:")
        # Si el usuario ha ingresado un nombre, guardar el chat
        if nombre_archivo:
            if st.sidebar.button("💾Guardar chat"):
                if " " in nombre_archivo:
                    st.sidebar.error("El nombre no puede contener espacios")
                else:
                    # Guardar el chat con el nombre proporcionado
                    respuesta=guardar_nuevo_chatDB(user, nombre_archivo, st.session_state.messages,AI)
                    st.session_state.last_model = nombre_archivo
                    st.session_state.nuevo_p=False
                    st.sidebar.success(respuesta)  
                    st.rerun()  
    # Muestra mensajes de chat desde la historia en la aplicación
    with st.container():
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Mostramos el campo para el prompt del usuario
    prompt = st.chat_input("Como te puedo ayudar?")
    if st.session_state.messages == [] :
        uploaded_file= st.file_uploader("Podemos iniciar la conversación,cargando la información.")
        if uploaded_file is not None:
            nombre_archivo = uploaded_file.name
            if   nombre_archivo.endswith('.pptx'):
                text=extract_text_from_pptx(uploaded_file)
                uploaded_file=None
                text=text+"En base a esta información de mi proyecto,analiza la información y usalo como contexto para seguir desarrollando el proyecto,brindame el objetivo smart, la justificación  y cualquier otro campo que sea necesario para desarrollar este documento y que se pueda extaer de esta infomración."
                prompt=text
            elif   nombre_archivo.endswith('.xlsx'):
                text=leer_excel_como_texto(uploaded_file)
                uploaded_file=None
                text=text+"En base a esta información de mi proyecto,analiza la información y usalo como contexto para seguir desarrollando el proyecto,brindame el objetivo smart, la justificación  y cualquier otro campo que sea necesario para desarrollar este documento y que se pueda extaer de esta infomración."
                prompt=text
            elif  nombre_archivo.endswith('.pdf'):
                text=leer_archivo_pdf(uploaded_file)
                uploaded_file=None
                text=text+"En base a esta información de mi proyecto,analiza la información  y usalo como contexto para seguir desarrollando el proyecto,brindame el objetivo smart, la justificación  y cualquier otro campo que sea necesario para desarrollar este documento y que se pueda extaer de esta infomración."
            elif nombre_archivo.endswith('.docx'):
                text=leer_archivo_word(uploaded_file)
                uploaded_file=None
                text=text+"En base a esta información de mi proyecto,analiza la información   y usalo como contexto para seguir desarrollando el proyecto,brindame el objetivo smart, la justificación  y cualquier otro campo que sea necesario para desarrollar este documento y que se pueda extaer de esta infomración."
                prompt=text
            else:
                st.error(f"el formato del archivo no es compatible")
    if prompt:
        # Mostrar mensaje de usuario en el contenedor de mensajes de chat
        st.chat_message("user").markdown(prompt)
        # Agregar mensaje de usuario al historial de chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        if  st.session_state.nuevo_p!=True:
            guardar_historial_chatDB([{"role": "user", "content": prompt}], parModelo, user,AI)
            #guardar_historial_chat([{"role": "user", "content": prompt}], archivo_id=parModelo,AI=ruta)
        try:
            # Mostrar respuesta del asistente en el contenedor de mensajes de chat
            with st.chat_message("assistant"):
                respuesta = Agente_AI(prompt,parModelo,st.session_state.messages,user) #Agente_UH_AI(prompt,parModelo) #Agente_AI(prompt,parModelo) 
                chat_responses_generator = generate_chat_responses(respuesta)
                full_response = st.write_stream(chat_responses_generator)
                if ".pptx" in full_response:
                    frase_clave = ":"
                    # Extraer el nombre del archivo
                    if frase_clave in full_response :
                        nombre_archivo = full_response .split(frase_clave)[1].strip()
                        nombre_archivo=extraer_nombre_archivo(full_response, frase_clave,2)
                        print(" el nombre es"+nombre_archivo)
                        archivo_binario, archivo_nombre = obtener_archivo_gridfs( nombre_archivo)
                # Descargar el archivo
                        st.download_button(
                            label="📥 Haz clic aquí para descargar el archivo",
                            data=archivo_binario,
                            file_name=archivo_nombre,
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                            )                            
            # Agregar respuesta de asistente al historial de chat
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            if st.session_state.nuevo_p!=True:
                #guardar_historial_chat([{"role": "assistant", "content": full_response}], archivo_id=parModelo,AI="L_Proyectos")
                guardar_historial_chatDB([{"role": "assistant", "content": full_response}], parModelo, user,AI)
        except Exception as e:
            try:
                for error  in e.errors():
                    if  error.get("loc", ["Desconocido"])[0]=="nombre_archivo":
                        field = error.get("loc", ["Desconocido"])[0]  # Campo con el error
                        st.error(f"No se pudo crear el documento la IA no esta enviando la información de '{field}' ,asegurate de pedirle a la AI que envie esa información.")
                    else:
                        field = error.get("loc", ["Desconocido"])[1]  # Campo con el error
                        st.error(f"No se pudo crear el documento la IA no esta enviando la información de '{field}' ,asegurate de pedirle a la AI que envie esa información.")
                
            except:
                st.error(e)


def extraer_nombre_archivo(texto, frase_clave,num):
    # Patrón para buscar el nombre del archivo hasta ".xlsx"
    if num==1:
        patron = re.escape(frase_clave) + r"\s*(.+?\.xlsx)"
    elif num==2:
        patron = re.escape(frase_clave) + r"\s*(.+?\.pptx)"
    # Buscar coincidencia
    match = re.search(patron, texto)
    if match:
        # Extraer el nombre y eliminar los asteriscos "**" si existen
        nombre_archivo = match.group(1).replace("**", "").strip()
        return nombre_archivo
    return None

def generate_chat_responses(chat_completion) -> Generator[str, None, None]:   
    """Genera respuestas de chat a partir de información de completado de chat."""
    for chunk in chat_completion:
        yield chunk



def leer_archivo_word(ruta_archivo):
    """
    Lee el contenido de un archivo .docx y lo devuelve como string.
    """
    try:
        doc = Document(ruta_archivo)
        contenido = ""
        for parrafo in doc.paragraphs:
            contenido += parrafo.text + "\n"
        return contenido
    except Exception as e:
        return f"Error al leer el archivo Word: {e}"

def leer_archivo_pdf(ruta_archivo):
    """
    Lee el contenido de un archivo PDF y lo devuelve como string.
    """
    try:
        lector = PdfReader(ruta_archivo)
        contenido = ""
        for pagina in lector.pages:
            contenido += pagina.extract_text() + "\n"
        return contenido
    except Exception as e:
        return f"Error al leer el archivo PDF: {e}"
# Función para manejar las ventanas
def  sub_main(cookie_controller):
    logo_path = r"media/cohete.png"  # Reemplaza con la ruta de tu archivo de imagen
    logo = Image.open(logo_path)
    if "last_AI" not in st.query_params:
        st.query_params["last_AI"]  = False
    # Mostrar el contenido de la página activa
    if st.query_params["page"]  == "User_history":
        user_history_page(st.session_state["name"],logo)
    elif st.query_params["page"]  == "L_Proyectos":
        levantamiento_proyectos_page(st.session_state["name"],logo)
    
    # Navegación entre ventanas
    with st.sidebar:
        # Usar Markdown y CSS para darle forma circular a la imagen en el sidebar
        st.title("Navegación")

        if st.button("1)💡 Levantamiento de Proyectos"):
            if st.query_params["page"]!="L_Proyectos":
                st.session_state.messages = []
                st.session_state.nuevo_HU=False
                st.query_params["last_AI"]=True
                st.query_params["page"]="L_Proyectos"
            st.rerun() 
        if st.button("2)📝 User History"):
            if st.query_params["page"]!="User_history":
                st.session_state.messages = []
                st.session_state.nuevo_p=False
                st.query_params["last_AI"]=True
                st.query_params["page"]="User_history"
            st.rerun() 
        st.divider()
        with st.expander("SESIÓN"):
            st.subheader(st.session_state["name"])
            st.caption(st.session_state["roles"])
            if st.button('Cerrar Sesión'):
                st.session_state['authentication_status']=None
                st.session_state.messages = []
                cookie_controller.delete_cookie()
            st.divider()

# Configuración de la app
st.set_page_config(page_title="SCRUM IA", page_icon="🤖")
if "page" not in st.query_params:
    #st.query_params.page=""
    st.query_params["page"]="L_Proyectos"
# Obtener nombres de los archivos en la carpeta "chats"
nombres_archivos = []
plantilla_datos = r'plantillas/PLANTILLA1.pptx'
if "messages" not in st.session_state:
    st.session_state.messages = []

def main():
    # Cargar el logo del cohete
    logo_path = r"media/cohete.png"  # Reemplaza con la ruta de tu archivo de imagen
    logo = Image.open(logo_path)
    col2, col3= st.columns(2)
    cookie_controller=   CookieController("ScrumAI","ScrumAI",1)#0.000694444
    if  'authentication_status' not in st.session_state:
            st.session_state['authentication_status']=None
            token = cookie_controller.get_cookie()
            if token:
                st.session_state['email']=token['email']
                st.session_state['name']=token['name']
                st.session_state['roles'] = token['roles']
                st.session_state['authentication_status'] = True
                st.session_state['username'] = token['username']
                #self.credentials['usernames'][token['username']]['logged_in'] = True
            time.sleep(params.PRE_LOGIN_SLEEP_TIME)
        # Obtener el token de la cookie si existe
    
    try:
        #authenticator.login(max_concurrent_users=1,max_login_attempts=3,fields=  {'Form name':'LOGIN', 'Username':'Usuario', 'Password':'Contraseña', 'Login':'Login'})
        with col2:  # Usamos la columna del medio para centrar el formulario
             #Título del formulario
            if  st.session_state['authentication_status']!=True:
                st.header("Accede a tu cuenta")
                
                # Campos del formulario de login
                username = st.text_input("Usuario:", max_chars=50)
                password = st.text_input("Contraseña:", type="password", max_chars=50)

                # Botón de login
                login=st.button("Login")
                if login:
                    respuesta,verificacion=Autentificar(username,password)
                    print(respuesta)
                    if verificacion==True:
                        credentials = {"usernames":{
                            'username':username,
                            'password': password,
                            'email': "jhurtado@pentalab.tech",
                            'roles':"Usuario",
                            "failed_login_attempts": "0",  # Will be managed automatically
                            "logged_in": "False",  # Will be managed automatically
                            'name':respuesta}
                        }
                        # Inicializar el objeto AuthenticationController con los parámetros deseados
                        auth_controller = AuthenticationController(
                            credentials=credentials,    # Credenciales del usuario
                            auto_hash=True,             # Establecer si los passwords deben ser automáticamente hasheados
                        )
                    # Realizar el intento de inicio de sesión
                        if auth_controller.login(respuesta, password, 3, 3,single_session=True):
                                cookie_controller.set_cookie()
                                st.rerun()

                    else:
                        st.session_state['authentication_status'] = False

        if st.session_state['authentication_status']:
            st.title("ASISTENTE DE SCRUM 🤖")
            sub_main(cookie_controller)
        elif st.session_state['authentication_status'] is False:
            with col3:
                    st.image(logo, width=300)
            st.error('Usuario y/o Contraseña Incorrectos')
        elif st.session_state['authentication_status'] is None:    
            with col3:
                    st.image(logo, width=300)
            st.warning('Por favor ingrese su Usuario  y Contraseña')
    except Exception as e:
        st.error(e)
  
import requests
def Autentificar(username,password):
    # URL de la API
    url = "https://apicorporativo.curbe.com.ec/api/login"

    # Datos del cuerpo de la solicitud
    payload = {
        "id": username,
        "clave": password,
        "project": 4
    }

    try:
        # Realizar la solicitud POST
        response = requests.post(url, json=payload)

        # Verificar el estado de la respuesta
        if response.status_code == 200:
            print("Solicitud exitosa:")
            data=response.json()  # Imprimir la respuesta en formato JSON
            # Validar si existe la clave 'usuario'
            if 'usuario' in data:
                nombrecompleto= data['usuario']['nombre_completo']
                for roles in  data['usuario']['roles']:
                    if  "id" in roles:
                        if roles['id']=="IASCRUM":
                            return nombrecompleto,True

            else:
                return None,False
        else:
            print(f"Error en la solicitud: {response.status_code}")
            return response.json()['message'],False

    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return None

# Ejecutar la aplicación principal
if __name__ == "__main__":
    main()
