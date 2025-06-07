from flask import Blueprint, send_file, request, jsonify
from ..reportes.generador import GeneradorReportes
from ..utils.database import Database
from datetime import datetime

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/reportes/pertenencias', methods=['GET'])
def generar_reporte_pertenencias():
    try:
        # Obtener filtros
        filtros = {
            'estudiante': request.args.get('estudiante'),
            'estado': request.args.get('estado')
        }
        
        # Generar reporte
        db = Database()
        generador = GeneradorReportes(db)
        excel_buffer = generador.generar_reporte_pertenencias(filtros)
        
        # Enviar archivo
        return send_file(
            excel_buffer,
            as_attachment=True,
            download_name=f"Reporte_Pertenencias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reportes_bp.route('/reportes/pertenencias/consulta', methods=['POST'])
def consultar_pertenencias():
    try:
        # Obtener filtros del body
        filtros = request.json or {}
        
        # Generar reporte
        db = Database()
        generador = GeneradorReportes(db)
        excel_buffer = generador.generar_reporte_pertenencias(filtros)
        
        # Enviar archivo
        return send_file(
            excel_buffer,
            as_attachment=True,
            download_name=f"Reporte_Pertenencias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 