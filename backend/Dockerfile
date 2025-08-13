FROM python:latest

# ADD . /

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY providers/ ./providers/
COPY vdb/ ./vdb/
COPY backend.py .

CMD [ "flask", "--app", "backend.py", "run"]
