FROM python:3.12-slim AS builder

WORKDIR /src
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir build \
    && python -m build --wheel --outdir /dist

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd --create-home --uid 10001 app
COPY --from=builder /dist/*.whl /tmp/
RUN python -m pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl

USER app
ENTRYPOINT ["cicd-demo-complete"]
