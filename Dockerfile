FROM python:3.11-slim as requirements-stage

WORKDIR /tmp

RUN pip install --no-cache-dir poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY ./app ./
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
ENV PYTHONPATH=/code

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
