# Usa una imagen oficial de Python
FROM python:3.10-slim

# Instala dependencias del sistema necesarias para opencv
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Crea el directorio de la app
WORKDIR /app

# Copia los archivos del proyecto
COPY . .

# Instala las dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expone el puerto 8000
EXPOSE 8000

# Comando para correr la app con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"] 
