from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from app.models import db
import os

def create_app(config_name='development'):
    """创建Flask应用"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')), 'instance'), exist_ok=True)

    # 初始化扩展
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    JWTManager(app)

    # 注册蓝图
    from app.api.user import bp as user_bp
    from app.api.paper import bp as paper_bp
    from app.api.generate import bp as generate_bp

    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(paper_bp, url_prefix='/api/paper')
    app.register_blueprint(generate_bp, url_prefix='/api/generate')

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app
