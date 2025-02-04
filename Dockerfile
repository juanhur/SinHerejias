# Usa una imagen base de Python
FROM python:3.11

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY pyproject.toml poetry.lock ./

COPY .env /app/.env

# Instala Poetry
RUN pip install --no-cache-dir poetry

# Instala las dependencias del proyecto
RUN poetry install --no-root --no-interaction --no-ansi

# Copia el resto del código del proyecto
COPY . .
COPY agent.py /usr/local/lib/python3.11/site-packages/langchain/agents/agent.py

# Expone el puerto 8501 para Strea
EXPOSE 9191

# Comando para ejecutar Streamlit
CMD ["poetry", "run", "streamlit", "run", "front.py", "--server.port", "9191", "--server.address", "0.0.0.0"]
#CMD ["sh", "-c", "set -a && source .env && poetry run streamlit run front.py --server.port 9191 --server.address 0.0.0.0"]

