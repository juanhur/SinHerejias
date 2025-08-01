
# Usa una imagen base de Python
FROM python:3.11

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY pyproject.toml poetry.lock ./

COPY .env /app/.env

# Instala Poetry
RUN pip install --no-cache-dir poetry

# Deshabilita la creación de entornos virtuales y luego instala las dependencias globalmente
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi


# Expone el puerto 9191 para Streamlit
EXPOSE 9191

# Comando para ejecutar Streamlit
CMD ["streamlit", "run", "front.py", "--server.port", "9191", "--server.address", "0.0.0.0"]
