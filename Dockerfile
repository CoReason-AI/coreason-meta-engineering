# Stage 1: Builder
FROM python:3.14-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Set the working directory
WORKDIR /app

# Copy project manifest files
COPY pyproject.toml uv.lock ./
# Copy .git if it exists for versioning
COPY .gi[t] ./.git/



# Copy the project files
COPY src/ ./src/
COPY README.md .
COPY LICENSE .

# Install dependencies and build the wheel
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen

# Ensure project build step is included
RUN uv build --wheel --out-dir /wheels


# Stage 2: Runtime
FROM python:3.14-slim AS runtime

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create a non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Add user's local bin to PATH
ENV PATH="/home/appuser/app/.venv/bin:/home/appuser/.local/bin:${PATH}"

# Set the working directory
WORKDIR /home/appuser/app
COPY --from=builder --chown=appuser:appuser /app/.venv ./.venv

# Copy the wheel from the builder stage
COPY --from=builder /wheels /wheels

# Install the application wheel
RUN uv pip install --no-cache /wheels/*.whl

CMD ["coreason-meta-mcp"]
