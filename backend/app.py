from flask import Flask, request, jsonify, send_from_directory, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from flask_migrate import Migrate
import os
import logging
import uuid
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from openai import OpenAI

# 加载.env文件中的环境变量
from dotenv import load_dotenv
load_dotenv()

# 导入自定义模块
from config import get_config
from models import db, bcrypt, User, Note, NoteVersion, Category, Tag, Flowchart, FlowchartVersion, TableDocument, Whiteboard, Mindmap, ShareLink

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
        
        note = Note(
            title=data.get('title', '新笔记'),
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
        
        # 更新笔记字段
        note.title = data.get('title', note.title)
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
        data = request.json
        title = data.get('title', '新脑图')
        
        # 检查是否已存在同名脑图
        existing_mindmap = Mindmap.query.filter_by(user_id=user_id, title=title).first()
        if existing_mindmap:
            return jsonify({'code': 400, 'message': '已存在同名脑图，请使用其他名称'}), 400
        
        mindmap = Mindmap(
            title=title,
            data=data.get('data', {}),
            user_id=user_id
        )
        
        db.session.add(mindmap)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '创建成功',
            'data': mindmap.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"创建脑图接口异常: {str(e)}", exc_info=True)
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
        
        if resource_type == 'note':
            resource = Note.query.filter_by(id=resource_id, user_id=user_id).first()
        elif resource_type == 'flowchart':
            resource = Flowchart.query.filter_by(id=resource_id, user_id=user_id).first()
        elif resource_type == 'mindmap':
            resource = Mindmap.query.filter_by(id=resource_id, user_id=user_id).first()
        else:
            return jsonify({'code': 400, 'message': '不支持的资源类型'}), 400
        
        if not resource:
            return jsonify({'code': 404, 'message': '资源不存在或无权限'}), 404
        
        # 创建共享链接
        share_link = ShareLink(
            **{f'{resource_type}_id': resource_id},
            token=str(uuid.uuid4()),
            permission=data.get('permission', 'view'),
            expire_at=datetime.now() + timedelta(days=data.get('expire_days', 7))
        )
        
        db.session.add(share_link)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '创建成功',
            'data': {
                'token': share_link.token,
                'permission': share_link.permission,
                'expire_at': share_link.expire_at.isoformat()
            }
        }), 201
    except Exception as e:
        logger.error(f"创建共享链接接口异常: {str(e)}", exc_info=True)
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
        
        # 使用OpenAI SDK调用千帆v2 API
        qianfan_api_key = os.getenv('QIANFAN_API_KEY', '')
        qianfan_base_url = os.getenv('QIANFAN_BASE_URL', '')
        qianfan_model = os.getenv('QIANFAN_MODEL', 'deepseek-r1-distill-qwen-32b')
        
        logger.info(f"千帆API密钥配置: {qianfan_api_key[:10]}..." if qianfan_api_key else "未配置")
        logger.info(f"千帆API基础URL: {qianfan_base_url}")
        logger.info(f"千帆API模型: {qianfan_model}")
        
        if not qianfan_api_key or not qianfan_base_url:
            logger.error("千帆API配置不完整")
            return jsonify({
                'code': 500,
                'message': 'AI服务配置不完整',
                'data': {
                    'content': ''
                }
            }), 500
        
        logger.info("开始使用千帆v2 API")
        
        # 初始化OpenAI客户端（用于调用千帆API）
        logger.info("正在初始化OpenAI客户端...")
        client = OpenAI(
            api_key=qianfan_api_key,
            base_url=qianfan_base_url,
            timeout=60  # 增加超时时间到60秒，适应AI生成内容的长时间处理
        )
        logger.info("OpenAI客户端初始化成功")
        
        # 调用千帆API获取回复
        logger.info(f"准备发送千帆API请求: 模型={qianfan_model}, 消息数量={len(messages)}")
        
        # 记录完整的消息格式
        for i, msg in enumerate(messages):
            logger.info(f"消息{i+1}: role={msg.get('role')}, content={msg.get('content')[:50]}...")
        
        logger.info("正在发送千帆API请求...")
        logger.info(f"请求参数: model={qianfan_model}, messages={messages}, temperature=0.9, top_p=0.7, max_tokens=3000")
        
        # 调用API并处理异常
        try:
            response = client.chat.completions.create(
                model=qianfan_model,
                messages=messages,
                temperature=0.9,
                top_p=0.7,
                max_tokens=3000  # 增加max_tokens值，允许生成更长的内容
            )
            
            logger.info(f"千帆API请求发送成功")
            
            logger.info(f"千帆API响应类型: {type(response)}")
            logger.info(f"千帆API响应内容: {response}")
            
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
            logger.error(f"千帆API异常: {type(e).__name__}: {str(e)}", exc_info=True)
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

# -------------------------- 主函数 --------------------------
if __name__ == '__main__':
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 启动定时任务调度器
    scheduler = BackgroundScheduler()
    scheduler.add_job(clean_expired_share_links, 'interval', days=1)
    scheduler.start()
    
    # 启动应用
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
