import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent,AgentExecutor, tool
import requests,os,json
from dotenv import load_dotenv, find_dotenv
from langchain_core.prompts import PromptTemplate
from Crear_pptx import Crear_Diapositiva
from MongoDB import Cargar_HistorialDB
import uuid
from datetime import datetime
from langchain_core.output_parsers import StrOutputParser
import streamlit as st

from typing import Optional
from langchain_core.utils.utils import secret_from_env
from pydantic import Field, SecretStr
_ = load_dotenv(find_dotenv())

openai_api_key = os.environ["OPENAI_API_KEY"]
class ChatOpenRouter(ChatOpenAI):
    openai_api_key: Optional[SecretStr] = Field(
        alias="api_key", default_factory=secret_from_env("OPENROUTER_API_KEY", default=None)
    )
    @property
    def lc_secrets(self) -> dict[str, str]:
        return {"openai_api_key": "OPENROUTER_API_KEY"}

    def __init__(self,
                 openai_api_key: Optional[str] = None,
                 **kwargs):
        openai_api_key = openai_api_key or os.environ.get("OPENROUTER_API_KEY")
        super().__init__(base_url="https://openrouter.ai/api/v1", openai_api_key=openai_api_key, **kwargs)



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
CELIA_PROMPT = PromptTemplate.from_template(
'''
Eres un experto en metodología Scrum, levantamiento de proyectos, y desarrollo de software. Tu objetivo es ayudar a elaborar un documento que estructure un proyecto con base en los conocimientos de estas áreas.

### Estructura del documento a generar:
1. Información General:
   - Nombre del Proyecto: Especifica el nombre del proyecto.
   - Encargado: Indica el nombre del Product Owner (persona responsable del proyecto).
   - Clúster / Área: Define el clúster Y el área al que pertenece el proyecto.

2. Detalles del Proyecto:
   - Objetivos: Describe los objetivos específicos que el proyecto pretende alcanzar.Usando metodologia SMART

3. Detalles Específicos:
   - Justificación: Explica la razón de ser del proyecto y su relevancia para la organización.
   - Riesgos y Consideraciones: Identifica al menos cuatro riesgos potenciales y las consideraciones clave para mitigar esos riesgos durante el desarrollo del proyecto.
   - Especificaciones: Detalla el alcance, los beneficios y los indicadores de éxito del proyecto:
      - a) Alcance: Define el alcance medible del proyecto.
      - b) Beneficios: Identifica al menos tres beneficios que se obtendrán al implementar el proyecto.
      - c) Indicadores de Éxito: Especifica al menos tres indicadores que se usarán para evaluar el éxito del proyecto.
   - Cronograma de Ejecución: Genera un cronograma tentativo basado en metodología Scrum, considerando un equipo compuesto por personal junior y semi-senior.Ademas de espesificar cuantos meses segun tu criterio duraria ,los meses empezando desde el actual y en cantidad de horas.trabajando cada persona 6horas diarias.ejemplo:
         Duración total: 6 meses
         Horas totales: 720 horas (considerando 6 horas diarias por 20 días al mes) 
         meses:Enero,febrero,marzo,abril,mayo,Junio
         Estructura del equipo:
            - 1 Product Owner (Juan Hurtado)
            - 1 Scrum Master
            - 2 Developers Junior
            - 1 Developer Semi-Senior
        Scrum Sprints: 1 semanas por sprint, con revisiones al final de cada sprint para evaluar el avance. 

    
4. Recursos:
   - Describe los recursos tecnológicos, humanos(Produc Owner, Scrum Master, Developers,etc) y financieros necesarios para ejecutar el proyecto.

### Pasos para desarrollar esta tarea:
1. Interactúa con el usuario para recopilar toda la información necesaria para completar las secciones de "Información General" y "Detalles del Proyecto".
   - Haz preguntas claras y específicas para asegurarte de obtener toda la información requerida.
   -la seccion de Detalles Específicos debes completar mediante tus conocimientos y los objetivos dados por el usuario.
2. Con la información proporcionada por el usuario, desarrolla cada punto del documento siguiendo la estructura indicada.
3. **Comparte con el usuario tu  propuesta preliminar y ** pregunta si desea realizar  algun ajustes, realiza las correcciones necesarias.
4. **solicita  al usario su confirmacion para generar el documento** Unicamente Si el usuario aprueba, genera el documento utilizando la herramienta de creación de PowerPoint.
    - **Formato:** Asegúrate de incluir saltos de línea (`\n\n`) y **negritas**  y el formato en los inputs de las funciones para mayor legibilidad.

### Pautas adicionales:
 -**Secuencia Obligatoria:** No avances a un siguiente paso sin haber completado y confirmado el anterior.
- **Uso de Herramientas:** Solo utiliza la herramienta de Docs cuando el usuario lo apruebe explícitamente.
- Piensa antes de actuar: Siempre analiza qué información falta o qué herramienta es necesaria antes de avanzar.
- No uses herramientas si no son necesarias: Solo utiliza la herramienta de PowerPoint al recibir la aprobación del usuario.
- Agente interactivo: Guía al usuario de manera clara y estructurada para que la colaboración sea eficiente y productiva.
 **Formato:** Asegúrate de incluir saltos de línea (`\n\n`) y **negritas**   y el formato en los inputs de las funciones para mayor legibilidad.
-Si ejecutas la tool 'Docs' y recives como resultado un mensaje parecido a "El documento se ha creado y  guardado como" ,la tool  se ejecuto correctamente no necesitas volver a iterar.Devuelve el mensaje exactamente igual al que te devolvio la tool.
-Siempre que el usuario aprueba algo, verifica que es lo que esta aprobando.

**Cuando se consulte por el nombre de algun  archivo(documento) siempre devuelve el nombre completo(nombre y extension del archivo).**
Thought:you should always think about what to do, do not use any tool if it is not needed. 
 {agent_scratchpad}

Historial del chat:
{historial}
fecha_actual:{fecha_actual}
chat_name: {chat_name}
usuario:{usuario}
 User Input: {input} 

   '''
    )
LAST_PROMPT=PromptTemplate.from_template('''
Si el usuario pide generar el documento,Identifica  del contexto ,el ultimo archivo creado  pptx y guardado.  devuelveme    el nombre del archivo(no omitas la extension).
#Ejemplos de resupesta#:
- El documento se ha creado y  guardado como: presentacion_nuevo_proyecto_0a6320d9.pptx
- El documento se ha creado y  guardado como: carroIA_guar_2a55r0df.pptx
 New input user: {input} 

<<BEGIN CONTEXT>>
{historial}                                  

**Begin!**
        ''')

from pydantic import BaseModel, Field
from typing import List, Dict

# Paso 1: Crear el modelo de entrada para los textos
class NuevosTextosInput(BaseModel):
    NOMBRE_PROYECTO_IA: str = Field(..., description="Nombre del proyecto de IA ,incluye  marcas de salto de linea\n\n y negritas  respectivas.")
    JUSTIFICACION_IA: str = Field(..., description="Justificación del proyecto,incluye  marcas de salto de linea\n\n y negritas   respectivas.")
    OBJETIVOS_IA: str = Field(..., description="objetivos del proyecto,incluye  marcas de salto de linea\n\n y negritas   respectivas.")
    RIESGOS_IA: str = Field(..., description="Posibles riesgos del proyecto,incluye  marcas de salto de linea\n\n y negritas  respectivas.")
    CLUSTER_IA: str = Field(..., description="Cluster  y Area ,incluye  marcas de salto de linea\n\n y negritas respectivas. ")
    PRODUCT_OWNER_IA: str = Field(..., description="Nombre del Product Owner")
    ESPECIFICACIONES_IA: str = Field(..., description="Especificaciones del proyecto,incluye  marcas de salto de linea\n\n y negritas  respectivas.")
    RECURSOS_IA: str = Field(..., description="Recursos necesarios para el proyecto,incluye  marcas de salto de linea\n\n y negritas  respectivas.")
    CRONOGRAMA_IA: str = Field(..., description="Cronograma del proyecto,incluye  marcas de salto de linea\n\n y negritas   respectivas.")
    usuario: str = Field(..., description="Nombre del usuario")
    chat_name: str = Field(..., description="chat_name(nombre del chat)")



# Paso 2: Crear la función para generar los nuevos textos
@tool
def Doc(input_data: NuevosTextosInput) ->  str:
    '''Funcion que permite generar la documentacion en PowerPoint del proyecto y la almacena dicha docuemntacion en la carpeta espesifica '''
    nuevos_textos = [
        {
            "NOMBRE_PROYECTO_IA": input_data.NOMBRE_PROYECTO_IA,
            "JUSTIFICACION_IA": input_data.JUSTIFICACION_IA,
            "RIESGOS_IA": input_data.RIESGOS_IA,
            "CLUSTER_IA": input_data.CLUSTER_IA,
            "PRODUCT_OWNER_IA": input_data.PRODUCT_OWNER_IA,
            "ESPECIFICACIONES_IA": input_data.ESPECIFICACIONES_IA,
            "RECURSOS_IA": input_data.RECURSOS_IA,
            "CRONOGRAMA_IA": input_data.CRONOGRAMA_IA,
            "OBJETIVOS_IA": input_data.OBJETIVOS_IA,
        }
    ]
    chat_name=input_data.chat_name
    chat_name = chat_name.replace("/", "__")
    usuario=input_data.usuario
    id_unico_corto = str(uuid.uuid4())[:8]
    print( nuevos_textos)
    
    nombre_doc=  "presentacion_"+chat_name+"_"+id_unico_corto+'.pptx'
    ruta_documento=Crear_Diapositiva( nuevos_textos,  nombre_doc,usuario,chat_name,st.session_state.area)
    val=1
    return f"El documento se ha creado y  guardado como: {ruta_documento}"
   
def Cambio():
       st.session_state.val_L = "Si, genera el documento"
# Initialize agent and executor
llm=ChatOpenRouter(model_name="openai/gpt-4o-mini", temperature=0.7)
llm2=ChatOpenRouter(model_name="openai/gpt-4o-mini", temperature=0.2)
#llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
#llm2 = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
tools = [Doc]
agent = create_tool_calling_agent(llm, tools, CELIA_PROMPT)
agent_executor = AgentExecutor(agent=agent, tools=tools, max_iterations=1,early_stopping_method='generate', verbose=True)

def Agente_AI_local(input: str, chat:str,ruta:str,historial:list):
        if chat =="nuevo_proyecto":
            chat_history = historial
        else:
            chat_history=Cargar_Historial(chat,ruta)
        print(chat_history)
        response = agent_executor.invoke(
            {"input": input,"historial":chat_history},
        )
        return(response['output'])
def Agente_AI(input: str, chat:str,historial:str,user:str):
        if chat =="nuevo_chat":
                    chat_history = historial
        else:
            chat_history=Cargar_HistorialDB(user,chat,"L_Proyectos")
             # Obtener la fecha actual
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        response = agent_executor.invoke(
            {"input": input,"historial":chat_history,"chat_name":chat,"usuario":user,"fecha_actual":fecha_actual}
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

