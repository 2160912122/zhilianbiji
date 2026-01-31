import os
import uuid
import json
import logging
from datetime import datetime,date,timedelta
from sqlalchemy import Date,cast
from functools import wraps
from flask import Flask, request, jsonify, session, send_from_directory,request
from functools import wraps
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_apscheduler import APScheduler
from zhipuai import ZhipuAI
from dotenv import load_dotenv

from config import config
from models import (
    db, bcrypt, User, Note,NoteVersion, Category, Tag, ShareLink,
    Flowchart, TableDocument, Whiteboard, Mindmap,
    FlowchartVersion, TableDocumentVersion, WhiteboardVersion, MindmapVersion,
    generate_unique_name, note_tag, flowchart_tag  # 补全关联表导入
)

load_dotenv()

app = Flask(__name__)
app.config.from_object(config['default'])

# 补充默认配置（防止config缺失）
app.config.setdefault('CORS_ORIGINS', '*')
app.config.setdefault('UPLOAD_FOLDER', 'uploads')
app.config.setdefault('ZHIPUAI_API_KEY', os.getenv('ZHIPUAI_API_KEY', ''))
app.config.setdefault('ZHIPUAI_MODEL', 'glm-4')
# 使用与config.py一致的JWT密钥
app.config.setdefault('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 优化CORS配置：允许凭证、所有方法、必要请求头
CORS(app,
     origins=app.config['CORS_ORIGINS'],
     supports_credentials=True,
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'])

scheduler = APScheduler()
scheduler.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@login_manager.user_loader
def load_user(user_id):
    """用户加载函数：兼容新旧SQLAlchemy版本"""
    try:
        return db.session.get(User, int(user_id))
    except Exception as e:
        logger.warning(f"用户加载失败（降级查询）: {e}")
        return User.query.get(int(user_id))


# -------------------------- 核心修改：重构管理员权限装饰器 --------------------------
def admin_required(f):
    """兼容JWT和Flask-Login的管理员权限校验"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 优先校验JWT（API请求）
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            # 调试信息
            logger.debug(f"JWT校验成功，用户ID: {user_id}, 用户: {user}, 管理员权限: {user.is_admin if user else None}")
            if not user:
                return jsonify({'message': '用户不存在'}), 403
            if not user.is_admin:
                return jsonify({'message': '需要管理员权限'}), 403
        # 降级到Flask-Login（会话登录）
        except Exception as e:
            logger.debug(f"JWT校验失败，降级到会话登录: {e}")
            logger.debug(f"会话登录状态: {current_user.is_authenticated}, 管理员权限: {current_user.is_admin if current_user.is_authenticated else None}")
            if not current_user.is_authenticated or not current_user.is_admin:
                return jsonify({'message': '请先登录并拥有管理员权限'}), 401
        return f(*args, **kwargs)

    return decorated_function


def call_zhipu(prompt, system_message=""):
    """调用智谱AI接口"""
    try:
        api_key = app.config['ZHIPUAI_API_KEY']
        model = app.config['ZHIPUAI_MODEL']

        if not api_key:
            logger.error("未设置ZHIPUAI_API_KEY环境变量")
            return None

        client = ZhipuAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2048
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"智谱AI调用失败：{str(e)}")
        return None


# -------------------------- 基础接口 --------------------------
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok', 'message': '服务正常运行'}), 200


@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    email = data.get('email', '').strip()

    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
    if len(username) < 3:
        return jsonify({'message': '用户名至少3个字符'}), 400
    if len(password) < 6:
        return jsonify({'message': '密码至少6个字符'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400

    user = User(username=username, email=email)
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': '注册成功'}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"注册失败: {str(e)}")
        return jsonify({'message': '注册失败'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        user.last_login = datetime.now()
        db.session.commit()

        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'code': 200,  # 新增code字段，匹配前端预期
            'msg': '登录成功',
            'data': {
                'token': access_token,  # 改用实际的access_token变量
                'userId': user.id,
                'username': user.username,
                'is_admin': 1 if user.is_admin else 0
            }
        }), 200

    return jsonify({'message': '用户名或密码错误'}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    """支持JWT和会话的登出接口"""
    try:
        # 尝试JWT登出（清除token在前端处理）
        verify_jwt_in_request(optional=True)
        # 尝试会话登出
        if current_user.is_authenticated:
            logout_user()
        return jsonify({'message': '登出成功'}), 200
    except Exception as e:
        logger.debug(f"登出错误: {e}")
        # 即使出错也返回成功，因为前端会清除token
        return jsonify({'message': '登出成功'}), 200


@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify({'user': user.to_dict()}), 200


@app.route('/api/user', methods=['PUT'])
@jwt_required()
def update_user():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    data = request.json

    if 'username' in data:
        if User.query.filter(User.username == data['username'], User.id != user_id).first():
            return jsonify({'message': '用户名已存在'}), 400
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']

    try:
        db.session.commit()
        return jsonify({'message': '更新成功', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新用户失败: {e}")
        return jsonify({'message': '更新失败'}), 500


# -------------------------- 分类接口 --------------------------
@app.route('/api/categories', methods=['GET'])
@jwt_required()
def get_categories():
    user_id = get_jwt_identity()
    categories = Category.query.filter_by(user_id=user_id).all()
    return jsonify([cat.to_dict() for cat in categories]), 200


@app.route('/api/categories', methods=['POST'])
@jwt_required()
def create_category():
    user_id = get_jwt_identity()
    data = request.json
    name = data.get('name', '').strip()

    if not name:
        return jsonify({'message': '分类名称不能为空'}), 400

    category = Category(name=name, user_id=user_id)

    try:
        db.session.add(category)
        db.session.commit()
        return jsonify({'message': '创建成功', 'category': category.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建分类失败: {e}")
        return jsonify({'message': '创建失败'}), 500


@app.route('/api/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    user_id = get_jwt_identity()
    category = Category.query.filter_by(id=category_id, user_id=user_id).first_or_404()
    data = request.json

    if 'name' in data:
        category.name = data['name']

    try:
        db.session.commit()
        return jsonify({'message': '更新成功', 'category': category.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新分类失败: {e}")
        return jsonify({'message': '更新失败'}), 500


@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    user_id = get_jwt_identity()
    category = Category.query.filter_by(id=category_id, user_id=user_id).first_or_404()

    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除分类失败: {e}")
        return jsonify({'message': '删除失败'}), 500


# -------------------------- 标签接口 --------------------------
@app.route('/api/tags', methods=['GET'])
@jwt_required()
def get_tags():
    user_id = get_jwt_identity()
    tags = Tag.query.filter_by(user_id=user_id).all()
    return jsonify([tag.to_dict() for tag in tags]), 200


@app.route('/api/tags', methods=['POST'])
@jwt_required()
def create_tag():
    user_id = get_jwt_identity()
    data = request.json
    name = data.get('name', '').strip()

    if not name:
        return jsonify({'message': '标签名称不能为空'}), 400

    existing_tag = Tag.query.filter_by(name=name, user_id=user_id).first()
    if existing_tag:
        return jsonify({'message': '标签已存在', 'tag': existing_tag.to_dict()}), 200

    tag = Tag(name=name, user_id=user_id)

    try:
        db.session.add(tag)
        db.session.commit()
        return jsonify({'message': '创建成功', 'tag': tag.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建标签失败: {e}")
        return jsonify({'message': '创建失败'}), 500


@app.route('/api/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    user_id = get_jwt_identity()
    tag = Tag.query.filter_by(id=tag_id, user_id=user_id).first_or_404()

    try:
        db.session.delete(tag)
        db.session.commit()
        return jsonify({'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除标签失败: {e}")
        return jsonify({'message': '删除失败'}), 500


# -------------------------- 笔记接口 --------------------------
@app.route('/api/notes', methods=['GET'])
@jwt_required()
def get_notes():
    user_id = get_jwt_identity()
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id')
    tag_ids = request.args.get('tag_ids', '').strip()
    note_type = request.args.get('type', '').strip()

    query = Note.query.filter_by(user_id=user_id)

    if search:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Note.title.ilike(f'%{search}%'),
                Note.content.ilike(f'%{search}%')
            )
        )

    if category_id:
        query = query.filter_by(category_id=int(category_id))

    if note_type:
        query = query.filter_by(type=note_type)

    if tag_ids:
        tag_id_list = [int(tid) for tid in tag_ids.split(',') if tid.isdigit()]
        if tag_id_list:
            from sqlalchemy import func
            note_ids = db.session.query(Note.id).join(
                note_tag, Note.id == note_tag.c.note_id
            ).filter(
                note_tag.c.tag_id.in_(tag_id_list)
            ).group_by(Note.id).having(
                func.count(note_tag.c.tag_id) == len(tag_id_list)
            ).all()
            note_ids = [nid[0] for nid in note_ids]
            if note_ids:
                query = query.filter(Note.id.in_(note_ids))
            else:
                return jsonify([]), 200

    notes = query.order_by(Note.updated_at.desc()).all()
    return jsonify([note.to_dict(include_content=False) for note in notes]), 200


@app.route('/api/notes', methods=['POST'])
@jwt_required()
def create_note():
    user_id = get_jwt_identity()
    data = request.json

    base_title = data.get('title', '').strip() or '未命名笔记'
    existing_notes = Note.query.filter_by(user_id=user_id).all()
    existing_titles = [n.title for n in existing_notes]
    unique_title = generate_unique_name(base_title, existing_titles)

    note = Note(
        title=unique_title,
        content=data.get('content', ''),
        type=data.get('type', 'richtext'),
        user_id=user_id,
        category_id=data.get('category_id'),
        is_public=data.get('is_public', False)
    )

    try:
        db.session.add(note)
        db.session.flush()

        if 'tags' in data and data['tags']:
            for tag_data in data['tags']:
                tag = None
                if 'id' in tag_data:
                    tag = Tag.query.filter_by(id=tag_data['id'], user_id=user_id).first()
                elif 'name' in tag_data:
                    tag = Tag.query.filter_by(name=tag_data['name'], user_id=user_id).first()
                    if not tag:
                        tag = Tag(name=tag_data['name'], user_id=user_id)
                        db.session.add(tag)
                        db.session.flush()

                if tag:
                    note.tags.append(tag)

        db.session.commit()
        return jsonify({'message': '创建成功', 'note': note.to_full_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建笔记失败: {str(e)}")
        return jsonify({'message': '创建失败'}), 500


@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except:
        user_id = None

    note = Note.query.get_or_404(note_id)

    if not note.is_public and (not user_id or note.user_id != int(user_id)):
        return jsonify({'message': '无权访问'}), 403

    return jsonify({'note': note.to_full_dict()}), 200


@app.route('/api/notes/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()
    data = request.json

    if 'title' in data:
        note.title = data['title']
    if 'content' in data:
        note.content = data['content']
    if 'type' in data:
        note.type = data['type']
    if 'category_id' in data:
        note.category_id = data['category_id']
    if 'is_public' in data:
        note.is_public = data['is_public']

    if 'tags' in data:
        note.tags.clear()
        for tag_data in data['tags']:
            tag = None
            if 'id' in tag_data:
                tag = Tag.query.filter_by(id=tag_data['id'], user_id=user_id).first()
            elif 'name' in tag_data:
                tag = Tag.query.filter_by(name=tag_data['name'], user_id=user_id).first()
                if not tag:
                    tag = Tag(name=tag_data['name'], user_id=user_id)
                    db.session.add(tag)
                    db.session.flush()

            if tag:
                note.tags.append(tag)

    note.updated_at = datetime.now()

    try:
        note.save_version(user_id)
        db.session.commit()
        return jsonify({'message': '更新成功', 'note': note.to_full_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新笔记失败: {e}")
        return jsonify({'message': '更新失败'}), 500


@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()

    try:
        db.session.delete(note)
        db.session.commit()
        return jsonify({'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除笔记失败: {e}")
        return jsonify({'message': '删除失败'}), 500


@app.route('/api/notes/<int:note_id>/versions', methods=['GET'])
@jwt_required()
def get_note_versions(note_id):
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()
    versions = NoteVersion.query.filter_by(note_id=note_id).order_by(NoteVersion.updated_at.desc()).all()

    return jsonify([{
        'id': v.id,
        'content': v.content,
        'updater': {'username': v.updater.username},
        'updated_at': v.updated_at.isoformat() if v.updated_at else None,
        'content_preview': v.content[:150] + '...' if len(v.content) > 150 else v.content
    } for v in versions]), 200


@app.route('/api/notes/<int:note_id>/versions', methods=['POST'])
@jwt_required()
def save_note_version(note_id):
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()

    version = NoteVersion(
        note_id=note.id,
        content=note.content or '',
        updater_id=user_id
    )

    try:
        db.session.add(version)
        db.session.commit()
        return jsonify({'message': '版本保存成功'}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"保存笔记版本失败: {e}")
        return jsonify({'message': '保存失败'}), 500


@app.route('/api/notes/<int:note_id>/versions/<int:version_id>/rollback', methods=['POST'])
@jwt_required()
def rollback_note_version(note_id, version_id):
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()
    version = NoteVersion.query.filter_by(id=version_id, note_id=note_id).first_or_404()

    note.save_version(user_id)
    note.content = version.content
    note.updated_at = datetime.now()

    try:
        db.session.commit()
        return jsonify({'message': '回滚成功'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"回滚笔记版本失败: {e}")
        return jsonify({'message': '回滚失败'}), 500


# -------------------------- 笔记分享接口 --------------------------
@app.route('/api/notes/<int:note_id>/share', methods=['POST'])
@jwt_required()
def share_note(note_id):
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()
    data = request.json

    permission = data.get('permission', 'view')
    expires_at_str = data.get('expire_at')

    if permission not in ('view', 'edit'):
        return jsonify({'message': '无效的权限类型'}), 400

    token = str(uuid.uuid4())

    expire_at = None
    if expires_at_str:
        try:
            expire_at = datetime.fromisoformat(expires_at_str)
            expire_at = expire_at.replace(tzinfo=None)
        except ValueError as e:
            logger.error(f"有效期解析错误: {e}, 输入: {expires_at_str}")
            return jsonify({'message': '无效的有效期格式'}), 400

    share_link = ShareLink(
        note_id=note.id,
        token=token,
        permission=permission,
        expire_at=expire_at
    )

    try:
        db.session.add(share_link)
        db.session.commit()

        return jsonify({
            'share_url': f'/share/{token}',
            'token': token,
            'permission': permission,
            'expire_at': expire_at.isoformat() if expire_at else None
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建分享链接失败: {str(e)}")
        return jsonify({'message': '创建分享链接失败'}), 500


@app.route('/api/notes/<int:note_id>/shares', methods=['GET'])
@jwt_required()
def get_shares(note_id):
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()
    shares = ShareLink.query.filter_by(note_id=note.id).all()

    result = []
    for share in shares:
        result.append({
            'token': share.token,
            'share_url': f'/share/{share.token}',
            'permission': share.permission,
            'created_at': share.created_at.isoformat() if share.created_at else None,
            'expire_at': share.expire_at.isoformat() if share.expire_at else None
        })

    return jsonify(result)


@app.route('/api/shares/<token>', methods=['DELETE'])
@jwt_required()
def delete_share(token):
    user_id = get_jwt_identity()
    share = ShareLink.query.filter_by(token=token).first_or_404()
    
    # 检查分享链接属于当前用户的笔记、流程图或脑图
    if share.note_id:
        Note.query.filter_by(id=share.note_id, user_id=user_id).first_or_404()
    elif share.flowchart_id:
        Flowchart.query.filter_by(id=share.flowchart_id, user_id=user_id).first_or_404()
    elif share.mindmap_id:
        Mindmap.query.filter_by(id=share.mindmap_id, user_id=user_id).first_or_404()
    else:
        return jsonify({'message': '无效的分享链接'}), 400

    db.session.delete(share)
    db.session.commit()

    return jsonify({'message': '分享链接已删除'})


@app.route('/api/share/<token>', methods=['GET'])
def get_shared_content(token):
    share_link = ShareLink.query.filter_by(token=token).first()

    if not share_link:
        return jsonify({'message': '分享链接不存在'}), 404

    if share_link.expire_at and share_link.expire_at < datetime.now():
        return jsonify({'message': '分享链接已过期'}), 404

    if share_link.note_id:
        note = share_link.note
        return jsonify({
            'type': 'note',
            'note': note.to_full_dict(),
            'permission': share_link.permission
        }), 200
    elif share_link.flowchart_id:
        flowchart = share_link.flowchart
        return jsonify({
            'type': 'flowchart',
            'flowchart': flowchart.to_dict(),
            'permission': share_link.permission
        }), 200
    elif share_link.mindmap_id:
        mindmap = share_link.mindmap
        return jsonify({
            'type': 'mindmap',
            'mindmap': mindmap.to_dict(),
            'permission': share_link.permission
        }), 200
    else:
        return jsonify({'message': '无效的分享链接'}), 400


# -------------------------- AI接口 --------------------------
@app.route('/api/ai/generate', methods=['POST'])
@jwt_required()
def ai_generate():
    data = request.json
    topic = data.get('topic', '')

    if not topic:
        return jsonify({'message': '请输入主题'}), 400

    prompt = f"请围绕「{topic}」生成一篇详细笔记，结构清晰（分点或分段），内容详实，适合保存为个人笔记。"
    system_msg = "你是专业的笔记生成助手，生成内容需逻辑连贯、重点突出，避免冗余。"

    content = call_zhipu(prompt, system_msg)

    if not content:
        return jsonify({'message': 'AI生成失败，请重试'}), 500

    return jsonify({
        'content': content,
        'suggested_title': topic
    }), 200


@app.route('/api/ai/summarize', methods=['POST'])
@jwt_required()
def ai_summarize():
    data = request.json
    content = data.get('content', '')

    if not content:
        return jsonify({'message': '请提供需要总结的内容'}), 400

    prompt = f"请总结以下笔记内容（不超过300字，提炼核心观点，分点说明更佳）：\n\n{content}"
    system_msg = "你是专业的内容总结专家，总结需简洁、准确，覆盖笔记关键信息。"

    summary = call_zhipu(prompt, system_msg)

    return jsonify({'summary': summary or '未生成有效总结，请重试'}), 200


@app.route('/api/ai/suggest_tags', methods=['POST'])
@jwt_required()
def ai_suggest_tags():
    data = request.json
    content = data.get('content', '')

    if not content:
        return jsonify({'message': '请提供笔记内容'}), 400

    content_preview = content[:500]

    prompt = f"""请为以下笔记内容推荐3-5个相关标签，要求：
    1. 标签简洁明了，1-4个汉字
    2. 覆盖内容的核心主题
    3. 用中文逗号分隔，不要编号和解释

    笔记内容：
    {content_preview}

    推荐标签："""

    system_msg = "你是专业的标签推荐助手，只返回用中文逗号分隔的标签，不要任何其他文字。"

    tags_str = call_zhipu(prompt, system_msg)

    if tags_str:
        tags_str = tags_str.replace('推荐标签：', '').replace('标签：', '')
        tags_str = tags_str.strip('。.，, ')

        tags = []
        for tag in tags_str.split(','):
            tag = tag.strip()
            if tag and len(tag) <= 4:
                tags.append(tag)

        tags = list(dict.fromkeys(tags))[:5]
    else:
        tags = []

    if not tags:
        tags = ['学习', '笔记', '知识']

    return jsonify({'tags': tags}), 200


# -------------------------- 表格接口 --------------------------
@app.route('/api/tables', methods=['GET'])
@jwt_required()
def get_tables():
    user_id = get_jwt_identity()
    tables = TableDocument.query.filter_by(user_id=user_id).order_by(TableDocument.updated_at.desc()).all()
    return jsonify([table.to_dict() for table in tables]), 200


@app.route('/api/tables', methods=['POST'])
@jwt_required()
def create_table():
    user_id = get_jwt_identity()
    data = request.json

    base_title = data.get('title', '').strip() or '新表格'
    existing_tables = TableDocument.query.filter_by(user_id=user_id).all()
    existing_titles = [t.title for t in existing_tables]
    unique_title = generate_unique_name(base_title, existing_titles)

    table = TableDocument(
        title=unique_title,
        columns_data=data.get('columns', ['列1', '列2', '列3']),
        rows_data=data.get('rows', [['', '', ''], ['', '', ''], ['', '', '']]),
        cell_styles=data.get('cellStyles', {}),
        user_id=user_id
    )

    try:
        db.session.add(table)
        db.session.commit()
        return jsonify({'message': '创建成功', 'table': table.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建表格失败: {e}")
        return jsonify({'message': '创建失败'}), 500


@app.route('/api/tables/<int:table_id>', methods=['GET'])
@jwt_required()
def get_table(table_id):
    user_id = get_jwt_identity()
    table = TableDocument.query.filter_by(id=table_id, user_id=user_id).first_or_404()
    return jsonify({'table': table.to_dict()}), 200


@app.route('/api/tables/<int:table_id>', methods=['PUT'])
@jwt_required()
def update_table(table_id):
    user_id = get_jwt_identity()
    table = TableDocument.query.filter_by(id=table_id, user_id=user_id).first_or_404()
    data = request.json

    if 'title' in data:
        table.title = data['title']
    if 'columns' in data:
        table.columns_data = data['columns']
    if 'rows' in data:
        table.rows_data = data['rows']
    if 'cellStyles' in data:
        table.cell_styles = data['cellStyles']

    table.updated_at = datetime.now()

    try:
        table.save_version(user_id)
        db.session.commit()
        return jsonify({'message': '更新成功', 'table': table.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新表格失败: {e}")
        return jsonify({'message': '更新失败'}), 500


@app.route('/api/tables/<int:table_id>', methods=['DELETE'])
@jwt_required()
def delete_table(table_id):
    user_id = get_jwt_identity()
    table = TableDocument.query.filter_by(id=table_id, user_id=user_id).first_or_404()

    try:
        db.session.delete(table)
        db.session.commit()
        return jsonify({'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除表格失败: {e}")
        return jsonify({'message': '删除失败'}), 500


@app.route('/api/tables/<int:table_id>/versions', methods=['GET'])
@jwt_required()
def get_table_versions(table_id):
    user_id = get_jwt_identity()
    table = TableDocument.query.filter_by(id=table_id, user_id=user_id).first_or_404()

    versions = TableDocumentVersion.query.filter_by(table_document_id=table_id).order_by(
        TableDocumentVersion.updated_at.desc()).all()
    return jsonify({'versions': [v.to_dict() for v in versions]}), 200


@app.route('/api/tables/<int:table_id>/versions/<int:version_id>', methods=['POST'])
@jwt_required()
def rollback_table_version(table_id, version_id):
    user_id = get_jwt_identity()
    table = TableDocument.query.filter_by(id=table_id, user_id=user_id).first_or_404()
    version = TableDocumentVersion.query.filter_by(id=version_id, table_document_id=table_id).first_or_404()

    table.columns_data = version.columns_data
    table.rows_data = version.rows_data
    table.cell_styles = version.cell_styles
    table.save_version(user_id)

    try:
        db.session.commit()
        return jsonify({'message': '回滚成功', 'table': table.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"回滚表格版本失败: {e}")
        return jsonify({'message': '回滚失败'}), 500


# -------------------------- 白板接口 --------------------------
@app.route('/api/whiteboards', methods=['GET'])
@jwt_required()
def get_whiteboards():
    user_id = get_jwt_identity()
    whiteboards = Whiteboard.query.filter_by(user_id=user_id).order_by(Whiteboard.updated_at.desc()).all()
    return jsonify([wb.to_dict() for wb in whiteboards]), 200


@app.route('/api/whiteboards', methods=['POST'])
@jwt_required()
def create_whiteboard():
    user_id = get_jwt_identity()
    data = request.json

    base_title = data.get('title', '').strip() or '新白板'
    existing_whiteboards = Whiteboard.query.filter_by(user_id=user_id).all()
    existing_titles = [w.title for w in existing_whiteboards]
    unique_title = generate_unique_name(base_title, existing_titles)

    whiteboard = Whiteboard(
        title=unique_title,
        room_key=str(uuid.uuid4())[:22],
        data=data.get('data', {}),
        user_id=user_id
    )

    try:
        db.session.add(whiteboard)
        db.session.commit()
        return jsonify({'message': '创建成功', 'whiteboard': whiteboard.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建白板失败: {e}")
        return jsonify({'message': '创建失败'}), 500


@app.route('/api/whiteboards/<int:whiteboard_id>', methods=['GET'])
@jwt_required()
def get_whiteboard(whiteboard_id):
    user_id = get_jwt_identity()
    whiteboard = Whiteboard.query.filter_by(id=whiteboard_id, user_id=user_id).first_or_404()
    return jsonify({'whiteboard': whiteboard.to_dict()}), 200


@app.route('/api/whiteboards/<int:whiteboard_id>', methods=['PUT'])
@jwt_required()
def update_whiteboard(whiteboard_id):
    user_id = get_jwt_identity()
    whiteboard = Whiteboard.query.filter_by(id=whiteboard_id, user_id=user_id).first_or_404()
    data = request.json

    if 'title' in data:
        whiteboard.title = data['title']
    if 'data' in data:
        whiteboard.data = data['data']

    whiteboard.updated_at = datetime.now()

    try:
        whiteboard.save_version(user_id)
        db.session.commit()
        return jsonify({'message': '更新成功', 'whiteboard': whiteboard.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新白板失败: {e}")
        return jsonify({'message': '更新失败'}), 500


@app.route('/api/whiteboards/<int:whiteboard_id>', methods=['DELETE'])
@jwt_required()
def delete_whiteboard(whiteboard_id):
    user_id = get_jwt_identity()
    whiteboard = Whiteboard.query.filter_by(id=whiteboard_id, user_id=user_id).first_or_404()

    try:
        db.session.delete(whiteboard)
        db.session.commit()
        return jsonify({'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除白板失败: {e}")
        return jsonify({'message': '删除失败'}), 500


@app.route('/api/whiteboards/<int:whiteboard_id>/versions', methods=['GET'])
@jwt_required()
def get_whiteboard_versions(whiteboard_id):
    user_id = get_jwt_identity()
    whiteboard = Whiteboard.query.filter_by(id=whiteboard_id, user_id=user_id).first_or_404()

    versions = WhiteboardVersion.query.filter_by(whiteboard_id=whiteboard_id).order_by(
        WhiteboardVersion.updated_at.desc()).all()
    return jsonify({'versions': [v.to_dict() for v in versions]}), 200


@app.route('/api/whiteboards/<int:whiteboard_id>/versions/<int:version_id>', methods=['POST'])
@jwt_required()
def rollback_whiteboard_version(whiteboard_id, version_id):
    user_id = get_jwt_identity()
    whiteboard = Whiteboard.query.filter_by(id=whiteboard_id, user_id=user_id).first_or_404()
    version = WhiteboardVersion.query.filter_by(id=version_id, whiteboard_id=whiteboard_id).first_or_404()

    whiteboard.data = version.data
    whiteboard.save_version(user_id)

    try:
        db.session.commit()
        return jsonify({'message': '回滚成功', 'whiteboard': whiteboard.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"回滚白板版本失败: {e}")
        return jsonify({'message': '回滚失败'}), 500


# -------------------------- 脑图接口（接续） --------------------------
@app.route('/api/mindmaps', methods=['GET'])
@jwt_required()
def get_mindmaps():
    user_id = get_jwt_identity()
    mindmaps = Mindmap.query.filter_by(user_id=user_id).order_by(Mindmap.updated_at.desc()).all()
    return jsonify([mm.to_dict() for mm in mindmaps]), 200


@app.route('/api/mindmaps', methods=['POST'])
@jwt_required()
def create_mindmap():
    user_id = get_jwt_identity()
    data = request.json

    base_title = data.get('title', '').strip() or '新脑图'
    existing_mindmaps = Mindmap.query.filter_by(user_id=user_id).all()
    existing_titles = [m.title for m in existing_mindmaps]
    unique_title = generate_unique_name(base_title, existing_titles)

    # 兼容前端发送的数据格式
    mindmap_data = data.get('data', {})

    mindmap = Mindmap(
        title=unique_title,
        data=mindmap_data,
        user_id=user_id
    )

    try:
        db.session.add(mindmap)
        db.session.commit()
        return jsonify({'message': '创建成功', 'mindmap': mindmap.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建脑图失败: {e}")
        return jsonify({'message': '创建失败'}), 500


@app.route('/api/mindmaps/<int:mindmap_id>', methods=['GET'])
@jwt_required()
def get_mindmap(mindmap_id):
    user_id = get_jwt_identity()
    mindmap = Mindmap.query.filter_by(id=mindmap_id, user_id=user_id).first_or_404()
    return jsonify({'mindmap': mindmap.to_dict()}), 200


@app.route('/api/mindmaps/<int:mindmap_id>', methods=['PUT'])
@jwt_required()
def update_mindmap(mindmap_id):
    user_id = get_jwt_identity()
    mindmap = Mindmap.query.filter_by(id=mindmap_id, user_id=user_id).first_or_404()
    data = request.json

    if 'title' in data:
        mindmap.title = data['title']
    # 兼容前端发送的数据格式
    if 'data' in data:
        mindmap.data = data['data']

    mindmap.updated_at = datetime.now()

    try:
        mindmap.save_version(user_id)
        db.session.commit()
        return jsonify({'message': '更新成功', 'mindmap': mindmap.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新脑图失败: {e}")
        return jsonify({'message': '更新失败'}), 500


@app.route('/api/mindmaps/<int:mindmap_id>', methods=['DELETE'])
@jwt_required()
def delete_mindmap(mindmap_id):
    user_id = get_jwt_identity()
    mindmap = Mindmap.query.filter_by(id=mindmap_id, user_id=user_id).first_or_404()

    try:
        db.session.delete(mindmap)
        db.session.commit()
        return jsonify({'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除脑图失败: {e}")
        return jsonify({'message': '删除失败'}), 500


@app.route('/api/mindmaps/<int:mindmap_id>/versions', methods=['GET'])
@jwt_required()
def get_mindmap_versions(mindmap_id):
    user_id = get_jwt_identity()
    mindmap = Mindmap.query.filter_by(id=mindmap_id, user_id=user_id).first_or_404()

    versions = MindmapVersion.query.filter_by(mindmap_id=mindmap_id).order_by(MindmapVersion.updated_at.desc()).all()
    return jsonify({'versions': [v.to_dict() for v in versions]}), 200


@app.route('/api/mindmaps/<int:mindmap_id>/versions/<int:version_id>', methods=['POST'])
@jwt_required()
def rollback_mindmap_version(mindmap_id, version_id):
    user_id = get_jwt_identity()
    mindmap = Mindmap.query.filter_by(id=mindmap_id, user_id=user_id).first_or_404()
    version = MindmapVersion.query.filter_by(id=version_id, mindmap_id=mindmap_id).first_or_404()

    # 回滚到指定版本
    mindmap.data = version.data

    try:
        db.session.commit()
        return jsonify({'message': '回滚成功', 'mindmap': mindmap.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"回滚脑图版本失败: {e}")
        return jsonify({'message': '回滚失败'}), 500


# -------------------------- 脑图分享接口 --------------------------
@app.route('/api/mindmaps/<int:mindmap_id>/share', methods=['POST'])
@jwt_required()
def share_mindmap(mindmap_id):
    user_id = get_jwt_identity()
    mindmap = Mindmap.query.filter_by(id=mindmap_id, user_id=user_id).first_or_404()
    data = request.json

    permission = data.get('permission', 'view')
    expires_at_str = data.get('expire_at')

    if permission not in ('view', 'edit'):
        return jsonify({'message': '无效的权限类型'}), 400

    token = str(uuid.uuid4())

    expire_at = None
    if expires_at_str:
        try:
            expire_at = datetime.fromisoformat(expires_at_str)
            expire_at = expire_at.replace(tzinfo=None)
        except ValueError as e:
            logger.error(f"有效期解析错误: {e}, 输入: {expires_at_str}")
            return jsonify({'message': '无效的有效期格式'}), 400

    share_link = ShareLink(
        mindmap_id=mindmap.id,
        token=token,
        permission=permission,
        expire_at=expire_at
    )

    try:
        db.session.add(share_link)
        db.session.commit()

        return jsonify({
            'share_url': f'/share/{token}',
            'token': token,
            'permission': permission,
            'expire_at': expire_at.isoformat() if expire_at else None
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建分享链接失败: {str(e)}")
        return jsonify({'message': '创建分享链接失败'}), 500


@app.route('/api/mindmaps/<int:mindmap_id>/shares', methods=['GET'])
@jwt_required()
def get_mindmap_shares(mindmap_id):
    user_id = get_jwt_identity()
    mindmap = Mindmap.query.filter_by(id=mindmap_id, user_id=user_id).first_or_404()
    shares = ShareLink.query.filter_by(mindmap_id=mindmap.id).all()

    result = []
    for share in shares:
        result.append({
            'token': share.token,
            'share_url': f'/share/{share.token}',
            'permission': share.permission,
            'created_at': share.created_at.isoformat() if share.created_at else None,
            'expire_at': share.expire_at.isoformat() if share.expire_at else None
        })

    return jsonify(result)


@app.route('/api/mindmaps/<int:mindmap_id>/shared', methods=['GET'])
def get_shared_mindmap(mindmap_id):
    mindmap = Mindmap.query.filter_by(id=mindmap_id).first_or_404()
    return jsonify({
        'mindmap': mindmap.to_dict()
    }), 200


# -------------------------- 流程图接口 --------------------------
@app.route('/api/flowcharts', methods=['GET'])
@jwt_required()
def get_flowcharts():
    user_id = get_jwt_identity()
    flowcharts = Flowchart.query.filter_by(user_id=user_id).order_by(Flowchart.updated_at.desc()).all()
    return jsonify([fc.to_dict() for fc in flowcharts]), 200


@app.route('/api/flowcharts', methods=['POST'])
@jwt_required()
def create_flowchart():
    user_id = get_jwt_identity()
    data = request.json

    base_title = data.get('title', '').strip() or '新流程图'
    existing_flowcharts = Flowchart.query.filter_by(user_id=user_id).all()
    existing_titles = [f.title for f in existing_flowcharts]
    unique_title = generate_unique_name(base_title, existing_titles)

    # 兼容前端发送的flow_data格式
    flow_data = data.get('flow_data', {})
    
    if not flow_data and ('nodes' in data or 'edges' in data):
        flow_data = {
            'nodes': data.get('nodes', []),
            'edges': data.get('edges', [])
        }
    
    flowchart = Flowchart(
        title=unique_title,
        flow_data=flow_data,
        user_id=user_id
    )

    try:
        db.session.add(flowchart)
        db.session.flush()

        if 'tags' in data and data['tags']:
            for tag_data in data['tags']:
                tag = None
                if 'id' in tag_data:
                    tag = Tag.query.filter_by(id=tag_data['id'], user_id=user_id).first()
                elif 'name' in tag_data:
                    tag = Tag.query.filter_by(name=tag_data['name'], user_id=user_id).first()
                    if not tag:
                        tag = Tag(name=tag_data['name'], user_id=user_id)
                        db.session.add(tag)
                        db.session.flush()

                if tag:
                    flowchart.tags.append(tag)

        db.session.commit()
        return jsonify({'message': '创建成功', 'flowchart': flowchart.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建流程图失败: {e}")
        return jsonify({'message': '创建失败'}), 500


@app.route('/api/flowcharts/<int:flowchart_id>', methods=['GET'])
@jwt_required()
def get_flowchart(flowchart_id):
    user_id = get_jwt_identity()
    flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first_or_404()
    return jsonify({'flowchart': flowchart.to_dict()}), 200


@app.route('/api/flowcharts/<int:flowchart_id>', methods=['PUT'])
@jwt_required()
def update_flowchart(flowchart_id):
    user_id = get_jwt_identity()
    flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first_or_404()
    data = request.json

    if 'title' in data:
        flowchart.title = data['title']
    
    # 兼容前端发送的flow_data格式
    if 'flow_data' in data:
        flowchart.flow_data = data['flow_data']
    
    # 兼容直接发送nodes和edges的格式
    elif 'nodes' in data or 'edges' in data:
        flow_data = flowchart.flow_data or {}
        flow_data['nodes'] = data.get('nodes', flow_data.get('nodes', []))
        flow_data['edges'] = data.get('edges', flow_data.get('edges', []))
        flowchart.flow_data = flow_data

    if 'tags' in data:
        flowchart.tags.clear()
        for tag_data in data['tags']:
            tag = None
            if 'id' in tag_data:
                tag = Tag.query.filter_by(id=tag_data['id'], user_id=user_id).first()
            elif 'name' in tag_data:
                tag = Tag.query.filter_by(name=tag_data['name'], user_id=user_id).first()
                if not tag:
                    tag = Tag(name=tag_data['name'], user_id=user_id)
                    db.session.add(tag)
                    db.session.flush()

            if tag:
                flowchart.tags.append(tag)

    flowchart.updated_at = datetime.now()

    try:
        flowchart.save_version(user_id)
        db.session.commit()
        return jsonify({'message': '更新成功', 'flowchart': flowchart.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新流程图失败: {e}")
        return jsonify({'message': '更新失败'}), 500


@app.route('/api/flowcharts/<int:flowchart_id>', methods=['DELETE'])
@jwt_required()
def delete_flowchart(flowchart_id):
    user_id = get_jwt_identity()
    flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first_or_404()

    try:
        db.session.delete(flowchart)
        db.session.commit()
        return jsonify({'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除流程图失败: {e}")
        return jsonify({'message': '删除失败'}), 500


@app.route('/api/flowcharts/<int:flowchart_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_flowchart(flowchart_id):
    user_id = get_jwt_identity()
    original_flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first_or_404()

    # 创建新的流程图副本
    base_title = f"{original_flowchart.title} (副本)"
    existing_flowcharts = Flowchart.query.filter_by(user_id=user_id).all()
    existing_titles = [f.title for f in existing_flowcharts]
    unique_title = generate_unique_name(base_title, existing_titles)

    new_flowchart = Flowchart(
        title=unique_title,
        flow_data=original_flowchart.flow_data,
        user_id=user_id
    )

    try:
        db.session.add(new_flowchart)
        db.session.commit()
        return jsonify({'message': '复制成功', 'flowchart': new_flowchart.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"复制流程图失败: {e}")
        return jsonify({'message': '复制失败'}), 500


@app.route('/api/flowcharts/<int:flowchart_id>/share', methods=['POST'])
@jwt_required()
def share_flowchart(flowchart_id):
    user_id = get_jwt_identity()
    flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first_or_404()
    data = request.json

    token = str(uuid.uuid4())
    days = data.get('days', 7)
    expire_at = datetime.now() + timedelta(days=days)

    share_link = ShareLink(
        flowchart_id=flowchart.id,
        token=token,
        permission='view',
        expire_at=expire_at
    )

    try:
        db.session.add(share_link)
        db.session.commit()

        return jsonify({
            'share_url': f'/share/{token}',
            'token': token,
            'expire_at': expire_at.isoformat()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建分享链接失败: {e}")
        return jsonify({'message': '创建分享链接失败'}), 500


@app.route('/api/flowcharts/<int:flowchart_id>/versions', methods=['GET'])
@jwt_required()
def get_flowchart_versions(flowchart_id):
    user_id = get_jwt_identity()
    flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first_or_404()

    versions = FlowchartVersion.query.filter_by(flowchart_id=flowchart_id).order_by(
        FlowchartVersion.updated_at.desc()).all()
    return jsonify({'versions': [v.to_dict() for v in versions]}), 200


@app.route('/api/flowcharts/<int:flowchart_id>/versions/<int:version_id>', methods=['POST'])
@jwt_required()
def rollback_flowchart_version(flowchart_id, version_id):
    user_id = get_jwt_identity()
    flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first_or_404()
    version = FlowchartVersion.query.filter_by(id=version_id, flowchart_id=flowchart_id).first_or_404()

    flowchart.nodes = version.nodes
    flowchart.edges = version.edges
    flowchart.save_version(user_id)

    try:
        db.session.commit()
        return jsonify({'message': '回滚成功', 'flowchart': flowchart.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"回滚流程图版本失败: {e}")
        return jsonify({'message': '回滚失败'}), 500


# -------------------------- 管理员接口 --------------------------
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    """管理员获取所有用户列表"""
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'is_admin': 1 if u.is_admin else 0,
        'created_at': u.created_at.isoformat(),
        'last_login': u.last_login.isoformat() if u.last_login else None
    } for u in users]), 200


@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    """管理员修改用户角色（设置/取消管理员）"""
    data = request.json
    is_admin = data.get('is_admin', False)

    user = User.query.get_or_404(user_id)
    user.is_admin = is_admin

    try:
        db.session.commit()
        return jsonify({'message': '用户角色更新成功', 'user': {
            'id': user.id,
            'username': user.username,
            'is_admin': user.is_admin
        }}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新用户角色失败: {e}")
        return jsonify({'message': '更新失败'}), 500

# ========== 1. 切换用户管理员状态接口（修正is_admin布尔值判断） ==========
@app.route('/api/admin/user/set_admin/<int:user_id>', methods=['POST'])
@admin_required
def set_admin(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

    # 修正：is_admin是布尔值（True/False），不是数字
    user.is_admin = not user.is_admin  # 直接取反，切换状态
    db.session.commit()

    # 返回清晰的提示（告诉前端切换后的状态）
    return jsonify({
        "code": 200,
        "msg": "设置成功",
        "data": {
            "user_id": user.id,
            "username": user.username,
            "is_admin": 1 if user.is_admin else 0  # 转数字方便前端处理
        }
    })


# ========== 2. 管理员仪表盘统计接口（删除重复定义，修正所有报错） ==========
@app.route('/api/admin/dashboard/stats', methods=['GET'])
@admin_required
def admin_dashboard_stats():
    """管理员仪表盘：全平台数据统计"""
    try:
        # 1. 统计总用户数
        user_count = User.query.count()

        # 2. 统计平台各类型内容总数（替换Table为TableDocument）
        total_notes = Note.query.count()
        total_tables = TableDocument.query.count()  # 修正：Table→TableDocument
        total_flowcharts = Flowchart.query.count()
        total_whiteboards = Whiteboard.query.count()
        total_mindmaps = Mindmap.query.count()
        
        # 计算总笔记数（包含所有类型）
        all_notes_count = total_notes + total_tables + total_flowcharts + total_whiteboards + total_mindmaps

        # 3. 统计今日新增内容（所有类型，修正cast使用方式）
        today = date.today()
        # 今日新增用户
        today_users = User.query.filter(cast(User.created_at, Date) == today).count()
        # 今日新增笔记（cast和Date已导入，不再报错）
        today_notes = Note.query.filter(cast(Note.created_at, Date) == today).count()
        # 今日新增表格（修正：Table→TableDocument）
        today_tables = TableDocument.query.filter(cast(TableDocument.created_at, Date) == today).count()
        # 今日新增流程图
        today_flowcharts = Flowchart.query.filter(cast(Flowchart.created_at, Date) == today).count()
        # 今日新增白板
        today_whiteboards = Whiteboard.query.filter(cast(Whiteboard.created_at, Date) == today).count()
        # 今日新增脑图
        today_mindmaps = Mindmap.query.filter(cast(Mindmap.created_at, Date) == today).count()

        # 4. 统计最近7天的用户增长数据
        recent_user_growth = []
        for i in range(6, -1, -1):
            target_date = today - timedelta(days=i)
            daily_user_count = User.query.filter(cast(User.created_at, Date) == target_date).count()
            recent_user_growth.append(daily_user_count)

        # 今日新增内容总数
        today_new = today_notes + today_tables + today_flowcharts + today_whiteboards + today_mindmaps

        return jsonify({
            'code': 200,
            'msg': '获取统计数据成功',
            'data': {
                'userCount': user_count,  # 总用户数
                'todayUsers': today_users,  # 今日新增用户数
                'totalNotes': all_notes_count,  # 总笔记数（包含所有类型）
                'normalNotes': total_notes,  # 普通笔记数
                'totalTables': total_tables,  # 总表格数
                'totalFlowcharts': total_flowcharts,  # 总流程图数
                'totalWhiteboards': total_whiteboards,  # 总白板数
                'totalMindmaps': total_mindmaps,  # 总脑图数
                'todayNew': today_new,  # 今日新增内容总数
                'recentUserGrowth': recent_user_growth,  # 最近7天的用户增长数据
                # 细分今日各类型新增（前端可展示）
                'todayNewDetail': {
                    'notes': today_notes,
                    'tables': today_tables,
                    'flowcharts': today_flowcharts,
                    'whiteboards': today_whiteboards,
                    'mindmaps': today_mindmaps
                }
            }
        })
    except Exception as e:
        # 异常捕获，避免接口崩溃
        print(f'管理员统计接口报错：{str(e)}')
        return jsonify({
            'code': 500,
            'msg': '获取统计数据失败',
            'error': str(e) if app.debug else '服务器内部错误'  # 生产环境隐藏具体错误
        }), 500

# -------------------------- 定时任务 --------------------------
def clean_expired_share_links():
    """定时清理过期的分享链接"""
    with app.app_context():
        expired_links = ShareLink.query.filter(
            ShareLink.expire_at.isnot(None),
            ShareLink.expire_at < datetime.now()
        ).all()

        for link in expired_links:
            db.session.delete(link)

        db.session.commit()
        logger.info(f"清理了 {len(expired_links)} 个过期分享链接")


# 每天凌晨1点执行清理任务
scheduler.add_job(
    id='clean_expired_share_links',
    func=clean_expired_share_links,
    trigger='cron',
    hour=1
)

# -------------------------- 程序入口 --------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建数据库表

        # 创建默认管理员（首次运行时）
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin_user.set_password('admin123')  # 默认密码，建议运行后修改
            db.session.add(admin_user)
            db.session.commit()
            logger.info("默认管理员创建成功：用户名admin，密码admin123")

    scheduler.start()
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000),
        debug=app.config.get('DEBUG', True)
    )