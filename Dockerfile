FROM python:3.11-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        libssl-dev \
        libkrb5-dev \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install uv \
    && uv pip install --system -e .[dev,docs,testing]

CMD ["bash"]
