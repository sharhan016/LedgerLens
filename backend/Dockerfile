FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml ./
ARG INSTALL_ML=false
RUN mkdir -p app && touch app/__init__.py && \
    if [ "$INSTALL_ML" = "true" ]; then \
      pip install --no-cache-dir '.[ml]'; \
    else \
      pip install --no-cache-dir .; \
    fi && rm -rf app
COPY app ./app
COPY alembic.ini ./
COPY migrations ./migrations
COPY scripts ./scripts
RUN chmod +x scripts/start.sh

EXPOSE 8000
CMD ["./scripts/start.sh"]
