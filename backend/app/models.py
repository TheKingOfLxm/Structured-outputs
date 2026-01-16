from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    papers = db.relationship('Paper', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    generate_records = db.relationship('GenerateRecord', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Paper(db.Model):
    """论文模型"""
    __tablename__ = 'papers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    filesize = db.Column(db.Integer)

    # 解析后的论文信息
    title = db.Column(db.String(500), default='')
    authors = db.Column(db.Text, default='')  # 存储为JSON字符串
    abstract = db.Column(db.Text, default='')
    keywords = db.Column(db.Text, default='')  # 存储为JSON字符串
    publish_date = db.Column(db.String(50), default='')
    source = db.Column(db.String(200), default='')
    sections = db.Column(db.Text, default='')  # 存储为JSON字符串

    # 状态
    status = db.Column(db.String(20), default='pending', index=True)  # pending, parsing, parsed, failed
    error_message = db.Column(db.Text, default='')

    # 时间
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    parse_time = db.Column(db.DateTime)

    # 关系
    generate_records = db.relationship('GenerateRecord', backref='paper', lazy='dynamic', cascade='all, delete-orphan')

    # 复合索引
    __table_args__ = (
        db.Index('idx_user_upload', 'user_id', 'upload_time'),
    )

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'filename': self.filename,
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'keywords': self.keywords,
            'sections': self.sections,
            'publishDate': self.publish_date,
            'source': self.source,
            'status': self.status,
            'uploadTime': self.upload_time.isoformat() if self.upload_time else None
        }


class GenerateRecord(db.Model):
    """生成记录模型"""
    __tablename__ = 'generate_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    paper_id = db.Column(db.Integer, db.ForeignKey('papers.id'), nullable=False)

    # 生成类型和内容
    type = db.Column(db.String(50), nullable=False)  # mindmap, timeline, graph, summary
    content = db.Column(db.Text, default='')  # 存储为JSON字符串
    description = db.Column(db.Text, default='')

    # 状态
    status = db.Column(db.String(20), default='pending')  # pending, generating, completed, failed
    error_message = db.Column(db.Text, default='')

    # 时间
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Float, default=0)  # 生成耗时（秒）

    # 复合索引 - 提升查询性能
    __table_args__ = (
        db.Index('idx_user_paper_type', 'user_id', 'paper_id', 'type'),
        db.Index('idx_user_paper_status', 'user_id', 'paper_id', 'status'),
        db.Index('idx_paper_type_time', 'paper_id', 'type', 'create_time'),
    )

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'paperId': self.paper_id,
            'type': self.type,
            'content': self.content,
            'description': self.description,
            'status': self.status,
            'createTime': self.create_time.isoformat() if self.create_time else None,
            'duration': self.duration
        }
