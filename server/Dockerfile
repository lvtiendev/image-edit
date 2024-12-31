FROM nvidia/cuda:12.0.0-base-ubuntu22.04

# Install Python and uv
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml .

RUN python3 -m venv .venv
RUN .venv/bin/python3 -m pip install uv

COPY . .

# Use the virtual environment's Python and uvicorn
CMD ["/app/.venv/bin/uv", "run", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
