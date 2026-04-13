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
from sqlalchemy import text, or_
import eventlet
from eventlet import wsgi
import threading

# 加载.env文件中的环境变量
from dotenv import load_dotenv
load_dotenv()

# 导入自定义模块
from config import get_config
from models import db, bcrypt, User, Note, NoteVersion, Category, Tag, Flowchart, FlowchartVersion, TableDocument, TableDocumentVersion, Whiteboard, WhiteboardVersion, Mindmap, MindmapVersion, ShareLink, KnowledgeGraph, KnowledgeNode, KnowledgeRelation
from whiteboard.socket_handler import init_socketio

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
# 使用自定义的 SocketIO 初始化函数，集成 Whitebophir 白板功能
socketio = init_socketio(app)

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

@app.route('/api/user/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """更新用户个人信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
        
        # 更新用户信息
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新用户信息接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@app.route('/api/user/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            return jsonify({'code': 400, 'message': '密码不能为空'}), 400
        
        if new_password != confirm_password:
            return jsonify({'code': 400, 'message': '两次输入的密码不一致'}), 400
        
        # 验证当前密码（使用User模型的check_password方法）
        if not user.check_password(current_password):
            return jsonify({'code': 400, 'message': '当前密码错误'}), 400
        
        # 更新密码（使用User模型的set_password方法）
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '密码修改成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"修改密码接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


# -------------------------- 数据导出接口 --------------------------
@app.route('/api/user/export-data', methods=['GET'])
@jwt_required()
def export_data():
    """导出用户所有数据"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 导出用户数据
        export_data = {
            'user': user.to_dict(),
            'notes': [],
            'categories': [],
            'tags': [],
            'flowcharts': [],
            'tables': [],
            'whiteboards': [],
            'mindmaps': [],
            'export_time': datetime.now().isoformat()
        }
        
        # 导出笔记
        notes = Note.query.filter_by(user_id=user_id, is_deleted=False).all()
        for note in notes:
            export_data['notes'].append(note.to_full_dict())
        
        # 导出分类
        categories = Category.query.filter_by(user_id=user_id).all()
        for category in categories:
            export_data['categories'].append(category.to_dict())
        
        # 导出标签
        tags = Tag.query.filter_by(user_id=user_id).all()
        for tag in tags:
            export_data['tags'].append(tag.to_dict())
        
        # 导出流程图
        flowcharts = Flowchart.query.filter_by(user_id=user_id, is_deleted=False).all()
        for flowchart in flowcharts:
            export_data['flowcharts'].append(flowchart.to_dict())
        
        # 导出表格
        tables = TableDocument.query.filter_by(user_id=user_id, is_deleted=False).all()
        for table in tables:
            export_data['tables'].append(table.to_dict())
        
        # 导出白板
        whiteboards = Whiteboard.query.filter_by(user_id=user_id, is_deleted=False).all()
        for whiteboard in whiteboards:
            export_data['whiteboards'].append(whiteboard.to_dict())
        
        # 导出脑图
        mindmaps = Mindmap.query.filter_by(user_id=user_id, is_deleted=False).all()
        for mindmap in mindmaps:
            export_data['mindmaps'].append(mindmap.to_dict())
        
        logger.info(f"用户 {user_id} 导出数据成功")
        
        return jsonify({
            'code': 200,
            'message': '数据导出成功',
            'data': export_data
        }), 200
    
    except Exception as e:
        logger.error(f"数据导出接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


# -------------------------- 数据导入接口 --------------------------
@app.route('/api/user/import-data', methods=['POST'])
@jwt_required()
def import_data():
    """导入用户数据"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
        
        imported_count = {
            'notes': 0,
            'categories': 0,
            'tags': 0,
            'flowcharts': 0,
            'tables': 0,
            'whiteboards': 0,
            'mindmaps': 0
        }
        
        # 导入分类
        if 'categories' in data:
            for category_data in data['categories']:
                existing_category = Category.query.filter_by(
                    user_id=user_id, 
                    name=category_data.get('name')
                ).first()
                if not existing_category:
                    new_category = Category(
                        name=category_data.get('name'),
                        user_id=user_id
                    )
                    db.session.add(new_category)
                    imported_count['categories'] += 1
        
        # 导入标签
        if 'tags' in data:
            for tag_data in data['tags']:
                existing_tag = Tag.query.filter_by(
                    user_id=user_id, 
                    name=tag_data.get('name')
                ).first()
                if not existing_tag:
                    new_tag = Tag(
                        name=tag_data.get('name'),
                        user_id=user_id
                    )
                    db.session.add(new_tag)
                    imported_count['tags'] += 1
        
        db.session.commit()
        
        # 导入笔记（需要先导入分类和标签）
        if 'notes' in data:
            for note_data in data['notes']:
                new_note = Note(
                    title=note_data.get('title', '无标题'),
                    content=note_data.get('content', ''),
                    type=note_data.get('type', 'richtext'),
                    user_id=user_id,
                    is_public=note_data.get('is_public', False)
                )
                
                # 设置分类
                if note_data.get('category_id'):
                    category = Category.query.filter_by(
                        user_id=user_id,
                        id=note_data.get('category_id')
                    ).first()
                    if category:
                        new_note.category_id = category.id
                
                db.session.add(new_note)
                imported_count['notes'] += 1
        
        # 导入流程图
        if 'flowcharts' in data:
            for flowchart_data in data['flowcharts']:
                new_flowchart = Flowchart(
                    title=flowchart_data.get('title', '无标题'),
                    description=flowchart_data.get('description', ''),
                    flow_data=flowchart_data.get('flow_data'),
                    thumbnail=flowchart_data.get('thumbnail'),
                    is_public=flowchart_data.get('is_public', False),
                    user_id=user_id
                )
                db.session.add(new_flowchart)
                imported_count['flowcharts'] += 1
        
        # 导入表格
        if 'tables' in data:
            for table_data in data['tables']:
                new_table = TableDocument(
                    title=table_data.get('title', '无标题'),
                    columns_data=table_data.get('columns'),
                    rows_data=table_data.get('rows'),
                    cell_styles=table_data.get('cellStyles'),
                    user_id=user_id
                )
                db.session.add(new_table)
                imported_count['tables'] += 1
        
        # 导入白板
        if 'whiteboards' in data:
            for whiteboard_data in data['whiteboards']:
                new_whiteboard = Whiteboard(
                    title=whiteboard_data.get('title', '无标题'),
                    room_key=whiteboard_data.get('room_key'),
                    data=whiteboard_data.get('data'),
                    user_id=user_id
                )
                db.session.add(new_whiteboard)
                imported_count['whiteboards'] += 1
        
        # 导入脑图
        if 'mindmaps' in data:
            for mindmap_data in data['mindmaps']:
                new_mindmap = Mindmap(
                    title=mindmap_data.get('title', '无标题'),
                    data=mindmap_data.get('data'),
                    is_public=mindmap_data.get('is_public', False),
                    user_id=user_id
                )
                db.session.add(new_mindmap)
                imported_count['mindmaps'] += 1
        
        db.session.commit()
        logger.info(f"用户 {user_id} 导入数据成功: {imported_count}")
        
        return jsonify({
            'code': 200,
            'message': '数据导入成功',
            'data': imported_count
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"数据导入接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


# -------------------------- 清空数据接口 --------------------------
@app.route('/api/user/clear-data', methods=['DELETE'])
@jwt_required()
def clear_data():
    """清空用户所有数据（谨慎使用）"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 删除用户所有相关数据（通过级联删除）
        # 由于模型设置了cascade='all, delete-orphan'，删除用户会自动删除所有关联数据
        
        # 先统计要删除的数据量
        notes_count = Note.query.filter_by(user_id=user_id).count()
        flowcharts_count = Flowchart.query.filter_by(user_id=user_id).count()
        tables_count = TableDocument.query.filter_by(user_id=user_id).count()
        whiteboards_count = Whiteboard.query.filter_by(user_id=user_id).count()
        mindmaps_count = Mindmap.query.filter_by(user_id=user_id).count()
        categories_count = Category.query.filter_by(user_id=user_id).count()
        tags_count = Tag.query.filter_by(user_id=user_id).count()
        
        deleted_count = {
            'notes': notes_count,
            'flowcharts': flowcharts_count,
            'tables': tables_count,
            'whiteboards': whiteboards_count,
            'mindmaps': mindmaps_count,
            'categories': categories_count,
            'tags': tags_count
        }
        
        # 删除所有关联数据（保留用户本身）
        Note.query.filter_by(user_id=user_id).delete()
        Flowchart.query.filter_by(user_id=user_id).delete()
        TableDocument.query.filter_by(user_id=user_id).delete()
        Whiteboard.query.filter_by(user_id=user_id).delete()
        Mindmap.query.filter_by(user_id=user_id).delete()
        Category.query.filter_by(user_id=user_id).delete()
        Tag.query.filter_by(user_id=user_id).delete()
        
        db.session.commit()
        
        logger.warning(f"用户 {user_id} 清空所有数据: {deleted_count}")
        
        return jsonify({
            'code': 200,
            'message': '数据清空成功',
            'data': deleted_count
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"清空数据接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/search', methods=['GET'])
@jwt_required()
def search():
    """搜索内容"""
    try:
        user_id = get_jwt_identity()
        query = request.args.get('query', '')
        
        logger.info(f"========== 搜索请求到达 ==========")
        logger.info(f"用户ID: {user_id}")
        logger.info(f"搜索关键词: {query}")
        
        if not query:
            return jsonify({'code': 400, 'message': '搜索关键词不能为空'}), 400
        
        # 搜索笔记
        notes = Note.query.filter(
            Note.user_id == user_id,
            or_(
                Note.title.ilike(f'%{query}%'),
                Note.content.ilike(f'%{query}%')
            )
        ).all()
        
        # 搜索表格（使用正确的模型名称 TableDocument）
        tables = TableDocument.query.filter(
            TableDocument.user_id == user_id,
            TableDocument.title.ilike(f'%{query}%')
        ).all()
        
        # 搜索白板
        whiteboards = Whiteboard.query.filter(
            Whiteboard.user_id == user_id,
            Whiteboard.title.ilike(f'%{query}%')
        ).all()
        
        # 搜索脑图
        mindmaps = Mindmap.query.filter(
            Mindmap.user_id == user_id,
            Mindmap.title.ilike(f'%{query}%')
        ).all()
        
        # 搜索流程图
        flowcharts = Flowchart.query.filter(
            Flowchart.user_id == user_id,
            or_(
                Flowchart.title.ilike(f'%{query}%'),
                Flowchart.description.ilike(f'%{query}%')
            )
        ).all()
        
        # 整理搜索结果
        results = []
        
        for note in notes:
            results.append({
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'type': 'note',
                'updated_at': note.updated_at.isoformat()
            })
        
        for table in tables:
            content_preview = f"表格包含 {len(table.columns_data) if table.columns_data else 0} 列数据"
            results.append({
                'id': table.id,
                'title': table.title,
                'content': content_preview,
                'type': 'table',
                'updated_at': table.updated_at.isoformat()
            })
        
        for whiteboard in whiteboards:
            content_preview = "白板内容（可视化数据）"
            results.append({
                'id': whiteboard.id,
                'title': whiteboard.title,
                'content': content_preview,
                'type': 'whiteboard',
                'updated_at': whiteboard.updated_at.isoformat()
            })
        
        for mindmap in mindmaps:
            content_preview = "脑图数据"
            results.append({
                'id': mindmap.id,
                'title': mindmap.title,
                'content': content_preview,
                'type': 'mindmap',
                'updated_at': mindmap.updated_at.isoformat()
            })
        
        for flowchart in flowcharts:
            content_preview = flowchart.description or "流程图描述"
            results.append({
                'id': flowchart.id,
                'title': flowchart.title,
                'content': content_preview,
                'type': 'flowchart',
                'updated_at': flowchart.updated_at.isoformat()
            })
        
        # 按更新时间排序
        results.sort(key=lambda x: x['updated_at'], reverse=True)
        
        return jsonify({
            'code': 200,
            'message': '搜索成功',
            'data': results
        }), 200
    except Exception as e:
        logger.error(f"搜索接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

# -------------------------- 笔记管理接口 --------------------------
@app.route('/api/notes', methods=['GET'])
@jwt_required()
def get_notes():
    """获取用户的笔记列表"""
    try:
        user_id = get_jwt_identity()
        
        search_query = request.args.get('search', '')
        category_id = request.args.get('category_id', '')
        note_type = request.args.get('type', '')
        
        query = Note.query.filter_by(user_id=user_id, is_deleted=False)
        
        if search_query:
            query = query.filter(
                db.or_(
                    Note.title.ilike(f'%{search_query}%'),
                    Note.content.ilike(f'%{search_query}%')
                )
            )
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if note_type:
            query = query.filter_by(type=note_type)
        
        notes = query.order_by(Note.updated_at.desc()).all()
        
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
    """删除笔记（移动到回收站）"""
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id, is_deleted=False).first()
        
        if not note:
            return jsonify({'code': 404, 'message': '笔记不存在'}), 404
        
        # 标记为删除
        note.is_deleted = True
        note.deleted_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '已移至回收站'
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
        
        search_query = request.args.get('search', '')
        tag_ids = request.args.get('tag_ids', '')
        
        query = Flowchart.query.filter_by(user_id=user_id, is_deleted=False)
        
        if search_query:
            query = query.filter(
                db.or_(
                    Flowchart.title.ilike(f'%{search_query}%'),
                    Flowchart.description.ilike(f'%{search_query}%')
                )
            )
        
        if tag_ids:
            tag_id_list = [int(tid) for tid in tag_ids.split(',') if tid.strip()]
            if tag_id_list:
                query = query.filter(Flowchart.tags.any(id__in=tag_id_list))
        
        flowcharts = query.order_by(Flowchart.updated_at.desc()).all()
        
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
    """删除流程图（移动到回收站）"""
    try:
        user_id = get_jwt_identity()
        flowchart = Flowchart.query.filter_by(id=flowchart_id, user_id=user_id, is_deleted=False).first()
        
        if not flowchart:
            return jsonify({'code': 404, 'message': '流程图不存在'}), 404
        
        # 标记为删除
        flowchart.is_deleted = True
        flowchart.deleted_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '已移至回收站'
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
        tables = TableDocument.query.filter_by(user_id=user_id, is_deleted=False).order_by(TableDocument.updated_at.desc()).all()
        
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
    """删除表格（移动到回收站）"""
    try:
        user_id = get_jwt_identity()
        table = TableDocument.query.filter_by(id=table_id, user_id=user_id, is_deleted=False).first()
        
        if not table:
            return jsonify({'code': 404, 'message': '表格不存在'}), 404
        
        # 标记为删除
        table.is_deleted = True
        table.deleted_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '已移至回收站'
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
        whiteboards = Whiteboard.query.filter_by(user_id=user_id, is_deleted=False).order_by(Whiteboard.updated_at.desc()).all()
        
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
    """删除白板（移动到回收站）"""
    try:
        user_id = get_jwt_identity()
        whiteboard = Whiteboard.query.filter_by(id=whiteboard_id, user_id=user_id, is_deleted=False).first()
        
        if not whiteboard:
            return jsonify({'code': 404, 'message': '白板不存在'}), 404
        
        # 标记为删除
        whiteboard.is_deleted = True
        whiteboard.deleted_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '已移至回收站'
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
        mindmaps = Mindmap.query.filter_by(user_id=user_id, is_deleted=False).order_by(Mindmap.updated_at.desc()).all()
        
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
    """删除脑图（移动到回收站）"""
    try:
        user_id = get_jwt_identity()
        mindmap = Mindmap.query.filter_by(id=mindmap_id, user_id=user_id, is_deleted=False).first()
        
        if not mindmap:
            return jsonify({'code': 404, 'message': '脑图不存在'}), 404
        
        # 标记为删除
        mindmap.is_deleted = True
        mindmap.deleted_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '已移至回收站'
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

# -------------------------- 统一分享系统接口 --------------------------
@app.route('/api/shares', methods=['POST'])
@jwt_required()
def create_share():
    """创建分享链接（统一接口）"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        resource_id = data.get('resource_id')
        resource_type = data.get('resource_type')
        permission = data.get('permission', 'view')
        expire_days = data.get('expire_days', 7)
        is_collaborative = data.get('is_collaborative', False)
        
        supported_types = ['note', 'flowchart', 'mindmap', 'table_document', 'whiteboard', 'knowledge_graph']
        
        if resource_type not in supported_types:
            return jsonify({'code': 400, 'message': f'不支持的资源类型，支持: {", ".join(supported_types)}'}), 400
        
        if permission not in ['view', 'edit']:
            return jsonify({'code': 400, 'message': '权限类型只能是 view 或 edit'}), 400
        
        query = {'id': resource_id, 'user_id': user_id}
        resource = None
        
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
        elif resource_type == 'knowledge_graph':
            resource = KnowledgeGraph.query.filter_by(**query).first()
        
        if not resource:
            return jsonify({'code': 404, 'message': '资源不存在或无权限'}), 404
        
        existing_link = ShareLink.query.filter_by(
            **{f'{resource_type}_id': resource_id},
            permission=permission
        ).first()
        
        if existing_link:
            return jsonify({'code': 400, 'message': f'已存在{permission}权限的分享链接'}), 400
        
        share_link = ShareLink(
            **{f'{resource_type}_id': resource_id},
            token=str(uuid.uuid4()),
            room_id=str(uuid.uuid4()) if is_collaborative else None,
            permission=permission,
            is_collaborative=is_collaborative,
            expire_at=datetime.now() + timedelta(days=expire_days)
        )
        
        db.session.add(share_link)
        db.session.commit()
        
        response_data = {
            'id': share_link.id,
            'token': share_link.token,
            'permission': share_link.permission,
            'expire_at': share_link.expire_at.isoformat(),
            'is_collaborative': share_link.is_collaborative,
            'created_at': share_link.created_at.isoformat()
        }
        
        if is_collaborative and share_link.room_id:
            response_data['room_id'] = share_link.room_id
        
        return jsonify({
            'code': 201,
            'message': '分享链接创建成功',
            'data': response_data
        }), 201
    except Exception as e:
        logger.error(f"创建分享链接接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'服务器内部错误: {str(e)}'}), 500


@app.route('/api/shares/list', methods=['POST'])
@jwt_required()
def get_shares_list():
    """获取资源的分享链接列表"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        resource_id = data.get('resource_id')
        resource_type = data.get('resource_type')
        
        supported_types = ['note', 'flowchart', 'mindmap', 'table_document', 'whiteboard', 'knowledge_graph']
        
        if resource_type not in supported_types:
            return jsonify({'code': 400, 'message': f'不支持的资源类型'}), 400
        
        query = {'id': resource_id, 'user_id': user_id}
        resource = None
        
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
        elif resource_type == 'knowledge_graph':
            resource = KnowledgeGraph.query.filter_by(**query).first()
        
        if not resource:
            return jsonify({'code': 404, 'message': '资源不存在或无权限'}), 404
        
        share_links = ShareLink.query.filter_by(**{f'{resource_type}_id': resource_id}).all()
        
        shares = []
        for link in share_links:
            shares.append({
                'id': link.id,
                'token': link.token,
                'permission': link.permission,
                'expire_at': link.expire_at.isoformat() if link.expire_at else None,
                'is_collaborative': link.is_collaborative,
                'room_id': link.room_id,
                'created_at': link.created_at.isoformat()
            })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': shares
        }), 200
    except Exception as e:
        logger.error(f"获取分享链接列表接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/shares/<int:share_id>', methods=['PUT'])
@jwt_required()
def update_share(share_id):
    """更新分享链接（修改权限或过期时间）"""
    try:
        user_id = get_jwt_identity()
        share_link = ShareLink.query.get(share_id)
        
        if not share_link:
            return jsonify({'code': 404, 'message': '分享链接不存在'}), 404
        
        has_permission = False
        if share_link.note_id:
            has_permission = Note.query.filter_by(id=share_link.note_id, user_id=user_id).first() is not None
        elif share_link.flowchart_id:
            has_permission = Flowchart.query.filter_by(id=share_link.flowchart_id, user_id=user_id).first() is not None
        elif share_link.mindmap_id:
            has_permission = Mindmap.query.filter_by(id=share_link.mindmap_id, user_id=user_id).first() is not None
        elif share_link.table_document_id:
            has_permission = TableDocument.query.filter_by(id=share_link.table_document_id, user_id=user_id).first() is not None
        elif share_link.whiteboard_id:
            has_permission = Whiteboard.query.filter_by(id=share_link.whiteboard_id, user_id=user_id).first() is not None
        elif share_link.knowledge_graph_id:
            has_permission = KnowledgeGraph.query.filter_by(id=share_link.knowledge_graph_id, user_id=user_id).first() is not None
        
        if not has_permission:
            return jsonify({'code': 403, 'message': '无权修改此分享链接'}), 403
        
        data = request.json
        
        if 'permission' in data:
            new_permission = data['permission']
            if new_permission not in ['view', 'edit']:
                return jsonify({'code': 400, 'message': '权限类型只能是 view 或 edit'}), 400
            
            resource_type = None
            resource_id = None
            if share_link.note_id:
                resource_type = 'note'
                resource_id = share_link.note_id
            elif share_link.flowchart_id:
                resource_type = 'flowchart'
                resource_id = share_link.flowchart_id
            elif share_link.mindmap_id:
                resource_type = 'mindmap'
                resource_id = share_link.mindmap_id
            elif share_link.table_document_id:
                resource_type = 'table_document'
                resource_id = share_link.table_document_id
            elif share_link.whiteboard_id:
                resource_type = 'whiteboard'
                resource_id = share_link.whiteboard_id
            elif share_link.knowledge_graph_id:
                resource_type = 'knowledge_graph'
                resource_id = share_link.knowledge_graph_id
            
            if resource_type and resource_id:
                existing_link = ShareLink.query.filter(
                    ShareLink.id != share_id,
                    **{f'{resource_type}_id': resource_id},
                    permission=new_permission
                ).first()
                if existing_link:
                    return jsonify({'code': 400, 'message': f'已存在{new_permission}权限的分享链接'}), 400
            
            share_link.permission = new_permission
        
        if 'expire_days' in data:
            share_link.expire_at = datetime.now() + timedelta(days=data['expire_days'])
        
        if 'is_collaborative' in data:
            share_link.is_collaborative = data['is_collaborative']
            if data['is_collaborative'] and not share_link.room_id:
                share_link.room_id = str(uuid.uuid4())
            elif not data['is_collaborative']:
                share_link.room_id = None
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': {
                'id': share_link.id,
                'token': share_link.token,
                'permission': share_link.permission,
                'expire_at': share_link.expire_at.isoformat() if share_link.expire_at else None,
                'is_collaborative': share_link.is_collaborative,
                'room_id': share_link.room_id
            }
        }), 200
    except Exception as e:
        logger.error(f"更新分享链接接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/shares/<int:share_id>', methods=['DELETE'])
@jwt_required()
def delete_share(share_id):
    """删除分享链接"""
    try:
        user_id = get_jwt_identity()
        share_link = ShareLink.query.get(share_id)
        
        if not share_link:
            return jsonify({'code': 404, 'message': '分享链接不存在'}), 404
        
        has_permission = False
        if share_link.note_id:
            has_permission = Note.query.filter_by(id=share_link.note_id, user_id=user_id).first() is not None
        elif share_link.flowchart_id:
            has_permission = Flowchart.query.filter_by(id=share_link.flowchart_id, user_id=user_id).first() is not None
        elif share_link.mindmap_id:
            has_permission = Mindmap.query.filter_by(id=share_link.mindmap_id, user_id=user_id).first() is not None
        elif share_link.table_document_id:
            has_permission = TableDocument.query.filter_by(id=share_link.table_document_id, user_id=user_id).first() is not None
        elif share_link.whiteboard_id:
            has_permission = Whiteboard.query.filter_by(id=share_link.whiteboard_id, user_id=user_id).first() is not None
        elif share_link.knowledge_graph_id:
            has_permission = KnowledgeGraph.query.filter_by(id=share_link.knowledge_graph_id, user_id=user_id).first() is not None
        
        if not has_permission:
            return jsonify({'code': 403, 'message': '无权删除此分享链接'}), 403
        
        db.session.delete(share_link)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
    except Exception as e:
        logger.error(f"删除分享链接接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

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
            'totalKnowledgeGraphs': KnowledgeGraph.query.count(),
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
@jwt_required()
def get_shared_content(token):
    """获取分享内容（需要登录）"""
    try:
        user_id = get_jwt_identity()
        
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
        elif share_link.knowledge_graph_id:
            graph = KnowledgeGraph.query.get(share_link.knowledge_graph_id)
            if not graph:
                return jsonify({'code': 404, 'message': '分享的知识图谱不存在'}), 404
            response.update({
                'type': 'knowledge_graph',
                'knowledge_graph': graph.to_dict()
            })
        else:
            return jsonify({'code': 404, 'message': '分享链接无效'}), 404
        
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"获取分享内容接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500




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

# -------------------------- 回收站接口 --------------------------
@app.route('/api/trash', methods=['GET'])
@jwt_required()
def get_trash():
    """获取回收站列表"""
    try:
        user_id = get_jwt_identity()
        
        # 获取所有已删除的内容
        trash_items = []
        
        # 获取删除的笔记
        deleted_notes = Note.query.filter_by(user_id=user_id, is_deleted=True).order_by(Note.deleted_at.desc()).all()
        for note in deleted_notes:
            trash_items.append({
                'id': note.id,
                'title': note.title,
                'type': 'note',
                'deleted_at': note.deleted_at.isoformat() if note.deleted_at else None,
                'updated_at': note.updated_at.isoformat() if note.updated_at else None
            })
        
        # 获取删除的流程图
        deleted_flowcharts = Flowchart.query.filter_by(user_id=user_id, is_deleted=True).order_by(Flowchart.deleted_at.desc()).all()
        for flowchart in deleted_flowcharts:
            trash_items.append({
                'id': flowchart.id,
                'title': flowchart.title,
                'type': 'flowchart',
                'deleted_at': flowchart.deleted_at.isoformat() if flowchart.deleted_at else None,
                'updated_at': flowchart.updated_at.isoformat() if flowchart.updated_at else None
            })
        
        # 获取删除的表格
        deleted_tables = TableDocument.query.filter_by(user_id=user_id, is_deleted=True).order_by(TableDocument.deleted_at.desc()).all()
        for table in deleted_tables:
            trash_items.append({
                'id': table.id,
                'title': table.title,
                'type': 'table',
                'deleted_at': table.deleted_at.isoformat() if table.deleted_at else None,
                'updated_at': table.updated_at.isoformat() if table.updated_at else None
            })
        
        # 获取删除的白板
        deleted_whiteboards = Whiteboard.query.filter_by(user_id=user_id, is_deleted=True).order_by(Whiteboard.deleted_at.desc()).all()
        for whiteboard in deleted_whiteboards:
            trash_items.append({
                'id': whiteboard.id,
                'title': whiteboard.title,
                'type': 'whiteboard',
                'deleted_at': whiteboard.deleted_at.isoformat() if whiteboard.deleted_at else None,
                'updated_at': whiteboard.updated_at.isoformat() if whiteboard.updated_at else None
            })
        
        # 获取删除的脑图
        deleted_mindmaps = Mindmap.query.filter_by(user_id=user_id, is_deleted=True).order_by(Mindmap.deleted_at.desc()).all()
        for mindmap in deleted_mindmaps:
            trash_items.append({
                'id': mindmap.id,
                'title': mindmap.title,
                'type': 'mindmap',
                'deleted_at': mindmap.deleted_at.isoformat() if mindmap.deleted_at else None,
                'updated_at': mindmap.updated_at.isoformat() if mindmap.updated_at else None
            })
        
        # 按删除时间排序
        trash_items.sort(key=lambda x: x['deleted_at'], reverse=True)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': trash_items
        }), 200
    except Exception as e:
        logger.error(f"获取回收站列表接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/trash/restore', methods=['POST'])
@jwt_required()
def restore_trash():
    """恢复回收站中的项目"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        item_id = data.get('id')
        item_type = data.get('type')
        
        if not item_id or not item_type:
            return jsonify({'code': 400, 'message': '参数不能为空'}), 400
        
        # 根据类型恢复对应的项目
        restored = False
        
        if item_type == 'note':
            note = Note.query.filter_by(id=item_id, user_id=user_id, is_deleted=True).first()
            if note:
                note.is_deleted = False
                note.deleted_at = None
                restored = True
        elif item_type == 'flowchart':
            flowchart = Flowchart.query.filter_by(id=item_id, user_id=user_id, is_deleted=True).first()
            if flowchart:
                flowchart.is_deleted = False
                flowchart.deleted_at = None
                restored = True
        elif item_type == 'table':
            table = TableDocument.query.filter_by(id=item_id, user_id=user_id, is_deleted=True).first()
            if table:
                table.is_deleted = False
                table.deleted_at = None
                restored = True
        elif item_type == 'whiteboard':
            whiteboard = Whiteboard.query.filter_by(id=item_id, user_id=user_id, is_deleted=True).first()
            if whiteboard:
                whiteboard.is_deleted = False
                whiteboard.deleted_at = None
                restored = True
        elif item_type == 'mindmap':
            mindmap = Mindmap.query.filter_by(id=item_id, user_id=user_id, is_deleted=True).first()
            if mindmap:
                mindmap.is_deleted = False
                mindmap.deleted_at = None
                restored = True
        
        if not restored:
            return jsonify({'code': 404, 'message': '项目不存在或已被恢复'}), 404
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '恢复成功'
        }), 200
    except Exception as e:
        logger.error(f"恢复回收站项目接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/trash/delete', methods=['POST'])
@jwt_required()
def delete_trash_permanently():
    """永久删除回收站中的项目"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        item_id = data.get('id')
        item_type = data.get('type')
        
        if not item_id or not item_type:
            return jsonify({'code': 400, 'message': '参数不能为空'}), 400
        
        # 根据类型永久删除对应的项目
        deleted = False
        
        if item_type == 'note':
            note = Note.query.filter_by(id=item_id, user_id=user_id, is_deleted=True).first()
            if note:
                NoteVersion.query.filter_by(note_id=item_id).delete()
                ShareLink.query.filter_by(note_id=item_id).delete()
                db.session.delete(note)
                deleted = True
        elif item_type == 'flowchart':
            flowchart = Flowchart.query.filter_by(id=item_id, user_id=user_id, is_deleted=True).first()
            if flowchart:
                FlowchartVersion.query.filter_by(flowchart_id=item_id).delete()
                ShareLink.query.filter_by(flowchart_id=item_id).delete()
                db.session.delete(flowchart)
                deleted = True
        elif item_type == 'table':
            table = TableDocument.query.filter_by(id=item_id, user_id=user_id, is_deleted=True).first()
            if table:
                TableDocumentVersion.query.filter_by(table_document_id=item_id).delete()
                db.session.delete(table)
                deleted = True
        elif item_type == 'whiteboard':
            whiteboard = Whiteboard.query.filter_by(id=item_id, user_id=user_id, is_deleted=True).first()
            if whiteboard:
                WhiteboardVersion.query.filter_by(whiteboard_id=item_id).delete()
                ShareLink.query.filter_by(whiteboard_id=item_id).delete()
                db.session.delete(whiteboard)
                deleted = True
        elif item_type == 'mindmap':
            mindmap = Mindmap.query.filter_by(id=item_id, user_id=user_id, is_deleted=True).first()
            if mindmap:
                MindmapVersion.query.filter_by(mindmap_id=item_id).delete()
                ShareLink.query.filter_by(mindmap_id=item_id).delete()
                db.session.delete(mindmap)
                deleted = True
        
        if not deleted:
            return jsonify({'code': 404, 'message': '项目不存在'}), 404
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '永久删除成功'
        }), 200
    except Exception as e:
        logger.error(f"永久删除回收站项目接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/trash/clear', methods=['DELETE'])
@jwt_required()
def clear_trash():
    """清空回收站"""
    try:
        user_id = get_jwt_identity()
        
        # 删除所有已删除的笔记及其版本和分享链接
        deleted_notes = Note.query.filter_by(user_id=user_id, is_deleted=True).all()
        for note in deleted_notes:
            NoteVersion.query.filter_by(note_id=note.id).delete()
            ShareLink.query.filter_by(note_id=note.id).delete()
            db.session.delete(note)
        
        # 删除所有已删除的流程图及其版本和分享链接
        deleted_flowcharts = Flowchart.query.filter_by(user_id=user_id, is_deleted=True).all()
        for flowchart in deleted_flowcharts:
            FlowchartVersion.query.filter_by(flowchart_id=flowchart.id).delete()
            ShareLink.query.filter_by(flowchart_id=flowchart.id).delete()
            db.session.delete(flowchart)
        
        # 删除所有已删除的表格及其版本
        deleted_tables = TableDocument.query.filter_by(user_id=user_id, is_deleted=True).all()
        for table in deleted_tables:
            TableDocumentVersion.query.filter_by(table_document_id=table.id).delete()
            db.session.delete(table)
        
        # 删除所有已删除的白板及其版本和分享链接
        deleted_whiteboards = Whiteboard.query.filter_by(user_id=user_id, is_deleted=True).all()
        for whiteboard in deleted_whiteboards:
            WhiteboardVersion.query.filter_by(whiteboard_id=whiteboard.id).delete()
            ShareLink.query.filter_by(whiteboard_id=whiteboard.id).delete()
            db.session.delete(whiteboard)
        
        # 删除所有已删除的脑图及其版本和分享链接
        deleted_mindmaps = Mindmap.query.filter_by(user_id=user_id, is_deleted=True).all()
        for mindmap in deleted_mindmaps:
            MindmapVersion.query.filter_by(mindmap_id=mindmap.id).delete()
            ShareLink.query.filter_by(mindmap_id=mindmap.id).delete()
            db.session.delete(mindmap)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '清空回收站成功'
        }), 200
    except Exception as e:
        logger.error(f"清空回收站接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


# -------------------------- 知识图谱相关接口 --------------------------
@app.route('/api/knowledge-graphs', methods=['GET'])
@jwt_required()
def get_knowledge_graphs():
    """获取用户的知识图谱列表"""
    try:
        user_id = get_jwt_identity()
        
        search_query = request.args.get('search', '')
        
        query = KnowledgeGraph.query.filter_by(user_id=user_id)
        
        if search_query:
            query = query.filter(
                db.or_(
                    KnowledgeGraph.name.ilike(f'%{search_query}%'),
                    KnowledgeGraph.description.ilike(f'%{search_query}%')
                )
            )
        
        graphs = query.order_by(KnowledgeGraph.created_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [graph.to_dict() for graph in graphs]
        }), 200
    except Exception as e:
        logger.error(f"获取知识图谱列表接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/knowledge-graphs', methods=['POST'])
@jwt_required()
def create_knowledge_graph():
    """创建知识图谱"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        if not data or not data.get('name'):
            return jsonify({'code': 400, 'message': '图谱名称不能为空'}), 400
        
        existing_graph = KnowledgeGraph.query.filter_by(user_id=user_id, name=data.get('name')).first()
        if existing_graph:
            return jsonify({'code': 400, 'message': '图谱名称已存在'}), 400
        
        graph = KnowledgeGraph(
            name=data.get('name'),
            description=data.get('description'),
            user_id=user_id
        )
        
        db.session.add(graph)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': graph.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"创建知识图谱接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/knowledge-graphs/<int:graph_id>', methods=['GET'])
@jwt_required()
def get_knowledge_graph(graph_id):
    """获取知识图谱详情"""
    try:
        user_id = get_jwt_identity()
        graph = KnowledgeGraph.query.filter_by(id=graph_id, user_id=user_id).first()
        
        if not graph:
            return jsonify({'code': 404, 'message': '知识图谱不存在'}), 404
        
        nodes = [node.to_dict() for node in graph.nodes]
        relations = [relation.to_dict() for relation in graph.relations]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'graph': graph.to_dict(),
                'nodes': nodes,
                'relations': relations
            }
        }), 200
    except Exception as e:
        logger.error(f"获取知识图谱详情接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/knowledge-graphs/<int:graph_id>', methods=['PUT'])
@jwt_required()
def update_knowledge_graph(graph_id):
    """更新知识图谱"""
    try:
        user_id = get_jwt_identity()
        graph = KnowledgeGraph.query.filter_by(id=graph_id, user_id=user_id).first()
        
        if not graph:
            return jsonify({'code': 404, 'message': '知识图谱不存在'}), 404
        
        data = request.json
        if 'name' in data and data['name'] != graph.name:
            existing_graph = KnowledgeGraph.query.filter_by(user_id=user_id, name=data['name']).first()
            if existing_graph:
                return jsonify({'code': 400, 'message': '图谱名称已存在'}), 400
            graph.name = data['name']
        if 'description' in data:
            graph.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': graph.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"更新知识图谱接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/knowledge-graphs/<int:graph_id>', methods=['DELETE'])
@jwt_required()
def delete_knowledge_graph(graph_id):
    """删除知识图谱"""
    try:
        user_id = get_jwt_identity()
        graph = KnowledgeGraph.query.filter_by(id=graph_id, user_id=user_id).first()
        
        if not graph:
            return jsonify({'code': 404, 'message': '知识图谱不存在'}), 404
        
        db.session.delete(graph)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
    except Exception as e:
        logger.error(f"删除知识图谱接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/knowledge-graphs/<int:graph_id>/nodes', methods=['POST'])
@jwt_required()
def create_knowledge_node(graph_id):
    """在知识图谱中创建节点"""
    try:
        user_id = get_jwt_identity()
        graph = KnowledgeGraph.query.filter_by(id=graph_id, user_id=user_id).first()
        
        if not graph:
            return jsonify({'code': 404, 'message': '知识图谱不存在'}), 404
        
        data = request.json
        if not data or not data.get('name'):
            return jsonify({'code': 400, 'message': '节点名称不能为空'}), 400
        
        node = KnowledgeNode(
            type=data.get('type', 'concept'),
            name=data.get('name'),
            content=data.get('content'),
            properties=data.get('properties'),
            graph_id=graph_id
        )
        
        db.session.add(node)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': node.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"创建知识节点接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/knowledge-graphs/<int:graph_id>/nodes/<int:node_id>', methods=['PUT'])
@jwt_required()
def update_knowledge_node(graph_id, node_id):
    """更新知识节点"""
    try:
        user_id = get_jwt_identity()
        graph = KnowledgeGraph.query.filter_by(id=graph_id, user_id=user_id).first()
        
        if not graph:
            return jsonify({'code': 404, 'message': '知识图谱不存在'}), 404
        
        node = KnowledgeNode.query.filter_by(id=node_id, graph_id=graph_id).first()
        if not node:
            return jsonify({'code': 404, 'message': '节点不存在'}), 404
        
        data = request.json
        if 'type' in data:
            node.type = data['type']
        if 'name' in data:
            node.name = data['name']
        if 'content' in data:
            node.content = data['content']
        if 'properties' in data:
            node.properties = data['properties']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': node.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"更新知识节点接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/knowledge-graphs/<int:graph_id>/nodes/<int:node_id>', methods=['DELETE'])
@jwt_required()
def delete_knowledge_node(graph_id, node_id):
    """删除知识节点"""
    try:
        user_id = get_jwt_identity()
        graph = KnowledgeGraph.query.filter_by(id=graph_id, user_id=user_id).first()
        
        if not graph:
            return jsonify({'code': 404, 'message': '知识图谱不存在'}), 404
        
        node = KnowledgeNode.query.filter_by(id=node_id, graph_id=graph_id).first()
        if not node:
            return jsonify({'code': 404, 'message': '节点不存在'}), 404
        
        db.session.delete(node)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
    except Exception as e:
        logger.error(f"删除知识节点接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/knowledge-graphs/<int:graph_id>/relations', methods=['POST'])
@jwt_required()
def create_knowledge_relation(graph_id):
    """在知识图谱中创建关系"""
    try:
        user_id = get_jwt_identity()
        graph = KnowledgeGraph.query.filter_by(id=graph_id, user_id=user_id).first()
        
        if not graph:
            return jsonify({'code': 404, 'message': '知识图谱不存在'}), 404
        
        data = request.json
        if not data or not data.get('source_id') or not data.get('target_id'):
            return jsonify({'code': 400, 'message': '源节点和目标节点不能为空'}), 400
        
        source_node = KnowledgeNode.query.filter_by(id=data['source_id'], graph_id=graph_id).first()
        target_node = KnowledgeNode.query.filter_by(id=data['target_id'], graph_id=graph_id).first()
        
        if not source_node or not target_node:
            return jsonify({'code': 404, 'message': '源节点或目标节点不存在'}), 404
        
        relation = KnowledgeRelation(
            type=data.get('type', 'related'),
            label=data.get('label'),
            properties=data.get('properties'),
            graph_id=graph_id,
            source_id=data['source_id'],
            target_id=data['target_id']
        )
        
        db.session.add(relation)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': relation.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"创建知识关系接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/knowledge-graphs/<int:graph_id>/relations/<int:relation_id>', methods=['PUT'])
@jwt_required()
def update_knowledge_relation(graph_id, relation_id):
    """更新知识关系"""
    try:
        user_id = get_jwt_identity()
        graph = KnowledgeGraph.query.filter_by(id=graph_id, user_id=user_id).first()
        
        if not graph:
            return jsonify({'code': 404, 'message': '知识图谱不存在'}), 404
        
        relation = KnowledgeRelation.query.filter_by(id=relation_id, graph_id=graph_id).first()
        if not relation:
            return jsonify({'code': 404, 'message': '关系不存在'}), 404
        
        data = request.json
        if 'type' in data:
            relation.type = data['type']
        if 'label' in data:
            relation.label = data['label']
        if 'properties' in data:
            relation.properties = data['properties']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': relation.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"更新知识关系接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


@app.route('/api/knowledge-graphs/<int:graph_id>/relations/<int:relation_id>', methods=['DELETE'])
@jwt_required()
def delete_knowledge_relation(graph_id, relation_id):
    """删除知识关系"""
    try:
        user_id = get_jwt_identity()
        graph = KnowledgeGraph.query.filter_by(id=graph_id, user_id=user_id).first()
        
        if not graph:
            return jsonify({'code': 404, 'message': '知识图谱不存在'}), 404
        
        relation = KnowledgeRelation.query.filter_by(id=relation_id, graph_id=graph_id).first()
        if not relation:
            return jsonify({'code': 404, 'message': '关系不存在'}), 404
        
        db.session.delete(relation)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
    except Exception as e:
        logger.error(f"删除知识关系接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


# -------------------------- 语音转写 API --------------------------
# 延迟导入 Whisper，避免启动时加载模型
def load_whisper_model():
    try:
        import whisper
        return whisper.load_model('base')
    except ImportError:
        return None

whisper_model = None

@app.route('/api/transcribe', methods=['POST'])
@jwt_required()
def transcribe_audio():
    global whisper_model
    
    try:
        logger.info("========== 语音转写接口开始 ==========")
        
        # 检查请求文件
        logger.info("检查请求文件...")
        if 'audio' not in request.files:
            logger.error("请求中没有音频文件")
            return jsonify({'code': 400, 'message': '请上传音频文件'}), 400
        
        audio_file = request.files['audio']
        logger.info(f"音频文件: {audio_file.filename}")
        
        if audio_file.filename == '':
            logger.error("音频文件名为空")
            return jsonify({'code': 400, 'message': '请选择音频文件'}), 400
        
        # 检查文件大小
        file_size = len(audio_file.read())
        audio_file.seek(0)  # 重置文件指针
        logger.info(f"音频文件大小: {file_size} bytes")
        
        if file_size == 0:
            logger.error("音频文件为空")
            return jsonify({'code': 400, 'message': '音频文件为空'}), 400
        
        # 加载 Whisper 模型（首次调用时加载）
        if whisper_model is None:
            try:
                logger.info("开始加载 Whisper 模型...")
                import whisper
                logger.info("Whisper模块导入成功")
                logger.info("正在加载base模型...")
                whisper_model = whisper.load_model('base')
                logger.info("Whisper 模型加载成功")
            except ImportError as e:
                logger.error(f"Whisper 模块未安装: {str(e)}")
                return jsonify({
                    'code': 500,
                    'message': '未安装 Whisper 模块，请安装: pip install openai-whisper'
                }), 500
            except Exception as e:
                logger.error(f"Whisper 模型加载失败: {str(e)}", exc_info=True)
                return jsonify({
                    'code': 500,
                    'message': f'模型加载失败: {str(e)}'
                }), 500
        else:
            logger.info("Whisper 模型已加载，跳过加载步骤")
        
        # 保存临时音频文件
        import tempfile
        import os
        temp_path = None
        try:
            logger.info("正在保存临时音频文件...")
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
                audio_file.save(temp_file.name)
                temp_path = temp_file.name
            logger.info(f"临时文件保存成功: {temp_path}")
            logger.info(f"临时文件大小: {os.path.getsize(temp_path)} bytes")
        except Exception as e:
            logger.error(f"临时文件保存失败: {str(e)}", exc_info=True)
            return jsonify({
                'code': 500,
                'message': f'文件保存失败: {str(e)}'
            }), 500
        
        try:
            # 使用 Whisper 进行语音转写
            logger.info("开始语音转写...")
            result = whisper_model.transcribe(temp_path, language='zh')
            logger.info(f"转写完成，结果长度: {len(result.get('text', ''))}")
            
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.info("临时文件已清理")
            
            return jsonify({
                'code': 200,
                'data': {
                    'text': result['text'],
                    'segments': result.get('segments', [])
                }
            }), 200
        except Exception as transcribe_error:
            # 清理临时文件
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.info("转写失败，临时文件已清理")
            logger.error(f"语音转写失败: {str(transcribe_error)}", exc_info=True)
            return jsonify({
                'code': 500,
                'message': f'转写失败: {str(transcribe_error)}'
            }), 500
            
    except Exception as e:
        logger.error(f"语音转写接口异常: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'服务器内部错误: {str(e)}'}), 500


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
