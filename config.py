# Configuración centralizada para la aplicación Flask
import os
from datetime import timedelta

class Config:
    """
    Clase base de configuración con valores por defecto
    Contiene todas las configuraciones comunes del sistema
    """

    # Configuración básica de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Configuración de OpenAI
    # Ahora solo usa Clavekey
    OPENAI_API_KEY = os.environ.get('Clavekey', '')
    OPENAI_MODEL = 'gpt-4o-mini'   # Modelo específico para respuestas técnicas
    OPENAI_TEMPERATURE = 0.3       # Temperatura baja para respuestas más precisas
    OPENAI_MAX_TOKENS = 1500       # Límite de tokens por respuesta

    # Configuración de sesiones
    SESSION_LIFETIME = timedelta(hours=8)   # Tiempo de vida de sesión: 8 horas
    MAX_INTERACTIONS_PER_SESSION = 50       # Límite de interacciones por sesión
    RATE_LIMIT_PER_MINUTE = 10              # Máximo 10 consultas por minuto

    # Configuración de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # Límite de 16MB para uploads
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'aac'}
    MAX_TEXT_LENGTH = 10000                 # Máximo 10,000 caracteres para texto

    # Configuración de base de datos (Railway PostgreSQL o SQLite local)
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///omar_dev.db')

    # Configuración de Redis para cache y sesiones
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

    # Contexto técnico ABB ACS150
    ABB_ACS150_CONTEXT = """
    Eres un asistente técnico especializado en el variador de frecuencia ABB ACS150.
    Tu función es ayudar a técnicos, operadores y supervisores con:
    - Diagnóstico de problemas y fallas
    - Configuración y parametrización
    - Procedimientos de mantenimiento
    - Interpretación de códigos de error
    - Guías de instalación y conexión
    
    Siempre proporciona respuestas técnicas precisas, concisas y orientadas a la solución.
    Si necesitas más información para dar una respuesta precisa, solicita clarificación específica.
    """

class DevelopmentConfig(Config):
    """ Configuración específica para entorno de desarrollo """
    DEBUG = True
    TESTING = False
    DATABASE_URL = 'sqlite:///omar_dev.db'
    REDIS_URL = 'redis://localhost:6379/0'
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """ Configuración específica para entorno de producción (Railway) """
    DEBUG = False
    TESTING = False
    DATABASE_URL = os.environ.get('DATABASE_URL')
    REDIS_URL = os.environ.get('REDIS_URL')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """ Configuración específica para testing """
    TESTING = True
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'
    RATE_LIMIT_PER_MINUTE = 1000
    OPENAI_API_KEY = 'test-key'

# Diccionario para seleccionar configuración según entorno
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
