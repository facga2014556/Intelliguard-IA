from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from .database import Database
from .config import JWT_SECRET_KEY

db = Database()

def generar_token(admin_id):
    """Genera un token JWT para el administrador"""
    payload = {
        'admin_id': admin_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def verificar_token(token):
    """Verifica un token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload['admin_id']
    except:
        return None

def login_required(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Obtener token del header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Token inválido'}), 401

        if not token:
            return jsonify({'error': 'Token no proporcionado'}), 401

        admin_id = verificar_token(token)
        if not admin_id:
            return jsonify({'error': 'Token inválido o expirado'}), 401

        return f(*args, **kwargs)
    return decorated

def crear_admin_inicial(usuario, contraseña, nombre):
    """Crea el administrador inicial si no existe ninguno"""
    try:
        # Verificar si ya existe un admin
        cursor = db.ejecutar("SELECT COUNT(*) FROM administradores")
        if cursor and cursor.fetchone()[0] > 0:
            return False, "Ya existe un administrador"

        # Crear hash de la contraseña
        contraseña_hash = generate_password_hash(contraseña)
        
        # Insertar admin
        db.ejecutar(
            "INSERT INTO administradores (usuario, contraseña, nombre) VALUES (%s, %s, %s)",
            (usuario, contraseña_hash, nombre)
        )
        return True, "Administrador creado exitosamente"
    except Exception as e:
        return False, str(e)

def autenticar_admin(usuario, contraseña):
    """Autentica un administrador"""
    try:
        # Buscar admin
        admin = db.obtener_uno(
            "SELECT id, contraseña FROM administradores WHERE usuario = %s",
            (usuario,)
        )
        
        if not admin:
            return None, "Usuario no encontrado"
            
        # Verificar contraseña
        if not check_password_hash(admin[1], contraseña):
            return None, "Contraseña incorrecta"
            
        # Generar token
        token = generar_token(admin[0])
        return token, None
    except Exception as e:
        return None, str(e) 