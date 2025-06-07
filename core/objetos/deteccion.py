import cv2
import numpy as np
import os
from pathlib import Path
import sys
from datetime import datetime

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from utils.config import PERTENENCIAS_DIR

class DeteccionObjetos:
    def __init__(self):
        """Inicializa el detector de objetos"""
        pass
        
    def guardar_imagen(self, imagen, codigo_estudiante, tipo_objeto):
        """
        Guarda la imagen del objeto
        
        Args:
            imagen: Imagen en formato numpy array
            codigo_estudiante: Código del estudiante
            tipo_objeto: Tipo de objeto
            
        Returns:
            str: Ruta de la imagen guardada o None si hay error
        """
        try:
            # Crear directorio si no existe
            fecha = datetime.now().strftime("%Y%m%d")
            ruta_directorio = os.path.join(PERTENENCIAS_DIR, codigo_estudiante, fecha)
            os.makedirs(ruta_directorio, exist_ok=True)
            
            # Generar nombre único para la imagen
            timestamp = datetime.now().strftime("%H%M%S")
            nombre_archivo = f"{tipo_objeto}_{timestamp}.jpg"
            ruta_imagen = os.path.join(ruta_directorio, nombre_archivo)
            
            # Guardar imagen
            cv2.imwrite(ruta_imagen, imagen)
            
            return ruta_imagen
            
        except Exception as e:
            print(f"Error al guardar imagen: {str(e)}")
            return None 