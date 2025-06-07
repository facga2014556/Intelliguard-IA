from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import base64
from core.reconocimiento.facial import ReconocimientoFacial
from core.pertenencias.gestion import GestionPertenencias
from core.objetos.deteccion import DeteccionObjetos
from utils.auth import login_required, autenticar_admin, crear_admin_inicial, generar_token
import os
from datetime import datetime
from utils.config import ROOT_DIR, DATASET_FACIAL
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

# Inicializar servicios
reconocedor = ReconocimientoFacial()
gestionador = GestionPertenencias()
detector = DeteccionObjetos()


@app.route('/ia/reconocimiento/capturar', methods=['POST'])
def capturar_rostro():
    try:
        data = request.json
        codigo_estudiante = data.get('codigo_estudiante')
        if not codigo_estudiante:
            return jsonify({'error': 'Código de estudiante requerido'}), 400
            
        reconocedor.capturar_rostro(codigo_estudiante)
        return jsonify({'mensaje': 'Rostro capturado exitosamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ia/reconocimiento/verificar', methods=['POST'])
def verificar_rostro():
    try:
        # Obtener imagen en base64
        data = request.json
        imagen_base64 = data.get('imagen')
        if not imagen_base64:
            return jsonify({'error': 'Imagen requerida'}), 400
        # Convertir base64 a imagen (ya viene puro, sin prefijo)
        imagen_bytes = base64.b64decode(imagen_base64)
        nparr = np.frombuffer(imagen_bytes, np.uint8)
        imagen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # Realizar reconocimiento
        codigo, confianza = reconocedor.reconocimiento_facial(imagen)
        return jsonify({
            'codigo_estudiante': codigo,
            'confianza': confianza
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ia/pertenencias/registrar', methods=['POST'])
@login_required
def registrar_pertenencia():
    try:
        data = request.json
        codigo_estudiante = data.get('codigo_estudiante')
        tipo_objeto = data.get('tipo_objeto')
        descripcion = data.get('descripcion')
        imagen_base64 = data.get('imagen')

        if not all([codigo_estudiante, tipo_objeto, imagen_base64]):
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        # Convertir base64 a imagen
        imagen_bytes = base64.b64decode(imagen_base64.split(',')[1])
        nparr = np.frombuffer(imagen_bytes, np.uint8)
        imagen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Guardar imagen
        ruta_imagen = detector.guardar_imagen(imagen, codigo_estudiante, tipo_objeto)
        if not ruta_imagen:
            return jsonify({'error': 'Error al guardar la imagen'}), 500

        # Registrar en la base de datos
        resultado = gestionador.registrar_pertenencia(
            codigo_estudiante=codigo_estudiante,
            tipo_objeto=tipo_objeto,
            descripcion=descripcion,
            ruta_imagen=ruta_imagen
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ia/pertenencias/consultar', methods=['GET'])
@login_required
def consultar_pertenencias():
    try:
        codigo_estudiante = request.args.get('codigo_estudiante')
        # Usar la función obtener_pertenencias, que permite filtrar o traer todo
        resultado = gestionador.obtener_pertenencias(codigo_estudiante)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ia/objetos/detectar', methods=['POST'])
@login_required
def detectar_objetos():
    try:
        # Obtener imagen en base64
        data = request.json
        imagen_base64 = data.get('imagen')
        if not imagen_base64:
            return jsonify({'error': 'Imagen requerida'}), 400
            
        # Convertir base64 a imagen
        imagen_bytes = base64.b64decode(imagen_base64.split(',')[1])
        nparr = np.frombuffer(imagen_bytes, np.uint8)
        imagen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Detectar objetos
        objetos = detector.detectar_objetos(imagen)
        return jsonify(objetos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ia/estudiantes/registrar', methods=['POST'])
def registrar_estudiante():
    try:
        data = request.json
        codigo_estudiante = data.get('codigo_estudiante')
        imagenes_base64 = data.get('imagenes', [])
        
        if not codigo_estudiante or not imagenes_base64:
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        # Asegurar que el directorio DATASET_FACIAL existe
        os.makedirs(DATASET_FACIAL, exist_ok=True)

        # Guardar cada imagen
        rutas_imagenes = []
        for i, imagen_base64 in enumerate(imagenes_base64):
            # Convertir base64 a imagen
            imagen_bytes = base64.b64decode(imagen_base64)
            nparr = np.frombuffer(imagen_bytes, np.uint8)
            imagen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Convertir a escala de grises para el reconocimiento facial
            gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            
            # Detectar rostros
            rostros = reconocedor.detector.detectMultiScale(
                gris,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(rostros) > 0:
                # Tomar el primer rostro detectado
                x, y, w, h = rostros[0]
                rostro = gris[y:y+h, x:x+w]
                
                # Guardar rostro en DATASET_FACIAL
                ruta_imagen = os.path.join(DATASET_FACIAL, f"{codigo_estudiante}_{i}.jpg")
                cv2.imwrite(ruta_imagen, rostro)
                rutas_imagenes.append(ruta_imagen)
            else:
                print(f"No se detectó rostro en la imagen {i}")

        if not rutas_imagenes:
            return jsonify({'error': 'No se detectaron rostros en ninguna imagen'}), 400

        # Entrenar el modelo con las nuevas imágenes
        reconocedor.entrenar_modelo()

        # Registrar estudiante en la base de datos si no existe
        db = gestionador.db
        cursor = db.ejecutar('SELECT codigo_estudiante FROM estudiantes WHERE codigo_estudiante = %s', (codigo_estudiante,))
        if not cursor or not cursor.fetchone():
            db.ejecutar(
                'INSERT INTO estudiantes (codigo_estudiante) VALUES (%s)',
                (codigo_estudiante,)
            )

        return jsonify({
            'mensaje': 'Estudiante registrado exitosamente',
            'rutas_imagenes': rutas_imagenes
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ia/login/administrador', methods=['POST'])
def login_administrador():
    try:
        data = request.json
        usuario = data.get('usuario')
        contraseña = data.get('contraseña')
        
        if not usuario or not contraseña:
            return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
            
        token, error = autenticar_admin(usuario, contraseña)
        if error:
            return jsonify({'error': error}), 401
            
        return jsonify({
            'access_token': token,
            'mensaje': 'Login exitoso'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ia/admin/inicial', methods=['POST'])
def crear_admin():
    try:
        data = request.json
        usuario = data.get('usuario')
        contraseña = data.get('contraseña')
        nombre = data.get('nombre')
        
        if not all([usuario, contraseña, nombre]):
            return jsonify({'error': 'Todos los campos son requeridos'}), 400
            
        exito, mensaje = crear_admin_inicial(usuario, contraseña, nombre)
        if not exito:
            return jsonify({'error': mensaje}), 400
            
        return jsonify({'mensaje': mensaje})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ia/estudiantes/listar', methods=['GET'])
def listar_estudiantes():
    try:
        estudiantes = {}
        for archivo in os.listdir(DATASET_FACIAL):
            if archivo.endswith('.jpg'):
                codigo = archivo.split('_')[0]
                if codigo not in estudiantes:
                    estudiantes[codigo] = []
                estudiantes[codigo].append(f"/ia/estudiantes/foto/{archivo}")
        resultado = []
        for codigo, fotos in estudiantes.items():
            resultado.append({
                "codigo": codigo,
                "fotos": fotos
            })
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ia/estudiantes/foto/<nombre_foto>', methods=['GET'])
def servir_foto_estudiante(nombre_foto):
    try:
        ruta = os.path.join(DATASET_FACIAL, nombre_foto)
        if not os.path.exists(ruta):
            return "No encontrada", 404
        return send_file(ruta, mimetype='image/jpeg')
    except Exception as e:
        return str(e), 500

@app.route('/ia/login/estudiante', methods=['POST', 'OPTIONS'])
def login_estudiante():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.json
        codigo_estudiante = data.get('codigo_estudiante')
        
        if not codigo_estudiante:
            return jsonify({'error': 'Código de estudiante requerido'}), 400
            
        # Verificar que el estudiante existe en el dataset facial
        estudiante_existe = False
        for archivo in os.listdir(DATASET_FACIAL):
            if archivo.startswith(f"{codigo_estudiante}_"):
                estudiante_existe = True
                break
                
        if not estudiante_existe:
            return jsonify({'error': 'Estudiante no encontrado'}), 404
            
        # Generar token JWT
        token = generar_token(codigo_estudiante)
        
        return jsonify({
            'access_token': token,
            'mensaje': 'Login exitoso'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ia/pertenencias/reporte/pdf', methods=['GET'])
@login_required
def reporte_pertenencias_pdf():
    try:
        registros = gestionador.obtener_pertenencias()
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 40
        p.setFont("Helvetica-Bold", 14)
        p.drawString(40, y, "Reporte de Pertenencias")
        y -= 30
        p.setFont("Helvetica", 10)
        for reg in registros:
            texto = f"{reg['codigo_estudiante']} | {reg['tipo_objeto']} | {reg['descripcion']} | {reg['fecha_entrada']} | {reg['estado']}"
            p.drawString(40, y, texto)
            y -= 15
            if y < 40:
                p.showPage()
                y = height - 40
        p.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="reporte_pertenencias.pdf", mimetype='application/pdf')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ia/pertenencias/registrar-salida', methods=['POST'])
@login_required
def registrar_salida_pertenencia():
    try:
        data = request.json
        codigo_estudiante = data.get('codigo_estudiante')
        tipo_objeto = data.get('tipo_objeto')
        if not codigo_estudiante or not tipo_objeto:
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        resultado = gestionador.registrar_salida(codigo_estudiante, tipo_objeto)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 