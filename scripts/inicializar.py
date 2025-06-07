import os
import sys
import shutil
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from utils.config import (
    MODELO_FACIAL,
    MODELO_OBJETOS,
    DATASET_FACIAL,
    DATASET_OBJETOS,
    PERTENENCIAS_DIR
)
from utils.database import Database

def copiar_archivos_origen():
    """Copia archivos desde las carpetas originales"""
    try:
        # Copiar dataset de objetos
        origen_objetos = ROOT_DIR.parent / 'ObjetosDataSetYolo'
        if origen_objetos.exists():
            for archivo in origen_objetos.glob('*'):
                if archivo.is_file():
                    shutil.copy2(archivo, DATASET_OBJETOS)
            print("Dataset de objetos copiado exitosamente")
            
    except Exception as e:
        print(f"Error al copiar archivos: {str(e)}")

def inicializar_sistema():
    """Inicializa el sistema completo"""
    print("Iniciando sistema Intelliguard-IA...")
    
    # Crear directorios
    print("\nCreando estructura de directorios...")
    for directorio in [DATASET_FACIAL, DATASET_OBJETOS, PERTENENCIAS_DIR]:
        os.makedirs(directorio, exist_ok=True)
        print(f"✓ {directorio}")
    
    # Copiar archivos originales
    print("\nCopiando archivos originales...")
    copiar_archivos_origen()
    
    # Inicializar base de datos
    print("\nInicializando base de datos...")
    db = Database()
    db.cerrar()
    
    print("\nSistema inicializado exitosamente!")

if __name__ == "__main__":
    inicializar_sistema() 