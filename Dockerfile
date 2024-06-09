FROM python:3.11-bullseye as BUILDER
RUN curl -sSL https://install.python-poetry.org | python3 -
WORKDIR /app
COPY pyproject.toml .
ENV PATH="/root/.local/bin:${PATH}"
RUN poetry lock && poetry export --without-hashes --format=requirements.txt > requirements.txt


FROM python:3.11 as PROD
RUN useradd -m worker
USER worker
WORKDIR /home/worker
COPY --chown=root:worker --from=BUILDER /app/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
COPY --chown=worker:worker . .
ENV PYTHONUNBUFFERED 1
ENV NEO4J_HOST=$NEO4J_HOST
CMD ["python", "-u", "main.py"]