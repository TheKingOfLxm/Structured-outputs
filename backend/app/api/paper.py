import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models import db, Paper
from app.services.pdf_parser import PDFParser

bp = Blueprint('paper', __name__)


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_paper():
    """上传论文"""
    user_id = get_jwt_identity()

    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '没有上传文件'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'code': 400, 'message': '没有选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'code': 400, 'message': '只支持PDF格式文件'}), 400

    try:
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 创建论文记录
        paper = Paper(
            user_id=user_id,
            filename=filename,
            filepath=filepath,
            filesize=os.path.getsize(filepath),
            status='parsing'
        )

        db.session.add(paper)
        db.session.commit()

        # 异步解析PDF（这里同步处理，实际可以使用Celery等异步任务）
        try:
            parser = PDFParser(filepath)
            result = parser.parse()

            paper.title = result.get('title', '')
            paper.authors = result.get('authors', '')
            paper.abstract = result.get('abstract', '')
            paper.keywords = result.get('keywords', '')
            paper.publish_date = result.get('publish_date', '')
            paper.category = result.get('category', '未分类')
            paper.sections = result.get('sections', '')
            paper.status = 'parsed'
            paper.parse_time = datetime.utcnow()

            db.session.commit()

        except Exception as e:
            paper.status = 'failed'
            paper.error_message = str(e)
            db.session.commit()

        return jsonify({
            'code': 200,
            'message': '上传成功',
            'data': {
                'paperId': paper.id
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'上传失败: {str(e)}'}), 500


@bp.route('/list', methods=['GET'])
@jwt_required()
def get_paper_list():
    """获取论文列表"""
    user_id = get_jwt_identity()

    # 分页参数
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('pageSize', 10, type=int), 50)
    keyword = request.args.get('keyword', '').strip()

    # 构建查询
    query = Paper.query.filter_by(user_id=user_id)

    if keyword:
        query = query.filter(
            db.or_(
                Paper.title.contains(keyword),
                Paper.filename.contains(keyword)
            )
        )

    # 排序
    query = query.order_by(Paper.upload_time.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'list': [paper.to_dict() for paper in pagination.items],
            'total': pagination.total,
            'page': page,
            'pageSize': page_size
        }
    })


@bp.route('/<int:paper_id>', methods=['GET'])
@jwt_required()
def get_paper_detail(paper_id):
    """获取论文详情"""
    user_id = get_jwt_identity()

    paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()

    if not paper:
        return jsonify({'code': 404, 'message': '论文不存在'}), 404

    paper_data = paper.to_dict()

    # 解析JSON字段
    if paper.authors:
        try:
            paper_data['authors'] = json.loads(paper.authors)
        except:
            paper_data['authors'] = []

    if paper.keywords:
        try:
            paper_data['keywords'] = json.loads(paper.keywords)
        except:
            paper_data['keywords'] = []

    if paper.sections:
        try:
            paper_data['sections'] = json.loads(paper.sections)
        except:
            paper_data['sections'] = []

    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': paper_data
    })


@bp.route('/<int:paper_id>', methods=['DELETE'])
@jwt_required()
def delete_paper(paper_id):
    """删除论文"""
    user_id = get_jwt_identity()

    paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()

    if not paper:
        return jsonify({'code': 404, 'message': '论文不存在'}), 404

    try:
        # 删除文件
        if os.path.exists(paper.filepath):
            os.remove(paper.filepath)

        # 删除数据库记录
        db.session.delete(paper)
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '删除成功'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500


@bp.route('/<int:paper_id>/parse', methods=['POST'])
@jwt_required()
def parse_paper(paper_id):
    """重新解析论文"""
    user_id = get_jwt_identity()

    paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()

    if not paper:
        return jsonify({'code': 404, 'message': '论文不存在'}), 404

    try:
        parser = PDFParser(paper.filepath)
        result = parser.parse()

        paper.title = result.get('title', '')
        paper.authors = result.get('authors', '')
        paper.abstract = result.get('abstract', '')
        paper.keywords = result.get('keywords', '')
        paper.publish_date = result.get('publish_date', '')
        paper.category = result.get('category', '未分类')
        paper.sections = result.get('sections', '')
        paper.status = 'parsed'
        paper.parse_time = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '解析成功',
            'data': paper.to_dict()
        })

    except Exception as e:
        paper.status = 'failed'
        paper.error_message = str(e)
        db.session.commit()
        return jsonify({'code': 500, 'message': f'解析失败: {str(e)}'}), 500


@bp.route('/<int:paper_id>/download', methods=['GET'])
@jwt_required()
def download_paper(paper_id):
    """下载论文"""
    user_id = get_jwt_identity()

    paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()

    if not paper:
        return jsonify({'code': 404, 'message': '论文不存在'}), 404

    if not os.path.exists(paper.filepath):
        return jsonify({'code': 404, 'message': '文件不存在'}), 404

    return send_file(
        paper.filepath,
        as_attachment=True,
        download_name=paper.filename
    )
