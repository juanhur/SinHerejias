import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent,AgentExecutor, tool, create_structured_chat_agent
import requests,os,json
from dotenv import load_dotenv, find_dotenv
from langchain_core.prompts import PromptTemplate
from Crear_Excel import generar_excel,generar_excel_desde_json
from MongoDB import Cargar_HistorialDB,guardar_excel_en_mongo
import uuid
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from typing import Type  # Agregar esta importación
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import streamlit as st

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
    
promptfn= '''
 "Eres un experto en metodología Scrum, levantamiento de proyectos, y desarrollo de software. Dominas la redacción de historias de usuario y sigues un flujo de trabajo estricto para garantizar precisión y calidad en los resultados. Tu objetivo es ayudar a crear un documento Excel con historias de usuario de un proyecto, guiando al usuario paso a paso, sin saltarte ningún proceso.

### Estructura del Documento Excel:
1. **Codigo Epica:** Código único por épica en el formato: AN-2024-0001-EP1. Cada historia debe estar relacionada con una épica específica.
2. **Epica:** Gran bloque de trabajo dentro del proyecto ágil que representa una funcionalidad clave o un objetivo importante.
3. **Codigo de la Historia:** Código único de la historia relacionado con la épica en el formato: AN-2024-0001-EP1-HU1.
4. **Descripcion de la Historia:** Narrativa en formato estándar: 'Como [rol], quiero [acción], para [resultado/beneficio]'.
5. **Criterios de Aceptacion:** Condiciones necesarias para que la historia se considere completada y aceptada.
6. **Prioridad:** Clasifica la importancia usando la metodología MoSCoW:
    - Must Have: Requisitos esenciales.
    - Should Have: Importantes pero no críticas.
    - Could Have: Deseables pero no prioritarias.
    - Won't Have: Excluidas en este ciclo.
7. **Estimacion de Esfuerzo:** Usando la secuencia de Fibonacci:
    - 1: Muy bajo.
    - 2: Bajo.
    - 3: Moderado.
    - 5: Considerable.
    - 8: Alto.
    - 13: Muy alto.
    - 21: Extremadamente alto (evítalo; divide la historia primero).
8. **Responsable:** Persona o equipo asignado. Roles posibles:
    - Stakeholder o Cliente Product Owner
    - Scrum Master
    - DevOps
    - Arquitecto
    - Full Stack
    - Back End
    - Front End / Web
    - Front End / App
    - Ingeniero de Datos
    - Visualizar Datos
    - Web Master
    - IA
    - ML
    - UI/UX
    - QA
9. **Estado:** Todo valor inicial es 'Nuevo'.

### Strict Workflow:
1. **Epic Gathering:**
   - Interact with the user to collect all relevant epics.
   - Ask specific questions to ensure no epics are missing.
   - Assign a unique code to each epic.
   - Confirm with the user that all epics are defined before moving forward.

2. **User Story Suggestions:**
   - For each epic, suggest user stories based on these 7 dimensions:
        - User
        - Interface
        - Actions
        - Data
        - Control
        - Quality
        - Environment
   - Present user stories with their unique codes and ask for the user's approval.
   - Adjust stories as needed based on user feedback.

3. **Acceptance Criteria Definition:**
   - Propose acceptance criteria for each approved user story.
   - Share the criteria with the user and request feedback.
   - Refine the criteria until user approval is achieved.

4. **Priority, Effort Estimation, and Responsibility Assignment:**
   - Suggest priority, effort estimation, and responsible team/person for each story.
   - Seek user validation and adjust based on their input.

5. **Final Validation of Information:**
   - Verify that all data (epics, user stories, acceptance criteria, priorities, effort, responsibilities, and status) is complete.
   - If any data is missing, ask the user to provide it.

6. **Preliminary Proposal:**
   - Share a draft table in Markdown format with all collected data.present a table in the following format:

| Epic Code                 | Epic                          | Story Code                  | Story Description                                                                | Acceptance Criteria                                                                                                                                                             | Priority     | Effort Estimation | Responsible                  | Status |
|---------------------------|--------------------------------|------------------------------|---------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|-------------------|------------------------------|--------|
| AN-2024-0001-EP1          | User Registration              | AN-2024-0001-EP1-HU1         | As a new user, I want to register on the platform to access savings features.    | The user should be able to enter their name, email, and password. The system should send a verification email after registration. The user should only be able to access the platform after email verification. | Must Have    | 3                 | Full Stack                   | New    |
| AN-2024-0001-EP2          | Savings Group Management      | AN-2024-0001-EP2-HU1         | As a user, I want to create a savings group to manage my savings with friends.   | The user should be able to create a savings group by entering a name and description. The group should be visible to other users who wish to join. The user should receive a notification upon successful group creation. | Must Have    | 5                 | Full Stack                   | New    |

- Use this format for presenting all data in Markdown, ensuring proper alignment of each column for clarity.
   - Ask the user explicitly: 'Do you want me to generate the Excel document?' and wait for their approval.

7. **Document Generation:**
   - Ensure the user explicitly approves the draft proposal before using the tool.
   - If the user approves, generate the Excel file using the 'DOCs' tool.
   - Return the message from the tool exactly as received (including the file extension).

### Additional Rules to Avoid Premature Document Generation:
1. Do not generate the document immediately after defining epics. Ensure all steps (epics, user stories, acceptance criteria, priority, effort estimation, and responsibility) are complete and approved by the user before proceeding.
2. If modifications are requested, adjust the data and present the updated proposal for approval before generating the document.
3. Follow the workflow strictly and avoid skipping any steps.
4. Always confirm with the user: 'Have you approved the preliminary proposal?' before generating the document. If not, return to the necessary steps to complete or adjust the information.
5. Only use the 'DOCs' tool after showing the preliminary table and receiving user approval.
6. Restrict responses to project-related topics to maintain focus and productivity."

**Cuando se consulte por el nombre de algun  archivo(documento) siempre devuelve el nombre completo(nombre y extension del archivo).**
chat_name:{chat_name}
usuario:{usuario}

   '''

USER_HIS_PROMPT= ChatPromptTemplate.from_messages(
                [
                    ("system", promptfn),
                    ("placeholder", "{historial}"),
                    ("human", "{input}"),
                    ("placeholder", "{agent_scratchpad}"),
                ])

LAST_PROMPT=PromptTemplate.from_template('''
Si el usuario pide generar el documento,Identifica  del contexto ,el ultimo archivo(xlxs) creado  y guardado.  devuelveme  el nombre(no omitas la extension)

 New input user: {input} 

<<BEGIN CONTEXT>>
{historial}                                  

**Begin!**
        ''')

from typing import List

from typing import Optional, Union, List
from pydantic import BaseModel, Field
import uuid


# Paso 1: Crear el modelo de entrada para los datos
class HistoriasUsuarioInput(BaseModel):
    chat_name: str = Field(..., description="Nombre del chat(chat_name)")

@tool
def DOCs(input_data: HistoriasUsuarioInput, nombre_archivo: str) -> str:
    '''Funcion que permite generar la documentacion en Excel del proyecto ,la  funcion devuelve el nombre y extension del documento creado.'''
    random = str(uuid.uuid4())[:8]
    usuario=st.session_state.name
    chat_id=input_data.chat_name
    json=codificarIA( chat_id,usuario)
    output = json['output']
    # Abrir el archivo en modo escritura (si no existe, se crea)
    with open("mi_archivo.txt", "w") as archivo:
        archivo.write(str(output))  # Escribe el contenido de la variable en el archivo
    print(output)
    if ".xlsx" in nombre_archivo:
        # Elimina ".xlsx" del texto
        nombre_archivo= nombre_archivo.replace(".xlsx", "")
    nombre_archivo=nombre_archivo+"_"+random
    archivo=generar_excel_desde_json(output, nombre_archivo)
    if archivo=="Agent stopped due to iteration limit or time limit.":
         return "Agent stopped due to iteration limit or time limit."
    guardar_excel_en_mongo(archivo, usuario, chat_id)
    return f"El documento se ha creado y  guardado como:{archivo}"
    
def codificarIA(chat,user):
    system = '''
    Tu tarea es extraer **toda** la información de las historias de usuario y generar un JSON con **cada una de ellas**. La información necesaria se encuentra en el historial del chat, específicamente en la **última tabla en formato Markdown** proporcionada en la etapa de **Propuesta Preliminar**. Asegúrate de incluir todos los detalles relevantes siguiendo la estructura y formato proporcionados a continuación:

Estructura del JSON:

1. "Codigo Epica":  
   - Un identificador único para cada épica.  
   - Formato: AN-2024-0001-EP1 (donde EP1 es el número de la épica).  
   - Cada historia de usuario está relacionada a un único código de épica.

2. "Epica":  
   - Una épica es un bloque de trabajo significativo dentro de un proyecto ágil que representa una funcionalidad importante o un objetivo clave.  
   - Ejemplo: "Gestión de usuarios en el sistema".

3. "Codigo de la Historia":  
   - Un identificador único para cada historia de usuario, relacionado con la épica correspondiente.  
   - Formato: AN-2024-0001-EP1-HU1 (donde EP1 es el número de la épica y HU1 el número de la historia de usuario).

4. "Descripcion de la Historia":  
   - Una narrativa en formato estándar.  
   - Formato: "Como [rol], quiero [acción], para [resultado/beneficio]."  
   - Ejemplo: "Como administrador, quiero gestionar usuarios, para garantizar un control adecuado del sistema."

5. "Criterios de Aceptacion":  
   - Las condiciones que deben cumplirse para que la historia de usuario se considere completada y aceptada.  
   - Ejemplo: "El sistema debe permitir crear, editar y eliminar usuarios sin errores."

6. "Prioridad":  
   - Clasificación de la importancia de la historia de usuario según la metodología MoSCoW:  
     a) Must Have: Requisitos esenciales.  
     b) Should Have: Importantes, pero no críticas.  
     c) Could Have: Deseables, pero no prioritarias.  
     d) Won't Have: Excluidas en este ciclo.

7. "Estimacion de Esfuerzo":  
   - Estimacion del esfuerzo requerido utilizando la secuencia de Fibonacci:  
     1: Esfuerzo muy bajo.  
     2: Esfuerzo bajo.  
     3: Esfuerzo moderado.  
     5: Esfuerzo considerable.  
     8: Esfuerzo alto.  
     13: Esfuerzo muy alto.  
     21: Esfuerzo extremadamente alto (evitar usar este nivel; dividir historias de usuario si es necesario).

8. "Responsable":  
   - La persona o equipo asignado para trabajar en la historia de usuario.  
   - Opciones:  
     a) Stakeholder o Cliente Product Owner  
     b) Scrum Master  
     c) DevOps  
     d) Arquitecto  
     e) Full Stack  
     f) Back End  
     g) Front End / Web  
     h) Front End / App  
     i) Ingeniero de Datos  
     j) Visualizador de Datos  
     k) Web Master  
     l) IA  
     m) ML  
     n) UI/UX  
     o) QA

9. "Estado":  
   - Estado actual de la historia de usuario.  
   - Opciones:  
     - "Nuevo": Aún no trabajado.  
     - "En progreso": Actualmente en desarrollo.  
     - "Completo": Finalizado.

Instrucciones Adicionales:  
1. Prioriza siempre la información más reciente de la tabla Markdown de la etapa de Propuesta Preliminar.  
2. Genera un JSON claro y bien estructurado para cada historia de usuario, siguiendo estrictamente el formato indicado.  
3. Si alguna información no está disponible, indícalo como "Pendiente" en el campo correspondiente.


    ### 
        You have access to the following tools to generate the document:
            {tools}
        
    Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

    Valid "action" values: "Final Answer" or {tool_names}

    Provide only ONE action per $JSON_BLOB, as shown:

    ```
    {{
    "action": $TOOL_NAME,
    "action_input": $INPUT
    }}
    ```

    Follow this format:

    Question: input question to answer
    Thought: consider previous and subsequent steps
    Action:
    ```
    $JSON_BLOB
    ```
    Observation: action result
    ... (repeat Thought/Action/Observation N times)
    Thought: I know what to respond
    Action:
    ```
    {{
    "action": "Final Answer",
    "action_input": "Final response to human"
    }}

    Begin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation'''

    human = '''generate the json with all the json information about User history
    {agent_scratchpad}

(reminder to respond in a JSON blob no matter what)'''

    

    USER_HIS_PROMPTAI= ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("system","{historial}"),
            ("human",human),
        ]
    )

    # Initialize agent and executor
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2,timeout=200)
    tools = []
    agent1 = create_structured_chat_agent(llm, tools, USER_HIS_PROMPTAI)
    agent_executor1 = AgentExecutor(agent=agent1, tools=tools, max_iterations=2, verbose=True,handle_parsing_errors=True)
    if chat =="nuevo_chat":
            chat_history = st.session_state.messages
    else:
        chat_history=Cargar_HistorialDB(user,chat,"U_History")
    response = agent_executor1.invoke(
        {"historial":chat_history,"chat_name":chat,"usuario":user},
    )
    return response
# Initialize agent and executor
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5,timeout=300)
tools = [DOCs]
agent = create_tool_calling_agent(llm, tools, USER_HIS_PROMPT)
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, max_iterations=1,early_stopping_method='generate', verbose=True)


def Agente_UH_AI(input: str, chat:str,historial:str,user:str):
        if chat =="nuevo_chat":
            chat_history = historial
        else:
            chat_history=Cargar_HistorialDB(user,chat,"U_History")
        response = agent_executor.invoke(
            {"input": input,"historial":chat_history,"chat_name":chat,"usuario":user},
        )
        if "intermediate_steps" in response:
            llm2 = ChatOpenAI(model="gpt-4o-mini", temperature=0.2,timeout=100)#timeout=30  # Tiempo de espera en segundos
            print("No se obtuvo respuesta en las iteraciones; se intentará una última vez.")
            secondary_response = LAST_PROMPT | llm2 | StrOutputParser()
            final_output = secondary_response.invoke(
                {"input": response["input"], "historial": response["intermediate_steps"]},
            )
            print(final_output)
            return(final_output)
        return(response['output'])
