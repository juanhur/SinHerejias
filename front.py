import streamlit as st
import re
import os 
import requests
from authenticator.controller.authentication_controller import AuthenticationController
from authenticator.controller.cookie_controller import CookieController
import  authenticator.params as params
from typing import Generator
from PIL import Image
from docx import Document
from PyPDF2 import PdfReader
import extra_streamlit_components as stx
import time
from collections import defaultdict
import bcrypt
import requests
import psycopg2
import bcrypt
import json
def main():
    st.set_page_config(layout="wide")
    if "page" not in st.query_params:
    #st.query_params.page=""
        st.query_params["page"]="Simple_chat"
    # Cargar el logo del cohete
    logo_path = r"media/sh logo.png"  # Reemplaza con la ruta de tu archivo de imagen
    logo = Image.open(logo_path)
    col2, col3= st.columns(2)
    cookie_controller=   CookieController("Cristiana","Cristiana",1)#0.000694444
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
                    print(password)
                    hash = password
                    #hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                    respuesta,verificacion,mail=Autentificar(username,hash)
                    print(respuesta)
                    if verificacion==True:
                        credentials = {"usernames":{
                            'username':username,
                            'password': password,
                            'email': mail,
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
            st.title("SinHerejías.ai")
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
  

def conectar_dbSupabase():
    # Configuración de conexión a la base de datos
    DB_CONFIG = {
        'user': 'postgres.nxrcboulzolgtzlbzamt',
        'password': 'Astrid2025@',
        'host': 'aws-0-us-west-1.pooler.supabase.com',
        'port': 5432,
        'dbname': 'postgres'
    }
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
def Autentificar(username,password):
    conn = conectar_dbSupabase()
    if conn is None:
        return None, False

    try:
        cursor = conn.cursor()
        # Trae el hash y el nombre del usuario
        query = 'SELECT * FROM public."Usuarios" WHERE mail = %s'
        cursor.execute(query, (username,))
        resultado = cursor.fetchone()
        print("respeusta"+str(resultado))
        if resultado:
            print("entro")
            id_usuario, fecha_creacion, mail, nombre, apellido, hash_guardado = resultado
            print(password)
            #hash_guardado=bcrypt.hashpw(hash_guardado.encode('utf-8'), bcrypt.gensalt())
            print(hash_guardado)
            if password==hash_guardado:
                return nombre + " " + apellido, True, mail
            else:
                return None, False

    except Exception as e:
        print(f"Error en la consulta: {e}")
        return None, False,None
    finally:
        conn.close()

def  sub_main(cookie_controller):
    logo_path = r"media/sh logo.png"  
    logo = Image.open(logo_path)
    st.sidebar.image(logo, caption="Demo",use_container_width=True)
    if "last_AI" not in st.query_params:
        st.query_params["last_AI"]  = False
    if "nuevo_HU" not in st.session_state:
        st.session_state.nuevo_HU = False
    if "page" not in st.session_state:
        st.session_state.page = None
    
    if st.query_params["page"]  == "Simple_chat":
        Simple_page(st.session_state["name"])
    elif st.query_params["page"]  == "TeoExpertResearch":
        TeoExpert(st.session_state["name"])
    elif st.query_params["page"]  == "Exegesis":
        Exegesis(st.session_state["name"])
    # Navegación entre ventanas
    with st.sidebar:
        # Usar Markdown y CSS para darle forma circular a la imagen en el sidebar
        st.title("Proceso")

        # Obtener la página actual
        current_page = st.query_params.get("page", "")

        buttons = [
            ("1)💡 Chatear con IA", "Simple_chat"),
            ("2)📖 TeoExpert Research", "TeoExpertResearch"),
            ("3)📜 Exegesis Biblica", "Exegesis")
        ]

        for label, page in buttons:
            button_type = "primary" if current_page == page else "secondary"
            
            if st.button(label, use_container_width=True, type=button_type):
                if current_page != page:
                    st.session_state.messages = []
                    st.session_state.nuevo_HU = False
                    st.session_state.nuevo_p = False
                    st.query_params["last_AI"] = True
                    st.query_params["page"] = page
                    st.rerun()
            st.divider()
        st.divider()
        with st.expander("SESIÓN"):
            st.subheader(st.session_state["name"])
            st.caption(st.session_state["roles"])
            if st.button('Cerrar Sesión'):
                st.session_state['authentication_status']=None
                st.session_state.messages = []
                cookie_controller.delete_cookie()
            st.divider()

# Página 1: User History
def Simple_page(user:str):
    st.title("chatea con una IA📝")
    print("inicio"+ user)  
    if "messages" not in st.session_state:
        st.session_state.messages = []
    #chats= Obtener_Chat(ruta)
    if "nuevo_p"not in st.session_state:
        st.session_state.nuevo_p = False
    print("el usuario es"+user)  
    chats=obtener_chat_names_por_usuario(st.session_state['email'],1)
    print(chats)

    if not chats :
        print("entro2")
        st.session_state.nuevo_HU=True

    if st.session_state.nuevo_HU==False:
        parModelo = st.sidebar.selectbox('Chats', options=chats, index=0,disabled= st.session_state.nuevo_HU )
    else:
        parModelo="nuevo_chat"
    print(st.session_state.nuevo_HU)
    if "last_model" not in st.session_state :
        try:
            st.session_state.messages = Cargar_HistorialDB(st.session_state['email']+"_"+parModelo)
            st.session_state.nuevo_HU = False
            st.session_state.last_model = parModelo
        except FileNotFoundError:
            st.session_state.messages = []
            st.session_state.last_model = parModelo
            st.session_state.nuevo_HU = False
            st.session_state.last_model = parModelo

    if st.session_state.last_model != parModelo and parModelo!="nuevo_chat" :
        try:
            st.session_state.messages = Cargar_HistorialDB(st.session_state['email']+"_"+parModelo)
            st.session_state.last_model = parModelo
            st.session_state.nuevo_HU = False
        except FileNotFoundError:
            st.session_state.messages = []
            st.session_state.last_model = parModelo

    if st.query_params.last_AI=='True'and parModelo!= "nuevo_chat" :
        st.session_state.messages = Cargar_HistorialDB(st.session_state['email']+"_"+parModelo)
        st.session_state.last_model = parModelo
        st.session_state.nuevo_HU = False
        st.query_params.last_AI=False

    if  st.session_state.nuevo_HU==False:
        col1, col2 = st.sidebar.columns(2)  # Divide la pantalla en dos columnas

        with col1:
            if st.button("🗑️Borrar chat"):
                #borrar_chat(parModelo, ruta)  # Borrar el archivo correspondiente      # Muestra mensajes de chat desde la historia en la aplicación
                eliminar_chat_por_usuario(st.session_state['email'],1,parModelo)
                st.rerun() 

        with col2:
            if st.button("💾Nuevo chat"):
                ##borrar_chat(parModelo, ruta)  # Borrar el archivo correspondiente      # Muestra mensajes de chat desde la historia en la aplicación
                st.session_state.nuevo_HU = True
                st.session_state.messages = []
                st.session_state.nuevo_p=True
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
                    respuesta=guardar_chat_usuario(st.session_state['email'],1,nombre_archivo)
                    st.session_state.last_model = nombre_archivo
                    st.session_state.nuevo_HU=False
                    st.sidebar.success("Informacion guardada con exito")  
                    st.rerun()   
        # Crear pestañas
    #tabs = st.tabs(["📖 Resumen", "📜 Fundamento Bíblico", "🔥 Doctrina Pentecostal"])
    
    col1, col2 = st.columns(spec=[0.7, 0.3])
    print("pilas")
    print(st.session_state.messages)
    with col1:
        with st.container():
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    content = message.get("content")

                    # Mostrar si es solo string
                    if isinstance(content, str):
                        st.markdown(content)

                    # Mostrar si es dict estructurado
                    elif isinstance(content, dict):
                        if content.get("titulo_general"):
                            st.markdown(f"### {content['titulo_general']}")

                        secciones = content.get("secciones", {})

                        # Normalizar claves de secciones
                        secciones_modificadas = {}
                        for clave, texto in secciones.items():
                            clave_lower = clave.lower()
                            if "fundamento bíblico" in clave_lower:
                                secciones_modificadas["📖 Fundamento bíblico"] = texto
                            elif "aplicación práctica" in clave_lower:
                                secciones_modificadas["✅ Aplicación práctica"] = texto
                            elif "fuentes consultadas" in clave_lower:
                                secciones_modificadas["🌐 Fuentes consultadas"] = texto
                            elif "respuesta completa" in clave_lower:
                                secciones_modificadas["respuesta_completa"] = texto
                            else:
                                secciones_modificadas[clave] = texto

                        # Mostrar secciones normalizadas
                        for titulo, texto in secciones_modificadas.items():
                            if titulo.lower().strip() == "b). perspectiva doctrinal pentecostal":
                                continue  # ❌ NO mostrar esta sección

                            if titulo == "respuesta_completa":
                                st.markdown(texto, unsafe_allow_html=True)
                            else:
                                with st.expander(titulo):
                                    st.markdown(texto, unsafe_allow_html=True)

                    # Secciones adicionales estándar
                    if message["role"] == "assistant":
                        if message.get("fundamento_biblico"):
                            with st.expander("📖 Fundamento bíblico"):
                                st.markdown(message["fundamento_biblico"], unsafe_allow_html=True)

                        if message.get("aplicacion_practica"):
                            with st.expander("✅ Aplicación práctica"):
                                st.markdown(message["aplicacion_practica"], unsafe_allow_html=True)

                        if message.get("fuentes_consultadas"):
                            with st.expander("🌐 Fuentes consultadas"):
                                st.markdown(message["fuentes_consultadas"], unsafe_allow_html=True)

                        if message.get("respuesta_completa"):
                            st.markdown(message["respuesta_completa"], unsafe_allow_html=True)


                    # Mostramos el campo para el prompt del usuario
        # Set style of chat input so that it shows up at the bottom of the column
        chat_input_style = """
        <style>
        /* Contenedor del chat input */
        div[data-testid="stChatInput"] {
            width: 800px; /* ancho fijo o máximo que quieras */
            max-width: 90vw; /* para que no sea más ancho que la ventana */
            position: fixed;
            bottom: 6rem;
            left: 47%;
            transform: translateX(-50%);
            padding: 0 1rem;
            z-index: 9999;
            background-color: #0e1117; /* igual al fondo de Streamlit */
            box-sizing: border-box;
            border-radius: 8px; /* opcional para que se vea más bonito */
        }
        </style>

        """
        st.markdown(chat_input_style, unsafe_allow_html=True)
        prompt = st.chat_input(
                            "Como te puedo ayudar?",
                            accept_file=True,
                            width="stretch",
                            file_type=["jpg", "jpeg", "png"],
                        )
                #if prompt and prompt["files"]:
                    #st.image(prompt["files"][0])
        if prompt and prompt.text:
            # Mostrar mensaje de usuario en el contenedor de mensajes de chat
            st.chat_message("user").markdown(prompt.text)
            # Agregar mensaje de usuario al historial de chat
            st.session_state.messages.append({"role":  "user", "content":prompt.text})
            if  st.session_state.nuevo_p!=True:
                 guardar_imput_usuario(st.session_state['email']+"_"+parModelo,prompt.text)
            try:
                # Mostrar respuesta del asistente en el contenedor de mensajes de chat
                with st.chat_message("assistant"):
                    respuesta = enviar_input(prompt.text, parModelo, st.session_state['email'])
                    secciones = json.loads(respuesta)[0].get("secciones", {})
                    # Inicializar variables con valores por defecto
                    fundamento_biblico = ""
                    aplicacion_practica = ""
                    fuentes_consultadas = ""
                    respuesta_completa = ""

                    # Asignar según coincidencias parciales en las llaves
                    for clave, contenido in secciones.items():
                        clave_lower = clave.lower()

                        if "fundamento bíblico" in clave_lower:
                            fundamento_biblico = contenido
                        elif "aplicación práctica" in clave_lower:
                            aplicacion_practica = contenido
                        elif "fuentes consultadas" in clave_lower:
                            fuentes_consultadas = contenido
                        elif "respuesta completa" in clave_lower:
                            respuesta_completa = contenido

                    # Imprimir para verificar
                    print("Fundamento bíblico:\n", fundamento_biblico[:100], "\n")
                    print("Aplicación práctica:\n", aplicacion_practica[:100], "\n")
                    print("Fuentes consultadas:\n", fuentes_consultadas[:100], "\n")
                    print("Respuesta completa:\n", respuesta_completa[:100], "\n")
                    if fundamento_biblico:
                        guardar_bloque_fundamento(st.session_state['email']+"_"+parModelo,fundamento_biblico)
                        with st.expander("📖 Fundamento bíblico"):
                            st.markdown(fundamento_biblico, unsafe_allow_html=True)

                    if aplicacion_practica:
                        with st.expander("✅ Aplicación práctica"):
                            st.markdown(aplicacion_practica, unsafe_allow_html=True)

                    if fuentes_consultadas:
                        guardar_referencias(st.session_state['email']+"_"+parModelo,fuentes_consultadas)
                        with st.expander("🌐 Fuentes consultadas"):
                            st.markdown(fuentes_consultadas, unsafe_allow_html=True)
                    chat_responses_generator = generate_chat_responses(respuesta_completa)
                    full_response = st.write_stream(chat_responses_generator)   
                    if st.session_state.nuevo_p!=True:
                        guardar_respuesta_completa(st.session_state['email']+"_"+parModelo,respuesta)
                    #guardar_historial_chat([{"role": "assistant", "content": full_response}], archivo_id=parModelo,AI="L_Proyectos")
                   # guardar_historial_chatDB([{"role": "assistant", "content": full_response}], parModelo, user,AI)       
                # Agregar respuesta de asistente al historial de chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "fundamento_biblico": fundamento_biblico,
                    "aplicacion_practica": aplicacion_practica,
                    "fuentes_consultadas": fuentes_consultadas,
                    "content": full_response
                })
                
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
          

    #with tabs[1]:
        #st.subheader("Fundamento bíblico")
        #st.markdown("Versículos, contexto, referencias...")

    #with tabs[2]:
       # st.subheader("Perspectiva doctrinal pentecostal")
       # st.markdown("Enseñanzas del movimiento pentecostal sobre este tema...")
        # Muestra mensajes de chat desde la historia en la aplicación

    
def generate_chat_responses(chat_completion) -> Generator[str, None, None]:   
    """Genera respuestas de chat a partir de información de completado de chat."""
    for chunk in chat_completion:
        yield chunk

def enviar_input(valor,chat_id,email):
    """
    Envía un input al webhook de n8n.

    Parámetros:
    - valor (str): El valor que se enviará en el campo 'input'.

    Retorna:
    - La respuesta del servidor en texto.
    """
    url = "https://devwebhookn8n.hurtadoai.com/webhook/3780cfba-40e2-4cf2-bf25-52fc430f3433"
    payload = {
        "input": valor,
        "session_id":email+"_"+chat_id
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Lanza un error si el status code es 4xx o 5xx
        print(response)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error en la solicitud: {e}"
def guardar_respuesta_completa(session_id: str, respuesta_completa: str):
    conn = conectar_dbSupabase()
    print("lo que guardo de respeusta completa")
    print (respuesta_completa)
    if not conn:
        print("❌ No se pudo establecer conexión con la base de datos.")
        return

    mensaje = [{"role": "assistant", "content": respuesta_completa}]

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO public.ai_simple_chat_histories (session_id, message)
                VALUES (%s, %s)
            """, (session_id, json.dumps(mensaje)))
        conn.commit()
        print("✅ Mensaje guardado con éxito.")
    except Exception as e:
        print(f"❌ Error al insertar el mensaje: {e}")
        conn.rollback()
    finally:
        conn.close()
def guardar_imput_usuario(session_id: str,input: str):
    conn = conectar_dbSupabase()
    if not conn:
        print("❌ No se pudo establecer conexión con la base de datos.")
        return

    mensaje = [{"role": "user", "content": input}]

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO public.ai_simple_chat_histories (session_id, message)
                VALUES (%s, %s)
            """, (session_id, json.dumps(mensaje)))
        conn.commit()
        print("✅ Mensaje guardado con éxito.")
    except Exception as e:
        print(f"❌ Error al insertar el mensaje: {e}")
        conn.rollback()
    finally:
        conn.close()
def guardar_referencias(session_id: str, referencias_str: str):
    conn = conectar_dbSupabase()
    if not conn:
        print("❌ No se pudo establecer conexión con la base de datos.")
        return

    # Encapsular en una lista para cumplir con el tipo jsonb[]
    data = [{"texto": referencias_str}]

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO public.ai_simple_referencias (session_id, referencias)
                VALUES (%s, %s)
            """, (session_id, json.dumps(data)))
        conn.commit()
        print("✅ Referencias guardadas con éxito.")
    except Exception as e:
        print(f"❌ Error al insertar referencias: {e}")
        conn.rollback()
    finally:
        conn.close()

def guardar_bloque_fundamento(session_id: str, texto_fundamento: str):
    """
    Guarda el texto completo del bloque de versículos como un solo objeto en JSONB.
    """
    conn = conectar_dbSupabase()
    if not conn:
        print("❌ No se pudo establecer conexión con la base de datos.")
        return

    data = [{"texto": texto_fundamento}]

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO public.ai_simple_versiculos (session_id, versicles)
                VALUES (%s, %s)
            """, (session_id, json.dumps(data)))
        conn.commit()
        print("✅ Texto de versículos guardado con éxito.")
    except Exception as e:
        print(f"❌ Error al insertar versículos: {e}")
        conn.rollback()
    finally:
        conn.close()


def Cargar_HistorialDB(session_id: str, limite: int = 10, page:  int=1):
    if page == 1:
        conn = conectar_dbSupabase()
        if not conn:
            print("❌ No se pudo establecer conexión con la base de datos.")
            return []

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT message
                    FROM public.ai_simple_chat_histories
                    WHERE session_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (session_id, limite))
                
                resultados = cursor.fetchall()
                mensajes = [fila[0][0] for fila in resultados]

                mensajes_procesados = []
                for mensaje in mensajes:
                    content = mensaje.get('content', '')
                    if isinstance(content, str):
                        try:
                            parsed = json.loads(content)
                            if isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
                                mensaje['content'] = parsed[0]  # convertir a dict directamente
                        except json.JSONDecodeError:
                            pass  # dejar el contenido como está si no es un JSON válido
                    mensajes_procesados.append(mensaje)

                # Invertir el orden: de más antiguo a más reciente
                mensajes_procesados.reverse()

                return mensajes_procesados

        except Exception as e:
            print(f"❌ Error al obtener los mensajes: {e}")
            return []
        finally:
            conn.close()

def obtener_chat_names_por_usuario(usuario_mail: str, herramienta: int):
    conn = conectar_dbSupabase()
    if not conn:
        print("❌ No se pudo establecer conexión con la base de datos.")
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT chat_name
                FROM public."Usuario_chats"
                WHERE usuario_mail = %s AND herramienta = %s
                ORDER BY created_at DESC
            """, (usuario_mail, herramienta))
            
            resultados = cursor.fetchall()
            chat_names = [row[0] for row in resultados if row[0] is not None]

        print(f"✅ Se encontraron {len(chat_names)} chats para el usuario {usuario_mail}.")
        return chat_names
    except Exception as e:
        print(f"❌ Error al obtener los chats: {e}")
        return []
    finally:
        conn.close()
def eliminar_chat_por_usuario(usuario_mail: str, herramienta: int, chat_name: str):
    conn = conectar_dbSupabase()
    if not conn:
        print("❌ No se pudo establecer conexión con la base de datos.")
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM public."Usuario_chats"
                WHERE usuario_mail = %s AND herramienta = %s AND chat_name = %s
            """, (usuario_mail, herramienta, chat_name))
        
        conn.commit()
        print(f"✅ Chat '{chat_name}' eliminado con éxito.")
        return True
    except Exception as e:
        print(f"❌ Error al eliminar el chat: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def guardar_chat_usuario(usuario_mail: str, herramienta: int = None, chat_name: str = None):
    conn = conectar_dbSupabase()
    if not conn:
        print("❌ No se pudo establecer conexión con la base de datos.")
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO public."Usuario_chats" (usuario_mail, herramienta, chat_name)
                VALUES (%s, %s, %s)
            """, (usuario_mail, herramienta, chat_name))
        
        conn.commit()
        print(f"✅ Chat '{chat_name}' guardado con éxito para {usuario_mail}.")
        guardar_historial_mensajes_nuevo_chat(usuario_mail+"_"+chat_name,st.session_state.messages)
        return True
    except Exception as e:
        print(f"❌ Error al guardar el chat: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def guardar_historial_mensajes_nuevo_chat(session_id: str, mensajes: list):
    conn = conectar_dbSupabase()
    if not conn:
        print("❌ No se pudo establecer conexión con la base de datos.")
        return False

    try:
        with conn.cursor() as cursor:
            for mensaje in mensajes:
                # Asegurarse de que sea una lista con un solo dict (como espera la tabla)
                mensaje_json = json.dumps([mensaje])
                cursor.execute("""
                    INSERT INTO public.ai_simple_chat_histories (session_id, message)
                    VALUES (%s, %s)
                """, (session_id, mensaje_json))
        conn.commit()
        print(f"✅ Se guardaron {len(mensajes)} mensajes para la sesión '{session_id}'.")
        return True
    except Exception as e:
        print(f"❌ Error al guardar los mensajes: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def TeoExpert(user:str):
    st.title("📖 TeoExpert Research")
    #chats= Obtener_Chat(ruta)
    if "nuevo_p"not in st.session_state:
        st.session_state.nuevo_p = False
    print("el usuario es"+user)  
    st.session_state.messages = []
    chats=obtener_chat_names_por_usuario(st.session_state['email'],2)
    if "referencias" not in st.session_state:
        st.session_state.referencias= []
    if "FundamentoB" not in st.session_state:
        st.session_state.FundamentoB= []
    if "resumen" not in st.session_state:
        st.session_state.resumen= []
    if "doctrina penecostal" not in st.session_state:
        st.session_state.doctrina= []
    if "aplicacion" not in st.session_state:
        st.session_state.aplicacion= []
    if "titulo" not in st.session_state:
         st.session_state.titulo=""
    if "research" not in st.session_state:
         st.session_state.research=[]
    
    if not chats :
        print("entro2")
        st.session_state.nuevo_HU=True

    if st.session_state.nuevo_HU==False:
        parModelo = st.sidebar.selectbox('research guardadas', options=chats, index=0,disabled= st.session_state.nuevo_HU )
        if st.sidebar.button("🗑️Borrar research"):
            #borrar_chat(parModelo, ruta)  # Borrar el archivo correspondiente      # Muestra mensajes de chat desde la historia en la aplicación
            eliminar_chat_por_usuario(st.session_state['email'],2,parModelo)
            st.session_state.research=[]
            st.session_state.referencias = None
            st.session_state.resumen= None
            st.session_state.doctrina=  None
            st.session_state.aplicacion= None
            st.session_state.FundamentoB= None
            st.session_state.titulo = None
            st.rerun() 
    else:
        parModelo="nuevo_chat"

    if "last_model" not in st.session_state :
        try:
            Cargar_researchDB(st.session_state['email']+"_teo_"+parModelo)
            st.session_state.last_model = parModelo
            st.session_state.messages = []
        except FileNotFoundError:
            st.session_state.messages = []
            st.session_state.last_model = parModelo
            st.session_state.nuevo_HU = False
            st.session_state.last_model = parModelo

    if st.session_state.last_model != parModelo and parModelo!="nuevo_chat" :
        try:
            Cargar_researchDB(st.session_state['email']+"_teo_"+parModelo)
            st.session_state.messages = []
            st.session_state.last_model = parModelo
            st.session_state.nuevo_HU = False
        except FileNotFoundError:
            st.session_state.messages = []
            st.session_state.last_model = parModelo

    if st.query_params.last_AI=='True'and parModelo!= "nuevo_chat" :
        Cargar_researchDB(st.session_state['email']+"_teo_"+parModelo)
        st.session_state.messages = []
        st.session_state.last_model = parModelo
        st.session_state.nuevo_HU = False
        st.query_params.last_AI=False
      
    
    col1, col2 = st.columns(spec=[0.7, 0.3])
    with col1:
        col3, col4 = st.columns(spec=[0.9, 0.1])
        with col3:
            prompt = st.chat_input(
                                "Escribe el topico del cual quieres investigar",
                            )
                    #if prompt and prompt["files"]:
                        #st.image(prompt["files"][0])
        with col4:
            if st.button("💾"):
                if st.session_state.titulo.strip() == "":
                    st.error("No existe búsqueda para guardar")
                else:
                    existentes=obtener_chat_names_por_usuario(st.session_state['email'],2)
                    flag=0
                    for ex in existentes:
                        if st.session_state.titulo.replace(" ", "_")==ex:
                            flag=1
                    if flag==0:
                        respuesta=guardar_teoexpert_research(st.session_state['email'],2,st.session_state.titulo)
                        st.session_state.last_model=st.session_state.titulo.replace(" ", "_")
                        st.session_state.nuevo_HU=False
                        st.rerun()
                    else:
                        print("Bsqueda ya guardada") 
                        st.rerun()  
        if prompt :
            respuesta = enviar_inputTeo(prompt, parModelo, st.session_state['email'])
            st.session_state.research=respuesta
        
        if st.session_state.research:
            print(st.session_state.research)
            mostrar_research( st.session_state.research)

          
    with col2:
        with st.expander("📖 Fundamento bíblico"):
            st.markdown( st.session_state.FundamentoB, unsafe_allow_html=True)
        with st.expander("🌐 Fuentes consultadas"):
            st.markdown( st.session_state.referencias, unsafe_allow_html=True)

def enviar_inputTeo(valor,chat_id,email):
    """
    Envía un input al webhook de n8n.

    Parámetros:
    - valor (str): El valor que se enviará en el campo 'input'.

    Retorna:
    - La respuesta del servidor en texto.
    """
    url = "https://devwebhookn8n.hurtadoai.com/webhook/efeeff7b-6606-43d0-8c35-b4a9a6e69bf7"
    payload = {
        "input": valor,
        "session_id":email+"_"+chat_id
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Lanza un error si el status code es 4xx o 5xx
        return response.text
        print(response)
    except requests.exceptions.RequestException as e:
        return f"Error en la solicitud: {e}"
def enviar_versiculos(valor,chat_id,email):
    """
    Envía un input al webhook de n8n.

    Parámetros:
    - valor (str): El valor que se enviará en el campo 'input'.

    Retorna:
    - La respuesta del servidor en texto.
    """
    url = "https://devwebhookn8n.hurtadoai.com/webhook/58c147a8-b2c5-4346-b06b-16ab1b26519b"
    payload = {
        "input": valor,
        "session_id":email+"_"+chat_id
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Lanza un error si el status code es 4xx o 5xx
        return response.text
        print(response)
    except requests.exceptions.RequestException as e:
        return f"Error en la solicitud: {e}"
def guardar_teoexpert_research(usuario_mail: str, herramienta: int = None, chat_name: str = None):
    conn = conectar_dbSupabase()
    chat_name=chat_name.replace(" ", "_")
    if not conn:
        print("❌ No se pudo establecer conexión con la base de datos.")
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO public."Usuario_chats" (usuario_mail, herramienta, chat_name)
                VALUES (%s, %s, %s)
            """, (usuario_mail, herramienta, chat_name))
        
        conn.commit()
        print(f"✅ teoexpert '{chat_name}' guardado con éxito para {usuario_mail}.")
        guardar_research_info_teoexpert(usuario_mail+"_teo_"+chat_name,st.session_state.research)
        return True
    except Exception as e:
        print(f"❌ Error al guardar el chat: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def guardar_exegesis(usuario_mail: str, herramienta: int = None, chat_name: str = None):
    conn = conectar_dbSupabase()
    chat_name=chat_name.replace(" ", "_")
    if not conn:
        print("❌ No se pudo establecer conexión con la base de datos.")
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO public."Usuario_chats" (usuario_mail, herramienta, chat_name)
                VALUES (%s, %s, %s)
            """, (usuario_mail, herramienta, chat_name))
        
        conn.commit()
        print(f"✅ exegesis '{chat_name}' guardado con éxito para {usuario_mail}.")
        guardar_exegesis_info(usuario_mail+"_exe_"+chat_name,st.session_state.exegesis)
        return True
    except Exception as e:
        print(f"❌ Error al guardar el chat: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
def guardar_research_info_teoexpert(session_id: str, mensajes: list):

    conn = conectar_dbSupabase()
    if not conn:
        print("❌ No se pudo establecer conexión con la base de datos.")
        return False

    try:
        with conn.cursor() as cursor:
                # Asegurarse de que sea una lista con un solo dict (como espera la tabla)
                mensaje_json = json.dumps([mensajes])
                cursor.execute("""
                    INSERT INTO public.teoexpert_research (session_id, message)
                    VALUES (%s, %s)
                """, (session_id, mensaje_json))
        conn.commit()
        print(f"✅ Se guardaron {len(mensajes)} mensajes para la sesión '{session_id}'.")
        return True
    except Exception as e:
        print(f"❌ Error al guardar los mensajes: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
def guardar_exegesis_info(session_id: str, mensajes: list):

    conn = conectar_dbSupabase()
    if not conn:
        print("❌ No se pudo establecer conexión con la base de datos.")
        return False

    try:
        with conn.cursor() as cursor:
                # Asegurarse de que sea una lista con un solo dict (como espera la tabla)
                mensaje_json = json.dumps([mensajes])
                cursor.execute("""
                    INSERT INTO  public.exegesis(session_id, message)
                    VALUES (%s, %s)
                """, (session_id, mensaje_json))
        conn.commit()
        print(f"✅ Se guardaron {len(mensajes)} mensajes para la sesión '{session_id}'.")
        return True
    except Exception as e:
        print(f"❌ Error al guardar los mensajes: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
def Cargar_researchDB(session_id: str, limite: int = 10, page:  int=1):
    if page == 1:
        conn = conectar_dbSupabase()
        if not conn:
            print("❌ No se pudo establecer conexión con la base de datos.")
            return []

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT message
                    FROM public.teoexpert_research
                    WHERE session_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (session_id, limite))
                
                resultados = cursor.fetchall()
                mensajes = [fila[0][0] for fila in resultados]
                print(len(mensajes))
                st.session_state.research= mensajes[0]

        except Exception as e:
            print(f"❌ Error al obtener los mensajes: {e}")
            return []
        finally:
            conn.close()
def Cargar_exegesisDB(session_id: str, limite: int = 10, page:  int=1):
    if page == 1:
        conn = conectar_dbSupabase()
        if not conn:
            print("❌ No se pudo establecer conexión con la base de datos.")
            return []

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT message
                    FROM public.exegesis
                    WHERE session_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (session_id, limite))
                
                resultados = cursor.fetchall()
                mensajes = [fila[0][0] for fila in resultados]
                print(len(mensajes))
                st.session_state.exegesis= mensajes[0]

        except Exception as e:
            print(f"❌ Error al obtener los mensajes: {e}")
            return []
        finally:
            conn.close()
def mostrar_research(respuesta):
    respuesta=json.loads(respuesta)
    secciones = respuesta[1].get("secciones", {})
    citas = respuesta[0].get("citas", [])
    citas = "\n\n".join([f"[{i+1}] {ref['descripcionFuente']} – {ref['url']}" for i, ref in enumerate(citas) if ref['descripcionFuente']])
    st.session_state.referencias = citas
    st.session_state.resumen= secciones["1. Resumen teológico"]
    st.session_state.doctrina=  secciones['3. Perspectiva doctrinal pentecostal']
    st.session_state.aplicacion= secciones[ '4. Aplicación práctica para el creyente']
    st.session_state.FundamentoB= secciones[ '2. Fundamento bíblico']
    st.session_state.titulo = respuesta[1]["titulo_general"].strip()
    st.title( st.session_state.titulo)
    st.markdown( st.session_state.resumen, unsafe_allow_html=True)
    st.markdown( st.session_state.doctrina, unsafe_allow_html=True)
    st.subheader("Aplicación práctica")
    st.markdown( st.session_state.aplicacion, unsafe_allow_html=True)
def Exegesis(user:str):
    st.title("📜 Exegesis(explicación de versiculos)")
    #chats= Obtener_Chat(ruta)
    if "nuevo_p"not in st.session_state:
        st.session_state.nuevo_p = False
    print("el usuario es"+user)  
    st.session_state.messages = []
    chats=obtener_chat_names_por_usuario(st.session_state['email'],3)
    if "referencias" not in st.session_state:
        st.session_state.referencias= []
    if "FundamentoB" not in st.session_state:
        st.session_state.FundamentoB= []
    if "resumen" not in st.session_state:
        st.session_state.resumen= []
    if "doctrina penecostal" not in st.session_state:
        st.session_state.doctrina= []
    if "aplicacion" not in st.session_state:
        st.session_state.aplicacion= []
    if "titulo" not in st.session_state:
         st.session_state.titulo=""
    if "exegesis" not in st.session_state:
         st.session_state.exegesis=[]
    
    if not chats :
        print("entro2")
        st.session_state.nuevo_HU=True

    if st.session_state.nuevo_HU==False:
        parModelo = st.sidebar.selectbox('Exegesis guardadas', options=chats, index=0,disabled= st.session_state.nuevo_HU )
        if st.sidebar.button("🗑️Borrar Exegesis"):
            #borrar_chat(parModelo, ruta)  # Borrar el archivo correspondiente      # Muestra mensajes de chat desde la historia en la aplicación
            eliminar_chat_por_usuario(st.session_state['email'],3,parModelo)
            st.session_state.research=[]
            st.session_state.referencias = None
            st.session_state.resumen= None
            st.session_state.doctrina=  None
            st.session_state.aplicacion= None
            st.session_state.FundamentoB= None
            st.session_state.titulo = None
            st.rerun() 
    else:
        parModelo="nuevo_chat"

    if "last_model" not in st.session_state :
        try:
            Cargar_exegesisDB(st.session_state['email']+"_exe_"+parModelo)
            st.session_state.last_model = parModelo
            st.session_state.messages = []
        except FileNotFoundError:
            st.session_state.messages = []
            st.session_state.last_model = parModelo
            st.session_state.nuevo_HU = False
            st.session_state.last_model = parModelo

    if st.session_state.last_model != parModelo and parModelo!="nuevo_chat" :
        try:
            Cargar_exegesisDB(st.session_state['email']+"_exe_"+parModelo)
            st.session_state.messages = []
            st.session_state.last_model = parModelo
            st.session_state.nuevo_HU = False
        except FileNotFoundError:
            st.session_state.messages = []
            st.session_state.last_model = parModelo

    if st.query_params.last_AI=='True'and parModelo!= "nuevo_chat" :
        Cargar_exegesisDB(st.session_state['email']+"_exe_"+parModelo)
        st.session_state.messages = []
        st.session_state.last_model = parModelo
        st.session_state.nuevo_HU = False
        st.query_params.last_AI=False
      
    
    col1, col2 = st.columns(spec=[0.7, 0.3])
    with col1:
        col3, col4 = st.columns(spec=[0.9, 0.1])
        with col3:
            prompt = st.chat_input(
                                "Escribe el o los versiculos a profundizar",
                            )
        with col4:
            if st.button("💾"):
                if st.session_state.titulo.strip() == "":
                    st.error("No existe búsqueda para guardar")
                else:
                    existentes=obtener_chat_names_por_usuario(st.session_state['email'],3)
                    print("exegesis guardadas")
                    print(existentes)
                    print(st.session_state.titulo)
                    flag=0
                    for ex in existentes:
                        if st.session_state.titulo.replace(" ", "_")==ex:
                            flag=1
                    if flag==0:
                        respuesta=guardar_exegesis(st.session_state['email'],3,st.session_state.titulo)
                        st.session_state.last_model=st.session_state.titulo.replace(" ", "_")
                        st.session_state.nuevo_HU=False
                        st.rerun()
                    else:
                        print("Bsqueda ya guardada") 
                        st.rerun()  
        if prompt :
            respuesta = enviar_versiculos(prompt, parModelo, st.session_state['email'])
            st.session_state.exegesis=respuesta
        
        if st.session_state.exegesis:
            print(st.session_state.exegesis)
            mostrar_exegesis( st.session_state.exegesis)
    with col2:
        with st.expander("🌐 Fuentes consultadas"):
            st.markdown( st.session_state.referencias, unsafe_allow_html=True)

def mostrar_exegesis(respuesta):
    if isinstance(respuesta, str):
        respuesta = json.loads(respuesta)

    data = respuesta.get("data", [])

    if not data:
        st.warning("No se encontraron datos en la respuesta.")
        return

    # Inicializamos la lista para acumular todas las fuentes
    referencias_globales = []
    st.session_state.referencias = []
    tabs = st.tabs([item.get("titulo_general", "Sin título").strip() for item in data])

    for tab, item in zip(tabs, data):
        with tab:
            titulo = item.get("titulo_general", "Sin título").strip()
            secciones = item.get("secciones", {})
            st.session_state.titulo=titulo
            st.title(titulo)

            for clave, contenido in secciones.items():
                if clave.strip() == "🌐 FUENTES CONSULTADAS":
                    # Agregamos las referencias a la lista global
                    referencias_globales.append(contenido.strip())
                    continue

                titulo_limpio = re.sub(r"^[a-zA-Z]\)\.\s*", "", clave.strip())
                with st.expander(titulo_limpio):
                    st.markdown(contenido, unsafe_allow_html=True)

    # Guardamos todas las referencias concatenadas en una sola variable de sesión
    st.session_state.referencias = "\n\n".join(referencias_globales)
    # Si deseas mostrarlo después, puedes usar esto:
    # if "referencias" in st.session_state:
    #     st.subheader("🌐 Fuentes consultadas")
    #     st.markdown(st.session_state.referencias, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
