FROM python:latest AS base

# ADD . /

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip\
  pip install -r requirements.txt

COPY providers/ ./providers/
COPY vdb/ ./vdb/
COPY backend.py .

FROM base AS development

CMD [ "flask", "--app", "backend.py", "run", "--debug", "--host=0.0.0.0" ]

FROM base AS production

# CMD [ "flask", "--app", "backend.py", "run", "--host=0.0.0.0"]
CMD [ "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend:app" ]
