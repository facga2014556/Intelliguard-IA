import psycopg2
import os

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.conectar()
        # Ya no creamos tablas aquí, se asume que están creadas en PostgreSQL

    def conectar(self):
        """Establece conexión con la base de datos PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                dbname=os.environ.get('PGDATABASE'),
                user=os.environ.get('PGUSER'),
                password=os.environ.get('PGPASSWORD'),
                host=os.environ.get('PGHOST'),
                port=os.environ.get('PGPORT')
            )
            self.cursor = self.conn.cursor()
            print("Conexión a base de datos PostgreSQL establecida")
        except Exception as e:
            print(f"Error al conectar a la base de datos: {str(e)}")

    def cerrar(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
            print("Conexión a base de datos cerrada")

    def ejecutar(self, query, params=None):
        """Ejecuta una consulta SQL"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return self.cursor
        except Exception as e:
            print(f"Error al ejecutar consulta: {str(e)}")
            return None

    def obtener_uno(self, query, params=None):
        """Obtiene un solo resultado"""
        cursor = self.ejecutar(query, params)
        if cursor:
            return cursor.fetchone()
        return None

    def obtener_todos(self, query, params=None):
        """Obtiene todos los resultados"""
        cursor = self.ejecutar(query, params)
        if cursor:
            return cursor.fetchall()
        return [] 