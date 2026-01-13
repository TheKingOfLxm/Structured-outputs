import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Paper, GenerateRecord
from app.services.ai_generator import AIGenerator

bp = Blueprint('generate', __name__)


@bp.route('/mindmap', methods=['POST'])
@jwt_required()
def generate_mindmap():
    """生成思维导图"""
    user_id = get_jwt_identity()
    data = request.get_json()
    paper_id = data.get('paperId')

    if not paper_id:
        return jsonify({'code': 400, 'message': '论文ID不能为空'}), 400

    # 获取论文
    paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
    if not paper:
        return jsonify({'code': 404, 'message': '论文不存在'}), 404

    try:
        # 创建生成记录
        record = GenerateRecord(
            user_id=user_id,
            paper_id=paper_id,
            type='mindmap',
            status='generating'
        )
        db.session.add(record)
        db.session.commit()

        # 调用AI生成
        generator = AIGenerator()
        paper_info = {
            'title': paper.title,
            'authors': paper.authors,
            'abstract': paper.abstract,
            'keywords': paper.keywords
        }

        result = generator.generate_mindmap(paper_info)

        # 更新记录
        record.content = json.dumps(result, ensure_ascii=False)
        record.status = 'completed'
        record.description = f'《{paper.title}》的思维导图'

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '生成成功',
            'data': {
                'recordId': record.id,
                'content': result
            }
        })

    except Exception as e:
        if record:
            record.status = 'failed'
            record.error_message = str(e)
            db.session.commit()

        return jsonify({'code': 500, 'message': f'生成失败: {str(e)}'}), 500


@bp.route('/timeline', methods=['POST'])
@jwt_required()
def generate_timeline():
    """生成时间线"""
    user_id = get_jwt_identity()
    data = request.get_json()
    paper_id = data.get('paperId')

    if not paper_id:
        return jsonify({'code': 400, 'message': '论文ID不能为空'}), 400

    paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
    if not paper:
        return jsonify({'code': 404, 'message': '论文不存在'}), 404

    try:
        record = GenerateRecord(
            user_id=user_id,
            paper_id=paper_id,
            type='timeline',
            status='generating'
        )
        db.session.add(record)
        db.session.commit()

        generator = AIGenerator()
        paper_info = {
            'title': paper.title,
            'abstract': paper.abstract
        }

        result = generator.generate_timeline(paper_info)

        record.content = json.dumps(result, ensure_ascii=False)
        record.status = 'completed'
        record.description = f'《{paper.title}》的研究时间线'

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '生成成功',
            'data': {
                'recordId': record.id,
                'content': result
            }
        })

    except Exception as e:
        if record:
            record.status = 'failed'
            record.error_message = str(e)
            db.session.commit()

        return jsonify({'code': 500, 'message': f'生成失败: {str(e)}'}), 500


@bp.route('/graph', methods=['POST'])
@jwt_required()
def generate_graph():
    """生成概念图谱"""
    user_id = get_jwt_identity()
    data = request.get_json()
    paper_id = data.get('paperId')

    if not paper_id:
        return jsonify({'code': 400, 'message': '论文ID不能为空'}), 400

    paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
    if not paper:
        return jsonify({'code': 404, 'message': '论文不存在'}), 404

    try:
        record = GenerateRecord(
            user_id=user_id,
            paper_id=paper_id,
            type='graph',
            status='generating'
        )
        db.session.add(record)
        db.session.commit()

        generator = AIGenerator()
        paper_info = {
            'title': paper.title,
            'abstract': paper.abstract,
            'keywords': paper.keywords
        }

        result = generator.generate_graph(paper_info)

        record.content = json.dumps(result, ensure_ascii=False)
        record.status = 'completed'
        record.description = f'《{paper.title}》的概念图谱'

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '生成成功',
            'data': {
                'recordId': record.id,
                'content': result
            }
        })

    except Exception as e:
        if record:
            record.status = 'failed'
            record.error_message = str(e)
            db.session.commit()

        return jsonify({'code': 500, 'message': f'生成失败: {str(e)}'}), 500


@bp.route('/summary', methods=['POST'])
@jwt_required()
def generate_summary():
    """生成核心观点总结"""
    user_id = get_jwt_identity()
    data = request.get_json()
    paper_id = data.get('paperId')

    if not paper_id:
        return jsonify({'code': 400, 'message': '论文ID不能为空'}), 400

    paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
    if not paper:
        return jsonify({'code': 404, 'message': '论文不存在'}), 404

    try:
        record = GenerateRecord(
            user_id=user_id,
            paper_id=paper_id,
            type='summary',
            status='generating'
        )
        db.session.add(record)
        db.session.commit()

        generator = AIGenerator()
        paper_info = {
            'title': paper.title,
            'authors': paper.authors,
            'abstract': paper.abstract
        }

        result = generator.generate_summary(paper_info)

        record.content = result
        record.status = 'completed'
        record.description = f'《{paper.title}》的核心观点总结'

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '生成成功',
            'data': {
                'recordId': record.id,
                'content': result
            }
        })

    except Exception as e:
        if record:
            record.status = 'failed'
            record.error_message = str(e)
            db.session.commit()

        return jsonify({'code': 500, 'message': f'生成失败: {str(e)}'}), 500


@bp.route('/history/<int:paper_id>', methods=['GET'])
@jwt_required()
def get_generate_history(paper_id):
    """获取论文的生成历史"""
    user_id = get_jwt_identity()

    # 验证论文所有权
    paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
    if not paper:
        return jsonify({'code': 404, 'message': '论文不存在'}), 404

    # 获取生成记录
    records = GenerateRecord.query.filter_by(
        paper_id=paper_id,
        user_id=user_id
    ).order_by(GenerateRecord.create_time.desc()).all()

    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'list': [record.to_dict() for record in records]
        }
    })


@bp.route('/save', methods=['POST'])
@jwt_required()
def save_generate_result():
    """保存生成结果（前端生成后保存）"""
    user_id = get_jwt_identity()
    data = request.get_json()

    paper_id = data.get('paperId')
    content = data.get('content')
    gen_type = data.get('type')
    description = data.get('description', '')

    if not all([paper_id, content, gen_type]):
        return jsonify({'code': 400, 'message': '缺少必要参数'}), 400

    # 验证论文所有权
    paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
    if not paper:
        return jsonify({'code': 404, 'message': '论文不存在'}), 404

    try:
        record = GenerateRecord(
            user_id=user_id,
            paper_id=paper_id,
            type=gen_type,
            content=json.dumps(content) if isinstance(content, (dict, list)) else content,
            description=description,
            status='completed'
        )

        db.session.add(record)
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '保存成功',
            'data': {'recordId': record.id}
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'保存失败: {str(e)}'}), 500


@bp.route('/record/<int:record_id>', methods=['GET'])
@jwt_required()
def get_generate_record(record_id):
    """获取生成记录详情"""
    user_id = get_jwt_identity()

    record = GenerateRecord.query.filter_by(id=record_id, user_id=user_id).first()

    if not record:
        return jsonify({'code': 404, 'message': '记录不存在'}), 404

    record_data = record.to_dict()

    # 解析content
    try:
        record_data['content'] = json.loads(record.content)
    except:
        pass

    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': record_data
    })


@bp.route('/record/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_generate_record(record_id):
    """删除生成记录"""
    user_id = get_jwt_identity()

    record = GenerateRecord.query.filter_by(id=record_id, user_id=user_id).first()

    if not record:
        return jsonify({'code': 404, 'message': '记录不存在'}), 404

    try:
        db.session.delete(record)
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '删除成功'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500
