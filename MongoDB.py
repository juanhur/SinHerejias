from pymongo import MongoClient
import os
import json
import gridfs
import pandas as pd
from datetime import datetime
from collections import defaultdict

import streamlit as st
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

def Obtener_Nombres_ChatDB(usuario,AI,area):
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
        documentos = chat.find({"usuario": usuario, "area":area}, {"chat_id": 1, "_id": 0}).sort("_id", -1) 
        # Extraer los nombres de los chat_id
        nombres_chats = [doc["chat_id"] for doc in documentos]
        # Agregar "nuevo_proyecto" al inicio de la lista como en el código original
        modelos = nombres_chats
        return modelos
    except Exception as e:
        print(f"Error al obtener los chat_id: {str(e)}")
        return ["nuevo_proyecto"]  # Devuelve solo "nuevo_proyecto" en caso de error


def guardar_nuevo_chatDB(usuario, chat_id, mensajes,AI,area):
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
            "area":area,
            "contenido": mensajes  # Almacena los mensajes del chat
        }
        
        # Verificar si ya existe un chat con el mismo usuario y chat_id
        if chat.find_one({"usuario": usuario, "chat_id": chat_id,"area":area}):
            return f"El chat con ID '{chat_id}' para el usuario '{usuario}' ya existe. No se ha guardado."

        # Insertar el nuevo chat en la colección
        chat.insert_one(documento)
        return f"El chat con ID '{chat_id}' para el usuario '{usuario}' se ha guardado correctamente."
    except Exception as e:
        return f"Error al guardar el chat: {str(e)}"

def borrar_chatDB(usuario, chat_id,AI,area):
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
        resultado = chat.delete_one({"usuario": usuario, "chat_id": chat_id,"area":area})
        
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
def  insertar_matriz_producto1(df,proyecto):

    # Conexión a MongoDB con autenticación
    db = client["AIProjects"]  # Base de datos
    collection = db["matriz_Pri"]  # Colección donde se guardarán los datos
    # Suponiendo que ya tienes un DataFrame llamado df
    data_dict = df.to_dict(orient="records")
    # Agregar el campo "campo": "an1" a cada elemento
    for i, item in enumerate(data_dict):  
        item["proyecto"] = proyecto  
        item["epica"] = df.index[i]

    # Insertar los datos en MongoDB
    collection.insert_many(data_dict)
    print("Datos de la matriz  guardados en MongoDB ")

def  insertar_matriz_producto(df,proyecto):
    db = client["AIProjects"]  # Base de datos
    collection = db["matriz_Pri"]  # Colección donde se guardarán los datos
    lista_orden,proyectos_ord=obtener_orden_matriz(proyecto)
    # Suponiendo que ya tienes un DataFrame llamado df
    data_dict = df.to_dict(orient="records")
        # Estructura para almacenar los datos organizados por proyecto
    proyectos_dict = {}

    for i, item in enumerate(data_dict):  # Identificador del proyecto
        epica_nombre = df.index[i]  # Nombre de la épica

        # Obtener el id_epica según la lista_orden
        id_epica = lista_orden.index(epica_nombre) + 1 if epica_nombre in lista_orden else None

        # Solo procesamos si la épica está en la lista_orden
        if id_epica is not None:
            # Removemos los campos innecesarios
            valores = {key: value for key, value in item.items() if key not in ["proyecto", "epica", "_id"]}

            # Si el proyecto aún no está en el diccionario, lo creamos
            if proyecto not in proyectos_dict:
                proyectos_dict[proyecto] = {
                    "proyecto": proyecto,
                    "epicas": []
                }

            # Transformamos las claves de valores a id_epica en lugar de nombres
            valores_transformados = []
            for nombre, valor in valores.items():
                id_epica_valor = lista_orden.index(nombre) + 1 if nombre in lista_orden else None
                if id_epica_valor is not None:
                    valores_transformados.append({"proyecto": proyecto,"id_epica": id_epica_valor, "valor": valor})

            # Agregar la épica a la lista de épicas del proyecto
            proyectos_dict[proyecto]["epicas"].append({
                "id_epica": id_epica,  # Se usa el índice de la lista como id_epica
                "valores": valores_transformados
            })

    # Convertir el diccionario en una lista de proyectos
    proyectos_list = list(proyectos_dict.values())

    # Insertar los datos en MongoDB
    collection.insert_many(proyectos_list)
    print("Datos de la matriz guardados en MongoDB")
def  insertar_matriz_producto_multi(df,proyectos):
    db = client["AIProjects"]  # Base de datos
    collection = db["matriz_Pri"]  # Colección donde se guardarán los datos
    #lista_orden,proyectos_ord=obtener_orden_matriz(proyecto)
    # Suponiendo que ya tienes un DataFrame llamado df
    # Suponiendo que tienes un DataFrame llamado df
    columnas_ordenadas = df.columns  # Guardamos el orden original de las columnas

    df_dict = {proyecto: df_proyecto[columnas_ordenadas] for proyecto, df_proyecto in df.groupby("proyecto")}
        # Estructura para almacenar los datos organizados por proyecto
    for proyecto in proyectos:
        #st.dataframe(df_dict[proyecto])
        data_dict = df_dict[proyecto].to_dict(orient="records")
        lista_orden,proyectos_ord=obtener_orden_matriz(proyecto)
        borrar_proyecto_matriz(proyecto)
        proyectos_dict = {}
        for i, item in enumerate(data_dict):  # Identificador del proyecto
            epica_nombre = df_dict[proyecto].index[i]  # Nombre de la épica
            id_epica = lista_orden.index(epica_nombre) + 1 if epica_nombre in lista_orden else None

            # Removemos los campos innecesarios
            valores = {key: value for key, value in item.items() if key not in ["proyecto", "epica", "_id"]}

            # Si el proyecto aún no está en el diccionario, lo creamos
            if proyecto not in proyectos_dict:
                proyectos_dict[proyecto] = {
                    "proyecto": proyecto,
                    "epicas": []
                }
            # Transformamos las claves de valores a id_epica en lugar de nombres
            valores_transformados = []
            for nombre, valor in valores.items():
                if valor is not None and not pd.isna(valor):  
                    proyecto1,id_epica=nombre.split("-EP")
                    valores_transformados.append({"proyecto": proyecto1,"id_epica":int( id_epica), "valor": valor})
            # Agregar la épica a la lista de épicas del proyecto
            proyectos_dict[proyecto]["epicas"].append({
                "id_epica": i+1,  # Se usa el índice de la lista como id_epica
                "valores": valores_transformados
            })

        # Convertir el diccionario en una lista de proyectos
        proyectos_list = list(proyectos_dict.values())
        print( proyectos_list)
        # Insertar los datos en MongoDB
        collection.insert_many(proyectos_list)
    print("Datos de la matriz guardados en MongoDB")

def  consultar_matriz_producto(area):
    db = client["AIProjects"]  # Base de datos
    collection = db["matriz_Pri"]  # Colección donde se guardarán los datos
    resultado = collection.find({"proyecto": {"$regex": area, "$options": "i"}})
    return resultado
def  consultar_matriz_producto_global(area,epicas_Proyecto,proyectos_seleccionados,epicas_proyecto_codigo,proyectos_ord):
        db = client["AIProjects"]
        collection = db["matriz_Pri"]
        # Consulta a MongoDB
        resultado = collection.find({"proyecto": {"$regex": area, "$options": "i"}})
        proyectos_unicos = []
        for valor in proyectos_ord:
            if valor not in proyectos_unicos:
                proyectos_unicos.append(valor)
        data = []
        resultado  = list(resultado)
# Ordenar los resultados según el orden en 'proyectos_unicos'
        resultado  = sorted(resultado , key=lambda doc: proyectos_unicos.index(doc['proyecto']) if doc['proyecto'] in proyectos_unicos else float('inf'))
        for doc in resultado:
            proyecto = doc["proyecto"]  # Nombre del proyecto
            if proyecto in proyectos_seleccionados:
                #lista_epicas=epicas_Proyecto[proyecto]
                for epica in sorted(doc.get("epicas", []), key=lambda x: x['id_epica']):
                    lista_epicas=epicas_Proyecto[proyecto]
                    fila = {
                        "proyecto": proyecto,
                        "id_epica": lista_epicas[epica["id_epica"]-1]
                    }
                    # Extraer los valores de cada épica y guardarlos en columnas dinámicas
                    for valor in sorted(epica.get("valores", []), key=lambda x: x['id_epica']):
                        #print(valor)
                        lista_epicas=epicas_Proyecto[valor["proyecto"]]
                        lista_epicas_C=epicas_proyecto_codigo[valor["proyecto"]]
                        #print(lista_epicas)
                        columna =lista_epicas_C[lista_epicas[valor['id_epica']-1]]
                        fila[columna] = valor["valor"]
                    
                    data.append(fila)

        # Crear DataFrame
        #print(data)
        df = pd.DataFrame(data)

        # Llenar valores faltantes con 0
        #df.fillna(0, inplace=True)
        return df


def actualizar_un_elemento_matriz(filtro,actualizacion):
    db = client["AIProjects"]  # Base de datos
    collection = db["matriz_Pri"]  # Colección donde se guardarán los datos
    collection.update_one(filtro, actualizacion, upsert=True)
def actualizar_un_elemento_matriz_n(index,dic,filtro):
    db = client["AIProjects"]  # Base de datos
    collection = db["matriz_Pri"]  # Colección donde se guardarán los datos
    # Actualización usando operadores posicionales
    actualizacion = {
        "$set": {
            "epicas.$[epica].valores.$[valor].valor": int(dic["valor"])  # Cambiar el valor
        }
    }

    # Filtros para los arrays anidados
    array_filters = [
        {"epica.id_epica": dic["id_epica"]},  # Filtra la epica correcta
        {"valor.proyecto":  dic["proyecto"]}  # Filtra dentro de valores
    ]
    print(actualizacion)
    resultado = collection.update_one(filtro, actualizacion, array_filters=array_filters)
    print(resultado)
    # Verificar si se actualizó correctamente
    if resultado.modified_count > 0:
        print("Valor actualizado correctamente.")
    else:
        print("No se encontró el documento para actualizar.")

def consultar_matriz_exis_proyecto(proyecto):
    db = client["AIProjects"]  # Base de datos
    collection = db["matriz_Pri"]  # Colección donde se guardarán los datos
    resultado=None
    # Buscar coincidencias que contengan la palabra "ant" (insensible a mayúsculas)
    resultado = collection.find_one({"proyecto": {"$regex": proyecto, "$options": "i"}})
    if resultado is not None:
        return True  # Retorna True si hay coincidencias, False si no
    else:
        return False
def consultar_matriz_exis_proyecto_nombre(proyecto):
    db = client["AIProjects"]  # Base de datos
    collection = db["cod_proyectos"]  # Colección donde se guardarán los datos
    resultado=None
    # Buscar coincidencias que contengan la palabra "ant" (insensible a mayúsculas)
    resultado = collection.find_one({"Nombre_proyecto": {"$regex": proyecto, "$options": "i"}})
    if resultado is not None:
        return True  # Retorna True si hay coincidencias, False si no
    else:
        return False

def agregar_info_pro(proyectos_array, epicas_agregar,nombre,nombre_proyecto,total_prioridad,df_prioridad):
    db = client["AIProjects"]  
    collection = db["cod_proyectos"]  
    # Crear DataFrame solo con las columnas necesarias
    df_filtered = pd.DataFrame({'Código Proyecto': proyectos_array, 'Nombre Épica': epicas_agregar})
    #st.dataframe(df_prioridad)
    # Extraer Año, Número de Proyecto y Número de Épica usando regex
    df_filtered[['Año', 'Número_Proyecto', 'Número_Épica']] = df_filtered['Código Proyecto'].str.extract(r'AN-(\d{4})-(\d+)-EP(\d+)')
    df_filtered["Proyecto"]=nombre_proyecto
    # Convertir a valores numéricos
    df_filtered[['Año', 'Número_Proyecto', 'Número_Épica']] = df_filtered[['Año', 'Número_Proyecto', 'Número_Épica']].apply(pd.to_numeric)
    df_filtered['Nombre Épica'] = epicas_agregar
    df_filtered['Nombre_proyecto'] = nombre
    df_filtered['Puntuacion_proyecto']=total_prioridad
    df_filtered = df_filtered.merge(df_prioridad, left_on='Nombre Épica', right_index=True, how='left').drop(columns=['Estimación de Esfuerzo', 'Prioridad(Valor)'], errors='ignore')

    #st.dataframe(df_filtered)
    # Convertir DataFrame a lista de diccionarios para MongoDB
    documents = df_filtered.to_dict(orient='records')

    # Insertar en MongoDB
    collection.insert_many(documents)

    print(f"Datos insertados en MongoDB correctamente. Nombre del Proyecto: {nombre_proyecto}")
def obtener_orden_matriz(area):
    print(area)
    db = client["AIProjects"]
    collection = db["cod_proyectos"]
    # Obtener los datos de la colección
    data = list(collection.find({"Proyecto": {"$regex": area, "$options": "i"}}))
# Crear DataFrame
    df = pd.DataFrame(data)
        # Asegurarse de que las columnas Año, Número_Proyecto y Número_Épica son numéricas para hacer el ordenamiento
    df['Año'] = pd.to_numeric(df['Año'])
    df['Número_Proyecto'] = pd.to_numeric(df['Número_Proyecto'])
    df['Número_Épica'] = pd.to_numeric(df['Número_Épica'])

    # Ordenar los datos: Primero por Año, luego por Número de Proyecto, y luego por Número de Épica
    df_sorted = df.sort_values(by=['Año', 'Número_Proyecto', 'Número_Épica'])

    # Obtener la lista de nombres de las épicas ordenada
    epicas_ordenadas = df_sorted['Nombre Épica'].tolist()
    # Imprimir la lista ordenada
    print("Epicas ordenadas:", epicas_ordenadas)
    return epicas_ordenadas, df_sorted['Proyecto']
def Obtener_area(NombreCompleto):
    db = client["AIProjects"]  # Base de datos
    collection = db["Usuario_Scrum_Area"]  # Colección donde se guardarán los datos
    resultado=None
    # Buscar coincidencias que contengan la palabra "ant" (insensible a mayúsculas)
    resultado = collection.find({"NombreCompleto": {"$regex": NombreCompleto, "$options": "i"}})
    return resultado
def obtener_ultimo_proyecto(area):
    print(area)
    db = client["AIProjects"]
    collection = db["cod_proyectos"]
    # Obtener los datos de la colección
    data = list(collection.find({"Proyecto": {"$regex": area, "$options": "i"}}))
    if data:
        año_actual = datetime.now().year
        # Filtrar la data para obtener solo los elementos del año actual
        data_filtrada = [item for item in data if item['Año'] == año_actual]

        # Obtener el último número de proyecto
        ultimo_numero_proyecto = max(item['Número_Proyecto'] for item in data_filtrada)
        ultimo_numero_proyecto=ultimo_numero_proyecto+1
        ultimo_numero_proyecto=f"{ultimo_numero_proyecto:04d}"
        return  año_actual,ultimo_numero_proyecto
    else:
        return datetime.now().year,"0001"
    

def obtener_proyectos(area):
    print(area)
    db = client["AIProjects"]
    collection = db["cod_proyectos"]
    # Obtener los datos de la colección
    data = list(collection.find({"Proyecto": {"$regex": area, "$options": "i"}}))
    return data
def borrar_proyecto_matriz(proyecto):
    db = client["AIProjects"]
    collection = db["matriz_Pri"]
    filtro = {"proyecto": proyecto}
    result = collection.delete_many(filtro)
    if result.deleted_count > 0:
            print("✅ proyecto eliminado correctamente de la codificacion..")
    else:
            print("⚠️ No se encontró el proyecto en la codificacion.")

def borrar_proyecto(proyecto):
    
    """
    Elimina un documento de la colección matriz_Pri basado en el proyecto y la épica.
    
    :param proyecto: El código del proyecto (Ej: "AN-2025-0002").
    :param epica: El nombre de la épica a eliminar.
    :return: Mensaje confirmando si se eliminó el documento.
    """
    db = client["AIProjects"]
    collection = db["cod_proyectos"]
    data = list(collection.find({"Proyecto": {"$regex": proyecto, "$options": "i"}}))
    proyectos_agrupados = defaultdict(lambda: {"Nombre_proyecto": "", "Proyecto": "", "Epicas": []})

    for item in data:
        clave_proyecto = item["Proyecto"]
        proyectos_agrupados[clave_proyecto]["Nombre_proyecto"] = item["Nombre_proyecto"]
        proyectos_agrupados[clave_proyecto]["Proyecto"] = clave_proyecto
        proyectos_agrupados[clave_proyecto]["Epicas"].append(item["Nombre Épica"])

    # Convertir a lista
    lista_final = list(proyectos_agrupados.values())
    try:
        filtro = {"Proyecto": proyecto}
        result = collection.delete_many(filtro)

        if result.deleted_count > 0:
            print("✅ proyecto eliminado correctamente de la codificacion..")
        else:
            print("⚠️ No se encontró el proyecto en la codificacion.")
    except Exception as e:
        print("❌ Error al eliminar proyecto")
    try:
        for pro in lista_final:
            borrar_epicas(pro["Epicas"])
    except Exception as e:
        print("❌ Error al eliminar las columnas del proyecto en la matriz")

    collection = db["matriz_Pri"]
    try:
        filtro = {"proyecto": proyecto}
        result = collection.delete_many(filtro)

        if result.deleted_count > 0:
            print("✅ proyecto eliminado correctamente de la matriz..")
        else:
            print("⚠️ No se encontró el proyecto en la matriz.")
    except Exception as e:
         print("❌ Error al eliminar proyecto")
    

def borrar_epicas(lista_epicas):
    """
    Elimina claves específicas dentro de todos los documentos de la colección.

    :param lista_epicas: Lista con los nombres de las épicas a eliminar.
    :return: Mensaje confirmando la cantidad de documentos actualizados.
    """
    collection = db["matriz_Pri"]
    try:
        count = 0  # Contador de documentos modificados
        for epica in lista_epicas:
            actualizacion = {"$unset": {epica: ""}}  # Eliminar la clave de la épica
            
            result = collection.update_many({}, actualizacion)  # Aplicar a todos los documentos
            count += result.modified_count  # Sumar documentos modificados
        
        if count > 0:
            return f"✅ {count} documento(s) actualizado(s), eliminando las claves indicadas."
        else:
            return f"⚠️ No se encontraron claves de épicas para eliminar."
    except Exception as e:
        return f"❌ Error al eliminar las claves: {e}"


def actualizar_nombre_proyecto(proyecto,nuevo):
    collection = db["cod_proyectos"]
    try:
        # Filtro: Documentos que tengan el proyecto especificado
        filtro = {"Proyecto": proyecto}

        # Operación de actualización
        actualizacion = {
            "$set": {
                "Nombre_proyecto": nuevo,
            }
        }

        # Ejecutar la actualización
        result = collection.update_many(filtro, actualizacion)

        print (f"✅ {result.modified_count} documento(s) actualizado(s)." if result.modified_count > 0 else "⚠️ No se encontraron documentos para actualizar.")
    
    except Exception as e:
        print( f"❌ Error al actualizar documentos: {e}")

def consultar_epicas_exis_proyecto(epicas):
    db = client["AIProjects"]  # Base de datos
    collection = db["cod_proyectos"]  # Colección donde se guardarán los datos
    resultado=None
    for epica in epicas:
        print(epica)
        # Buscar coincidencias que contengan la palabra "ant" (insensible a mayúsculas)
        resultado = collection.find_one({"Nombre Épica": {"$regex": epica, "$options": "i"}})
        if resultado is not None:
            return True,epica  # Retorna True si hay coincidencias, False si no
    return  False,None
def consultar_epicas_por_codigo_proyecto(codigos_proyecto):
    db = client["AIProjects"]  # Base de datos
    collection = db["cod_proyectos"]  # Colección donde se guardarán los datos
    epicas_validas = {}  # Lista para almacenar las épicas válidas

    for codigo_proyecto in codigos_proyecto:
        print(f"Consultando proyecto: {codigo_proyecto}")
        # Buscar las épicas asociadas a un Código Proyecto
        resultado = collection.find({"Proyecto": codigo_proyecto})
        
        for doc in resultado:
            # Añadir la épica asociada a la lista de épicas válidas
            epicas_validas.append(doc["Nombre Épica"])
    
    return epicas_validas
def extraer_epicas_por_codigo_proyecto(codigos_proyecto):
    db = client["AIProjects"]  # Base de datos
    collection = db["cod_proyectos"]  # Colección donde se guardarán los datos
    epicas_validas = {}  # Lista para almacenar las épicas válidas
    for codigo_proyecto in codigos_proyecto:
        epicas_P=[]
        print(f"Consultando proyecto: {codigo_proyecto}")
        # Buscar las épicas asociadas a un Código Proyecto
        resultado = collection.find({"Proyecto": codigo_proyecto})
        
        for doc in resultado:
            # Añadir la épica asociada a la lista de épicas válidas
            epicas_P.append(doc["Nombre Épica"])

        epicas_validas[codigo_proyecto]=epicas_P
    
    return epicas_validas
def extraer_codigo_epicas_por_codigo_proyecto(codigos_proyecto):
    db = client["AIProjects"]  # Base de datos
    collection = db["cod_proyectos"]  # Colección donde se guardarán los datos
    epicas_validas = {}  # Diccionario para almacenar las épicas válida

    for codigo_proyecto in codigos_proyecto:
        epicas_P = {}  # Diccionario para almacenar las épicas de un proyecto
        print(f"Consultando proyecto: {codigo_proyecto}")
        
        # Buscar las épicas asociadas a un Código Proyecto
        resultado = collection.find({"Proyecto": codigo_proyecto})
        
        for doc in resultado:
            # Añadir la épica al diccionario del proyecto
            epicas_P[doc["Nombre Épica"]] = doc["Código Proyecto"]
        epicas_P_ordenadas = dict(sorted(epicas_P.items(), key=lambda item: int(item[1].split('-')[-1].replace('EP', ''))))
    # Guardar las épicas ordenadas del proyecto en el diccionario final
        epicas_validas[codigo_proyecto] = epicas_P_ordenadas
        # Guardar las épicas del proyecto en el diccionario final
    return epicas_validas

def obtener_proyectos_puntuacion1(area):
    db = client["AIProjects"]  # Base de datos
    collection = db["cod_proyectos"]  # Colección donde se guardarán los datos
     # Obtener los proyectos que coincidan con el área dada (con una búsqueda insensible al caso)
    data = list(collection.find({"Proyecto": {"$regex": area, "$options": "i"}}))

    # Crear un diccionario para almacenar los proyectos con su puntuación única
    proyectos_unicos = {}

    for doc in data:
        proyecto = doc["Proyecto"]
        puntuacion = doc["Puntuacion_proyecto"]

        # Solo añadir el proyecto si aún no existe en el diccionario
        if proyecto not in proyectos_unicos:
            proyectos_unicos[proyecto] = puntuacion

    # Convertir a DataFrame
    df = pd.DataFrame(list(proyectos_unicos.items()), columns=["Proyecto", "Puntuacion"])
    suma_puntuacion = df['Puntuacion'].sum()

    # Convertir el DataFrame a diccionario
    df_dict = df.to_dict(orient="records")

    # Devolver tanto los proyectos como la suma
    return df_dict, suma_puntuacion
def obtener_proyectos_puntuacion(area,epicas):
    db = client["AIProjects"]  # Asegúrate de que el nombre de tu base de datos sea correcto
    collection = db["cod_proyectos"]  # Asegúrate de que el nombre de tu colección sea correcto
    # Crear una nueva matriz con el mismo orden de filas y columnas
    # Obtener proyectos de MongoDB
    proyectos = list(collection.find({"Proyecto": {"$regex": area, "$options": "i"}}))  # Esto puede ser ajustado si tienes un filtro específico
    #proyectos=proyectos.drop(columns=['_id'])
    # Iterar sobre los proyectos y calcular los valores de la nueva matriz
    for proyecto in proyectos:
        # Obtener Prioridad_x_Esfuerzo y Puntuacion_proyecto
        prioridad_x_esfuerzo = proyecto["Prioridad_x_Esfuerzo"]
        puntuacion_proyecto = proyecto["Puntuacion_proyecto"]
        
        # Calcular la suma de puntuaciones de todos los proyectos
    suma_puntuacion = sum(set(p["Puntuacion_proyecto"] for p in proyectos))

    # Crear una matriz vacía con los nombres de las épicas como filas y columnas
    df_matriz = pd.DataFrame(0.0, index=epicas, columns=epicas)
    proyectos=pd.DataFrame( proyectos)
    #st.dataframe(proyectos)
    # Iterar sobre las filas y columnas de la matriz para calcular los valores

    for fila in epicas:
        esfuerzo_fila = proyectos.loc[proyectos["Nombre Épica"] == fila, "Prioridad_x_Esfuerzo"].values[0]
        puntuacion_proyecto_fila = proyectos.loc[proyectos["Nombre Épica"] == fila, "Puntuacion_proyecto"].values[0]
        
        for columna in epicas:
            esfuerzo_columna = proyectos.loc[proyectos["Nombre Épica"] == columna, "Prioridad_x_Esfuerzo"].values[0]

            # Aplicar la fórmula dada
            if esfuerzo_columna != 0:  # Evitar divisiones por cero
                valor_celda = (esfuerzo_fila * puntuacion_proyecto_fila) / (esfuerzo_columna * suma_puntuacion)
                df_matriz.loc[fila, columna] = valor_celda
    # Crear una matriz vacía con los nombres de las épicas como filas y columnas
    df_matriz_nueva = pd.DataFrame(0.0, index=epicas, columns=epicas)
    proyectos = pd.DataFrame(proyectos)

    # Iterar sobre las filas y columnas de la matriz para calcular los valores
    for fila in epicas:
        esfuerzo_fila = proyectos.loc[proyectos["Nombre Épica"] == fila, "Prioridad_x_Esfuerzo"].values[0]
        puntuacion_proyecto_fila = proyectos.loc[proyectos["Nombre Épica"] == fila, "Puntuacion_proyecto"].values[0]
        
        for columna in epicas:
            esfuerzo_columna = proyectos.loc[proyectos["Nombre Épica"] == columna, "Prioridad_x_Esfuerzo"].values[0]

            # Aplicar la nueva fórmula, evitando divisiones por cero
            if esfuerzo_columna != 0 and puntuacion_proyecto_fila != 0:
                valor_celda = (esfuerzo_fila * esfuerzo_fila) / (esfuerzo_columna * puntuacion_proyecto_fila)
                df_matriz_nueva.loc[fila, columna] = valor_celda

    # Mostrar la nueva matriz
    #st.dataframe(df_matriz_nueva)
    # Mostrar el DataFrame resultado
    return df_matriz,df_matriz_nueva
def obtener_proyectos_puntuacion_codigo(area,cod_epicas,proyectos_ord):
    db = client["AIProjects"]  # Asegúrate de que el nombre de tu base de datos sea correcto
    collection = db["cod_proyectos"]  # Asegúrate de que el nombre de tu colección sea correcto
    # Crear una nueva matriz con el mismo orden de filas y columnas
    # Obtener proyectos de MongoDB
    proyectos = list(collection.find({"Proyecto": {"$regex": area, "$options": "i"}}))  # Esto puede ser ajustado si tienes un filtro específico
    #proyectos=proyectos.drop(columns=['_id'])
    # Iterar sobre los proyectos y calcular los valores de la nueva matriz
        # Calcular la suma de puntuaciones de todos los proyectos
    suma_puntuacion = sum(set(p["Puntuacion_proyecto"] for p in proyectos))
    proyectos_unicos = []
    cod_epicas_list=[]

    for valor in proyectos_ord:
        if valor not in proyectos_unicos:
            proyectos_unicos.append(valor)
    
    for a in proyectos_unicos:
        for u in list(cod_epicas.get(a).values()):
            cod_epicas_list.append(u)
    # Crear una matriz vacía con los nombres de las épicas como filas y columnas
    df_matriz = pd.DataFrame(0.0, index=cod_epicas_list, columns=cod_epicas_list)
    proyectos=pd.DataFrame( proyectos)
    # Iterar sobre las filas y columnas de la matriz para calcular los valores

    for fila in cod_epicas_list:
        esfuerzo_fila = proyectos.loc[proyectos["Código Proyecto"] == fila, "Prioridad_x_Esfuerzo"].values[0]
        puntuacion_proyecto_fila = proyectos.loc[proyectos["Código Proyecto"] == fila, "Puntuacion_proyecto"].values[0]
        
        for columna in cod_epicas_list:
            esfuerzo_columna = proyectos.loc[proyectos["Código Proyecto"] == columna, "Prioridad_x_Esfuerzo"].values[0]

            # Aplicar la fórmula dada
            if esfuerzo_columna != 0:  # Evitar divisiones por cero
                valor_celda = (esfuerzo_fila * puntuacion_proyecto_fila) / (esfuerzo_columna * suma_puntuacion)
                df_matriz.loc[fila, columna] = valor_celda
    # Crear una matriz vacía con los nombres de las épicas como filas y columnas
    df_matriz_nueva = pd.DataFrame(0.0, index=cod_epicas_list, columns=cod_epicas_list)
    proyectos = pd.DataFrame(proyectos)

    # Iterar sobre las filas y columnas de la matriz para calcular los valores
    for fila in cod_epicas_list:
        esfuerzo_fila = proyectos.loc[proyectos["Código Proyecto"] == fila, "Prioridad_x_Esfuerzo"].values[0]
        puntuacion_proyecto_fila = proyectos.loc[proyectos["Código Proyecto"] == fila, "Puntuacion_proyecto"].values[0]
        
        for columna in cod_epicas_list:
            esfuerzo_columna = proyectos.loc[proyectos["Código Proyecto"] == columna, "Prioridad_x_Esfuerzo"].values[0]

            # Aplicar la nueva fórmula, evitando divisiones por cero
            if esfuerzo_columna != 0 and puntuacion_proyecto_fila != 0:
                valor_celda = (esfuerzo_fila * esfuerzo_fila) / (esfuerzo_columna * puntuacion_proyecto_fila)
                df_matriz_nueva.loc[fila, columna] = valor_celda

    # Mostrar la nueva matriz
    #st.dataframe(df_matriz_nueva)
    # Mostrar el DataFrame resultado
    return df_matriz,df_matriz_nueva
    
def consultar_nombres_proyectos(codigos_proyecto):
    db = client["AIProjects"]  # Nombre de la base de datos
    collection = db["cod_proyectos"]  # Nombre de la colección

    nombres_proyectos = {}  # Diccionario para almacenar resultados

    for codigo in codigos_proyecto:
        resultado = collection.find_one({"Proyecto": codigo}, {"Nombre_proyecto": 1, "_id": 0})
        
        if resultado:  
            nombres_proyectos[codigo] = resultado["Nombre_proyecto"]
        else:
            nombres_proyectos[codigo] = None  # O podrías poner un string como "No encontrado"

    return nombres_proyectos