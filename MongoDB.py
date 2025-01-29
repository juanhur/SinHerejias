from pymongo import MongoClient
import os
import json
import gridfs


# Conexión a MongoDB
uri = "mongodb://dev_jhurtado:Pka12msE1b2qO1@192.168.193.5:27017/AIProjects?authSource=admin"
client = MongoClient(uri)

# Selección de la base de datos y colecciones
db = client["AIProjects"]
chats_proyectos = db["Chats_L_Proyectos"]
chats_historial = db["Chats_U_History"]

# Función para migrar chats desde almacenamiento local a MongoDB
def migrar_chats(ruta_base):
    for usuario in os.listdir(ruta_base):  # Iterar sobre carpetas de usuarios
        ruta_usuario = os.path.join(ruta_base, usuario)
        if os.path.isdir(ruta_usuario):
            print(f"Procesando usuario: {usuario}")

            # Migrar chats de L_Proyectos
            ruta_proyectos = os.path.join(ruta_usuario, "L_Proyectos")
            if os.path.exists(ruta_proyectos):
                for archivo in os.listdir(ruta_proyectos):
                    ruta_archivo = os.path.join(ruta_proyectos, archivo)
                    if os.path.isfile(ruta_archivo) and archivo.endswith(".json"):
                        with open(ruta_archivo, 'r', encoding='utf-8') as f:
                            contenido = json.load(f)
                            # Insertar chat completo en MongoDB
                            chats_proyectos.insert_one({
                                "usuario": usuario,
                                "chat_id": archivo.replace(".json", ""),
                                "contenido": contenido
                            })
                print(f"Chats de proyectos de {usuario} migrados.")

            # Migrar chats de U_History
            ruta_historial = os.path.join(ruta_usuario, "U_History")
            if os.path.exists(ruta_historial):
                for archivo in os.listdir(ruta_historial):
                    ruta_archivo = os.path.join(ruta_historial, archivo)
                    if os.path.isfile(ruta_archivo) and archivo.endswith(".json"):
                        with open(ruta_archivo, 'r', encoding='utf-8') as f:
                            contenido = json.load(f)
                            # Insertar chat completo en MongoDB
                            chats_historial.insert_one({
                                "usuario": usuario,
                                "chat_id": archivo.replace(".json", ""),
                                "contenido": contenido
                            })
                print(f"Chats del historial de {usuario} migrados.")





def Cargar_HistorialDB(usuario, chat_id,AI):
    if AI=="U_History":
        chat=  db["Chats_U_History"]
    elif AI=="L_Proyectos":
        chat=db["Chats_L_Proyectos"]

    """
    Carga el historial desde MongoDB basado en el usuario y chat_id.

    Args:
        usuario (str): Nombre del usuario.
        chat_id (str): Identificador del chat.

    Returns:
        list: Historial del chat (lista de mensajes) o una lista vacía si no se encuentra.
    """
    try:
        # Consultar el historial en la colección de MongoDB
        #chat.find_one({"usuario": usuario, "chat_id": chat_id}).limit(CANTIDAD)
        documento = chat.find_one({"usuario": usuario, "chat_id": chat_id})
        
        if documento:
            historial = documento.get("contenido", [])  # Obtener el contenido del historial
            historial= historial[-15:]
            print(f"Historial cargado correctamente para el usuario '{usuario}' y chat_id '{chat_id}':")
            #print(json.dumps(historial, indent=2, ensure_ascii=False))  # Imprimir el historial cargado
            return historial
        else:
            print(f"No se encontró historial para el usuario '{usuario}' y chat_id '{chat_id}'.")
            return []  # Retorna una lista vacía si no se encuentra
    except Exception as e:
        print(f"Error al cargar el historial: {str(e)}")
        return []  # Retorna una lista vacía en caso de error

def Obtener_Nombres_ChatDB(usuario,AI):
    """
    Obtiene la lista de chat_id asociados con un usuario desde MongoDB.

    Args:
        usuario (str): El nombre del usuario.

    Returns:
        list: Lista de chat_id asociados con el usuario.
    """
    try:
        if AI=="U_History":
            chat=  db["Chats_U_History"]
        elif AI=="L_Proyectos":
            chat=db["Chats_L_Proyectos"]
        # Consulta para obtener documentos del usuario
        documentos = chat.find({"usuario": usuario}, {"chat_id": 1, "_id": 0}).sort("_id", -1) 
        # Extraer los nombres de los chat_id
        nombres_chats = [doc["chat_id"] for doc in documentos]
        # Agregar "nuevo_proyecto" al inicio de la lista como en el código original
        modelos = nombres_chats
        return modelos
    except Exception as e:
        print(f"Error al obtener los chat_id: {str(e)}")
        return ["nuevo_proyecto"]  # Devuelve solo "nuevo_proyecto" en caso de error


def guardar_nuevo_chatDB(usuario, chat_id, mensajes,AI):
    if AI=="U_History":
        chat=  db["Chats_U_History"]
    elif AI=="L_Proyectos":
        chat=db["Chats_L_Proyectos"]
    """
    Guarda un nuevo chat en MongoDB.

    Args:
        usuario (str): El nombre del usuario.
        chat_id (str): Identificador único del chat.
        mensajes (list): Lista de mensajes del chat (en formato JSON).

    Returns:
        str: Mensaje indicando el resultado de la operación.
    """
    try:
        # Crear el documento que se insertará
        documento = {
            "usuario": usuario,
            "chat_id": chat_id,
            "contenido": mensajes  # Almacena los mensajes del chat
        }
        
        # Verificar si ya existe un chat con el mismo usuario y chat_id
        if chat.find_one({"usuario": usuario, "chat_id": chat_id}):
            return f"El chat con ID '{chat_id}' para el usuario '{usuario}' ya existe. No se ha guardado."

        # Insertar el nuevo chat en la colección
        chat.insert_one(documento)
        return f"El chat con ID '{chat_id}' para el usuario '{usuario}' se ha guardado correctamente."
    except Exception as e:
        return f"Error al guardar el chat: {str(e)}"

def borrar_chatDB(usuario, chat_id,AI):
    """
    Borra un chat guardado en MongoDB.

    Args:
        usuario (str): El nombre del usuario.
        chat_id (str): El identificador del chat a borrar.

    Returns:
        str: Mensaje indicando el resultado de la operación.
    """
    if AI=="U_History":
        chat=  db["Chats_U_History"]
    elif AI=="L_Proyectos":
        chat=db["Chats_L_Proyectos"]
    try:
        # Buscar y eliminar el chat correspondiente
        resultado = chat.delete_one({"usuario": usuario, "chat_id": chat_id})
        
        if resultado.deleted_count > 0:
            return f"El chat con ID '{chat_id}' del usuario '{usuario}' se ha eliminado correctamente."
        else:
            return f"No se encontró el chat con ID '{chat_id}' para el usuario '{usuario}'."
    except Exception as e:
        return f"Error al eliminar el chat: {str(e)}"

def guardar_historial_chatDB(historial, chat_id, usuario,AI):
    """
    Guarda o actualiza el historial de un chat en MongoDB.

    Args:
        historial (list): Lista de mensajes a guardar en el historial.
        chat_id (str): Identificador único del chat.
        usuario (str): Nombre del usuario propietario del chat.

    Returns:
        str: Mensaje indicando el resultado de la operación.
    """
    try:
        if AI=="U_History":
            chat=  db["Chats_U_History"]
        elif AI=="L_Proyectos":
            chat=db["Chats_L_Proyectos"]
        # Verificar si ya existe un chat con el mismo usuario y chat_id
        chat_existente = chat.find_one({"usuario": usuario, "chat_id": chat_id})

        if chat_existente:
            # Si el chat existe, agregar el nuevo historial al existente
            chat.update_one(
                {"usuario": usuario, "chat_id": chat_id},
                {"$push": {"contenido": {"$each": historial}}}  # Agregar nuevos mensajes
            )
            return f"El historial del chat con ID '{chat_id}' del usuario '{usuario}' se ha actualizado correctamente."
        else:
            # Si el chat no existe, crear uno nuevo
            nuevo_chat = {
                "usuario": usuario,
                "chat_id": chat_id,
                "contenido": historial  # Guardar la lista de mensajes
            }
            chat.insert_one(nuevo_chat)
            return f"El historial del chat con ID '{chat_id}' del usuario '{usuario}' se ha creado correctamente."
    except Exception as e:
        return f"Error al guardar el historial del chat: {str(e)}"
    


def guardar_presentacion_en_mongo(ruta_archivo, usuario,chat_id):
    fs = gridfs.GridFS(db, collection="docs_presentaciones")
    """
    Guarda la presentación PowerPoint en MongoDB usando GridFS.
    Args:
        ruta_archivo (str): Ruta del archivo PowerPoint local.
        usuario (str): Usuario que guarda la presentación.
    """
    with open(ruta_archivo, "rb") as archivo:
        archivo_id = fs.put(archivo, filename=ruta_archivo, usuario=usuario,chat_id=chat_id)
    if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
    return archivo_id


# Función para obtener y reconstruir un archivo desde GridFS
def obtener_archivo_gridfs(filename):
    try:
        # Buscar el archivo en la colección .files
        archivo_metadata = db["docs_presentaciones.files"].find_one({"filename": filename})

        if not archivo_metadata:
            print(f"No se encontró el archivo con el nombre '{filename}'.")
            return None, None

        # Recuperar el `_id` del archivo
        file_id = archivo_metadata["_id"]

        # Recuperar los fragmentos del archivo en orden (usando `files_id` como referencia)
        chunks = db["docs_presentaciones.chunks"].find({"files_id": file_id}).sort("n", 1)

        # Reconstruir el archivo concatenando los datos de cada fragmento
        archivo_reconstruido = b"".join(chunk["data"] for chunk in chunks)

        return archivo_reconstruido, archivo_metadata["filename"]

    except Exception as e:
        print(f"Error al recuperar el archivo: {e}")
        return None, None
    

def guardar_excel_en_mongo(ruta_archivo, usuario, chat_id):
    """
    Guarda un archivo Excel en MongoDB usando GridFS.
    Args:
        ruta_archivo (str): Ruta local del archivo Excel.
        usuario (str): Nombre del usuario que guarda el archivo.
        chat_id (str): ID del chat asociado.
    Returns:
        archivo_id (ObjectId): ID del archivo guardado en MongoDB.
    """
    fs = gridfs.GridFS(db, collection="docs_excel")  # Cambia el nombre de la colección
    try:
        with open(ruta_archivo, "rb") as archivo:
            archivo_id = fs.put(archivo, filename=ruta_archivo, usuario=usuario, chat_id=chat_id)
        print(f"Archivo {ruta_archivo} guardado en MongoDB con ID: {archivo_id}")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")
        archivo_id = None

    # Eliminar el archivo local después de subirlo
    if os.path.exists(ruta_archivo):
        os.remove(ruta_archivo)
        print(f"Archivo local eliminado: {ruta_archivo}")

    return archivo_id
def obtener_archivo_excel_gridfs(filename):
    """
    Obtiene un archivo Excel almacenado en MongoDB usando las colecciones `.files` y `.chunks`.
    Args:
        filename (str): Nombre del archivo a buscar en MongoDB.
    Returns:
        archivo_reconstruido (bytes): Contenido del archivo Excel en formato binario.
        filename (str): Nombre del archivo recuperado.
        None, None si el archivo no se encuentra o ocurre un error.
    """
    try:
        # Buscar el archivo en la colección `.files`
        archivo_metadata = db["docs_excel.files"].find_one({"filename": filename})

        if not archivo_metadata:
            print(f"No se encontró el archivo con el nombre '{filename}'.")
            return None, None

        # Recuperar el `_id` del archivo
        file_id = archivo_metadata["_id"]

        # Recuperar los fragmentos del archivo en orden (usando `files_id` como referencia)
        chunks = db["docs_excel.chunks"].find({"files_id": file_id}).sort("n", 1)

        # Reconstruir el archivo concatenando los datos de cada fragmento
        archivo_reconstruido = b"".join(chunk["data"] for chunk in chunks)

        return archivo_reconstruido, archivo_metadata["filename"]

    except Exception as e:
        print(f"Error al recuperar el archivo: {e}")
        return None, None
