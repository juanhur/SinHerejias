import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent,AgentExecutor, tool
import requests,os,json
from dotenv import load_dotenv, find_dotenv
from langchain_core.prompts import PromptTemplate
from Crear_Excel import generar_excel
from MongoDB import Cargar_HistorialDB,guardar_excel_en_mongo
import uuid
from langchain_core.output_parsers import StrOutputParser

_ = load_dotenv(find_dotenv())
openai_api_key = os.environ["OPENAI_API_KEY"]
def Cargar_Historial(session_Id,ruta):
    ruta_archivo=f"chats{ruta}{session_Id}.json"
        # Cargar el historial desde el archivo JSON
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            historial = json.load(archivo)  # Cargar el historial en la variable
            print("Historial cargado correctamente:")
            print(ruta_archivo)
            print(historial)
    except FileNotFoundError:
        print(f"No se encontró el archivo: {ruta_archivo}")
        historial = []  # Si no se encuentra, inicializar un historial vacío
    except json.JSONDecodeError:
        print("Error al decodificar el archivo JSON. Verifica su formato.")
        historial = []
    return historial
USER_HIS_PROMPT = PromptTemplate.from_template(
'''
 Eres un experto en metodología Scrum, levantamiento de proyectos, y desarrollo de software. Considerate como un experto en la redacción de historias de usuario. Tu objetivo es ayudar a realizar un documento excel sobre  historias de usuario de un proyecto.Tomando en cuenta cada paso.

### Estructura del documento a generar:
1. columna "Codigo Épica":
    codificacion unica por cada epica,el formato es:AN-2024-0001-EP1(numero de epica)(cada historia de usuario  esta relacionada a este codigo de epica)
2.columna "EPICA":
   Una épica es un gran bloque de trabajo dentro de un proyecto ágil que representa una funcionalidad importante o un objetivo clave. Se utiliza para organizar y estructurar tareas complejas que no pueden ser completadas en un solo sprint.
3.columna" Código de la Historia":
    codificacion unica de la historia de usuario  relacionada a la epica correspondiente,el formato es: AN-2024-0001-EP1-HU1 donde:  EP1 (numero de epica) y HU1(numero de historia de usuario)
4.columna  "Descricion de la Historia":
    La narrativa en formato estándar   Formato: "Como [rol], quiero [acción], para [resultado/beneficio].	
5.columna "Criterios de Aceptación":
    Las condiciones que deben cumplirse para que la historia se considere completada y aceptada.	
6.columna "Prioridad": 
    usando meotdologia Moscow que  clasifica cada historia según su importancia:
    a)Must Have: Requisitos esenciales.
    b)Should Have: Importantes pero no críticas.
    c)Could Have: Deseables pero no prioritarias.
    d)Won't Have: Excluidas en este ciclo."	"Planning Poker es una técnica colaborativa y efectiva que fomenta la discusión del esfuerzo requerido. Cómo funciona:

7.columna"Estimacion de Esfuerzo":
    La secuencia de Fibonacci es una serie de números donde cada número es la suma de los dos anteriores: 
    1: Esfuerzo muy bajo.
    2: Esfuerzo bajo.
    3: Esfuerzo moderado.
    5: Esfuerzo considerable.
    8: Esfuerzo alto.
    13: Esfuerzo muy alto.
    21: Esfuerzo extremadamente alto (evítalo para historias de usuario, dividirlas primero)."
8.columna"Resposable":
  La persona o equipo asignado para trabajar en la historia: (Cargo ) existen:
    a)Stakeholder o Cliente Product Owner
    b)Scrum Master
    c)DevOps
    d)Arquitecto
    f)Full Stack
    g)Back End
    h)Fron End /Web
    i)Fron End /App
    j)Ingeniero Datos
    k)Visualizar Datos
    m)Web Master
    n)IA
    o)ML
    p)UI/IX
    q)QA
9.columna"Estado":
    todo valor en esta columna es "Nuevo".



### Pasos para desarrollar esta tarea:
1. Recopilación de Épicas:
   - Interactúa con el usuario para recopilar toda la información necesaria sobre las épicas existentes.
   - Realiza preguntas claras, específicas y guiadas para asegurarte de identificar todas las épicas relevantes.
   - Confirma con el usuario que no faltan más épicas antes de continuar y brindale la codificacion de las mismas.

2. Sugerencia de Historias de Usuario:
   - Para cada épica proporcionada, utiliza tus conocimientos y comprensión para sugerir historias de usuario relevantes, en base a las siguientes 7 Dimensiones:
    •	Usuario
    •	Interfaz
    •	Acciones
    •	Datos
    •	Control
    •	Calidad
    •	Ambiente

   - Presenta tus sugerencias al usuario con la respectiva codificacion y solicita su confirmación.
   - Si el usuario no está conforme , interactúa con él para ajustar las historias de usuario según sus necesidades y sugerencias.

3. Definición de Criterios de Aceptación:
   - Con base en las historias de usuario aprobadas, propone criterios de aceptación para cada una de ellas.
   - Comparte estos criterios con el usuario y solicita su retroalimentación.
   - Si es necesario, ajusta los criterios de aceptación en función de sus comentarios.

4. Prioridad, Estimación de Esfuerzo y Responsable:
   - Sugiere la "Prioridad", "Estimación de Esfuerzo" y el "Responsable" para cada historia de usuario.
   - Solicita la validación del usuario sobre estas propuestas.
   - Realiza ajustes si el usuario no está conforme o propone cambios.

5. **Validación Final de la Información:**
   - Antes de continuar, verifica que toda la información necesaria (épicas, historias de usuario, criterios de aceptación, prioridad, esfuerzo, responsables y estado) esté completa.
   - Si falta algún dato, solicita al usuario que lo proporcione.

6. **Propuesta Preliminar**:
   - *Comparte con el usuario una versión preliminar de la propuesta(una tabla en formato Markdown), incluyendo todos los datos recopilados y estructurados .*
   - Pregunta al usuario: "¿Deseas que genere el documento en formato Excel?" y espera su aprobación.

7. Generación del Documento:
Antes de generar el documento en formato Excel, sigue estos pasos para garantizar que toda la información se conserve correctamente:
    a)Verificación previa de aprobación:
        -Confirma si el usuario aprobó explícitamente la propuesta preliminar en interacciones anteriores.
        -Si no hay evidencia de aprobación previa, solicita confirmación al usuario antes de continuar.
    b)Extracción completa de datos:
        -Identifica la tabla  Markdown proporcionada en la etapa de Propuesta Preliminar.
        -Asegúrate de que todas las columnas de la tabla estén presentes y correctamente etiquetadas.
        -Extracción de datos por columna: extrae la información correspondiente  de la tabla Markdown y asegúrate de que los datos sean completos.
        -Mapea las columnas extraídas a los campos de la tool:
            *codigo_epica → Columna correspondiente a los códigos de épica.
           *epica → Columna correspondiente a las épicas.
            *codigo_historia → Columna correspondiente a los códigos de historia.
            *descripcion_historia → Columna correspondiente a las descripciones de historia.
            *criterios_aceptacion → Columna correspondiente a los criterios de aceptación.
            *prioridad → Columna correspondiente a la prioridad de las historias.
            *estimacion_esfuerzo → Columna correspondiente a la estimación de esfuerzo (asegúrate de que sean números enteros).
            *responsable → Columna correspondiente a los responsables.

    c)Validación de consistencia:
        -Revisa que la cantidad de entradas en cada columna coincida exactamente con el total de filas de la propuesta preliminar.
    d)Generación del documento:
        -Una vez completados los pasos anteriores, genera el documento en formato Excel, asegurándote de que ninguna fila o dato se pierda durante la exportación.


### Pautas adicionales:
-limitate a responder solo temas relacionados al proyecto y que sirvan a la realizacion de este documento.
- Piensa antes de actuar: Siempre analiza qué información falta o qué herramienta es necesaria antes de avanzar.
- No uses herramientas si no son necesarias: Solo utiliza la herramienta de Excel al recibir la aprobación de la propuesta preliminar.
- Agente interactivo: Guía al usuario de manera clara y estructurada para que la colaboración sea eficiente y productiva.
-Si ejecutas la tool 'DOCs' y recives como resultado un mensaje parecido a "El documento se ha creado y  guardado como:" ,la tool  se ejecuto correctamente no necesitas volver a iterar.Devuelve el mensaje exactamente igual al que te devolvio la tool(no omitas la extension del documento)
-*la tool 'DOCs' solo se puede utilizar una vez durante la 'Chain of Thought'.
###IMPORTANTE:
-"Antes de generar el documento, verifica: '¿Has aprobado la propuesta preliminar?' Si la respuesta es afirmativa, procede a crear el documento. Si no, ajusta la propuesta y vuelve a pedir confirmacion."
-*No generes el documento hasta que hayas mostrado tu propuesta preliminar y el usuario haya aprobado la propuesta.*

##Cuando se consulte por el nombre de algun  archivo(documento) siempre devuelve el nombre completo(nombre y extension del archivo).##
Thought:you should always think about what to do, do not use any tool if it is not needed. 

 {agent_scratchpad}

Historial del chat:
{historial}
chat_name:{chat_name}
usuario:{usuario}
 User Input: {input} 

   '''
    )

LAST_PROMPT=PromptTemplate.from_template('''
Si el usuario pide generar el documento,Identifica  del contexto ,el ultimo archivo(xlxs) creado  y guardado.  devuelveme  el nombre(no omitas la extension)

 New input user: {input} 

<<BEGIN CONTEXT>>
{historial}                                  

**Begin!**
        ''')

from pydantic import BaseModel, Field
from typing import List

# Paso 1: Crear el modelo de entrada para los datos
class HistoriasUsuarioInput(BaseModel):
    usuario: str = Field(..., description="Nombre del usuario")
    chat_name: str = Field(..., description="Nombre del chat(chat_name)")
    codigo_epica: List[str] = Field(..., description="Lista de códigos de épica. Debe ser igual al numero de historias de usario que existen.")
    epica: List[str] = Field(..., description="Lista de las épicas correspondientes.")
    codigo_historia: List[str] = Field(..., description="Lista de los códigos de las historias.")
    descripcion_historia: List[str] = Field(..., description="Lista de descripciones de las historias.")
    criterios_aceptacion: List[str] = Field(..., description="Lista de criterios de aceptación.")
    prioridad: List[str] = Field(..., description="Lista de prioridades.")
    estimacion_esfuerzo: List[int] = Field(..., description="Lista de estimaciones de esfuerzo.")
    responsable: List[str] = Field(..., description="Lista de responsables.")

@tool
def DOCs(input_data: HistoriasUsuarioInput, nombre_archivo: str) -> str:
    '''Funcion que permite generar la documentacion en Excel del proyecto ,la  funcion devuelve el nombre y extension del documento creado.'''
    random = str(uuid.uuid4())[:8]
    usuario=input_data.usuario
    chat_id=input_data.chat_name
    if ".xlsx" in nombre_archivo:
        # Elimina ".xlsx" del texto
        nombre_archivo= nombre_archivo.replace(".xlsx", "")
    nombre_archivo=nombre_archivo+"_"+random
    archivo=generar_excel(
        input_data.codigo_epica,
        input_data.epica,
        input_data.codigo_historia,
        input_data.descripcion_historia,
        input_data.criterios_aceptacion,
        input_data.prioridad,
        input_data.estimacion_esfuerzo,
        input_data.responsable,
        nombre_archivo
    )

    #nombre_archivo=nombre_archivo+".xlsx"
    guardar_excel_en_mongo(archivo, usuario, chat_id)
    return f"El documento se ha creado y  guardado como:{archivo}"
    

# Initialize agent and executor
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5,timeout=120)
tools = [DOCs]
agent = create_tool_calling_agent(llm, tools, USER_HIS_PROMPT)

llm2 = ChatOpenAI(model="gpt-4o-mini", temperature=0.2,timeout=120)#timeout=30  # Tiempo de espera en segundos
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, max_iterations=1,early_stopping_method='generate', verbose=True)
def Agente_UH_AI_local(input: str, chat:str,ruta:str,historial:str):
        if chat =="nuevo_chat":
            chat_history = historial
        else:
            chat_history=Cargar_Historial(chat,ruta)
        response = agent_executor.invoke(
            {"input": input,"historial":chat_history},
        )
        return(response['output'])

def Agente_UH_AI(input: str, chat:str,historial:str,user:str):
        if chat =="nuevo_chat":
            chat_history = historial
        else:
            chat_history=Cargar_HistorialDB(user,chat,"U_History")
        response = agent_executor.invoke(
            {"input": input,"historial":chat_history,"chat_name":chat,"usuario":user},
        )
        if "intermediate_steps" in response:
            print("No se obtuvo respuesta en las iteraciones; se intentará una última vez.")
            secondary_response = LAST_PROMPT | llm2 | StrOutputParser()
            final_output = secondary_response.invoke(
                {"input": response["input"], "historial": response["intermediate_steps"]},
            )
            print(final_output)
            return(final_output)
        return(response['output'])
