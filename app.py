# Importaciones necesarias para Flask y funcionalidades del backend
from flask import Flask, request, jsonify
from flask_cors import CORS  # Para permitir requests desde la app Android
import os
import logging
from datetime import datetime
import uuid

# Configuración de logging para monitoreo y debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear instancia de la aplicación Flask
app = Flask(__name__)

# Habilitar CORS para permitir requests desde diferentes orígenes (Android app)
CORS(app)

# Configuración de la aplicación desde variables de entorno
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
# 🔑 Ahora solo lee la variable "Clavekey" de Railway
app.config['OPENAI_API_KEY'] = os.environ.get('Clavekey', '')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite de 16MB para uploads

# Diccionarios en memoria (en producción usar Redis/DB)
active_sessions = {}
pending_validations = {}

@app.route('/ping', methods=['GET'])
def ping():
    """Endpoint simple para verificar conectividad"""
    logger.info("Ping request received")
    return jsonify({
        'status': 'ok',
        'message': 'Server is running',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/status', methods=['GET'])
def status():
    """Endpoint para verificar estado de salud del sistema"""
    logger.info("Status check requested")

    openai_configured = bool(app.config['OPENAI_API_KEY'])
    active_session_count = len(active_sessions)
    pending_validation_count = len(pending_validations)

    status_response = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'openai': 'configured' if openai_configured else 'not_configured',
            'sessions': f'{active_session_count} active',
            'validations': f'{pending_validation_count} pending'
        },
        'version': '1.0.0'
    }
    return jsonify(status_response), 200

@app.route('/api/session/create', methods=['POST'])
def crear_sesion():
    """Crea una nueva sesión para el usuario"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400

        user_id = data.get('user_id', f'user_{uuid.uuid4().hex[:8]}')
        device_type = data.get('device_type', 'unknown')
        app_version = data.get('app_version', '1.0.0')

        session_id = str(uuid.uuid4())
        session_data = {
            'id': session_id,
            'user_id': user_id,
            'device_type': device_type,
            'app_version': app_version,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'interaction_count': 0
        }

        active_sessions[session_id] = session_data
        logger.info(f"Nueva sesión creada: {session_id} para usuario {user_id}")

        return jsonify({
            'session_id': session_id,
            'status': 'created',
            'message': 'Sesión creada exitosamente',
            'timestamp': datetime.now().isoformat()
        }), 201

    except Exception as e:
        logger.error(f"Error creando sesión: {e}")
        return jsonify({'error': 'Error interno del servidor', 'message': str(e)}), 500

@app.errorhandler(400)
def bad_request(error):
    """Manejador de errores 400"""
    logger.warning(f"Bad request: {error}")
    return jsonify({
        'error': 'Bad Request',
        'message': 'The request data is malformed or invalid',
        'timestamp': datetime.now().isoformat()
    }), 400

@app.errorhandler(404)
def not_found(error):
    """Manejador de errores 404"""
    logger.warning(f"Endpoint not found: {request.url}")
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejador de errores 500"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred. Please try again later.',
        'timestamp': datetime.now().isoformat()
    }), 500

@app.before_request
def log_request_info():
    """Middleware antes de cada request"""
    logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")

@app.after_request
def log_response_info(response):
    """Middleware después de cada request"""
    logger.info(f"Response: {response.status_code} for {request.method} {request.url}")
    return response

if __name__ == '__main__':
    """Punto de entrada principal de la aplicación"""
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')

    logger.info(f"Starting OMAR Industrial AI Backend on {host}:{port}")
    logger.info(f"Debug mode: {debug_mode}")

    app.run(host=host, port=port, debug=debug_mode)
