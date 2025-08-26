FROM public.ecr.aws/lambda/python:3.12 AS builder

RUN --mount=type=cache,target=/root/.cache/pip pip install sentence-transformers huggingface_hub

ARG MODEL_ID=sentence-transformers/all-MiniLM-L6-v2
ARG REVISION=main

# Download the model ahead of time
# ENV HF_HOME=/root/.cache/huggingface
RUN hf download "$MODEL_ID" --revision "$REVISION"
  # --cache-dir "$HF_HOME"

RUN ls -al $HF_HOME

# FROM python:latest AS base
FROM public.ecr.aws/lambda/python:3.12 AS base

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip\
  pip install -r requirements.txt

COPY --from=builder /root/.cache/huggingface /root/.cache/huggingface
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1

COPY providers/ ./providers/
COPY vdb/ ./vdb/
COPY backend.py .

FROM base AS development

CMD [ "flask", "--app", "backend.py", "run", "--debug", "--host=0.0.0.0" ]

FROM base AS production

CMD [ "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend:app" ]
