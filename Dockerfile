FROM python:3.12.8-alpine3.21 AS builder

# setup for pdm so changes don't cause rebuilding these layers
ENV PDM_CHECK_UPDATE=false
RUN pip install pdm

WORKDIR /setup

COPY pdm.lock .
COPY pyproject.toml .

RUN --mount=type=cache,target=/setup/.venv/,sharing=locked \
    --mount=type=bind,source=pyproject.toml,target=/setup/pyproject.toml,readwrite \
    --mount=type=bind,source=pdm.lock,target=/setup/pdm.lock,readwrite \
    pdm install --check --prod --no-editable && \
    cp -R /setup/.venv /setup/.ready-venv

FROM python:3.12.8-alpine3.21 AS runner

WORKDIR /app

COPY --from=builder /setup/.ready-venv /app/.venv

COPY . .

CMD [ "/app/.venv/bin/python", "-m", "litestar", "run", "--host", "0.0.0.0", "--port", "8000" ]
