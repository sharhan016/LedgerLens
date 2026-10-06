FROM python:3.12-slim

WORKDIR /app
COPY backend/pyproject.toml ./
ARG INSTALL_ML=false
RUN mkdir -p app && touch app/__init__.py && \
    if [ "$INSTALL_ML" = "true" ]; then \
      pip install --no-cache-dir '.[ml]'; \
    else \
      pip install --no-cache-dir .; \
    fi && rm -rf app
COPY backend/app ./app
COPY backend/alembic.ini ./
COPY backend/migrations ./migrations
COPY backend/scripts ./scripts
COPY data /data
COPY evaluation /evaluation
RUN chmod +x scripts/start.sh

EXPOSE 8000
CMD ["./scripts/start.sh"]
