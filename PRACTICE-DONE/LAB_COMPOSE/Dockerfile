FROM python:3.11-slim

WORKDIR /app

RUN pip install fastapi uvicorn
RUN apt-get update && apt-get install -y curl

COPY main.py .

CMD ["python", "main.py"]