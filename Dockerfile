FROM python:3.10-slim

# Установите зависимости системы
RUN apt-get update && apt-get install -y build-essential default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*

# Установите Poetry
RUN pip install poetry

# Установите рабочую директорию
WORKDIR /app

# Скопируйте файлы конфигурации Poetry
COPY poetry.lock pyproject.toml ./

# Установите зависимости проекта без установки самого проекта
RUN poetry install --no-interaction --no-ansi --no-root

# Скопируйте остальные файлы проекта
COPY . .

# Копируем entrypoint.sh и делаем его исполняемым
RUN chmod +x /app/entrypoint.sh

# Установите переменную окружения
ENV PYTHONUNBUFFERED=1

# Устанавливаем entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

