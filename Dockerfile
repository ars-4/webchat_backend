FROM python:3.7

# WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libpcre3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY . .

RUN poetry install

CMD ["poetry", "run", "daphne", "-b", "0.0.0.0", "-p", "8000", "WebChat.asgi:application"]