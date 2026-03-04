import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Paper, GenerateRecord
from app.services.ai_generator import AIGenerator

# 配置日志
logger = logging.getLogger(__name__)

bp = Blueprint('chat', __name__)


@bp.route('/translate', methods=['POST'])
@jwt_required()
def translate_paper():
    """翻译论文"""
    user_id = get_jwt_identity()
    data = request.get_json()
    paper_id = data.get('paperId')
    target_lang = data.get('targetLang', 'zh')  # 默认翻译成中文

    if not paper_id:
        return jsonify({'code': 400, 'message': '论文ID不能为空'}), 400

    # 获取论文
    paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
    if not paper:
        return jsonify({'code': 404, 'message': '论文不存在'}), 404

    # 检查是否有进行中的翻译任务
    existing = GenerateRecord.query.filter_by(
        user_id=user_id,
        paper_id=paper_id,
        type='translate',
        status='generating'
    ).first()

    if existing:
        return jsonify({
            'code': 409,
            'message': '已有翻译任务进行中，请稍后再试',
            'data': {'recordId': existing.id}
        }), 409

    try:
        start_time = datetime.now()
        logger.info(f"开始翻译: paper_id={paper_id}, user_id={user_id}, target_lang={target_lang}")

        # 创建生成记录
        record = GenerateRecord(
            user_id=user_id,
            paper_id=paper_id,
            type='translate',
            status='generating'
        )
        db.session.add(record)
        db.session.commit()

        # 调用AI翻译
        generator = AIGenerator()
        paper_info = {
            'title': paper.title,
            'authors': paper.authors,
            'abstract': paper.abstract,
            'keywords': paper.keywords,
            'sections': paper.sections,
            'filepath': paper.filepath  # 添加文件路径
        }

        logger.info(f"调用AI翻译服务: filepath={paper.filepath}")
        result = generator.translate_paper(paper_info, target_lang)
        logger.info(f"AI翻译完成: 原文段数={len(result.get('originalSections', []))}, 译文长度={len(result.get('translatedContent', ''))}")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 更新记录 - 保存翻译内容
        record.content = result.get('translatedContent', '')
        record.status = 'completed'
        record.description = f'《{paper.title}》的翻译'
        record.duration = duration

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '翻译成功',
            'data': {
                'recordId': record.id,
                'originalSections': result.get('originalSections', []),
                'translatedContent': result.get('translatedContent', '')
            }
        })

    except TimeoutError as e:
        logger.error(f"翻译超时: paper_id={paper_id}, user_id={user_id}, error={str(e)}")
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
        logger.error(f"翻译参数错误: paper_id={paper_id}, user_id={user_id}, error={str(e)}")
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
        logger.error(f"翻译失败: paper_id={paper_id}, user_id={user_id}, error={str(e)}", exc_info=True)
        if record:
            record.status = 'failed'
            record.error_message = f'翻译失败: {str(e)}'
            db.session.commit()

        return jsonify({
            'code': 500,
            'message': '服务器错误，请稍后重试',
            'data': {'recordId': record.id if record else None}
        }), 500


@bp.route('/papers', methods=['POST'])
@jwt_required()
def chat_with_papers():
    """与论文知识库对话"""
    user_id = get_jwt_identity()
    data = request.get_json()

    question = data.get('question', '')
    conversation_history = data.get('history', [])

    if not question:
        return jsonify({'code': 400, 'message': '问题不能为空'}), 400

    try:
        # 获取用户的所有已解析论文
        papers = Paper.query.filter_by(
            user_id=user_id,
            status='parsed'
        ).order_by(Paper.upload_time.desc()).all()

        if not papers:
            return jsonify({
                'code': 404,
                'message': '暂无论文，请先上传论文'
            }), 404

        # 构建论文信息列表
        papers_info = []
        for paper in papers:
            paper_dict = {
                'title': paper.title,
                'abstract': paper.abstract,
                'keywords': paper.keywords
            }
            papers_info.append(paper_dict)

        # 调用AI对话
        generator = AIGenerator()
        answer = generator.chat_with_papers(question, papers_info, conversation_history)

        return jsonify({
            'code': 200,
            'message': '对话成功',
            'data': {
                'answer': answer,
                'papersCount': len(papers)
            }
        })

    except TimeoutError as e:
        logger.error(f"对话超时: user_id={user_id}, error={str(e)}")
        return jsonify({
            'code': 408,
            'message': '请求超时，请检查网络连接后重试'
        }), 408

    except Exception as e:
        logger.error(f"对话失败: user_id={user_id}, error={str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': '服务器错误，请稍后重试'
        }), 500


@bp.route('/papers/<int:paper_id>', methods=['POST'])
@jwt_required()
def chat_with_paper():
    """与单篇论文对话"""
    user_id = get_jwt_identity()
    data = request.get_json()

    question = data.get('question', '')
    conversation_history = data.get('history', [])

    if not question:
        return jsonify({'code': 400, 'message': '问题不能为空'}), 400

    # 获取论文
    paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
    if not paper:
        return jsonify({'code': 404, 'message': '论文不存在'}), 404

    if paper.status != 'parsed':
        return jsonify({'code': 400, 'message': '论文尚未解析完成'}), 400

    try:
        # 构建论文信息
        papers_info = [{
            'title': paper.title,
            'abstract': paper.abstract,
            'keywords': paper.keywords
        }]

        # 调用AI对话
        generator = AIGenerator()
        answer = generator.chat_with_papers(question, papers_info, conversation_history)

        return jsonify({
            'code': 200,
            'message': '对话成功',
            'data': {
                'answer': answer
            }
        })

    except TimeoutError as e:
        logger.error(f"对话超时: paper_id={paper_id}, user_id={user_id}, error={str(e)}")
        return jsonify({
            'code': 408,
            'message': '请求超时，请检查网络连接后重试'
        }), 408

    except Exception as e:
        logger.error(f"对话失败: paper_id={paper_id}, user_id={user_id}, error={str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': '服务器错误，请稍后重试'
        }), 500
