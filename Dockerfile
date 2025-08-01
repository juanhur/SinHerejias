FROM python:3.11

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY .env /app/.env

# Copia todo el código de la app, incluyendo front.py
COPY . /app

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

EXPOSE 9191

CMD ["streamlit", "run", "front.py", "--server.port", "9191", "--server.address", "0.0.0.0"]
