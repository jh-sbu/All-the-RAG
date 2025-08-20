FROM python:latest AS builder

RUN --mount=type=cache,target=/root/.cache/pip pip install sentence-transformers huggingface_hub

ARG MODEL_ID=sentence-transformers/all-MiniLM-L6-v2
ARG REVISION=main

# Download the model ahead of time
RUN huggingface-cli download "$MODEL_ID" --revision "$REVISION"\
  --local-dir /opt/models/all-MiniLM-L6-v2 \
  --local-dir-use-symlinks False

FROM python:latest AS base

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip\
  pip install -r requirements.txt

COPY --from=builder /opt/models /opt/models
ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
ENV SENTENCE_TRANSFORMERS_HOME=/opt/models

COPY providers/ ./providers/
COPY vdb/ ./vdb/
COPY backend.py .

FROM base AS development

CMD [ "flask", "--app", "backend.py", "run", "--debug", "--host=0.0.0.0" ]

FROM base AS production

CMD [ "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend:app" ]
