FROM python:3

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY poetry.lock pyproject.toml /usr/src/app/

RUN pip3 install poetry

RUN poetry install

CMD ["poetry", "run", "daphne", "-b", "0.0.0.0", "-p", "8000", "WebChat.asgi:application"]