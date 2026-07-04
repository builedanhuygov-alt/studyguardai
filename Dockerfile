# Slim runtime image for StudyGuard AI.
# Note: webcam access is host/OS specific. On Linux, pass a device, e.g.
#   docker run --rm --device /dev/video0 studyguard-ai python -m studyguard
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install -e ".[dev]"

# Default: print CLI help. Override to run tests or the app.
CMD ["python", "-m", "studyguard", "--help"]
