import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Paper, GenerateRecord
from app.services.ai_generator import AIGenerator

# 配置日志
logger = logging.getLogger(__name__)

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

    # 检查是否有进行中的相同请求
    existing = GenerateRecord.query.filter_by(
        user_id=user_id,
        paper_id=paper_id,
        type='mindmap',
        status='generating'
    ).first()

    if existing:
        return jsonify({
            'code': 409,
            'message': '已有生成任务进行中，请稍后再试',
            'data': {'recordId': existing.id}
        }), 409

    try:
        # 记录开始时间
        start_time = datetime.now()

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
            'keywords': paper.keywords,
            'sections': paper.sections  # 添加章节数据
        }

        # 调试日志
        print(f"[DEBUG] 生成思维导图 - 论文信息:")
        print(f"[DEBUG]   标题: {paper_info['title'][:50] if paper_info['title'] else '无'}...")
        print(f"[DEBUG]   摘要长度: {len(paper_info.get('abstract', ''))}")
        print(f"[DEBUG]   章节数据: {'有' if paper_info.get('sections') else '无'}")

        result = generator.generate_mindmap(paper_info)

        # 计算耗时
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 更新记录
        record.content = json.dumps(result, ensure_ascii=False)
        record.status = 'completed'
        record.description = f'《{paper.title}》的思维导图'
        record.duration = duration

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '生成成功',
            'data': {
                'recordId': record.id,
                'content': result
            }
        })

    except TimeoutError as e:
        # 处理超时错误
        logger.error(f"生成思维导图超时: paper_id={paper_id}, user_id={user_id}, error={str(e)}")
        if record:
            record.status = 'failed'
            record.error_message = f'请求超时: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 408,
            'message': '请求超时，请检查网络连接后重试',
            'data': {'recordId': record.id if record else None}
        }), 408

    except ValueError as e:
        # 处理参数错误
        logger.error(f"生成思维导图参数错误: paper_id={paper_id}, user_id={user_id}, error={str(e)}")
        if record:
            record.status = 'failed'
            record.error_message = f'参数错误: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 400,
            'message': f'请求参数错误: {str(e)}',
            'data': {'recordId': record.id if record else None}
        }), 400

    except Exception as e:
        # 处理其他错误
        logger.error(f"生成思维导图失败: paper_id={paper_id}, user_id={user_id}, error={str(e)}", exc_info=True)
        if record:
            record.status = 'failed'
            record.error_message = f'生成失败: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 500,
            'message': '服务器错误，请稍后重试',
            'data': {'recordId': record.id if record else None}
        }), 500


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

    # 检查是否有进行中的相同请求
    existing = GenerateRecord.query.filter_by(
        user_id=user_id,
        paper_id=paper_id,
        type='timeline',
        status='generating'
    ).first()

    if existing:
        return jsonify({
            'code': 409,
            'message': '已有生成任务进行中，请稍后再试',
            'data': {'recordId': existing.id}
        }), 409

    try:
        start_time = datetime.now()

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
            'authors': paper.authors,
            'abstract': paper.abstract,
            'keywords': paper.keywords,
            'sections': paper.sections  # 添加章节数据
        }

        result = generator.generate_timeline(paper_info)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        record.content = json.dumps(result, ensure_ascii=False)
        record.status = 'completed'
        record.description = f'《{paper.title}》的研究时间线'
        record.duration = duration

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '生成成功',
            'data': {
                'recordId': record.id,
                'content': result
            }
        })

    except TimeoutError as e:
        logger.error(f"生成时间线超时: paper_id={paper_id}, user_id={user_id}, error={str(e)}")
        if record:
            record.status = 'failed'
            record.error_message = f'请求超时: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 408,
            'message': '请求超时，请检查网络连接后重试',
            'data': {'recordId': record.id if record else None}
        }), 408

    except ValueError as e:
        logger.error(f"生成时间线参数错误: paper_id={paper_id}, user_id={user_id}, error={str(e)}")
        if record:
            record.status = 'failed'
            record.error_message = f'参数错误: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 400,
            'message': f'请求参数错误: {str(e)}',
            'data': {'recordId': record.id if record else None}
        }), 400

    except Exception as e:
        logger.error(f"生成时间线失败: paper_id={paper_id}, user_id={user_id}, error={str(e)}", exc_info=True)
        if record:
            record.status = 'failed'
            record.error_message = f'生成失败: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 500,
            'message': '服务器错误，请稍后重试',
            'data': {'recordId': record.id if record else None}
        }), 500


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

    # 检查是否有进行中的相同请求
    existing = GenerateRecord.query.filter_by(
        user_id=user_id,
        paper_id=paper_id,
        type='graph',
        status='generating'
    ).first()

    if existing:
        return jsonify({
            'code': 409,
            'message': '已有生成任务进行中，请稍后再试',
            'data': {'recordId': existing.id}
        }), 409

    try:
        start_time = datetime.now()

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
            'authors': paper.authors,
            'abstract': paper.abstract,
            'keywords': paper.keywords,
            'sections': paper.sections  # 添加章节数据
        }

        result = generator.generate_graph(paper_info)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        record.content = json.dumps(result, ensure_ascii=False)
        record.status = 'completed'
        record.description = f'《{paper.title}》的概念图谱'
        record.duration = duration

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '生成成功',
            'data': {
                'recordId': record.id,
                'content': result
            }
        })

    except TimeoutError as e:
        logger.error(f"生成概念图谱超时: paper_id={paper_id}, user_id={user_id}, error={str(e)}")
        if record:
            record.status = 'failed'
            record.error_message = f'请求超时: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 408,
            'message': '请求超时，请检查网络连接后重试',
            'data': {'recordId': record.id if record else None}
        }), 408

    except ValueError as e:
        logger.error(f"生成概念图谱参数错误: paper_id={paper_id}, user_id={user_id}, error={str(e)}")
        if record:
            record.status = 'failed'
            record.error_message = f'参数错误: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 400,
            'message': f'请求参数错误: {str(e)}',
            'data': {'recordId': record.id if record else None}
        }), 400

    except Exception as e:
        logger.error(f"生成概念图谱失败: paper_id={paper_id}, user_id={user_id}, error={str(e)}", exc_info=True)
        if record:
            record.status = 'failed'
            record.error_message = f'生成失败: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 500,
            'message': '服务器错误，请稍后重试',
            'data': {'recordId': record.id if record else None}
        }), 500


@bp.route('/review', methods=['POST'])
@jwt_required()
def generate_review():
    """生成论文评审报告（基于学术要素完整性评分）"""
    user_id = get_jwt_identity()
    data = request.get_json()
    paper_id = data.get('paperId')

    if not paper_id:
        return jsonify({'code': 400, 'message': '论文ID不能为空'}), 400

    paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
    if not paper:
        return jsonify({'code': 404, 'message': '论文不存在'}), 404

    # 检查是否有进行中的相同请求
    existing = GenerateRecord.query.filter_by(
        user_id=user_id,
        paper_id=paper_id,
        type='review',
        status='generating'
    ).first()

    if existing:
        return jsonify({
            'code': 409,
            'message': '已有生成任务进行中，请稍后再试',
            'data': {'recordId': existing.id}
        }), 409

    try:
        start_time = datetime.now()

        record = GenerateRecord(
            user_id=user_id,
            paper_id=paper_id,
            type='review',
            status='generating'
        )
        db.session.add(record)
        db.session.commit()

        generator = AIGenerator()
        paper_info = {
            'title': paper.title,
            'authors': paper.authors,
            'abstract': paper.abstract,
            'keywords': paper.keywords
        }

        print(f"[DEBUG] 开始为论文 {paper_id} 生成评审报告")
        result = generator.generate_review(paper_info)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        record.content = json.dumps(result, ensure_ascii=False)
        record.status = 'completed'
        record.description = f'《{paper.title}》的评审报告'
        record.duration = duration

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '生成成功',
            'data': {
                'recordId': record.id,
                'content': result
            }
        })

    except TimeoutError as e:
        logger.error(f"生成评审报告超时: paper_id={paper_id}, user_id={user_id}, error={str(e)}")
        if record:
            record.status = 'failed'
            record.error_message = f'请求超时: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 408,
            'message': '请求超时，请检查网络连接后重试',
            'data': {'recordId': record.id if record else None}
        }), 408

    except ValueError as e:
        logger.error(f"生成评审报告参数错误: paper_id={paper_id}, user_id={user_id}, error={str(e)}")
        if record:
            record.status = 'failed'
            record.error_message = f'参数错误: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 400,
            'message': f'请求参数错误: {str(e)}',
            'data': {'recordId': record.id if record else None}
        }), 400

    except Exception as e:
        logger.error(f"生成评审报告失败: paper_id={paper_id}, user_id={user_id}, error={str(e)}", exc_info=True)
        if record:
            record.status = 'failed'
            record.error_message = f'生成失败: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 500,
            'message': '服务器错误，请稍后重试',
            'data': {'recordId': record.id if record else None}
        }), 500


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

    # 检查是否有进行中的相同请求
    existing = GenerateRecord.query.filter_by(
        user_id=user_id,
        paper_id=paper_id,
        type='summary',
        status='generating'
    ).first()

    if existing:
        return jsonify({
            'code': 409,
            'message': '已有生成任务进行中，请稍后再试',
            'data': {'recordId': existing.id}
        }), 409

    try:
        start_time = datetime.now()

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
            'abstract': paper.abstract,
            'keywords': paper.keywords,
            'sections': paper.sections  # 添加章节数据
        }

        result = generator.generate_summary(paper_info)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        record.content = json.dumps(result, ensure_ascii=False)
        record.status = 'completed'
        record.description = f'《{paper.title}》的论文阅读报告'
        record.duration = duration

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '生成成功',
            'data': {
                'recordId': record.id,
                'content': result
            }
        })

    except TimeoutError as e:
        logger.error(f"生成论文阅读报告超时: paper_id={paper_id}, user_id={user_id}, error={str(e)}")
        if record:
            record.status = 'failed'
            record.error_message = f'请求超时: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 408,
            'message': '请求超时，请检查网络连接后重试',
            'data': {'recordId': record.id if record else None}
        }), 408

    except ValueError as e:
        logger.error(f"生成论文阅读报告参数错误: paper_id={paper_id}, user_id={user_id}, error={str(e)}")
        if record:
            record.status = 'failed'
            record.error_message = f'参数错误: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 400,
            'message': f'请求参数错误: {str(e)}',
            'data': {'recordId': record.id if record else None}
        }), 400

    except Exception as e:
        logger.error(f"生成论文阅读报告失败: paper_id={paper_id}, user_id={user_id}, error={str(e)}", exc_info=True)
        if record:
            record.status = 'failed'
            record.error_message = f'生成失败: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 500,
            'message': '服务器错误，请稍后重试',
            'data': {'recordId': record.id if record else None}
        }), 500


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
