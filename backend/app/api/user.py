from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db, User

bp = Blueprint('user', __name__)


@bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401

    # 生成token
    access_token = create_access_token(identity=user.id)

    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'token': access_token,
            'userInfo': user.to_dict()
        }
    })


@bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    # 验证输入
    if not username or not email or not password:
        return jsonify({'code': 400, 'message': '用户名、邮箱和密码不能为空'}), 400

    if len(username) < 3 or len(username) > 20:
        return jsonify({'code': 400, 'message': '用户名长度为3-20个字符'}), 400

    if len(password) < 6 or len(password) > 20:
        return jsonify({'code': 400, 'message': '密码长度为6-20个字符'}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400

    # 检查邮箱是否已存在
    if User.query.filter_by(email=email).first():
        return jsonify({'code': 400, 'message': '邮箱已被注册'}), 400

    # 创建用户
    user = User(username=username, email=email)
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()

        # 生成token
        access_token = create_access_token(identity=user.id)

        return jsonify({
            'code': 200,
            'message': '注册成功',
            'data': {
                'token': access_token,
                'userInfo': user.to_dict()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'注册失败: {str(e)}'}), 500


@bp.route('/info', methods=['GET'])
@jwt_required()
def get_user_info():
    """获取用户信息"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': user.to_dict()
    })


@bp.route('/info', methods=['PUT'])
@jwt_required()
def update_user_info():
    """更新用户信息"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    data = request.get_json()

    # 更新邮箱
    if 'email' in data:
        email = data['email'].strip()
        if email:
            # 检查邮箱是否被其他用户使用
            existing = User.query.filter_by(email=email).first()
            if existing and existing.id != user_id:
                return jsonify({'code': 400, 'message': '邮箱已被其他用户使用'}), 400
            user.email = email

    # 更新头像
    if 'avatar' in data:
        user.avatar = data['avatar']

    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500


@bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    """修改密码"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    data = request.get_json()
    old_password = data.get('oldPassword', '')
    new_password = data.get('newPassword', '')

    if not old_password or not new_password:
        return jsonify({'code': 400, 'message': '旧密码和新密码不能为空'}), 400

    if len(new_password) < 6 or len(new_password) > 20:
        return jsonify({'code': 400, 'message': '新密码长度为6-20个字符'}), 400

    # 验证旧密码
    if not user.check_password(old_password):
        return jsonify({'code': 400, 'message': '旧密码错误'}), 400

    # 设置新密码
    user.set_password(new_password)

    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '密码修改成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'修改失败: {str(e)}'}), 500
