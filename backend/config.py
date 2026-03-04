import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """基础配置"""
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'pdf'}

    # 智谱AI配置
    ZHIPUAI_API_KEY = os.environ.get('ZHIPUAI_API_KEY') or ''

    # 支持的AI模型
    AI_MODELS = {
        'glm-4-flash': {
            'name': 'GLM-4 Flash',
            'description': '极速推理，适合快速响应',
            'provider': 'zhipu',
            'max_tokens': 128000,
            'default': True
        },
        'glm-4-plus': {
            'name': 'GLM-4 Plus',
            'description': '高性能模型，效果更佳',
            'provider': 'zhipu',
            'max_tokens': 128000
        },
        'glm-4-air': {
            'name': 'GLM-4 Air',
            'description': '轻量级模型，经济实惠',
            'provider': 'zhipu',
            'max_tokens': 128000
        },
        'glm-4': {
            'name': 'GLM-4',
            'description': '标准版GLM-4模型',
            'provider': 'zhipu',
            'max_tokens': 128000
        }
    }

    # 默认模型
    DEFAULT_AI_MODEL = os.environ.get('DEFAULT_AI_MODEL') or 'glm-4-flash'

    # CORS配置
    CORS_ORIGINS = [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:5176',
        'http://127.0.0.1:5176'
    ]


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
