FROM python:3.11

WORKDIR webserver

COPY backend /backend
COPY frontend /frontend

RUN pip install --no-cache-dir -r /backend/requirements.txt

WORKDIR webserver/backend

EXPOSE 5000

CMD ["python", "-m", "backend"]