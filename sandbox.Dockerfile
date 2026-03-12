FROM python:3.11-slim

# Create non-root user with specific UID/GID
RUN groupadd --gid 10001 sandboxgroup && \
    useradd --uid 10001 --gid 10001 --shell /bin/bash --create-home sandboxuser

# Set working directory
WORKDIR /workspace

# Install ONLY essential tools (NO network tools, NO sudo, NO curl, NO wget)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    ca-certificates \
    file \
    coreutils \
    grep \
    procps \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Verify available tools (no curl, wget, sudo, strings, netcat)
RUN which python3 ls cat grep head tail wc file && \
    ! which curl wget sudo nc nmap netcat strings 2>/dev/null || exit 1

# Set permissions
RUN chown -R sandboxuser:sandboxgroup /workspace

# Switch to non-root user (UID 10001, GID 10001)
USER 10001:10001

# Default command
CMD ["sh"]
