FROM python:3

ENV PYTHONUNBUFFERED 1

# WORKDIR /usr/src/app

# COPY poetry.lock pyproject.toml

RUN pip3 install poetry install --no-root --no-cache --no-interaction

RUN poetry install

CMD ["poetry", "run", "daphne", "-b", "0.0.0.0", "-p", "8000", "WebChat.asgi:application"]