import os
import uuid
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_apscheduler import APScheduler
from zhipuai import ZhipuAI
from dotenv import load_dotenv

from config import config
from models import db, bcrypt, User, Note, NoteVersion, Category, Tag, ShareLink, Flowchart, TableDocument, Whiteboard, Mindmap, FlowchartVersion, TableDocumentVersion, WhiteboardVersion, MindmapVersion, generate_unique_name

load_dotenv()

app = Flask(__name__)
app.config.from_object(config['default'])

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

scheduler = APScheduler()
scheduler.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except:
        return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'message': '请先登录'}), 401
        if not current_user.is_admin:
            return jsonify({'message': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function

def call_zhipu(prompt, system_message=""):
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

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok', 'message': '服务正常运行'})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
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
    data = request.json
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
            'message': '登录成功',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    
    return jsonify({'message': '用户名或密码错误'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
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
        return jsonify({'message': '更新失败'}), 500

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
        return jsonify({'message': '删除失败'}), 500

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
        return jsonify({'message': '删除失败'}), 500

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
        return jsonify({'message': '回滚失败'}), 500

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
    note = Note.query.filter_by(id=share.note_id, user_id=user_id).first_or_404()
    
    db.session.delete(share)
    db.session.commit()
    
    return jsonify({'message': '分享链接已删除'})

@app.route('/api/share/<token>', methods=['GET'])
def get_shared_note(token):
    share_link = ShareLink.query.filter_by(token=token).first()
    
    if not share_link:
        return jsonify({'message': '分享链接不存在'}), 404
    
    if share_link.expire_at and share_link.expire_at < datetime.now():
        return jsonify({'message': '分享链接已过期'}), 404
    
    note = share_link.note
    return jsonify({
        'note': note.to_full_dict(),
        'permission': share_link.permission
    }), 200

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
        return jsonify({'message': '删除失败'}), 500

@app.route('/api/tables/<int:table_id>/versions', methods=['GET'])
@jwt_required()
def get_table_versions(table_id):
    user_id = get_jwt_identity()
    table = TableDocument.query.filter_by(id=table_id, user_id=user_id).first_or_404()
    
    versions = TableDocumentVersion.query.filter_by(table_document_id=table_id).order_by(TableDocumentVersion.updated_at.desc()).all()
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
        return jsonify({'message': '回滚失败'}), 500

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
        return jsonify({'message': '删除失败'}), 500

@app.route('/api/whiteboards/<int:whiteboard_id>/versions', methods=['GET'])
@jwt_required()
def get_whiteboard_versions(whiteboard_id):
    user_id = get_jwt_identity()
    whiteboard = Whiteboard.query.filter_by(id=whiteboard_id, user_id=user_id).first_or_404()
    
    versions = WhiteboardVersion.query.filter_by(whiteboard_id=whiteboard_id).order_by(WhiteboardVersion.updated_at.desc()).all()
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
        return jsonify({'message': '回滚失败'}), 500

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
    
    mindmap = Mindmap(
        title=unique_title,
        data=data.get('data', {}),
        share_token=str(uuid.uuid4()),
        is_public=data.get('is_public', False),
        user_id=user_id
    )
    
    try:
        db.session.add(mindmap)
        db.session.commit()
        return jsonify({'message': '创建成功', 'mindmap': mindmap.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '创建失败'}), 500

@app.route('/api/mindmaps/<int:mindmap_id>', methods=['GET'])
def get_mindmap(mindmap_id):
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except:
        user_id = None
    
    mindmap = Mindmap.query.get_or_404(mindmap_id)
    
    if not mindmap.is_public and (not user_id or mindmap.user_id != int(user_id)):
        return jsonify({'message': '无权访问'}), 403
    
    return jsonify({'mindmap': mindmap.to_dict()}), 200

@app.route('/api/mindmaps/<int:mindmap_id>', methods=['PUT'])
@jwt_required()
def update_mindmap(mindmap_id):
    user_id = get_jwt_identity()
    mindmap = Mindmap.query.filter_by(id=mindmap_id, user_id=user_id).first_or_404()
    data = request.json
    
    if 'title' in data:
        mindmap.title = data['title']
    if 'data' in data:
        mindmap.data = data['data']
    if 'is_public' in data:
        mindmap.is_public = data['is_public']
    
    mindmap.updated_at = datetime.now()
    
    try:
        mindmap.save_version(user_id)
        db.session.commit()
        return jsonify({'message': '更新成功', 'mindmap': mindmap.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
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
    
    mindmap.data = version.data
    mindmap.save_version(user_id)
    
    try:
        db.session.commit()
        return jsonify({'message': '回滚成功', 'mindmap': mindmap.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '回滚失败'}), 500

@app.route('/api/flowcharts', methods=['GET'])
@jwt_required()
def get_flowcharts():
    user_id = get_jwt_identity()
    search = request.args.get('search', '').strip()
    tag_ids = request.args.get('tag_ids', '').strip()
    
    query = Flowchart.query.filter_by(user_id=user_id)
    
    if search:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Flowchart.title.ilike(f'%{search}%'),
                Flowchart.description.ilike(f'%{search}%')
            )
        )
    
    if tag_ids:
        tag_id_list = [int(tid) for tid in tag_ids.split(',') if tid.isdigit()]
        if tag_id_list:
            from sqlalchemy import func
            flowchart_ids = db.session.query(Flowchart.id).join(
                flowchart_tag, Flowchart.id == flowchart_tag.c.flowchart_id
            ).filter(
                flowchart_tag.c.tag_id.in_(tag_id_list)
            ).group_by(Flowchart.id).having(
                func.count(flowchart_tag.c.tag_id) == len(tag_id_list)
            ).all()
            flowchart_ids = [fid[0] for fid in flowchart_ids]
            if flowchart_ids:
                query = query.filter(Flowchart.id.in_(flowchart_ids))
            else:
                return jsonify([]), 200
    
    flowcharts = query.order_by(Flowchart.updated_at.desc()).all()
    
    result = []
    for fc in flowcharts:
        tags = [{'id': tag.id, 'name': tag.name} for tag in fc.tags]
        result.append({
            'id': fc.id,
            'title': fc.title,
            'description': fc.description,
            'thumbnail': fc.thumbnail,
            'is_public': fc.is_public,
            'share_token': fc.share_token,
            'created_at': fc.created_at.isoformat() if fc.created_at else None,
            'updated_at': fc.updated_at.isoformat() if fc.updated_at else None,
            'tags': tags
        })
    
    return jsonify(result), 200

@app.route('/api/flowcharts', methods=['POST'])
@jwt_required()
def create_flowchart():
    user_id = get_jwt_identity()
    data = request.json
    
    base_title = data.get('title', '未命名流程图')
    existing_flowcharts = Flowchart.query.filter_by(user_id=user_id).all()
    existing_titles = [f.title for f in existing_flowcharts]
    unique_title = generate_unique_name(base_title, existing_titles)
    
    flowchart = Flowchart(
        title=unique_title,
        description=data.get('description', ''),
        flow_data=data.get('flow_data', {}),
        thumbnail=data.get('thumbnail', ''),
        share_token=str(uuid.uuid4()),
        is_public=data.get('is_public', False),
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
        logger.error(f"创建流程图失败: {str(e)}")
        return jsonify({'message': '创建失败'}), 500

@app.route('/api/flowcharts/<int:flowchart_id>', methods=['GET'])
def get_flowchart(flowchart_id):
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except:
        user_id = None
    
    flowchart = Flowchart.query.get_or_404(flowchart_id)
    
    if not flowchart.is_public and (not user_id or flowchart.user_id != int(user_id)):
        return jsonify({'message': '无权访问'}), 403
    
    tags = [{'id': tag.id, 'name': tag.name} for tag in flowchart.tags]
    
    return jsonify({
        'flowchart': flowchart.to_dict(),
        'tags': tags,
        'author': flowchart.author.username if flowchart.author else '未知作者'
    }), 200

@app.route('/api/flowcharts/<int:flowchart_id>', methods=['PUT'])
@jwt_required()
def update_flowchart(flowchart_id):
    user_id = get_jwt_identity()
    flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first_or_404()
    data = request.json
    
    if 'title' in data:
        flowchart.title = data['title']
    if 'description' in data:
        flowchart.description = data['description']
    if 'flow_data' in data:
        flowchart.flow_data = data['flow_data']
    if 'thumbnail' in data:
        flowchart.thumbnail = data['thumbnail']
    if 'is_public' in data:
        flowchart.is_public = data['is_public']
    
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
        return jsonify({'message': '删除失败'}), 500

@app.route('/api/flowcharts/<int:flowchart_id>/versions', methods=['GET'])
@jwt_required()
def get_flowchart_versions(flowchart_id):
    user_id = get_jwt_identity()
    flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first_or_404()
    
    versions = FlowchartVersion.query.filter_by(flowchart_id=flowchart_id).order_by(FlowchartVersion.updated_at.desc()).all()
    return jsonify({'versions': [v.to_dict() for v in versions]}), 200

@app.route('/api/flowcharts/<int:flowchart_id>/versions/<int:version_id>', methods=['POST'])
@jwt_required()
def rollback_flowchart_version(flowchart_id, version_id):
    user_id = get_jwt_identity()
    flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first_or_404()
    version = FlowchartVersion.query.filter_by(id=version_id, flowchart_id=flowchart_id).first_or_404()
    
    flowchart.flow_data = version.flow_data
    flowchart.save_version(user_id)
    
    try:
        db.session.commit()
        return jsonify({'message': '回滚成功', 'flowchart': flowchart.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '回滚失败'}), 500

@app.route('/api/flowcharts/<int:flowchart_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_flowchart(flowchart_id):
    user_id = get_jwt_identity()
    original = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first_or_404()
    
    new_flowchart = Flowchart(
        title=f"{original.title} (副本)",
        description=original.description,
        flow_data=original.flow_data,
        thumbnail=original.thumbnail,
        share_token=str(uuid.uuid4()),
        is_public=False,
        user_id=user_id
    )
    
    try:
        db.session.add(new_flowchart)
        db.session.flush()
        
        for tag in original.tags:
            new_flowchart.tags.append(tag)
        
        db.session.commit()
        return jsonify({'message': '复制成功', 'flowchart': new_flowchart.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '复制失败'}), 500

@app.route('/api/flowcharts/<int:flowchart_id>/share', methods=['POST'])
@jwt_required()
def share_flowchart(flowchart_id):
    user_id = get_jwt_identity()
    flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first_or_404()
    data = request.json
    
    days = data.get('days', 7)
    
    share_url = f'/share/{flowchart.share_token}'
    
    return jsonify({
        'share_url': share_url,
        'share_token': flowchart.share_token,
        'expires_in': f'{days}天'
    }), 200

@app.route('/api/share/<share_token>', methods=['GET'])
def get_shared_flowchart(share_token):
    flowchart = Flowchart.query.filter_by(share_token=share_token).first()
    
    if not flowchart:
        return jsonify({'message': '分享不存在或已过期'}), 404
    
    tags = [{'id': tag.id, 'name': tag.name} for tag in flowchart.tags]
    
    return jsonify({
        'id': flowchart.id,
        'title': flowchart.title,
        'flow_data': flowchart.flow_data,
        'thumbnail': flowchart.thumbnail,
        'is_public': flowchart.is_public,
        'readonly': True,
        'tags': tags
    }), 200

@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        total_users = User.query.count()
        total_notes = Note.query.count()
        total_mindmaps = Mindmap.query.count()
        total_flowcharts = Flowchart.query.count()
        total_tables = TableDocument.query.count()
        total_whiteboards = Whiteboard.query.count()
        total_documents = total_notes + total_mindmaps + total_flowcharts + total_tables + total_whiteboards
        total_categories = Category.query.count()
        total_tags = Tag.query.count()
        total_shares = ShareLink.query.count()
        
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_users = User.query.filter(User.created_at >= seven_days_ago).count()
        
        return jsonify({
            'total_users': total_users,
            'total_notes': total_notes,
            'total_mindmaps': total_mindmaps,
            'total_flowcharts': total_flowcharts,
            'total_tables': total_tables,
            'total_whiteboards': total_whiteboards,
            'total_documents': total_documents,
            'total_categories': total_categories,
            'total_tags': total_tags,
            'total_shares': total_shares,
            'recent_users': recent_users,
            'is_admin': True
        }), 200
    else:
        user_notes = Note.query.filter_by(user_id=user_id).count()
        user_mindmaps = Mindmap.query.filter_by(user_id=user_id).count()
        user_flowcharts = Flowchart.query.filter_by(user_id=user_id).count()
        user_tables = TableDocument.query.filter_by(user_id=user_id).count()
        user_whiteboards = Whiteboard.query.filter_by(user_id=user_id).count()
        user_documents = user_notes + user_mindmaps + user_flowcharts + user_tables + user_whiteboards
        user_categories = Category.query.filter_by(user_id=user_id).count()
        user_tags = Tag.query.filter_by(user_id=user_id).count()
        
        return jsonify({
            'user_notes': user_notes,
            'user_mindmaps': user_mindmaps,
            'user_flowcharts': user_flowcharts,
            'user_tables': user_tables,
            'user_whiteboards': user_whiteboards,
            'user_documents': user_documents,
            'user_categories': user_categories,
            'user_tags': user_tags,
            'is_admin': False
        }), 200

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if not user.is_admin:
        return jsonify({'message': '需要管理员权限'}), 403
    
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'is_admin': u.is_admin,
        'created_at': u.created_at.isoformat() if u.created_at else None,
        'note_count': Note.query.filter_by(user_id=u.id).count()
    } for u in users]), 200

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    if not current_user.is_admin:
        return jsonify({'message': '需要管理员权限'}), 403
    
    if user_id == current_user_id:
        return jsonify({'message': '不能删除自己的账户'}), 400
    
    user_to_delete = User.query.get_or_404(user_id)
    
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return jsonify({'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '删除失败'}), 500

@app.route('/api/admin/set_admin/<int:user_id>', methods=['POST'])
@jwt_required()
def set_admin(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    if not current_user.is_admin:
        return jsonify({'message': '需要管理员权限'}), 403
    
    target_user = User.query.get_or_404(user_id)
    target_user.is_admin = not target_user.is_admin
    
    try:
        db.session.commit()
        return jsonify({'message': '设置成功', 'is_admin': target_user.is_admin}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '设置失败'}), 500

@scheduler.task('cron', hour=0)
def clean_expired_links():
    with app.app_context():
        expired_links = ShareLink.query.filter(
            ShareLink.expire_at < datetime.now()
        ).all()
        for link in expired_links:
            db.session.delete(link)
        db.session.commit()
        logger.info(f"清理了 {len(expired_links)} 个过期的分享链接")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', email='admin@example.com')
            admin_user.set_password('admin123')
            admin_user.is_admin = True
            db.session.add(admin_user)
            db.session.commit()
            logger.info("默认管理员账户已创建: admin/admin123")
    
    scheduler.start()
    app.run(debug=True, host='0.0.0.0', port=5000)
