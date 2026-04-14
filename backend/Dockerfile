FROM python:3.10-slim

WORKDIR /app

# Dependencias del sistema necesarias para dlib/face_recognition
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
