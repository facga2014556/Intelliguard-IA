import os
from pathlib import Path

# Directorio raíz del proyecto
ROOT_DIR = Path(__file__).parent.parent

# Directorio para almacenar imágenes de pertenencias
PERTENENCIAS_DIR = os.path.join(ROOT_DIR, 'data', 'pertenencias')

# Crear directorios si no existen
os.makedirs(PERTENENCIAS_DIR, exist_ok=True)

# Configuración de la API
API_URL = 'http://localhost:5000'

# Rutas base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Rutas de modelos
MODELO_FACIAL = os.path.join(BASE_DIR, 'data', 'models', 'facial', 'modeloEstudiantes.xml')
MODELO_OBJETOS = os.path.join(BASE_DIR, 'data', 'models', 'objetos', 'ModelObjetoFinal.pt')

# Rutas de datos
DATASET_FACIAL = os.path.join(BASE_DIR, 'data', 'datasets', 'facial')
DATASET_OBJETOS = os.path.join(BASE_DIR, 'data', 'datasets', 'objetos')

# Configuraciones de reconocimiento facial
CONFIANZA_MINIMA = 0.5
MAX_FOTOS = 10

# Configuraciones de detección de objetos
CONFIANZA_OBJETO = 0.5

# Configuración de JWT
JWT_SECRET_KEY = 'tu_clave_secreta_muy_segura'  # En producción, usar una clave segura y almacenarla en variables de entorno

# Asegurar que las carpetas existan
def crear_directorios():
    directorios = [
        os.path.dirname(MODELO_FACIAL),
        os.path.dirname(MODELO_OBJETOS),
        DATASET_FACIAL,
        DATASET_OBJETOS,
        PERTENENCIAS_DIR
    ]
    
    for directorio in directorios:
        if not os.path.exists(directorio):
            os.makedirs(directorio)
            print(f"Directorio creado: {directorio}")

# Crear directorios al importar el módulo
crear_directorios() 