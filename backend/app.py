from flask import Flask, request, jsonify, send_from_directory, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from flask_migrate import Migrate
from flask_socketio import SocketIO, join_room, leave_room, emit, send
import os
import logging
import uuid
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from openai import OpenAI
from sqlalchemy import text
import eventlet
from eventlet import wsgi
import threading

# 加载.env文件中的环境变量
from dotenv import load_dotenv
load_dotenv()

# 导入自定义模块
from config import get_config
from models import db, bcrypt, User, Note, NoteVersion, Category, Tag, Flowchart, FlowchartVersion, TableDocument, TableDocumentVersion, Whiteboard, WhiteboardVersion, Mindmap, MindmapVersion, ShareLink

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化应用
app = Flask(__name__)
app.config.from_object(get_config())

# 初始化扩展
db.init_app(app)
bcrypt.init_app(app)
JWTManager(app)
CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=app.config['CORS_SUPPORTS_CREDENTIALS'])
Migrate(app, db)

# 初始化SocketIO
# 配置CORS以允许所有来源
CORS(app, resources={"*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# 在线用户字典，用于跟踪每个房间的在线用户
online_users = {}

# 协作文档状态，用于存储当前文档的最新状态
collaborative_docs = {}

# 初始化定时任务调度器
scheduler = BackgroundScheduler()
scheduler.start()

# -------------------------- 用户认证接口 --------------------------
@app.route('/api/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
        
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401
        
        # 更新最后登录时间
        user.last_login = datetime.now()
        db.session.commit()
        
        # 创建JWT令牌
        access_token = create_access_token(identity=user.id, additional_claims={'is_admin': user.is_admin})
        
        return jsonify({
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': access_token,
                'user': user.to_dict()
            }
        }), 200
    except Exception as e:
        logger.error(f"登录接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """用户登出接口"""
    try:
        # JWT是无状态的，登出只需要前端删除token即可
        # 这里可以添加一些额外的登出逻辑，如记录登出日志等
        return jsonify({
            'code': 200,
            'message': '登出成功'
        }), 200
    except Exception as e:
        logger.error(f"登出接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册接口"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')
        
        if not username or not password:
            return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'code': 400, 'message': '用户名已存在'}), 400
        
        # 创建新用户
        user = User(username=username, email=email, is_admin=False)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'code': 201, 'message': '注册成功'}), 201
    except Exception as e:
        logger.error(f"注册接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """获取用户个人信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"获取用户信息接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

# -------------------------- 笔记管理接口 --------------------------
@app.route('/api/notes', methods=['GET'])
@jwt_required()
def get_notes():
    """获取用户的笔记列表"""
    try:
        user_id = get_jwt_identity()
        notes = Note.query.filter_by(user_id=user_id).order_by(Note.updated_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [note.to_dict() for note in notes]
        }), 200
    except Exception as e:
        logger.error(f"获取笔记列表接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/notes/<int:note_id>', methods=['GET'])
@jwt_required()
def get_note_detail(note_id):
    """获取笔记详情"""
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        
        if not note:
            return jsonify({'code': 404, 'message': '笔记不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': note.to_full_dict()
        }), 200
    except Exception as e:
        logger.error(f"获取笔记详情接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/notes', methods=['POST'])
@jwt_required()
def create_note():
    """创建笔记"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        title = data.get('title', '新笔记')
        
        # 检查是否已存在同名笔记
        existing_note = Note.query.filter_by(user_id=user_id, title=title).first()
        if existing_note:
            return jsonify({'code': 400, 'message': '已存在同名笔记，请使用其他名称'}), 400
        
        note = Note(
            title=title,
            content=data.get('content', ''),
            type=data.get('type', 'richtext'),
            is_public=data.get('is_public', False),
            user_id=user_id,
            category_id=data.get('category_id')
        )
        
        # 处理标签
        tags_data = data.get('tags', [])
        tag_ids = []
        
        for tag_obj in tags_data:
            if tag_obj.get('id'):
                # 已存在的标签，使用ID
                tag_ids.append(tag_obj['id'])
            elif tag_obj.get('name'):
                # 新标签，创建后获取ID
                tag_name = tag_obj['name']
                existing_tag = Tag.query.filter_by(name=tag_name, user_id=user_id).first()
                if existing_tag:
                    tag_ids.append(existing_tag.id)
                else:
                    new_tag = Tag(name=tag_name, user_id=user_id)
                    db.session.add(new_tag)
                    db.session.flush()  # 确保获取ID
                    tag_ids.append(new_tag.id)
        
        if tag_ids:
            tags = Tag.query.filter(Tag.id.in_(tag_ids), Tag.user_id == user_id).all()
            note.tags = tags
        
        db.session.add(note)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '创建成功',
            'data': note.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"创建笔记接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/notes/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    """更新笔记"""
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        
        if not note:
            return jsonify({'code': 404, 'message': '笔记不存在或无权限访问'}), 404
        
        data = request.json
        new_title = data.get('title', note.title)
        
        # 如果标题有变化，检查是否已存在同名笔记
        if new_title != note.title:
            existing_note = Note.query.filter_by(user_id=user_id, title=new_title).first()
            if existing_note:
                return jsonify({'code': 400, 'message': '已存在同名笔记，请使用其他名称'}), 400
        
        # 保存旧版本
        note.save_version(user_id)
        
        # 更新笔记字段
        note.title = new_title
        note.content = data.get('content', note.content)
        note.type = data.get('type', note.type)
        note.is_public = data.get('is_public', note.is_public)
        note.category_id = data.get('category_id', note.category_id)
        
        # 处理标签
        tags_data = data.get('tags', [])
        tag_ids = []
        
        for tag_obj in tags_data:
            if tag_obj.get('id'):
                # 已存在的标签，使用ID
                tag_ids.append(tag_obj['id'])
            elif tag_obj.get('name'):
                # 新标签，创建后获取ID
                tag_name = tag_obj['name']
                existing_tag = Tag.query.filter_by(name=tag_name, user_id=user_id).first()
                if existing_tag:
                    tag_ids.append(existing_tag.id)
                else:
                    new_tag = Tag(name=tag_name, user_id=user_id)
                    db.session.add(new_tag)
                    db.session.flush()  # 确保获取ID
                    tag_ids.append(new_tag.id)
        
        if tag_ids:
            tags = Tag.query.filter(Tag.id.in_(tag_ids), Tag.user_id == user_id).all()
            note.tags = tags
        else:
            note.tags = []
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': note.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"更新笔记接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/notes/<int:note_id>/versions', methods=['GET'])
@jwt_required()
def get_note_versions(note_id):
    """获取笔记版本历史"""
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        
        if not note:
            return jsonify({'code': 404, 'message': '笔记不存在或无权限访问'}), 404
        
        versions = note.versions.order_by(NoteVersion.updated_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [version.to_dict() for version in versions]
        }), 200
    except Exception as e:
        logger.error(f"获取笔记版本历史接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/notes/<int:note_id>/versions', methods=['POST'])
@jwt_required()
def save_note_version(note_id):
    """保存笔记版本"""
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        
        if not note:
            return jsonify({'code': 404, 'message': '笔记不存在或无权限访问'}), 404
        
        # 保存版本
        version = note.save_version(user_id)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '版本保存成功',
            'data': version.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"保存笔记版本接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/notes/<int:note_id>/versions/<int:version_id>/rollback', methods=['POST'])
@jwt_required()
def rollback_note_version(note_id, version_id):
    """回滚笔记版本"""
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        
        if not note:
            return jsonify({'code': 404, 'message': '笔记不存在或无权限访问'}), 404
        
        version = NoteVersion.query.filter_by(id=version_id, note_id=note_id).first()
        
        if not version:
            return jsonify({'code': 404, 'message': '版本不存在'}), 404
        
        # 回滚内容
        note.content = version.content
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '版本回滚成功',
            'data': note.to_dict(include_content=True)
        }), 200
    except Exception as e:
        logger.error(f"回滚笔记版本接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    """删除笔记"""
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        
        if not note:
            return jsonify({'code': 404, 'message': '笔记不存在'}), 404
        
        # 删除笔记版本记录
        NoteVersion.query.filter_by(note_id=note_id).delete()
        
        # 删除笔记
        db.session.delete(note)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
    except Exception as e:
        logger.error(f"删除笔记接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


# -------------------------- 分类管理接口 --------------------------
@app.route('/api/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """获取用户的分类列表"""
    try:
        user_id = get_jwt_identity()
        categories = Category.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [category.to_dict() for category in categories]
        }), 200
    except Exception as e:
        logger.error(f"获取分类列表接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/categories', methods=['POST'])
@jwt_required()
def create_category():
    """创建分类"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        if not data.get('name'):
            return jsonify({'code': 400, 'message': '分类名称不能为空'}), 400
        
        category = Category(
            name=data.get('name'),
            user_id=user_id
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '创建成功',
            'data': category.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"创建分类接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

# -------------------------- 标签管理接口 --------------------------
@app.route('/api/tags', methods=['GET'])
@jwt_required()
def get_tags():
    """获取用户的标签列表"""
    try:
        user_id = get_jwt_identity()
        tags = Tag.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [tag.to_dict() for tag in tags]
        }), 200
    except Exception as e:
        logger.error(f"获取标签列表接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/tags', methods=['POST'])
@jwt_required()
def create_tag():
    """创建标签"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        if not data.get('name'):
            return jsonify({'code': 400, 'message': '标签名称不能为空'}), 400
        
        tag = Tag(
            name=data.get('name'),
            user_id=user_id
        )
        
        db.session.add(tag)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '创建成功',
            'data': tag.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"创建标签接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/tags/<int:tag_id>', methods=['GET'])
@jwt_required()
def get_tag(tag_id):
    """获取标签详情"""
    try:
        user_id = get_jwt_identity()
        tag = Tag.query.filter_by(id=tag_id, user_id=user_id).first()
        
        if not tag:
            return jsonify({'code': 404, 'message': '标签不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': tag.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"获取标签详情接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

# -------------------------- 流程图管理接口 --------------------------
@app.route('/api/flowcharts', methods=['GET'])
@jwt_required()
def get_flowcharts():
    """获取用户的流程图列表"""
    try:
        user_id = get_jwt_identity()
        flowcharts = Flowchart.query.filter_by(user_id=user_id).order_by(Flowchart.updated_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [flowchart.to_dict() for flowchart in flowcharts]
        }), 200
    except Exception as e:
        logger.error(f"获取流程图列表接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/flowcharts', methods=['POST'])
@jwt_required()
def create_flowchart():
    """创建流程图"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        title = data.get('title', '新流程图')
        
        # 检查是否已存在同名流程图
        existing_flowchart = Flowchart.query.filter_by(user_id=user_id, title=title).first()
        if existing_flowchart:
            return jsonify({'code': 400, 'message': '已存在同名流程图，请使用其他名称'}), 400
        
        flowchart = Flowchart(
            title=title,
            description=data.get('description', ''),
            flow_data=data.get('flow_data', {}),
            thumbnail=data.get('thumbnail'),
            is_public=data.get('is_public', False),
            user_id=user_id
        )
        
        db.session.add(flowchart)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '创建成功',
            'data': flowchart.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"创建流程图接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/flowcharts/<int:flowchart_id>', methods=['GET'])
@jwt_required()
def get_flowchart(flowchart_id):
    """获取流程图详情"""
    try:
        user_id = get_jwt_identity()
        flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first()
        
        if not flowchart:
            return jsonify({'code': 404, 'message': '流程图不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': flowchart.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"获取流程图详情接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/flowcharts/<int:flowchart_id>', methods=['PUT'])
@jwt_required()
def update_flowchart(flowchart_id):
    """更新流程图"""
    try:
        user_id = get_jwt_identity()
        flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first()
        
        if not flowchart:
            return jsonify({'code': 404, 'message': '流程图不存在'}), 404
        
        data = request.json
        new_title = data.get('title', flowchart.title)
        
        # 如果标题有变化，检查是否已存在同名流程图
        if new_title != flowchart.title:
            existing_flowchart = Flowchart.query.filter_by(user_id=user_id, title=new_title).first()
            if existing_flowchart:
                return jsonify({'code': 400, 'message': '已存在同名流程图，请使用其他名称'}), 400
        
        # 保存旧版本
        flowchart.save_version(user_id)
        
        # 更新流程图数据
        flowchart.title = new_title
        flowchart.description = data.get('description', flowchart.description)
        flowchart.flow_data = data.get('flow_data', flowchart.flow_data)
        flowchart.thumbnail = data.get('thumbnail', flowchart.thumbnail)
        flowchart.is_public = data.get('is_public', flowchart.is_public)
        
        # 处理标签
        if data.get('tags') is not None:
            flowchart.tags = Tag.query.filter(Tag.id.in_(data.get('tags'))).all()
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': flowchart.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"更新流程图接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/flowcharts/<int:flowchart_id>', methods=['DELETE'])
@jwt_required()
def delete_flowchart(flowchart_id):
    """删除流程图"""
    try:
        user_id = get_jwt_identity()
        flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first()
        
        if not flowchart:
            return jsonify({'code': 404, 'message': '流程图不存在'}), 404
        
        # 删除流程图版本记录
        FlowchartVersion.query.filter_by(flowchart_id=flowchart_id).delete()
        
        # 删除流程图
        db.session.delete(flowchart)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
    except Exception as e:
        logger.error(f"删除流程图接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/flowcharts/<int:flowchart_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_flowchart(flowchart_id):
    """复制流程图"""
    try:
        user_id = get_jwt_identity()
        original_flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first()
        
        if not original_flowchart:
            return jsonify({'code': 404, 'message': '流程图不存在'}), 404
        
        # 创建新的流程图副本
        new_flowchart = Flowchart(
            title=f"{original_flowchart.title} (副本)",
            description=original_flowchart.description,
            flow_data=original_flowchart.flow_data,
            thumbnail=original_flowchart.thumbnail,
            user_id=user_id
        )
        
        # 复制标签
        new_flowchart.tags = original_flowchart.tags
        
        db.session.add(new_flowchart)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '复制成功',
            'data': new_flowchart.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"复制流程图接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/flowcharts/<int:flowchart_id>/share', methods=['POST'])
@jwt_required()
def share_flowchart(flowchart_id):
    """共享流程图"""
    try:
        user_id = get_jwt_identity()
        flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first()
        
        if not flowchart:
            return jsonify({'code': 404, 'message': '流程图不存在'}), 404
        
        data = request.json
        permission = data.get('permission', 'view')
        expire_at = data.get('expireAt')
        
        # 创建或更新共享链接
        share_link = ShareLink.query.filter_by(flowchart_id=flowchart_id, permission=permission).first()
        
        if not share_link:
            share_link = ShareLink(
                flowchart_id=flowchart_id,
                permission=permission,
                expire_at=expire_at,
                user_id=user_id
            )
            db.session.add(share_link)
        else:
            share_link.expire_at = expire_at
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '共享成功',
            'data': {
                'share_token': share_link.token,
                'permission': share_link.permission,
                'expire_at': share_link.expire_at.isoformat() if share_link.expire_at else None
            }
        }), 200
    except Exception as e:
        logger.error(f"共享流程图接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/notes/<int:note_id>/shares', methods=['GET'])
@jwt_required()
def get_note_shares(note_id):
    """获取笔记的分享链接列表"""
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        
        if not note:
            return jsonify({'code': 404, 'message': '笔记不存在'}), 404
        
        # 获取笔记的所有分享链接
        share_links = ShareLink.query.filter_by(note_id=note_id).all()
        
        # 转换为前端需要的格式
        shares = []
        for link in share_links:
            shares.append({
                'token': link.token,
                'permission': link.permission,
                'expire_at': link.expire_at.isoformat() if link.expire_at else None,
                'created_at': link.created_at.isoformat()
            })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': shares
        }), 200
    except Exception as e:
        logger.error(f"获取笔记分享链接列表接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/notes/<int:note_id>/share', methods=['POST'])
@jwt_required()
def share_note(note_id):
    """共享笔记"""
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        
        if not note:
            return jsonify({'code': 404, 'message': '笔记不存在'}), 404
        
        data = request.json
        permission = data.get('permission', 'view')
        expire_at = data.get('expire_at')
        is_collaborative = data.get('is_collaborative', False)
        
        # 转换expire_at为datetime对象
        if expire_at and isinstance(expire_at, str):
            try:
                expire_at = datetime.fromisoformat(expire_at)
            except (ValueError, TypeError):
                expire_at = None
        
        # 创建或更新共享链接
        share_link = ShareLink.query.filter_by(note_id=note_id, permission=permission).first()
        
        if not share_link:
            share_link = ShareLink(
                note_id=note_id,
                token=str(uuid.uuid4()),
                room_id=str(uuid.uuid4()) if is_collaborative else None,
                permission=permission,
                is_collaborative=is_collaborative,
                expire_at=expire_at
            )
            db.session.add(share_link)
        else:
            share_link.expire_at = expire_at
            share_link.is_collaborative = is_collaborative
            # 如果开启了协作但没有房间ID，生成一个
            if is_collaborative and not share_link.room_id:
                share_link.room_id = str(uuid.uuid4())
            # 如果关闭了协作，清空房间ID
            elif not is_collaborative:
                share_link.room_id = None
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '共享成功',
            'data': {
                'share_token': share_link.token,
                'permission': share_link.permission,
                'is_collaborative': share_link.is_collaborative,
                'room_id': share_link.room_id,
                'expire_at': share_link.expire_at.isoformat() if share_link.expire_at else None
            }
        }), 200
    except Exception as e:
        logger.error(f"共享笔记接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/notes/<int:note_id>/shares/<string:token>', methods=['DELETE'])
@jwt_required()
def delete_note_share(note_id, token):
    """删除笔记的分享链接"""
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        
        if not note:
            return jsonify({'code': 404, 'message': '笔记不存在'}), 404
        
        # 查找并删除分享链接
        share_link = ShareLink.query.filter_by(note_id=note_id, token=token).first()
        
        if not share_link:
            return jsonify({'code': 404, 'message': '分享链接不存在'}), 404
        
        db.session.delete(share_link)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
    except Exception as e:
        logger.error(f"删除笔记分享链接接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/flowcharts/<int:flowchart_id>/versions', methods=['GET'])
@jwt_required()
def get_flowchart_versions(flowchart_id):
    """获取流程图版本历史"""
    try:
        user_id = get_jwt_identity()
        flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first()
        
        if not flowchart:
            return jsonify({'code': 404, 'message': '流程图不存在'}), 404
        
        versions = FlowchartVersion.query.filter_by(flowchart_id=flowchart_id).order_by(FlowchartVersion.updated_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [version.to_dict() for version in versions]
        }), 200
    except Exception as e:
        logger.error(f"获取流程图版本历史接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/flowcharts/<int:flowchart_id>/versions/<int:version_id>', methods=['GET'])
@jwt_required()
def get_flowchart_version(flowchart_id, version_id):
    """获取流程图特定版本"""
    try:
        user_id = get_jwt_identity()
        flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first()
        
        if not flowchart:
            return jsonify({'code': 404, 'message': '流程图不存在'}), 404
        
        version = FlowchartVersion.query.filter_by(id=version_id, flowchart_id=flowchart_id).first()
        
        if not version:
            return jsonify({'code': 404, 'message': '版本不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': version.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"获取流程图特定版本接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/flowcharts/<int:flowchart_id>/versions/<int:version_id>', methods=['POST'])
@jwt_required()
def rollback_flowchart_version(flowchart_id, version_id):
    """回滚流程图版本"""
    try:
        user_id = get_jwt_identity()
        flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id).first()
        
        if not flowchart:
            return jsonify({'code': 404, 'message': '流程图不存在'}), 404
        
        version = FlowchartVersion.query.filter_by(id=version_id, flowchart_id=flowchart_id).first()
        
        if not version:
            return jsonify({'code': 404, 'message': '版本不存在'}), 404
        
        # 保存当前版本
        flowchart.save_version(user_id)
        
        # 回滚内容
        flowchart.flow_data = version.flow_data
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '版本回滚成功',
            'data': flowchart.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"回滚流程图版本接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

# -------------------------- 表格管理接口 --------------------------
@app.route('/api/tables', methods=['GET'])
@jwt_required()
def get_tables():
    """获取用户的表格列表"""
    try:
        user_id = get_jwt_identity()
        tables = TableDocument.query.filter_by(user_id=user_id).order_by(TableDocument.updated_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [table.to_dict() for table in tables]
        }), 200
    except Exception as e:
        logger.error(f"获取表格列表接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/tables', methods=['POST'])
@jwt_required()
def create_table():
    """创建表格"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        title = data.get('title', '新表格')
        
        # 检查是否已存在同名表格
        existing_table = TableDocument.query.filter_by(user_id=user_id, title=title).first()
        if existing_table:
            return jsonify({'code': 400, 'message': '已存在同名表格，请使用其他名称'}), 400
        
        table = TableDocument(
            title=title,
            columns_data=data.get('columns', []),
            rows_data=data.get('rows', []),
            cell_styles=data.get('cellStyles', {}),
            user_id=user_id
        )
        
        db.session.add(table)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '创建成功',
            'data': table.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"创建表格接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/tables/<int:table_id>', methods=['GET'])
@jwt_required()
def get_table(table_id):
    """获取表格详情"""
    try:
        user_id = get_jwt_identity()
        table = TableDocument.query.filter_by(id=table_id, user_id=user_id).first()
        
        if not table:
            return jsonify({'code': 404, 'message': '表格不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': table.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"获取表格详情接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/tables/<int:table_id>', methods=['PUT'])
@jwt_required()
def update_table(table_id):
    """更新表格"""
    try:
        user_id = get_jwt_identity()
        table = TableDocument.query.filter_by(id=table_id, user_id=user_id).first()
        
        if not table:
            return jsonify({'code': 404, 'message': '表格不存在'}), 404
        
        data = request.json
        new_title = data.get('title', table.title)
        
        # 如果标题有变化，检查是否已存在同名表格
        if new_title != table.title:
            existing_table = TableDocument.query.filter_by(user_id=user_id, title=new_title).first()
            if existing_table:
                return jsonify({'code': 400, 'message': '已存在同名表格，请使用其他名称'}), 400
        
        # 保存旧版本
        table.save_version(user_id)
        
        # 更新表格数据
        table.title = new_title
        table.columns_data = data.get('columns', table.columns_data)
        table.rows_data = data.get('rows', table.rows_data)
        table.cell_styles = data.get('cellStyles', table.cell_styles)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': table.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"更新表格接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/tables/<int:table_id>', methods=['DELETE'])
@jwt_required()
def delete_table(table_id):
    """删除表格"""
    try:
        user_id = get_jwt_identity()
        table = TableDocument.query.filter_by(id=table_id, user_id=user_id).first()
        
        if not table:
            return jsonify({'code': 404, 'message': '表格不存在'}), 404
        
        # 删除表格版本记录
        TableDocumentVersion.query.filter_by(table_document_id=table_id).delete()
        
        # 删除表格
        db.session.delete(table)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
    except Exception as e:
        logger.error(f"删除表格接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/tables/<int:table_id>/versions', methods=['GET'])
@jwt_required()
def get_table_versions(table_id):
    """获取表格版本历史"""
    try:
        user_id = get_jwt_identity()
        table = TableDocument.query.filter_by(id=table_id, user_id=user_id).first()
        
        if not table:
            return jsonify({'code': 404, 'message': '表格不存在'}), 404
        
        versions = TableDocumentVersion.query.filter_by(table_document_id=table_id).order_by(TableDocumentVersion.updated_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [version.to_dict() for version in versions]
        }), 200
    except Exception as e:
        logger.error(f"获取表格版本历史接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/tables/<int:table_id>/versions/<int:version_id>', methods=['GET'])
@jwt_required()
def get_table_version(table_id, version_id):
    """获取表格特定版本"""
    try:
        user_id = get_jwt_identity()
        table = TableDocument.query.filter_by(id=table_id, user_id=user_id).first()
        
        if not table:
            return jsonify({'code': 404, 'message': '表格不存在'}), 404
        
        version = TableDocumentVersion.query.filter_by(id=version_id, table_document_id=table_id).first()
        
        if not version:
            return jsonify({'code': 404, 'message': '版本不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': version.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"获取表格特定版本接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/tables/<int:table_id>/versions/<int:version_id>', methods=['POST'])
@jwt_required()
def rollback_table_version(table_id, version_id):
    """回滚表格版本"""
    try:
        user_id = get_jwt_identity()
        table = TableDocument.query.filter_by(id=table_id, user_id=user_id).first()
        
        if not table:
            return jsonify({'code': 404, 'message': '表格不存在'}), 404
        
        version = TableDocumentVersion.query.filter_by(id=version_id, table_document_id=table_id).first()
        
        if not version:
            return jsonify({'code': 404, 'message': '版本不存在'}), 404
        
        # 保存当前版本
        table.save_version(user_id)
        
        # 回滚内容
        table.columns_data = version.columns_data
        table.rows_data = version.rows_data
        table.cell_styles = version.cell_styles
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '版本回滚成功',
            'data': table.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"回滚表格版本接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

# -------------------------- 白板管理接口 --------------------------
@app.route('/api/whiteboards', methods=['GET'])
@jwt_required()
def get_whiteboards():
    """获取用户的白板列表"""
    try:
        user_id = get_jwt_identity()
        whiteboards = Whiteboard.query.filter_by(user_id=user_id).order_by(Whiteboard.updated_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [whiteboard.to_dict() for whiteboard in whiteboards]
        }), 200
    except Exception as e:
        logger.error(f"获取白板列表接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/whiteboards', methods=['POST'])
@jwt_required()
def create_whiteboard():
    """创建白板"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        title = data.get('title', '新白板')
        
        # 检查是否已存在同名白板
        existing_whiteboard = Whiteboard.query.filter_by(user_id=user_id, title=title).first()
        if existing_whiteboard:
            return jsonify({'code': 400, 'message': '已存在同名白板，请使用其他名称'}), 400
        
        whiteboard = Whiteboard(
            title=title,
            room_key=data.get('room_key', str(uuid.uuid4())),
            data=data.get('data', {}),
            user_id=user_id
        )
        
        db.session.add(whiteboard)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '创建成功',
            'data': whiteboard.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"创建白板接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/whiteboards/<int:whiteboard_id>', methods=['GET'])
@jwt_required()
def get_whiteboard(whiteboard_id):
    """获取白板详情"""
    try:
        user_id = get_jwt_identity()
        whiteboard = Whiteboard.query.filter_by(id=whiteboard_id, user_id=user_id).first()
        
        if not whiteboard:
            return jsonify({'code': 404, 'message': '白板不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': whiteboard.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"获取白板详情接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/whiteboards/<int:whiteboard_id>', methods=['PUT'])
@jwt_required()
def update_whiteboard(whiteboard_id):
    """更新白板"""
    try:
        user_id = get_jwt_identity()
        whiteboard = Whiteboard.query.filter_by(id=whiteboard_id, user_id=user_id).first()
        
        if not whiteboard:
            return jsonify({'code': 404, 'message': '白板不存在'}), 404
        
        data = request.json
        new_title = data.get('title', whiteboard.title)
        
        # 如果标题有变化，检查是否已存在同名白板
        if new_title != whiteboard.title:
            existing_whiteboard = Whiteboard.query.filter_by(user_id=user_id, title=new_title).first()
            if existing_whiteboard:
                return jsonify({'code': 400, 'message': '已存在同名白板，请使用其他名称'}), 400
        
        # 保存旧版本
        whiteboard.save_version(user_id)
        
        # 更新白板数据
        whiteboard.title = new_title
        whiteboard.room_key = data.get('room_key', whiteboard.room_key)
        whiteboard.data = data.get('data', whiteboard.data)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': whiteboard.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"更新白板接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/whiteboards/<int:whiteboard_id>', methods=['DELETE'])
@jwt_required()
def delete_whiteboard(whiteboard_id):
    """删除白板"""
    try:
        user_id = get_jwt_identity()
        whiteboard = Whiteboard.query.filter_by(id=whiteboard_id, user_id=user_id).first()
        
        if not whiteboard:
            return jsonify({'code': 404, 'message': '白板不存在'}), 404
        
        # 删除白板版本记录
        WhiteboardVersion.query.filter_by(whiteboard_id=whiteboard_id).delete()
        
        # 删除白板
        db.session.delete(whiteboard)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
    except Exception as e:
        logger.error(f"删除白板接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/whiteboards/<int:whiteboard_id>/versions', methods=['GET'])
@jwt_required()
def get_whiteboard_versions(whiteboard_id):
    """获取白板版本历史"""
    try:
        user_id = get_jwt_identity()
        whiteboard = Whiteboard.query.filter_by(id=whiteboard_id, user_id=user_id).first()
        
        if not whiteboard:
            return jsonify({'code': 404, 'message': '白板不存在'}), 404
        
        versions = WhiteboardVersion.query.filter_by(whiteboard_id=whiteboard_id).order_by(WhiteboardVersion.updated_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [version.to_dict() for version in versions]
        }), 200
    except Exception as e:
        logger.error(f"获取白板版本历史接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/whiteboards/<int:whiteboard_id>/versions/<int:version_id>', methods=['GET'])
@jwt_required()
def get_whiteboard_version(whiteboard_id, version_id):
    """获取白板特定版本"""
    try:
        user_id = get_jwt_identity()
        whiteboard = Whiteboard.query.filter_by(id=whiteboard_id, user_id=user_id).first()
        
        if not whiteboard:
            return jsonify({'code': 404, 'message': '白板不存在'}), 404
        
        version = WhiteboardVersion.query.filter_by(id=version_id, whiteboard_id=whiteboard_id).first()
        
        if not version:
            return jsonify({'code': 404, 'message': '版本不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': version.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"获取白板特定版本接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/whiteboards/<int:whiteboard_id>/versions/<int:version_id>', methods=['POST'])
@jwt_required()
def rollback_whiteboard_version(whiteboard_id, version_id):
    """回滚白板版本"""
    try:
        user_id = get_jwt_identity()
        whiteboard = Whiteboard.query.filter_by(id=whiteboard_id, user_id=user_id).first()
        
        if not whiteboard:
            return jsonify({'code': 404, 'message': '白板不存在'}), 404
        
        version = WhiteboardVersion.query.filter_by(id=version_id, whiteboard_id=whiteboard_id).first()
        
        if not version:
            return jsonify({'code': 404, 'message': '版本不存在'}), 404
        
        # 保存当前版本
        whiteboard.save_version(user_id)
        
        # 回滚内容
        whiteboard.data = version.data
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '版本回滚成功',
            'data': whiteboard.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"回滚白板版本接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/whiteboards/wbo-token', methods=['GET'])
@jwt_required()
def get_wbo_token():
    """获取WBO令牌"""
    try:
        user_id = get_jwt_identity()
        
        # 生成WBO令牌
        # 这里可以根据实际需求实现令牌生成逻辑
        # 目前返回一个简单的令牌作为示例
        import secrets
        token = secrets.token_urlsafe(32)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'token': token
        }), 200
    except Exception as e:
        logger.error(f"获取WBO令牌接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

# -------------------------- 脑图管理接口 --------------------------
@app.route('/api/mindmaps', methods=['GET'])
@jwt_required()
def get_mindmaps():
    """获取用户的脑图列表"""
    try:
        user_id = get_jwt_identity()
        mindmaps = Mindmap.query.filter_by(user_id=user_id).order_by(Mindmap.updated_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [mindmap.to_dict() for mindmap in mindmaps]
        }), 200
    except Exception as e:
        logger.error(f"获取脑图列表接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/mindmaps', methods=['POST'])
@jwt_required()
def create_mindmap():
    """创建脑图"""
    try:
        user_id = get_jwt_identity()
        logger.info(f"接收到创建脑图请求，用户ID: {user_id}")
        
        # 检查请求格式
        if not request.is_json:
            logger.error("请求格式错误，需要JSON格式")
            return jsonify({'code': 400, 'message': '请求格式错误，需要JSON格式'}), 400
        
        data = request.json
        logger.info(f"请求数据: {data}")
        
        if not data:
            logger.error("请求数据为空")
            return jsonify({'code': 400, 'message': '请求数据为空'}), 400
        
        # 验证必要字段
        title = data.get('title', '新脑图')
        if not title:
            logger.error("脑图标题不能为空")
            return jsonify({'code': 400, 'message': '脑图标题不能为空'}), 400
        
        logger.info(f"脑图标题: {title}")
        
        # 获取并验证数据结构
        mindmap_data = data.get('data', {})
        if not isinstance(mindmap_data, dict):
            logger.error("脑图数据格式错误，需要对象格式")
            return jsonify({'code': 400, 'message': '脑图数据格式错误，需要对象格式'}), 400
        
        # 确保nodes和edges字段存在且格式正确
        if 'nodes' not in mindmap_data:
            mindmap_data['nodes'] = []
        if 'edges' not in mindmap_data:
            mindmap_data['edges'] = []
        
        if not isinstance(mindmap_data['nodes'], list):
            logger.error("nodes字段格式错误，需要数组格式")
            return jsonify({'code': 400, 'message': 'nodes字段格式错误，需要数组格式'}), 400
        
        if not isinstance(mindmap_data['edges'], list):
            logger.error("edges字段格式错误，需要数组格式")
            return jsonify({'code': 400, 'message': 'edges字段格式错误，需要数组格式'}), 400
        
        # 处理is_public字段
        is_public = data.get('is_public', False)
        # 确保is_public是布尔值
        is_public = bool(is_public)
        
        logger.info(f"脑图数据: {mindmap_data}")
        logger.info(f"是否公开: {is_public}")
        logger.info(f"是否公开类型: {type(is_public)}")
        
        # 创建脑图对象
        mindmap = Mindmap(
            title=title,
            data=mindmap_data,
            is_public=is_public,
            user_id=user_id
        )
        
        db.session.add(mindmap)
        db.session.commit()
        
        logger.info(f"脑图创建成功，ID: {mindmap.id}")
        
        return jsonify({
            'code': 201,
            'message': '创建成功',
            'data': mindmap.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"创建脑图接口异常: {str(e)}", exc_info=True)
        # 捕获并返回具体的验证错误
        if isinstance(e, ValueError):
            return jsonify({'code': 400, 'message': f'数据验证错误: {str(e)}'}), 400
        elif isinstance(e, TypeError):
            return jsonify({'code': 400, 'message': f'数据类型错误: {str(e)}'}), 400
        else:
            return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/mindmaps/<int:mindmap_id>', methods=['GET'])
@jwt_required()
def get_mindmap(mindmap_id):
    """获取脑图详情"""
    try:
        user_id = get_jwt_identity()
        mindmap = Mindmap.query.filter_by(id=mindmap_id, user_id=user_id).first()
        
        if not mindmap:
            return jsonify({'code': 404, 'message': '脑图不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': mindmap.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"获取脑图详情接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/mindmaps/<int:mindmap_id>', methods=['PUT'])
@jwt_required()
def update_mindmap(mindmap_id):
    """更新脑图"""
    try:
        user_id = get_jwt_identity()
        mindmap = Mindmap.query.filter_by(id=mindmap_id, user_id=user_id).first()
        
        if not mindmap:
            return jsonify({'code': 404, 'message': '脑图不存在'}), 404
        
        data = request.json
        new_title = data.get('title', mindmap.title)
        
        # 如果标题有变化，检查是否已存在同名脑图
        if new_title != mindmap.title:
            existing_mindmap = Mindmap.query.filter_by(user_id=user_id, title=new_title).first()
            if existing_mindmap:
                return jsonify({'code': 400, 'message': '已存在同名脑图，请使用其他名称'}), 400
        
        # 保存旧版本
        mindmap.save_version(user_id)
        
        # 更新脑图数据
        mindmap.title = new_title
        mindmap.data = data.get('data', mindmap.data)
        mindmap.is_public = data.get('is_public', mindmap.is_public)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': mindmap.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"更新脑图接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/mindmaps/<int:mindmap_id>', methods=['DELETE'])
@jwt_required()
def delete_mindmap(mindmap_id):
    """删除脑图"""
    try:
        user_id = get_jwt_identity()
        mindmap = Mindmap.query.filter_by(id=mindmap_id, user_id=user_id).first()
        
        if not mindmap:
            return jsonify({'code': 404, 'message': '脑图不存在'}), 404
        
        # 删除脑图版本记录
        MindmapVersion.query.filter_by(mindmap_id=mindmap_id).delete()
        
        # 删除脑图
        db.session.delete(mindmap)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
    except Exception as e:
        logger.error(f"删除脑图接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/mindmaps/<int:mindmap_id>/versions', methods=['GET'])
@jwt_required()
def get_mindmap_versions(mindmap_id):
    """获取脑图版本历史"""
    try:
        user_id = get_jwt_identity()
        mindmap = Mindmap.query.filter_by(id=mindmap_id, user_id=user_id).first()
        
        if not mindmap:
            return jsonify({'code': 404, 'message': '脑图不存在'}), 404
        
        versions = MindmapVersion.query.filter_by(mindmap_id=mindmap_id).order_by(MindmapVersion.updated_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [version.to_dict() for version in versions]
        }), 200
    except Exception as e:
        logger.error(f"获取脑图版本历史接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/mindmaps/<int:mindmap_id>/versions/<int:version_id>', methods=['GET'])
@jwt_required()
def get_mindmap_version(mindmap_id, version_id):
    """获取脑图特定版本"""
    try:
        user_id = get_jwt_identity()
        mindmap = Mindmap.query.filter_by(id=mindmap_id, user_id=user_id).first()
        
        if not mindmap:
            return jsonify({'code': 404, 'message': '脑图不存在'}), 404
        
        version = MindmapVersion.query.filter_by(id=version_id, mindmap_id=mindmap_id).first()
        
        if not version:
            return jsonify({'code': 404, 'message': '版本不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': version.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"获取脑图特定版本接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/mindmaps/<int:mindmap_id>/versions/<int:version_id>', methods=['POST'])
@jwt_required()
def rollback_mindmap_version(mindmap_id, version_id):
    """回滚脑图版本"""
    try:
        user_id = get_jwt_identity()
        mindmap = Mindmap.query.filter_by(id=mindmap_id, user_id=user_id).first()
        
        if not mindmap:
            return jsonify({'code': 404, 'message': '脑图不存在'}), 404
        
        version = MindmapVersion.query.filter_by(id=version_id, mindmap_id=mindmap_id).first()
        
        if not version:
            return jsonify({'code': 404, 'message': '版本不存在'}), 404
        
        # 保存当前版本
        mindmap.save_version(user_id)
        
        # 回滚内容
        mindmap.data = version.data
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '版本回滚成功',
            'data': mindmap.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"回滚脑图版本接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

# -------------------------- 共享链接管理接口 --------------------------
@app.route('/api/share-links', methods=['POST'])
@jwt_required()
def create_share_link():
    """创建共享链接"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        # 验证资源所有权
        resource_id = data.get('resource_id')
        resource_type = data.get('resource_type')
        is_collaborative = data.get('is_collaborative', False)
        
        # 支持的资源类型列表
        supported_types = ['note', 'flowchart', 'mindmap', 'table_document', 'whiteboard']
        
        if resource_type not in supported_types:
            return jsonify({'code': 400, 'message': f'不支持的资源类型，支持的类型包括: {supported_types}'}), 400
        
        # 检查资源是否存在并属于当前用户
        query = {
            'id': resource_id,
            'user_id': user_id
        }
        
        if resource_type == 'note':
            resource = Note.query.filter_by(**query).first()
        elif resource_type == 'flowchart':
            resource = Flowchart.query.filter_by(**query).first()
        elif resource_type == 'mindmap':
            resource = Mindmap.query.filter_by(**query).first()
        elif resource_type == 'table_document':
            resource = TableDocument.query.filter_by(**query).first()
        elif resource_type == 'whiteboard':
            resource = Whiteboard.query.filter_by(**query).first()
        
        if not resource:
            return jsonify({'code': 404, 'message': '资源不存在或无权限'}), 404
        
        # 创建共享链接
        share_link = ShareLink(
            **{f'{resource_type}_id': resource_id},
            token=str(uuid.uuid4()),
            room_id=str(uuid.uuid4()) if is_collaborative else None,
            permission=data.get('permission', 'view'),
            is_collaborative=is_collaborative,
            expire_at=datetime.now() + timedelta(days=data.get('expire_days', 7))
        )
        
        db.session.add(share_link)
        db.session.commit()
        
        response_data = {
            'token': share_link.token,
            'permission': share_link.permission,
            'expire_at': share_link.expire_at.isoformat(),
            'is_collaborative': share_link.is_collaborative
        }
        
        # 如果是协作文档，返回房间ID
        if is_collaborative:
            response_data['room_id'] = share_link.room_id
        
        return jsonify({
            'code': 201,
            'message': '创建成功',
            'data': response_data
        }), 201
    except Exception as e:
        logger.error(f"创建共享链接接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'服务器内部错误: {str(e)}'}), 500

# -------------------------- 定时任务 --------------------------
def clean_expired_share_links():
    """清理过期的共享链接"""
    try:
        with app.app_context():
            expired_links = ShareLink.query.filter(ShareLink.expire_at < datetime.now()).all()
            for link in expired_links:
                db.session.delete(link)
            db.session.commit()
            logger.info(f"清理了 {len(expired_links)} 个过期共享链接")
    except Exception as e:
        logger.error(f"清理过期共享链接任务异常: {str(e)}", exc_info=True)

# 添加定时任务（每天凌晨执行）
scheduler.add_job(clean_expired_share_links, 'interval', days=1, start_date=datetime.now() + timedelta(seconds=5))

# -------------------------- AI聊天接口 --------------------------
# 导入OpenAI SDK
from openai import OpenAI

@app.route('/api/ai/chat', methods=['POST'])
@jwt_required()
def ai_chat():
    """AI聊天接口"""
    try:
        data = request.json
        messages = data.get('messages', [])
        user_id = get_jwt_identity()
        
        # 增强请求日志
        logger.info(f"AI聊天请求开始: 用户ID={user_id}, 消息数量={len(messages)}, IP={request.remote_addr}")
        
        # 记录消息类型分布
        message_types = {}
        for msg in messages:
            role = msg.get('role', 'unknown')
            message_types[role] = message_types.get(role, 0) + 1
        logger.info(f"消息类型分布: {message_types}")
        
        if not messages:
            logger.warning(f"AI聊天请求失败: 消息为空, 用户ID={user_id}")
            return jsonify({'code': 400, 'message': '请求参数不能为空'}), 400
        
        # 使用OpenAI SDK调用阿里云百炼API
        dashscope_api_key = os.getenv('DASHSCOPE_API_KEY', '')
        dashscope_base_url = os.getenv('DASHSCOPE_BASE_URL', '')
        dashscope_model = os.getenv('DASHSCOPE_MODEL', 'qwen-plus')
        
        logger.info(f"阿里云百炼API密钥配置: {dashscope_api_key[:10]}..." if dashscope_api_key else "未配置")
        logger.info(f"阿里云百炼API基础URL: {dashscope_base_url}")
        logger.info(f"阿里云百炼API模型: {dashscope_model}")
        
        if not dashscope_api_key or not dashscope_base_url:
            logger.error("阿里云百炼API配置不完整")
            return jsonify({
                'code': 500,
                'message': 'AI服务配置不完整',
                'data': {
                    'content': ''
                }
            }), 500
        
        logger.info("开始使用阿里云百炼API")
        
        # 初始化OpenAI客户端（用于调用阿里云百炼API）
        logger.info("正在初始化OpenAI客户端...")
        client = OpenAI(
            api_key=dashscope_api_key,
            base_url=dashscope_base_url,
            timeout=120  # 增加超时时间到120秒，与前端保持一致，适应AI生成内容的长时间处理
        )
        logger.info("OpenAI客户端初始化成功")
        
        # 调用阿里云百炼API获取回复
        logger.info(f"准备发送阿里云百炼API请求: 模型={dashscope_model}, 消息数量={len(messages)}")
        
        # 记录完整的消息格式
        for i, msg in enumerate(messages):
            logger.info(f"消息{i+1}: role={msg.get('role')}, content={msg.get('content')[:50]}...")
        
        logger.info("正在发送阿里云百炼API请求...")
        logger.info(f"请求参数: model={dashscope_model}, messages={messages}, temperature=0.9, top_p=0.7, max_tokens=3000")
        
        # 调用API并处理异常
        try:
            response = client.chat.completions.create(
                model=dashscope_model,
                messages=messages,
                temperature=0.9,
                top_p=0.7,
                max_tokens=3000  # 增加max_tokens值，允许生成更长的内容
            )
            
            logger.info(f"阿里云百炼API请求发送成功")
            
            logger.info(f"阿里云百炼API响应类型: {type(response)}")
            logger.info(f"阿里云百炼API响应内容: {response}")
            
            # 安全提取响应内容
            if hasattr(response, 'choices'):
                logger.info(f"响应包含choices: {len(response.choices)}")
                if response.choices:
                    first_choice = response.choices[0]
                    logger.info(f"第一个choice类型: {type(first_choice)}")
                    if hasattr(first_choice, 'message'):
                        logger.info("choice包含message属性")
                        if hasattr(first_choice.message, 'content'):
                            content = first_choice.message.content
                            # 检查reasoning_content字段（对于推理模型）
                            if not content and hasattr(first_choice.message, 'reasoning_content'):
                                content = first_choice.message.reasoning_content
                                logger.info(f"成功提取reasoning_content: {content[:50]}...")
                            else:
                                logger.info(f"成功提取content: {content[:50]}...")
                            return jsonify({
                                'code': 200,
                                'message': 'success',
                                'data': {
                                    'content': content
                                }
                            }), 200
                        else:
                            error_msg = "千帆API响应格式错误: 缺少message.content属性"
                            logger.error(error_msg)
                            return jsonify({
                                'code': 500,
                                'message': 'AI服务响应格式错误',
                                'data': {
                                    'content': ''
                                }
                            }), 500
                    else:
                        error_msg = "千帆API响应格式错误: 缺少message属性"
                        logger.error(error_msg)
                        return jsonify({
                            'code': 500,
                            'message': 'AI服务响应格式错误',
                            'data': {
                                'content': ''
                            }
                        }), 500
                else:
                    error_msg = "千帆API响应格式错误: choices列表为空"
                    logger.error(error_msg)
                    return jsonify({
                        'code': 500,
                        'message': 'AI服务响应格式错误',
                        'data': {
                            'content': ''
                        }
                    }), 500
            else:
                error_msg = "千帆API响应格式错误: 缺少choices属性"
                logger.error(error_msg)
                return jsonify({
                    'code': 500,
                    'message': 'AI服务响应格式错误',
                    'data': {
                        'content': ''
                    }
                }), 500
        except Exception as e:
            logger.error(f"阿里云百炼API异常: {type(e).__name__}: {str(e)}", exc_info=True)
            return jsonify({
                'code': 500,
                'message': f'AI服务调用失败: {type(e).__name__}',
                'data': {
                    'content': ''
                }
            }), 500
            
    except Exception as e:
        logger.error(f"AI聊天接口异常: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500

# -------------------------- 定时清理过期共享链接 --------------------------
def clean_expired_share_links():
    """清理过期的共享链接"""
    try:
        with app.app_context():
            expired_links = ShareLink.query.filter(ShareLink.expire_at < datetime.now()).all()
            for link in expired_links:
                db.session.delete(link)
            db.session.commit()
            logger.info(f"清理了 {len(expired_links)} 个过期共享链接")
    except Exception as e:
        logger.error(f"清理过期共享链接任务异常: {str(e)}", exc_info=True)

# -------------------------- 管理员接口 --------------------------
@app.route('/api/admin/dashboard/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    """获取管理员统计数据"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'code': 403, 'message': '无管理员权限'}), 403
        
        # 统计数据
        user_count = User.query.count()
        today_users = User.query.filter(User.created_at >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).count()
        
        # 计算最近7天用户增长
        recent_user_growth = []
        today = datetime.now()
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            count = User.query.filter(
                User.created_at >= start_of_day,
                User.created_at <= end_of_day
            ).count()
            recent_user_growth.append(count)
        
        stats = {
            'userCount': user_count,
            'todayUsers': today_users,
            'totalNotes': Note.query.count(),
            'normalNotes': Note.query.count(),
            'totalTables': TableDocument.query.count(),
            'totalWhiteboards': Whiteboard.query.count(),
            'totalMindmaps': Mindmap.query.count(),
            'totalFlowcharts': Flowchart.query.count(),
            'recentUserGrowth': recent_user_growth  # 最近7天用户增长
        }
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': stats
        }), 200
    except Exception as e:
        logger.error(f"获取管理员统计数据接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_admin_users():
    """获取用户列表（管理员）"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'code': 403, 'message': '无管理员权限'}), 403
        
        # 获取所有用户
        users = User.query.all()
        user_list = []
        
        for u in users:
            user_list.append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'is_admin': u.is_admin,
                'created_at': u.created_at.isoformat() if u.created_at else None
            })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': user_list
        }), 200
    except Exception as e:
        logger.error(f"获取用户列表接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user_status(user_id):
    """更新用户状态（管理员）"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin:
            return jsonify({'code': 403, 'message': '无管理员权限'}), 403
        
        # 获取要更新的用户
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 不允许修改自己的管理员状态
        if user_id == current_user_id:
            return jsonify({'code': 400, 'message': '不能修改自己的管理员状态'}), 400
        
        # 更新用户状态
        data = request.json
        if 'is_admin' in data:
            user.is_admin = bool(data['is_admin'])
            db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功'
        }), 200
    except Exception as e:
        logger.error(f"更新用户状态接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/admin/content', methods=['GET'])
@jwt_required()
def get_admin_content():
    """获取内容列表（管理员）"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'code': 403, 'message': '无管理员权限'}), 403
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        search = request.args.get('search', '')
        content_type = request.args.get('type', 'all')
        sort_by = request.args.get('sort_by', 'created_at')
        
        # 构建查询
        all_content = []
        
        # 查询笔记
        if content_type == 'all' or content_type == 'notes':
            notes = Note.query.all()
            for note in notes:
                all_content.append({
                    'id': note.id,
                    'title': note.title,
                    'type': '笔记',
                    'creator': note.author.username if note.author else '未知',
                    'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # 查询表格
        if content_type == 'all' or content_type == 'tables':
            tables = TableDocument.query.all()
            for table in tables:
                all_content.append({
                    'id': table.id,
                    'title': table.title,
                    'type': '表格',
                    'creator': table.author.username if table.author else '未知',
                    'created_at': table.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': table.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # 查询白板
        if content_type == 'all' or content_type == 'whiteboards':
            whiteboards = Whiteboard.query.all()
            for whiteboard in whiteboards:
                all_content.append({
                    'id': whiteboard.id,
                    'title': whiteboard.title,
                    'type': '白板',
                    'creator': whiteboard.author.username if whiteboard.author else '未知',
                    'created_at': whiteboard.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': whiteboard.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # 查询脑图
        if content_type == 'all' or content_type == 'mindmaps':
            mindmaps = Mindmap.query.all()
            for mindmap in mindmaps:
                all_content.append({
                    'id': mindmap.id,
                    'title': mindmap.title,
                    'type': '脑图',
                    'creator': mindmap.author.username if mindmap.author else '未知',
                    'created_at': mindmap.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': mindmap.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # 查询流程图
        if content_type == 'all' or content_type == 'flowcharts':
            flowcharts = Flowchart.query.all()
            for flowchart in flowcharts:
                all_content.append({
                    'id': flowchart.id,
                    'title': flowchart.title,
                    'type': '流程图',
                    'creator': flowchart.author.username if flowchart.author else '未知',
                    'created_at': flowchart.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': flowchart.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # 搜索过滤
        if search:
            all_content = [item for item in all_content if search.lower() in item['title'].lower() or search.lower() in item['creator'].lower()]
        
        # 排序
        if sort_by == 'created_at':
            all_content.sort(key=lambda x: x['created_at'], reverse=True)
        elif sort_by == 'updated_at':
            all_content.sort(key=lambda x: x['updated_at'], reverse=True)
        elif sort_by == 'title':
            all_content.sort(key=lambda x: x['title'])
        
        # 分页
        total = len(all_content)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_content = all_content[start:end]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'items': paginated_content,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }), 200
    except Exception as e:
        logger.error(f"获取内容列表接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/admin/content/<int:content_id>', methods=['DELETE'])
@jwt_required()
def delete_admin_content(content_id):
    """删除内容（管理员）"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'code': 403, 'message': '无管理员权限'}), 403
        
        # 尝试删除笔记
        note = Note.query.get(content_id)
        if note:
            db.session.delete(note)
            db.session.commit()
            return jsonify({'code': 200, 'message': '删除成功'}), 200
        
        # 尝试删除表格
        table = TableDocument.query.get(content_id)
        if table:
            db.session.delete(table)
            db.session.commit()
            return jsonify({'code': 200, 'message': '删除成功'}), 200
        
        # 尝试删除白板
        whiteboard = Whiteboard.query.get(content_id)
        if whiteboard:
            db.session.delete(whiteboard)
            db.session.commit()
            return jsonify({'code': 200, 'message': '删除成功'}), 200
        
        # 尝试删除脑图
        mindmap = Mindmap.query.get(content_id)
        if mindmap:
            db.session.delete(mindmap)
            db.session.commit()
            return jsonify({'code': 200, 'message': '删除成功'}), 200
        
        # 尝试删除流程图
        flowchart = Flowchart.query.get(content_id)
        if flowchart:
            db.session.delete(flowchart)
            db.session.commit()
            return jsonify({'code': 200, 'message': '删除成功'}), 200
        
        return jsonify({'code': 404, 'message': '内容不存在'}), 404
    except Exception as e:
        logger.error(f"删除内容接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/admin/export', methods=['GET'])
@jwt_required()
def export_admin_data():
    """导出数据（管理员）"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'code': 403, 'message': '无管理员权限'}), 403
        
        # 准备导出数据
        export_data = {
            'users': {
                'data': [],
                'summary': {
                    'total_users': 0,
                    'today_users': 0,
                    'recent_users': 0
                }
            },
            'content': {
                'data': [],
                'summary': {
                    'total_content': 0,
                    'notes': 0,
                    'tables': 0,
                    'whiteboards': 0,
                    'mindmaps': 0,
                    'flowcharts': 0
                }
            }
        }
        
        # 导出用户数据
        users = User.query.all()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_7_days = today - timedelta(days=7)
        today_users_count = 0
        recent_users_count = 0
        
        for u in users:
            user_data = {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'is_admin': u.is_admin,
                'created_at': u.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'last_login': u.last_login.strftime('%Y-%m-%d %H:%M:%S') if u.last_login else 'N/A'
            }
            export_data['users']['data'].append(user_data)
            
            # 统计今日新增用户
            if u.created_at >= today:
                today_users_count += 1
            
            # 统计近日新增用户（最近7天）
            if u.created_at >= recent_7_days:
                recent_users_count += 1
        
        # 填充用户统计数据
        export_data['users']['summary']['total_users'] = len(users)
        export_data['users']['summary']['today_users'] = today_users_count
        export_data['users']['summary']['recent_users'] = recent_users_count
        
        # 导出内容数据
        all_content = []
        
        # 导出笔记
        notes = Note.query.all()
        for note in notes:
            content_data = {
                'id': note.id,
                'title': note.title,
                'type': '笔记',
                'creator': note.author.username if note.author else '未知',
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            all_content.append(content_data)
        
        # 导出表格
        tables = TableDocument.query.all()
        for table in tables:
            content_data = {
                'id': table.id,
                'title': table.title,
                'type': '表格',
                'creator': table.author.username if table.author else '未知',
                'created_at': table.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': table.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            all_content.append(content_data)
        
        # 导出白板
        whiteboards = Whiteboard.query.all()
        for whiteboard in whiteboards:
            content_data = {
                'id': whiteboard.id,
                'title': whiteboard.title,
                'type': '白板',
                'creator': whiteboard.author.username if whiteboard.author else '未知',
                'created_at': whiteboard.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': whiteboard.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            all_content.append(content_data)
        
        # 导出脑图
        mindmaps = Mindmap.query.all()
        for mindmap in mindmaps:
            content_data = {
                'id': mindmap.id,
                'title': mindmap.title,
                'type': '脑图',
                'creator': mindmap.author.username if mindmap.author else '未知',
                'created_at': mindmap.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': mindmap.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            all_content.append(content_data)
        
        # 导出流程图
        flowcharts = Flowchart.query.all()
        for flowchart in flowcharts:
            content_data = {
                'id': flowchart.id,
                'title': flowchart.title,
                'type': '流程图',
                'creator': flowchart.author.username if flowchart.author else '未知',
                'created_at': flowchart.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': flowchart.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            all_content.append(content_data)
        
        # 填充内容数据
        export_data['content']['data'] = all_content
        export_data['content']['summary']['total_content'] = len(all_content)
        export_data['content']['summary']['notes'] = len(notes)
        export_data['content']['summary']['tables'] = len(tables)
        export_data['content']['summary']['whiteboards'] = len(whiteboards)
        export_data['content']['summary']['mindmaps'] = len(mindmaps)
        export_data['content']['summary']['flowcharts'] = len(flowcharts)
        
        return jsonify({
            'code': 200,
            'message': '导出成功',
            'data': export_data
        }), 200
    except Exception as e:
        logger.error(f"导出数据接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

# -------------------------- 错误处理 --------------------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({'code': 404, 'message': '资源不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

# -------------------------- 静态文件服务 --------------------------
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# -------------------------- 分享内容接口 --------------------------
@app.route('/api/share/<string:token>', methods=['GET'])
def get_shared_content(token):
    """获取分享内容"""
    try:
        # 查找分享链接
        share_link = ShareLink.query.filter_by(token=token).first()
        if not share_link:
            return jsonify({'code': 404, 'message': '分享链接不存在'}), 404
        
        # 检查是否过期
        if share_link.expire_at and share_link.expire_at < datetime.now():
            return jsonify({'code': 410, 'message': '分享链接已过期'}), 410
        
        # 构建基本响应数据
        response = {
            'code': 200,
            'message': '获取成功',
            'permission': share_link.permission,
            'is_collaborative': share_link.is_collaborative
        }
        
        # 如果是协作文档，添加房间ID
        if share_link.is_collaborative and share_link.room_id:
            response['room_id'] = share_link.room_id
        
        # 根据类型获取内容
        if share_link.note_id:
            note = Note.query.get(share_link.note_id)
            if not note:
                return jsonify({'code': 404, 'message': '分享的笔记不存在'}), 404
            response.update({
                'type': 'note',
                'note': note.to_full_dict()
            })
        elif share_link.flowchart_id:
            flowchart = Flowchart.query.get(share_link.flowchart_id)
            if not flowchart:
                return jsonify({'code': 404, 'message': '分享的流程图不存在'}), 404
            response.update({
                'type': 'flowchart',
                'flowchart': flowchart.to_dict()
            })
        elif share_link.mindmap_id:
            mindmap = Mindmap.query.get(share_link.mindmap_id)
            if not mindmap:
                return jsonify({'code': 404, 'message': '分享的脑图不存在'}), 404
            response.update({
                'type': 'mindmap',
                'mindmap': mindmap.to_dict()
            })
        elif share_link.table_document_id:
            table_doc = TableDocument.query.get(share_link.table_document_id)
            if not table_doc:
                return jsonify({'code': 404, 'message': '分享的表格不存在'}), 404
            response.update({
                'type': 'table_document',
                'table': table_doc.to_dict()
            })
        elif share_link.whiteboard_id:
            whiteboard = Whiteboard.query.get(share_link.whiteboard_id)
            if not whiteboard:
                return jsonify({'code': 404, 'message': '分享的白板不存在'}), 404
            response.update({
                'type': 'whiteboard',
                'whiteboard': whiteboard.to_dict()
            })
        else:
            return jsonify({'code': 404, 'message': '分享链接无效'}), 404
        
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"获取分享内容接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/share/<string:token>', methods=['GET'])
def get_shared_content_html(token):
    """获取分享内容（直接返回HTML）"""
    try:
        # 查找分享链接
        share_link = ShareLink.query.filter_by(token=token).first()
        if not share_link:
            return '''
            <html>
            <head>
                <title>分享链接无效</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .error { color: red; font-size: 24px; }
                </style>
            </head>
            <body>
                <div class="error">分享链接无效或已过期</div>
                <p>请检查链接是否正确，或联系分享者获取新的链接</p>
            </body>
            </html>
            ''', 404
        
        # 检查是否过期
        if share_link.expire_at and share_link.expire_at < datetime.now():
            return '''
            <html>
            <head>
                <title>分享链接已过期</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .error { color: red; font-size: 24px; }
                </style>
            </head>
            <body>
                <div class="error">分享链接已过期</div>
                <p>请联系分享者获取新的链接</p>
            </body>
            </html>
            ''', 410
        
        # 根据类型返回HTML内容
        if share_link.note_id:
            note = Note.query.get(share_link.note_id)
            if not note:
                return '''
                <html>
                <head>
                    <title>分享内容不存在</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .error { color: red; font-size: 24px; }
                    </style>
                </head>
                <body>
                    <div class="error">分享的内容不存在</div>
                    <p>请联系分享者获取新的链接</p>
                </body>
                </html>
                ''', 404
            
            # 生成笔记的HTML内容
            content = note.content
            if isinstance(content, str):
                try:
                    import json
                    content_obj = json.loads(content)
                    if isinstance(content_obj, dict) and 'ops' in content_obj:
                        # 处理富文本内容
                        html_content = ''
                        for op in content_obj['ops']:
                            if 'insert' in op:
                                html_content += op['insert'].replace('\n', '<br>')
                        content = html_content
                except:
                    # 如果解析失败，直接使用原始内容
                    content = content.replace('\n', '<br>')
            
            return f'''
            <html>
            <head>
                <title>{note.title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }}
                    h1 {{ color: #333; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
                    .content {{ margin-top: 20px; line-height: 1.6; }}
                    .meta {{ margin-top: 30px; font-size: 12px; color: #999; }}
                </style>
            </head>
            <body>
                <h1>{note.title}</h1>
                <div class="content">{content}</div>
                <div class="meta">
                    <p>分享时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>权限: {'只读' if share_link.permission == 'view' else '可编辑'}</p>
                </div>
            </body>
            </html>
            '''
        elif share_link.flowchart_id:
            flowchart = Flowchart.query.get(share_link.flowchart_id)
            if not flowchart:
                return '''
                <html>
                <head>
                    <title>分享内容不存在</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .error { color: red; font-size: 24px; }
                    </style>
                </head>
                <body>
                    <div class="error">分享的内容不存在</div>
                    <p>请联系分享者获取新的链接</p>
                </body>
                </html>
                ''', 404
            
            return f'''
            <html>
            <head>
                <title>{flowchart.title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }}
                    h1 {{ color: #333; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
                    .content {{ margin-top: 20px; }}
                    .meta {{ margin-top: 30px; font-size: 12px; color: #999; }}
                </style>
            </head>
            <body>
                <h1>{flowchart.title}</h1>
                <div class="content">
                    <p>这是一个流程图分享</p>
                    <p>描述: {flowchart.description or '无'}</p>
                </div>
                <div class="meta">
                    <p>分享时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>权限: {'只读' if share_link.permission == 'view' else '可编辑'}</p>
                </div>
            </body>
            </html>
            '''
        elif share_link.mindmap_id:
            mindmap = Mindmap.query.get(share_link.mindmap_id)
            if not mindmap:
                return '''
                <html>
                <head>
                    <title>分享内容不存在</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .error { color: red; font-size: 24px; }
                    </style>
                </head>
                <body>
                    <div class="error">分享的内容不存在</div>
                    <p>请联系分享者获取新的链接</p>
                </body>
                </html>
                ''', 404
            
            return f'''
            <html>
            <head>
                <title>{mindmap.title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }}
                    h1 {{ color: #333; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
                    .content {{ margin-top: 20px; }}
                    .meta {{ margin-top: 30px; font-size: 12px; color: #999; }}
                </style>
            </head>
            <body>
                <h1>{mindmap.title}</h1>
                <div class="content">
                    <p>这是一个脑图分享</p>
                </div>
                <div class="meta">
                    <p>分享时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>权限: {'只读' if share_link.permission == 'view' else '可编辑'}</p>
                </div>
            </body>
            </html>
            '''
        else:
            return '''
            <html>
            <head>
                <title>分享链接无效</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .error { color: red; font-size: 24px; }
                </style>
            </head>
            <body>
                <div class="error">分享链接无效</div>
                <p>请联系分享者获取新的链接</p>
            </body>
            </html>
            ''', 404
    except Exception as e:
        logger.error(f"获取分享内容HTML接口异常: {str(e)}", exc_info=True)
        return '''
        <html>
        <head>
            <title>服务器错误</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error { color: red; font-size: 24px; }
            </style>
        </head>
        <body>
            <div class="error">服务器内部错误</div>
            <p>请稍后重试</p>
        </body>
        </html>
        ''', 500

# -------------------------- WebSocket事件处理 --------------------------
@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    print(f'客户端 {request.sid} 已连接')
    emit('connected', {'message': '连接成功', 'sid': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开连接"""
    print(f'客户端 {request.sid} 已断开连接')
    # 从所有房间中移除用户
    for room_id in online_users.keys():
        if request.sid in online_users[room_id]:
            online_users[room_id].remove(request.sid)
            # 通知房间内其他用户有用户离开
            emit('user_left', {'user_id': request.sid}, room=room_id)
            # 如果房间为空，删除房间
            if not online_users[room_id]:
                del online_users[room_id]
            break

@socketio.on('join_room')
def handle_join_room(data):
    """处理用户加入房间"""
    room_id = data.get('room_id')
    user_info = data.get('user_info', {})
    if not room_id:
        emit('error', {'message': '房间ID不能为空'})
        return
    
    # 加入房间
    join_room(room_id)
    
    # 更新在线用户列表
    if room_id not in online_users:
        online_users[room_id] = []
    online_users[room_id].append({
        'sid': request.sid,
        'user_id': user_info.get('id', request.sid),
        'username': user_info.get('username', f'用户{request.sid[:5]}')
    })
    
    # 通知房间内其他用户有新用户加入
    emit('user_joined', {
        'user': {
            'sid': request.sid,
            'user_id': user_info.get('id', request.sid),
            'username': user_info.get('username', f'用户{request.sid[:5]}')
        }
    }, room=room_id)
    
    # 发送当前房间的在线用户列表给新加入的用户
    emit('online_users', {'users': online_users[room_id]})
    
    print(f'客户端 {request.sid} 加入了房间 {room_id}')

@socketio.on('leave_room')
def handle_leave_room(data):
    """处理用户离开房间"""
    room_id = data.get('room_id')
    if not room_id:
        emit('error', {'message': '房间ID不能为空'})
        return
    
    # 离开房间
    leave_room(room_id)
    
    # 更新在线用户列表
    if room_id in online_users:
        online_users[room_id] = [user for user in online_users[room_id] if user['sid'] != request.sid]
        # 通知房间内其他用户有用户离开
        emit('user_left', {'user_id': request.sid}, room=room_id)
        # 如果房间为空，删除房间
        if not online_users[room_id]:
            del online_users[room_id]
    
    print(f'客户端 {request.sid} 离开了房间 {room_id}')

@socketio.on('send_message')
def handle_send_message(data):
    """处理发送消息"""
    room_id = data.get('room_id')
    message = data.get('message')
    sender_id = data.get('sender_id', request.sid)
    timestamp = data.get('timestamp', datetime.now().isoformat())
    
    if not room_id or not message:
        emit('error', {'message': '房间ID和消息不能为空'})
        return
    
    # 广播消息给房间内所有用户（除了发送者）
    emit('new_message', {
        'sender_id': sender_id,
        'message': message,
        'timestamp': timestamp
    }, room=room_id)
    
    print(f'客户端 {sender_id} 在房间 {room_id} 发送了消息: {message}')

@socketio.on('sync_document')
def handle_sync_document(data):
    """处理文档同步"""
    room_id = data.get('room_id')
    doc_id = data.get('doc_id')
    doc_type = data.get('doc_type')
    doc_content = data.get('content')
    version = data.get('version', 0)
    
    if not room_id or not doc_id or not doc_type or doc_content is None:
        emit('error', {'message': '房间ID、文档ID、文档类型和内容不能为空'})
        return
    
    # 更新文档状态
    doc_key = f'{doc_type}:{doc_id}'
    collaborative_docs[doc_key] = {
        'content': doc_content,
        'version': version,
        'last_updated': datetime.now().isoformat()
    }
    
    # 广播文档更新给房间内所有用户（除了发送者）
    emit('document_updated', {
        'doc_id': doc_id,
        'doc_type': doc_type,
        'content': doc_content,
        'version': version,
        'timestamp': datetime.now().isoformat()
    }, room=room_id)
    
    print(f'文档 {doc_key} 已更新，版本: {version}')

@socketio.on('get_document_state')
def handle_get_document_state(data):
    """获取文档当前状态"""
    doc_id = data.get('doc_id')
    doc_type = data.get('doc_type')
    
    if not doc_id or not doc_type:
        emit('error', {'message': '文档ID和类型不能为空'})
        return
    
    # 获取文档状态
    doc_key = f'{doc_type}:{doc_id}'
    doc_state = collaborative_docs.get(doc_key, {
        'content': None,
        'version': 0,
        'last_updated': datetime.now().isoformat()
    })
    
    # 发送文档状态给请求者
    emit('document_state', {
        'doc_id': doc_id,
        'doc_type': doc_type,
        **doc_state
    })

# -------------------------- 主函数 --------------------------
if __name__ == '__main__':
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 启动定时任务调度器
    scheduler = BackgroundScheduler()
    scheduler.add_job(clean_expired_share_links, 'interval', days=1)
    scheduler.start()
    
    # 启动应用
    # 使用socketio.run而不是app.run来支持WebSocket
    socketio.run(app, debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
