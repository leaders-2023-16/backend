FROM python:3.11-slim as requirements

WORKDIR /tmp

RUN pip install --no-cache-dir poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11 as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=requirements /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt


FROM python:3.11-slim as release

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY --from=builder /opt/venv /opt/venv
COPY ./app ./

ENV PYTHONPATH=/code PATH="/opt/venv/bin:$PATH"

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
