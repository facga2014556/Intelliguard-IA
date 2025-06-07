import os
import cv2
from pathlib import Path
import sys
from datetime import datetime

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from core.reconocimiento.facial import ReconocimientoFacial
from core.pertenencias.gestion import GestionPertenencias
from utils.config import PERTENENCIAS_DIR

def test_reconocimiento_facial():
    """Prueba el módulo de reconocimiento facial"""
    print("\n=== Prueba de Reconocimiento Facial ===")
    
    # Inicializar reconocedor
    reconocedor = ReconocimientoFacial()
    
    # Menú de opciones
    while True:
        print("\n1. Capturar nuevo rostro")
        print("2. Reconocer rostro")
        print("3. Volver")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            codigo = input("Ingrese código de estudiante: ")
            reconocedor.capturar_rostro(codigo)
            
        elif opcion == "2":
            print("\nIniciando reconocimiento facial con cámara web...")
            print("Presione 'q' para salir")
            
            # Iniciar cámara web
            cap = cv2.VideoCapture(0)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error al acceder a la cámara web")
                    break
                
                # Realizar reconocimiento facial
                codigo, porcentaje = reconocedor.reconocimiento_facial(frame)
                
                # Mostrar resultados en tiempo real
                if codigo:
                    cv2.putText(frame, f"Estudiante: {codigo}", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, f"Similitud: {porcentaje:.2f}%", (10, 70),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, "No reconocido", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Mostrar frame
                cv2.imshow('Reconocimiento Facial', frame)
                
                # Salir con 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            # Liberar recursos
            cap.release()
            cv2.destroyAllWindows()
                
        elif opcion == "3":
            break
            
        else:
            print("\nOpción inválida")

def test_gestion_pertenencias():
    """Prueba el módulo de gestión de pertenencias"""
    print("\n=== Gestión de Pertenencias ===")
    gestor = GestionPertenencias()
    reconocedor = ReconocimientoFacial()
    
    while True:
        print("\n1. Registrar ENTRADA de pertenencia")
        print("2. Registrar SALIDA de pertenencia")
        print("3. Consultar pertenencias")
        print("4. Volver")
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            print("\nReconociendo estudiante...")
            cap = cv2.VideoCapture(0)
            codigo_estudiante = None
            reconocido = False
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error al acceder a la cámara web")
                    break
                codigo, porcentaje = reconocedor.reconocimiento_facial(frame)
                if codigo:
                    cv2.putText(frame, f"Estudiante: {codigo}", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, f"Similitud: {porcentaje:.2f}%", (10, 70), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    if porcentaje > 60 and not reconocido:
                        codigo_estudiante = codigo
                        reconocido = True
                        print(f"\n¡Estudiante reconocido: {codigo_estudiante}!")
                        break
                else:
                    cv2.putText(frame, "No reconocido", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow('Reconocimiento Facial', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()
            if not codigo_estudiante:
                print("No se reconoció al estudiante.")
                continue
            print("\nTomando foto del objeto...")
            print("Presione 'c' para capturar la foto, 'q' para cancelar")
            cap = cv2.VideoCapture(0)
            foto_tomada = False
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error al acceder a la cámara web")
                    break
                cv2.imshow('Captura de Objeto', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('c'):
                    tipo_objeto = input("Tipo de objeto: ")
                    descripcion = input("Descripción adicional (opcional): ")
                    if gestor.registrar_entrada(codigo_estudiante, tipo_objeto, descripcion, frame):
                        print("\nEntrada registrada exitosamente")
                    else:
                        print("\nError al registrar entrada")
                    foto_tomada = True
                    break
                elif key == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()
            if not foto_tomada:
                print("\nNo se tomó ninguna foto")
        elif opcion == "2":
            print("\nReconociendo estudiante para RETIRO...")
            cap = cv2.VideoCapture(0)
            codigo_estudiante = None
            reconocido = False
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error al acceder a la cámara web")
                    break
                codigo, porcentaje = reconocedor.reconocimiento_facial(frame)
                if codigo:
                    cv2.putText(frame, f"Estudiante: {codigo}", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, f"Similitud: {porcentaje:.2f}%", (10, 70), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    if porcentaje > 60 and not reconocido:
                        codigo_estudiante = codigo
                        reconocido = True
                        print(f"\n¡Estudiante reconocido: {codigo_estudiante}!")
                        break
                else:
                    cv2.putText(frame, "No reconocido", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow('Reconocimiento Facial', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()
            if not codigo_estudiante:
                print("No se reconoció al estudiante.")
                continue
            tipo_objeto = input("Tipo de objeto a retirar: ")
            if gestor.registrar_salida(codigo_estudiante, tipo_objeto):
                print("\nSalida registrada exitosamente")
            else:
                print("\nError al registrar salida")
        elif opcion == "3":
            print("\nReconociendo estudiante...")
            cap = cv2.VideoCapture(0)
            codigo_estudiante = None
            reconocido = False
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error al acceder a la cámara web")
                    break
                codigo, porcentaje = reconocedor.reconocimiento_facial(frame)
                if codigo:
                    cv2.putText(frame, f"Estudiante: {codigo}", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, f"Similitud: {porcentaje:.2f}%", (10, 70), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    if porcentaje > 60 and not reconocido:
                        codigo_estudiante = codigo
                        reconocido = True
                        print(f"\n¡Estudiante reconocido: {codigo_estudiante}!")
                        break
                else:
                    cv2.putText(frame, "No reconocido", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow('Reconocimiento Facial', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()
            if not codigo_estudiante:
                print("No se reconoció al estudiante.")
                continue
            estado = input("Estado (ENTREGADO/RETIRADO, opcional): ")
            pertenencias = gestor.obtener_pertenencias(codigo_estudiante, estado if estado else None)
            if pertenencias:
                print("\nPertenencias encontradas:")
                for p in pertenencias:
                    print(f"\nID: {p[0]}")
                    print(f"Tipo: {p[2]}")
                    print(f"Descripción: {p[3]}")
                    print(f"Ruta imagen: {p[4]}")
                    print(f"Fecha entrada: {p[5]}")
                    print(f"Fecha salida: {p[6]}")
                    print(f"Estado: {p[7]}")
            else:
                print("\nNo se encontraron pertenencias")
        elif opcion == "4":
            break
        else:
            print("\nOpción inválida")

def main():
    while True:
        print("\n=== Sistema Intelliguard-IA ===")
        print("\n1. Reconocimiento Facial")
        print("2. Gestión de Pertenencias")
        print("3. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            test_reconocimiento_facial()
        elif opcion == "2":
            test_gestion_pertenencias()
        elif opcion == "3":
            break
        else:
            print("\nOpción inválida")

if __name__ == "__main__":
    main() 