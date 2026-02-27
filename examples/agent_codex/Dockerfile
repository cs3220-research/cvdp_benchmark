FROM node:22-bookworm-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3 \
      git \
      ca-certificates \
      curl \
      jq \
      ripgrep \
      fd-find \
      less \
      procps \
      make \
      gcc \
      g++ \
      iverilog \
      verilator && \
    ln -sf /usr/bin/fdfind /usr/local/bin/fd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN npm install -g @openai/codex

COPY agent.py /app/agent.py

ENTRYPOINT ["python3", "/app/agent.py"]
