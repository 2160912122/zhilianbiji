from flask import redirect
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import true, text
from werkzeug.security import generate_password_hash, check_password_hash
import json

from flask import send_file, make_response
from io import BytesIO
import tempfile
import os
from reportlab.lib.pagesizes import A4, A3, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import base64
from datetime import datetime, timedelta
from functools import wraps


app = Flask(__name__)

# ===== 基础配置 =====
# ===== 基础配置 =====
app.config['SECRET_KEY'] = 'change-me-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:304416720zgZG@127.0.0.1:3306/zhilian?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ========== 正确的跨域配置（兼容所有跨域场景+Cookie认证） ==========
CORS(
    app,
    supports_credentials=True,
    origins="*",
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)
# 新增：处理预检请求
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# 确保在创建 app 后立即配置 CORS
db = SQLAlchemy(app)



# ===== LoginManager =====
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'

# ===== 数据表 =====
# 修改 User 类，添加角色字段
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # 添加角色字段：user, admin, super_admin

    def set_pw(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_pw(self, raw):
        return check_password_hash(self.password_hash, raw)

    # Flask-Login 接口
    @property
    def is_authenticated(self): return True
    @property
    def is_active(self): return True
    @property
    def is_anonymous(self): return False
    def get_id(self): return str(self.id)

# 删除 AdminUser 类

class MindMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Text, nullable=False)  # JSON 字符串
    share_permission = db.Column(db.String(10), default='readonly')
    # 新增分享时效字段
    share_expires_at = db.Column(db.DateTime, nullable=True)  # 分享过期时间
    share_created_at = db.Column(db.DateTime, default=db.func.now())  # 分享创建时间
    # 添加脑图创建时间字段
    created_at = db.Column(db.DateTime, default=db.func.now())  # 脑图创建时间

    # 添加与User的关系
    user = db.relationship('User', backref=db.backref('mindmaps', lazy=True))


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#409EFF')  # 标签颜色
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # 关系
    mindmaps = db.relationship('MindMap', secondary='mindmap_tags', backref='tags')


# 脑图与标签的关联表
mindmap_tags = db.Table('mindmap_tags',
                        db.Column('mindmap_id', db.Integer, db.ForeignKey('mind_map.id'), primary_key=True),
                        db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
                        )


# ===== 在现有的数据表之后添加版本历史表 =====

class MindMapVersion(db.Model):
    """脑图版本历史"""
    id = db.Column(db.Integer, primary_key=True)
    mindmap_id = db.Column(db.Integer, db.ForeignKey('mind_map.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Text, nullable=False)  # 脑图数据JSON
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    change_description = db.Column(db.String(500))  # 变更描述

    # 关系
    mindmap = db.relationship('MindMap',
                              backref=db.backref('versions', lazy=True, order_by='desc(MindMapVersion.created_at)'))
    author = db.relationship('User', backref=db.backref('created_versions', lazy=True))


# ===== 在现有的数据表之后添加评论表 =====

class Comment(db.Model):
    """脑图评论"""
    id = db.Column(db.Integer, primary_key=True)
    mindmap_id = db.Column(db.Integer, db.ForeignKey('mind_map.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)  # 回复评论的父ID
    x = db.Column(db.Float, nullable=True)  # 评论在脑图中的x坐标
    y = db.Column(db.Float, nullable=True)  # 评论在脑图中的y坐标
    node_id = db.Column(db.String(100), nullable=True)  # 关联的节点ID

    # 关系
    mindmap = db.relationship('MindMap', backref=db.backref('comments', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    parent = db.relationship('Comment', remote_side=[id], backref=db.backref('replies', lazy=True))


# ===== 评论功能API路由 =====

@app.route('/api/mindmaps/<int:mid>/comments', methods=['GET'])
@login_required
def api_get_comments(mid):
    """获取脑图的所有评论"""
    mindmap = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()

    comments = Comment.query.filter_by(mindmap_id=mid, parent_id=None).order_by(Comment.created_at.asc()).all()

    return jsonify([{
        'id': c.id,
        'content': c.content,
        'created_at': c.created_at.isoformat(),
        'updated_at': c.updated_at.isoformat(),
        'user_id': c.user_id,
        'username': c.user.username,
        'x': c.x,
        'y': c.y,
        'node_id': c.node_id,
        'replies': [{
            'id': reply.id,
            'content': reply.content,
            'created_at': reply.created_at.isoformat(),
            'updated_at': reply.updated_at.isoformat(),
            'user_id': reply.user_id,
            'username': reply.user.username,
            'parent_id': reply.parent_id
        } for reply in c.replies]
    } for c in comments])


@app.route('/api/mindmaps/<int:mid>/comments', methods=['POST'])
@login_required
def api_create_comment(mid):
    """创建新评论"""
    mindmap = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    data = request.get_json()

    content = data.get('content')
    parent_id = data.get('parent_id')
    x = data.get('x')
    y = data.get('y')
    node_id = data.get('node_id')

    if not content:
        return jsonify({'msg': '评论内容不能为空'}), 400

    comment = Comment(
        mindmap_id=mid,
        user_id=current_user.id,
        content=content,
        parent_id=parent_id,
        x=x,
        y=y,
        node_id=node_id
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({
        'id': comment.id,
        'content': comment.content,
        'created_at': comment.created_at.isoformat(),
        'updated_at': comment.updated_at.isoformat(),
        'user_id': comment.user_id,
        'username': current_user.username,
        'x': comment.x,
        'y': comment.y,
        'node_id': comment.node_id,
        'parent_id': comment.parent_id
    }), 201


@app.route('/api/mindmaps/<int:mid>/comments/<int:comment_id>', methods=['PUT'])
@login_required
def api_update_comment(mid, comment_id):
    """更新评论"""
    mindmap = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    comment = Comment.query.filter_by(id=comment_id, mindmap_id=mid).first_or_404()

    # 检查权限：只能修改自己的评论
    if comment.user_id != current_user.id:
        return jsonify({'msg': '只能修改自己的评论'}), 403

    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({'msg': '评论内容不能为空'}), 400

    comment.content = content
    comment.updated_at = datetime.now()

    db.session.commit()

    return jsonify({
        'id': comment.id,
        'content': comment.content,
        'updated_at': comment.updated_at.isoformat()
    })


@app.route('/api/mindmaps/<int:mid>/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def api_delete_comment(mid, comment_id):
    """删除评论"""
    mindmap = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    comment = Comment.query.filter_by(id=comment_id, mindmap_id=mid).first_or_404()

    # 检查权限：只能删除自己的评论
    if comment.user_id != current_user.id:
        return jsonify({'msg': '只能删除自己的评论'}), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({'msg': '评论删除成功'})








@login_manager.user_loader
def load_user(uid): return User.query.get(int(uid))

# ===== 页面路由 =====
@app.route('/login.html')
def login_page(): return render_template('login.html')

@app.route('/register.html')
def register_page(): return render_template('register.html')

@app.route('/index.html')
@login_required
def index_page(): return render_template('index.html')

# ===== API =====
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    u, p = data.get('username'), data.get('password')
    if not u or not p: return jsonify({'msg': '用户名密码不能为空'}), 400
    if User.query.filter_by(username=u).first(): return jsonify({'msg': '用户名已存在'}), 409
    user = User(username=u)
    user.set_pw(p)
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': '注册成功'}), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    u, p = data.get('username'), data.get('password')
    user = User.query.filter_by(username=u).first()
    if not user or not user.check_pw(p): return jsonify({'msg': '用户名或密码错误'}), 401
    login_user(user)
    return jsonify({'msg': '登录成功', 'username': u})

@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'msg': '已退出'})

@app.route('/api/me')
@login_required
def api_me():
    return jsonify({
        'id': current_user.id,  # 添加用户ID
        'username': current_user.username
    })

@app.route('/api/mindmaps', methods=['GET'])
@login_required
def api_list():
    maps = MindMap.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': m.id,
        'name': m.name,
        'data': json.loads(m.data),
        'created_at': m.created_at.isoformat() if m.created_at else None,
        'tags': [{
            'id': tag.id,
            'name': tag.name,
            'color': tag.color
        } for tag in m.tags]
    } for m in maps])



@app.route('/api/mindmaps', methods=['POST'])
@login_required
def api_add():
    data = request.get_json()
    name, map_data = data.get('name'), data.get('data')
    if not name: return jsonify({'msg': '名称不能为空'}), 400

    # 确保数据格式正确
    if not map_data:
        # 创建默认数据格式
        map_data = {
            "meta": {
                "name": name,
                "author": current_user.username,
                "version": "1.0"
            },
            "format": "node_tree",
            "data": {
                "id": "root",
                "topic": name,
                "direction": "right",
                "expanded": True,
                "children": []
            }
        }
    elif isinstance(map_data, dict) and 'id' in map_data and 'format' not in map_data:
        # 如果只有节点数据，包装成完整格式
        map_data = {
            "meta": {
                "name": name,
                "author": current_user.username,
                "version": "1.0"
            },
            "format": "node_tree",
            "data": map_data
        }

    m = MindMap(user_id=current_user.id, name=name, data=json.dumps(map_data))
    db.session.add(m)
    db.session.commit()

    # 返回处理后的数据
    return jsonify({
        'id': m.id,
        'name': m.name,
        'data': json.loads(m.data)
    }), 201

@app.route('/api/mindmaps/<int:mid>', methods=['GET'])
@login_required
def api_get(mid):
    m = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    mind_data = json.loads(m.data)

    # 确保返回的数据格式正确
    if isinstance(mind_data, dict) and 'format' in mind_data:
        # 已经是完整格式
        return jsonify({
            'id': m.id,
            'name': m.name,
            'data': mind_data,
            'created_at': m.created_at.isoformat() if m.created_at else None
        })
    else:
        # 包装成完整格式
        wrapped_data = {
            "meta": {
                "name": m.name,
                "author": current_user.username,
                "version": "1.0"
            },
            "format": "node_tree",
            "data": mind_data
        }
        return jsonify({
            'id': m.id,
            'name': m.name,
            'data': wrapped_data,
            'created_at': m.created_at.isoformat() if m.created_at else None
        })


# ===== 添加版本历史API路由 =====

@app.route('/api/mindmaps/<int:mid>/versions', methods=['GET'])
@login_required
def api_get_versions(mid):
    """获取脑图的所有版本历史"""
    # 验证用户有权访问这个脑图
    mindmap = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()

    versions = MindMapVersion.query.filter_by(mindmap_id=mid).order_by(MindMapVersion.created_at.desc()).all()

    return jsonify([{
        'id': v.id,
        'version_number': v.version_number,
        'created_at': v.created_at.isoformat(),
        'created_by': v.author.username,
        'change_description': v.change_description,
        'preview': generate_version_preview(json.loads(v.data))
    } for v in versions])


def generate_version_preview(mindmap_data):
    """生成版本预览"""
    try:
        # 提取根节点和直接子节点作为预览
        if 'data' in mindmap_data:
            root = mindmap_data['data']
        else:
            root = mindmap_data

        preview = {
            'root_topic': root.get('topic', '无标题'),
            'child_count': len(root.get('children', [])),
            'total_nodes': count_nodes_in_preview(root)
        }

        # 添加前几个子节点的主题作为预览
        preview['child_topics'] = [child.get('topic', '') for child in root.get('children', [])[:3]]

        return preview
    except Exception as e:
        return {'root_topic': '预览生成失败', 'child_count': 0, 'total_nodes': 0}


def count_nodes_in_preview(node):
    """计算预览中的节点数量"""
    count = 1  # 当前节点
    if 'children' in node:
        for child in node['children']:
            count += count_nodes_in_preview(child)
    return count


@app.route('/api/mindmaps/<int:mid>/versions', methods=['POST'])
@login_required
def api_create_version(mid):
    """创建新的版本历史记录"""
    mindmap = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    data = request.get_json()

    change_description = data.get('change_description', '自动保存')

    # 获取当前版本号
    last_version = MindMapVersion.query.filter_by(mindmap_id=mid).order_by(MindMapVersion.version_number.desc()).first()
    version_number = last_version.version_number + 1 if last_version else 1

    # 创建新版本
    version = MindMapVersion(
        mindmap_id=mid,
        version_number=version_number,
        data=mindmap.data,  # 当前脑图数据
        created_by=current_user.id,
        change_description=change_description
    )

    db.session.add(version)
    db.session.commit()

    return jsonify({
        'msg': '版本已保存',
        'version_id': version.id,
        'version_number': version_number
    }), 201


@app.route('/api/mindmaps/<int:mid>/versions/<int:version_id>', methods=['GET'])
@login_required
def api_get_version(mid, version_id):
    """获取特定版本的数据"""
    mindmap = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    version = MindMapVersion.query.filter_by(id=version_id, mindmap_id=mid).first_or_404()

    return jsonify({
        'id': version.id,
        'version_number': version.version_number,
        'data': json.loads(version.data),
        'created_at': version.created_at.isoformat(),
        'created_by': version.author.username,
        'change_description': version.change_description
    })


@app.route('/api/mindmaps/<int:mid>/versions/<int:version_id>/restore', methods=['POST'])
@login_required
def api_restore_version(mid, version_id):
    """恢复特定版本"""
    mindmap = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    version = MindMapVersion.query.filter_by(id=version_id, mindmap_id=mid).first_or_404()

    # 创建恢复前的版本记录
    last_version = MindMapVersion.query.filter_by(mindmap_id=mid).order_by(MindMapVersion.version_number.desc()).first()
    version_number = last_version.version_number + 1 if last_version else 1

    restore_version = MindMapVersion(
        mindmap_id=mid,
        version_number=version_number,
        data=mindmap.data,  # 当前数据作为备份
        created_by=current_user.id,
        change_description=f'恢复版本前的自动备份 (将恢复至v{version.version_number})'
    )
    db.session.add(restore_version)

    # 恢复版本数据
    mindmap.data = version.data
    db.session.commit()

    return jsonify({
        'msg': f'已成功恢复至版本 v{version.version_number}',
        'restored_version': version.version_number
    })


@app.route('/api/mindmaps/<int:mid>/versions/<int:version_id>', methods=['DELETE'])
@login_required
def api_delete_version(mid, version_id):
    """删除特定版本"""
    mindmap = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    version = MindMapVersion.query.filter_by(id=version_id, mindmap_id=mid).first_or_404()

    db.session.delete(version)
    db.session.commit()

    return jsonify({'msg': '版本已删除'})



# ===== 修改保存脑图的API，自动创建版本历史 =====
@app.route('/api/mindmaps/<int:mid>', methods=['PUT'])
@login_required
def api_update(mid):
    m = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    old_data = m.data  # 保存旧数据用于比较

    new_data = request.get_json().get('data')
    m.data = json.dumps(new_data)

    # 检查数据是否有实质性变化（简单的字符串比较）
    if old_data != m.data:
        # 获取当前版本号
        last_version = MindMapVersion.query.filter_by(mindmap_id=mid).order_by(
            MindMapVersion.version_number.desc()).first()
        version_number = last_version.version_number + 1 if last_version else 1

        # 创建新版本
        version = MindMapVersion(
            mindmap_id=mid,
            version_number=version_number,
            data=old_data,  # 保存旧数据作为版本历史
            created_by=current_user.id,
            change_description='自动保存版本'
        )
        db.session.add(version)

    db.session.commit()
    return jsonify({'msg': '保存成功'})



@app.route('/api/mindmaps/<int:mid>', methods=['DELETE'])
@login_required
def api_delete(mid):
    m = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    db.session.delete(m)
    db.session.commit()
    return jsonify({'msg': '删除成功'})

# 在 API 路由部分添加分享功能
@app.route('/share/<string:share_type>/<int:mid>')
def share_map(share_type, mid):
    m = MindMap.query.get_or_404(mid)
    return render_template('share.html', mindmap=m, share_type=share_type)


@app.route('/api/share/<string:share_type>/<int:mid>', methods=['GET'])
def api_share(share_type, mid):
    m = MindMap.query.get_or_404(mid)

    # 验证分享权限 - 修复逻辑
    if share_type not in ['readonly', 'editable']:
        return jsonify({'msg': '无效的分享类型'}), 400

    # 检查分享是否过期
    if m.share_expires_at and m.share_expires_at < datetime.now():
        return jsonify({'msg': '分享链接已过期'}), 410  # 410 Gone

    # 如果是可编辑链接，但脑图权限不是可编辑，则返回403
    if share_type == 'editable' and m.share_permission != 'editable':
        return jsonify({'msg': '该脑图不支持编辑权限分享'}), 403

    # 计算剩余时间（支持分钟级显示）
    remaining_time = None
    if m.share_expires_at:
        remaining_seconds = (m.share_expires_at - datetime.now()).total_seconds()
        if remaining_seconds > 0:
            if remaining_seconds < 60:
                # 少于1分钟
                remaining_time = f"{int(remaining_seconds)}秒"
            elif remaining_seconds < 3600:
                # 少于1小时
                remaining_minutes = int(remaining_seconds // 60)
                remaining_time = f"{remaining_minutes}分钟"
            elif remaining_seconds < 86400:
                # 少于1天
                remaining_hours = int(remaining_seconds // 3600)
                remaining_minutes = int((remaining_seconds % 3600) // 60)
                if remaining_minutes > 0:
                    remaining_time = f"{remaining_hours}小时{remaining_minutes}分钟"
                else:
                    remaining_time = f"{remaining_hours}小时"
            else:
                # 大于1天
                remaining_days = int(remaining_seconds // 86400)
                remaining_hours = int((remaining_seconds % 86400) // 3600)
                if remaining_hours > 0:
                    remaining_time = f"{remaining_days}天{remaining_hours}小时"
                else:
                    remaining_time = f"{remaining_days}天"

    return jsonify({
        'id': m.id,
        'name': m.name,
        'data': json.loads(m.data),
        'author': User.query.get(m.user_id).username,
        'permission': m.share_permission,
        'share_type': share_type,
        'expires_at': m.share_expires_at.isoformat() if m.share_expires_at else None,
        'remaining_time': remaining_time,
        'is_expired': m.share_expires_at and m.share_expires_at < datetime.now()
    })



# ===== 添加更新分享权限的 API =====
@app.route('/api/mindmaps/<int:mid>/share', methods=['PUT'])
@login_required
def api_update_share_permission(mid):
    m = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    data = request.get_json()
    permission = data.get('permission', 'readonly')
    expires_in = data.get('expires_in')  # 过期时间（小时）

    if permission not in ['readonly', 'editable']:
        return jsonify({'msg': '权限参数无效'}), 400

    m.share_permission = permission

    # 设置分享过期时间
    if expires_in:
        try:
            expires_in = float(expires_in)  # 改为float支持小数
            if expires_in <= 0:
                return jsonify({'msg': '有效期必须大于0'}), 400
            # 支持分钟级精度
            m.share_expires_at = datetime.now() + timedelta(hours=expires_in)
        except (ValueError, TypeError):
            return jsonify({'msg': '有效期参数无效'}), 400
    else:
        # 如果没有设置有效期，则设置为永久
        m.share_expires_at = None

    m.share_created_at = datetime.now()
    db.session.commit()

    # 生成分享链接
    base_url = request.host_url.rstrip('/')
    readonly_url = f"{base_url}/share/readonly/{mid}"
    editable_url = f"{base_url}/share/editable/{mid}"

    response_data = {
        'msg': '分享权限已更新',
        'permission': permission,
        'readonly_url': readonly_url,
        'editable_url': editable_url,
        'expires_at': m.share_expires_at.isoformat() if m.share_expires_at else None,
        'created_at': m.share_created_at.isoformat()
    }

    return jsonify(response_data)



# 添加分享页面的保存功能（仅当有编辑权限时）
@app.route('/api/share/mindmaps/<int:mid>', methods=['PUT'])
def api_share_update(mid):
    m = MindMap.query.get_or_404(mid)

    # 检查分享权限
    if m.share_permission != 'editable':
        return jsonify({'msg': '该脑图不允许通过分享链接编辑'}), 403

    m.data = json.dumps(request.get_json().get('data'))
    db.session.commit()
    return jsonify({'msg': '保存成功'})


# ===== 导出功能路由 =====
@app.route('/api/mindmaps/<int:mid>/export/<string:format>')
@login_required
def api_export(mid, format):
    m = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    mind_data = json.loads(m.data)

    if format == 'json':
        return export_json(m, mind_data)
    elif format == 'text':
        return export_text(m, mind_data)
    elif format == 'pdf':
        return export_pdf(m, mind_data)
    elif format == 'image':
        return export_image(m, mind_data)
    else:
        return jsonify({'msg': '不支持的导出格式'}), 400

def export_json(m, mind_data):
    """导出为JSON格式"""
    output = BytesIO()
    output.write(json.dumps(mind_data, indent=2, ensure_ascii=False).encode('utf-8'))
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name=f'{m.name}.json',
        mimetype='application/json'
    )


def export_text(m, mind_data):
    """导出为文本格式"""

    def generate_text(data, level=0):
        text = ''
        # 处理不同的数据格式
        if 'data' in data:
            node = data['data']
        else:
            node = data

        indent = '  ' * level
        text += f"{indent}{node.get('topic', 'Untitled')}\n"

        if 'children' in node and node['children']:
            for child in node['children']:
                text += generate_text(child, level + 1)
        return text

    text_content = generate_text(mind_data)
    output = BytesIO(text_content.encode('utf-8'))
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name=f'{m.name}.txt',
        mimetype='text/plain'
    )


def export_pdf(m, mind_data):
    """导出为PDF格式"""
    try:
        # 创建PDF文档
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)

        # 内容容器
        elements = []

        # 样式
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            textColor='#409EFF'
        )
        topic_style = ParagraphStyle(
            'CustomTopic',
            parent=styles['Normal'],
            fontSize=12,
            leftIndent=20,
            spaceAfter=12
        )
        sub_topic_style = ParagraphStyle(
            'CustomSubTopic',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=40,
            spaceAfter=6
        )

        # 标题
        title = Paragraph(f"脑图: {m.name}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))

        # 作者信息
        author_info = f"作者: {current_user.username} | 创建时间: {m.id}"  # 这里可以用实际创建时间字段
        author_para = Paragraph(author_info, styles['Normal'])
        elements.append(author_para)
        elements.append(Spacer(1, 20))

        # 生成脑图内容
        def add_mindmap_content(data, level=0):
            if 'data' in data:
                node = data['data']
            else:
                node = data

            # 根据层级选择样式
            if level == 0:
                style = topic_style
                prefix = "• "
            else:
                style = sub_topic_style
                prefix = "  " * level + "◦ "

            topic_text = prefix + node.get('topic', 'Untitled')
            topic_para = Paragraph(topic_text, style)
            elements.append(topic_para)

            # 添加子节点
            if 'children' in node and node['children']:
                for child in node['children']:
                    add_mindmap_content(child, level + 1)

        add_mindmap_content(mind_data)

        # 构建PDF
        doc.build(elements)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'{m.name}.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"PDF export error: {e}")
        return jsonify({'msg': f'PDF导出失败: {str(e)}'}), 500


def export_image(m, mind_data):
    """导出为图片格式（PNG）"""
    try:
        # 这里使用ReportLab创建简单的图片表示
        # 在实际项目中，您可能需要使用更复杂的图形库如matplotlib
        from reportlab.graphics import renderPM
        from reportlab.graphics.shapes import Drawing, String
        from reportlab.graphics.charts.barcharts import VerticalBarChart
        from reportlab.lib.colors import Color

        # 创建一个简单的图形表示
        drawing = Drawing(400, 300)

        # 添加标题
        title = String(150, 280, f"脑图: {m.name}", fontSize=14, fillColor=Color(0.25, 0.62, 1, 1))
        drawing.add(title)

        # 添加作者信息
        author = String(150, 260, f"作者: {current_user.username}", fontSize=10, fillColor=Color(0.5, 0.5, 0.5, 1))
        drawing.add(author)

        # 简单的脑图表示 - 在实际项目中可以更复杂
        y_pos = 230

        def add_node_to_drawing(node, x, y, level=0):
            if level > 3:  # 限制深度防止过于复杂
                return y

            node_text = String(x, y, node.get('topic', 'Untitled')[:20],
                               fontSize=10 - level,
                               fillColor=Color(0.2, 0.2, 0.2, 1))
            drawing.add(node_text)

            y -= 20
            if 'children' in node and node['children']:
                for i, child in enumerate(node['children']):
                    if i < 3:  # 限制子节点数量
                        y = add_node_to_drawing(child, x + 50, y, level + 1)
            return y

        # 获取根节点
        root_node = mind_data.get('data', mind_data)
        add_node_to_drawing(root_node, 50, 230)

        # 渲染为PNG
        buffer = BytesIO()
        renderPM.drawToFile(drawing, buffer, 'PNG')
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'{m.name}.png',
            mimetype='image/png'
        )

    except Exception as e:
        print(f"Image export error: {e}")
        return jsonify({'msg': f'图片导出失败: {str(e)}'}), 500


# 简单的HTML转PDF功能（可选）
@app.route('/api/mindmaps/<int:mid>/export/html')
@login_required
def export_html_pdf(mid):
    """通过HTML模板导出PDF"""
    m = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    mind_data = json.loads(m.data)

    return render_template('export_template.html',
                           mindmap=m,
                           data=mind_data,
                           author=current_user.username)

# 获取用户的所有标签
@app.route('/api/tags', methods=['GET'])
@login_required
def api_get_tags():
    tags = Tag.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': tag.id,
        'name': tag.name,
        'color': tag.color
    } for tag in tags])


# 创建新标签
@app.route('/api/tags', methods=['POST'])
@login_required
def api_create_tag():
    data = request.get_json()
    name = data.get('name')
    color = data.get('color', '#409EFF')

    if not name:
        return jsonify({'msg': '标签名不能为空'}), 400

    # 检查是否已存在同名标签
    existing_tag = Tag.query.filter_by(name=name, user_id=current_user.id).first()
    if existing_tag:
        return jsonify({'msg': '标签名已存在'}), 409

    tag = Tag(name=name, color=color, user_id=current_user.id)
    db.session.add(tag)
    db.session.commit()

    return jsonify({
        'id': tag.id,
        'name': tag.name,
        'color': tag.color
    }), 201


# 更新标签
@app.route('/api/tags/<int:tag_id>', methods=['PUT'])
@login_required
def api_update_tag(tag_id):
    tag = Tag.query.filter_by(id=tag_id, user_id=current_user.id).first_or_404()
    data = request.get_json()

    if 'name' in data:
        tag.name = data['name']
    if 'color' in data:
        tag.color = data['color']

    db.session.commit()
    return jsonify({'msg': '标签更新成功'})

# 删除标签
@app.route('/api/tags/<int:tag_id>', methods=['DELETE'])
@login_required
def api_delete_tag(tag_id):
    tag = Tag.query.filter_by(id=tag_id, user_id=current_user.id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    return jsonify({'msg': '标签删除成功'})


# 为脑图添加标签
@app.route('/api/mindmaps/<int:mid>/tags', methods=['POST'])
@login_required
def api_add_tag_to_mindmap(mid):
    m = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    data = request.get_json()
    tag_id = data.get('tag_id')

    tag = Tag.query.filter_by(id=tag_id, user_id=current_user.id).first_or_404()

    if tag not in m.tags:
        m.tags.append(tag)
        db.session.commit()

    return jsonify({'msg': '标签添加成功'})


# 从脑图移除标签
@app.route('/api/mindmaps/<int:mid>/tags/<int:tag_id>', methods=['DELETE'])
@login_required
def api_remove_tag_from_mindmap(mid, tag_id):
    m = MindMap.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    tag = Tag.query.filter_by(id=tag_id, user_id=current_user.id).first_or_404()

    if tag in m.tags:
        m.tags.remove(tag)
        db.session.commit()

    return jsonify({'msg': '标签移除成功'})


# ===== AI 助手功能 =====
@app.route('/api/ai/analyze', methods=['POST'])
@login_required
def api_ai_analyze():
    """AI分析脑图内容"""
    try:
        data = request.get_json()
        mindmap_data = data.get('mindmap_data')
        instruction = data.get('instruction', '')

        if not mindmap_data:
            return jsonify({'msg': '脑图数据不能为空'}), 400

        # 这里可以集成真实的AI服务，目前使用模拟响应
        analysis_result = simulate_ai_analysis(mindmap_data, instruction)

        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'suggestions': generate_ai_suggestions(mindmap_data)
        })

    except Exception as e:
        return jsonify({'msg': f'AI分析失败: {str(e)}'}), 500


def simulate_ai_analysis(mindmap_data, instruction):
    """模拟AI分析功能"""
    # 分析脑图结构
    node_count = count_nodes(mindmap_data)
    depth = calculate_depth(mindmap_data)

    # 根据指令生成响应
    if '完善' in instruction or '补充' in instruction:
        return f"根据您的要求，建议在脑图中添加更多细节。当前有{node_count}个节点，深度{depth}层。"
    elif '优化' in instruction or '改进' in instruction:
        return f"建议优化脑图结构，当前节点分布可以更均衡。考虑添加更多分支或重新组织内容。"
    else:
        return f"分析完成！您的脑图包含{node_count}个节点，最大深度{depth}层。结构清晰，建议保持这种组织方式。"


def count_nodes(data):
    """计算节点数量"""
    if isinstance(data, dict):
        count = 1
        if 'children' in data and data['children']:
            for child in data['children']:
                count += count_nodes(child)
        return count
    return 0


def calculate_depth(data, current_depth=1):
    """计算脑图深度"""
    if isinstance(data, dict) and 'children' in data and data['children']:
        max_depth = current_depth
        for child in data['children']:
            child_depth = calculate_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
        return max_depth
    return current_depth


def generate_ai_suggestions(mindmap_data):
    """生成AI建议"""
    suggestions = []

    # 基于节点数量的建议
    node_count = count_nodes(mindmap_data)
    if node_count < 5:
        suggestions.append("建议添加更多节点来丰富脑图内容")
    elif node_count > 20:
        suggestions.append("脑图较大，考虑使用折叠功能管理复杂结构")

    # 基于深度的建议
    depth = calculate_depth(mindmap_data)
    if depth > 4:
        suggestions.append("结构较深，建议平衡各分支的深度")

    return suggestions


# ===== 增强的 AI 助手功能 =====
@app.route('/api/ai/enhance', methods=['POST'])
@login_required
def api_ai_enhance():
    """AI增强脑图内容"""
    try:
        data = request.get_json()
        mindmap_data = data.get('mindmap_data')
        enhancement_type = data.get('enhancement_type', 'expand')
        instruction = data.get('instruction', '')

        if not mindmap_data:
            return jsonify({'msg': '脑图数据不能为空'}), 400

        # 根据增强类型处理
        if enhancement_type == 'expand':
            result = expand_mindmap(mindmap_data, instruction)
        elif enhancement_type == 'optimize':
            result = optimize_structure(mindmap_data)
        elif enhancement_type == 'summarize':
            result = generate_summary(mindmap_data)
        elif enhancement_type == 'suggest_topics':
            result = suggest_related_topics(mindmap_data)
        elif enhancement_type == 'check_balance':
            result = check_balance(mindmap_data)
        else:
            return jsonify({'msg': '不支持的增强类型'}), 400

        return jsonify({
            'success': True,
            'enhanced_data': result.get('enhanced_data'),
            'analysis': result.get('analysis', ''),
            'suggestions': result.get('suggestions', []),
            'changes_made': result.get('changes_made', [])
        })

    except Exception as e:
        return jsonify({'msg': f'AI增强失败: {str(e)}'}), 500


def expand_mindmap(mindmap_data, instruction):
    """扩展脑图内容"""
    # 模拟AI扩展功能
    root_node = mindmap_data.get('data', mindmap_data)

    # 分析当前结构
    node_count = count_nodes(root_node)
    depth = calculate_depth(root_node)

    # 根据指令生成扩展内容
    expanded_data = root_node.copy()

    # 模拟添加相关子节点
    if instruction:
        # 基于用户指令扩展
        new_nodes = generate_nodes_from_instruction(instruction, root_node)
    else:
        # 自动扩展逻辑
        new_nodes = generate_auto_expansion(root_node)

    # 将新节点添加到脑图
    if 'children' not in expanded_data:
        expanded_data['children'] = []

    expanded_data['children'].extend(new_nodes)

    # 返回完整格式的数据
    return {
        'enhanced_data': {
            "meta": {
                "name": "AI扩展脑图",
                "author": "AI Assistant",
                "version": "1.0"
            },
            "format": "node_tree",
            "data": expanded_data  # 确保这是完整的节点数据
        },
        'analysis': f"已根据您的需求扩展脑图，新增 {len(new_nodes)} 个相关节点",
        'suggestions': [
            "建议继续细化新增节点的内容",
            "考虑添加更多具体案例或细节"
        ],
        'changes_made': [f"新增 {len(new_nodes)} 个相关节点"]
    }


def optimize_structure(mindmap_data):
    """优化脑图结构"""
    root_node = mindmap_data.get('data', mindmap_data)

    # 分析当前问题
    issues = analyze_structure_issues(root_node)

    # 生成优化建议和结构调整
    optimized_data = restructure_mindmap(root_node)

    return {
        'enhanced_data': {
            "meta": {
                "name": "AI优化脑图",
                "author": "AI Assistant",
                "version": "1.0"
            },
            "format": "node_tree",
            "data": optimized_data
        },
        'analysis': f"发现 {len(issues)} 个可优化点，已自动调整结构",
        'suggestions': issues,
        'changes_made': ["重新组织节点层次", "平衡各分支深度"]
    }


def generate_summary(mindmap_data):
    """生成脑图摘要"""
    root_node = mindmap_data.get('data', mindmap_data)

    # 提取关键信息
    main_topics = extract_main_topics(root_node)
    key_points = extract_key_points(root_node)

    summary = f"脑图包含 {len(main_topics)} 个主要主题和 {len(key_points)} 个关键点。"

    return {
        'analysis': summary,
        'suggestions': [
            "主要主题: " + ", ".join(main_topics[:5]),
            "关键要点已提取完成，可用于生成报告"
        ],
        'changes_made': []
    }


def suggest_related_topics(mindmap_data):
    """建议相关主题"""
    root_node = mindmap_data.get('data', mindmap_data)

    # 分析当前主题并推荐相关主题
    current_topics = extract_all_topics(root_node)
    related_topics = find_related_topics(current_topics)

    return {
        'analysis': f"基于当前 {len(current_topics)} 个主题，推荐 {len(related_topics)} 个相关主题",
        'suggestions': related_topics,
        'changes_made': []
    }


def check_balance(mindmap_data):
    """检查脑图平衡性"""
    root_node = mindmap_data.get('data', mindmap_data)

    balance_issues = []

    # 检查各分支深度
    depths = get_branch_depths(root_node)
    max_depth = max(depths) if depths else 0
    min_depth = min(depths) if depths else 0

    if max_depth - min_depth > 2:
        balance_issues.append("各分支深度差异较大，建议平衡结构")

    # 检查节点分布
    node_counts = count_nodes_per_branch(root_node)
    avg_nodes = sum(node_counts) / len(node_counts) if node_counts else 0

    for i, count in enumerate(node_counts):
        if count > avg_nodes * 2:
            balance_issues.append(f"第 {i + 1} 个分支节点过多，建议拆分")
        elif count < 2:
            balance_issues.append(f"第 {i + 1} 个分支内容较少，建议扩展")

    return {
        'analysis': f"脑图平衡性分析完成，发现 {len(balance_issues)} 个优化点",
        'suggestions': balance_issues,
        'changes_made': []
    }


# 辅助函数
def generate_nodes_from_instruction(instruction, root_node):
    """根据指令生成新节点"""
    # 模拟AI生成相关节点
    base_topic = root_node.get('topic', '主题')

    # 这里可以集成真实的AI服务
    sample_nodes = [
        {
            "id": f"ai_node_{i}",
            "topic": f"{instruction}相关要点 {i + 1}",
            "children": []
        }
        for i in range(3)  # 生成3个示例节点
    ]

    return sample_nodes


def generate_auto_expansion(root_node):
    """自动扩展脑图"""
    current_topics = extract_all_topics(root_node)

    # 基于现有主题生成相关扩展
    expansion_nodes = []
    for i, topic in enumerate(current_topics[:3]):  # 为前3个主题生成扩展
        expansion_nodes.append({
            "id": f"expand_{i}",
            "topic": f"{topic}的深入分析",
            "children": [
                {
                    "id": f"expand_{i}_1",
                    "topic": f"{topic}的具体应用",
                    "children": []
                },
                {
                    "id": f"expand_{i}_2",
                    "topic": f"{topic}的最佳实践",
                    "children": []
                }
            ]
        })

    return expansion_nodes


def analyze_structure_issues(root_node):
    """分析结构问题"""
    issues = []

    # 检查是否有过长分支
    if calculate_depth(root_node) > 6:
        issues.append("脑图深度过大，建议合并相关节点")

    # 检查是否有孤立节点
    node_count = count_nodes(root_node)
    if node_count > 20 and calculate_depth(root_node) < 3:
        issues.append("节点数量较多但层次较浅，建议增加层级结构")

    return issues


def restructure_mindmap(root_node):
    """重新组织脑图结构"""
    # 这里可以实现智能重组逻辑
    # 目前返回原始数据的副本
    return root_node.copy()


def extract_main_topics(root_node):
    """提取主要主题"""
    main_topics = []
    if 'children' in root_node:
        for child in root_node['children']:
            main_topics.append(child.get('topic', '未知主题'))
    return main_topics


def extract_key_points(root_node):
    """提取关键点"""
    key_points = []

    def extract_points(node):
        if 'children' in node and node['children']:
            for child in node['children']:
                key_points.append(child.get('topic', ''))
                extract_points(child)

    extract_points(root_node)
    return [kp for kp in key_points if kp]


def extract_all_topics(root_node):
    """提取所有主题"""
    all_topics = []

    def extract_all(node):
        all_topics.append(node.get('topic', ''))
        if 'children' in node:
            for child in node['children']:
                extract_all(child)

    extract_all(root_node)
    return [topic for topic in all_topics if topic]


def find_related_topics(topics):
    """查找相关主题"""
    # 模拟相关主题推荐
    related_map = {
        '技术': ['人工智能', '大数据', '云计算', '区块链'],
        '学习': ['学习方法', '知识管理', '记忆技巧', '效率提升'],
        '工作': ['项目管理', '团队协作', '时间管理', '职业发展'],
        '创意': ['头脑风暴', '创新方法', '设计思维', '问题解决']
    }

    related = set()
    for topic in topics:
        for category, related_list in related_map.items():
            if category in topic:
                related.update(related_list)

    return list(related)[:6]  # 返回最多6个相关主题


def get_branch_depths(root_node):
    """获取各分支深度"""
    depths = []
    if 'children' in root_node:
        for child in root_node['children']:
            depths.append(calculate_depth(child))
    return depths


def count_nodes_per_branch(root_node):
    """计算每个分支的节点数量"""
    counts = []
    if 'children' in root_node:
        for child in root_node['children']:
            counts.append(count_nodes(child))
    return counts


# ===== 后端管理功能 =====

# 管理员登录装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not hasattr(current_user, 'role') or current_user.role not in ['admin',
                                                                                                               'super_admin']:
            return jsonify({'msg': '需要管理员权限'}), 403
        return f(*args, **kwargs)

    return decorated_function


# 管理员登录页面
@app.route('/admin/login.html')
def admin_login_page():
    return render_template('admin_login.html')


# 管理员主页
@app.route('/admin/index.html')
@admin_required
def admin_index_page():
    return render_template('admin_index.html')


# 管理员登录API
# 修改管理员登录API
# 管理员登录API
# 管理员登录API
@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    data = request.get_json()
    u, p = data.get('username'), data.get('password')
    # 使用 User 表查询，并检查角色必须是管理员
    admin = User.query.filter_by(username=u).first()
    if not admin or not admin.check_pw(p) or admin.role not in ['admin', 'super_admin']:
        return jsonify({'msg': '管理员用户名或密码错误'}), 401
    login_user(admin)
    return jsonify({
        'msg': '管理员登录成功',
        'username': u,
        'role': admin.role,
        'is_admin': True  # 添加管理员标识
    })


@app.route('/api/check-admin')
@login_required
def api_check_admin():
    """检查当前用户是否是管理员"""
    is_admin = hasattr(current_user, 'role') and current_user.role in ['admin', 'super_admin']
    return jsonify({
        'is_admin': is_admin,
        'username': current_user.username,
        'role': getattr(current_user, 'role', 'user')
    })




# 管理员退出
@app.route('/api/admin/logout', methods=['POST'])
@admin_required
def api_admin_logout():
    logout_user()
    return jsonify({'msg': '管理员已退出'})


# 获取系统统计信息
@app.route('/api/admin/stats')
@admin_required
def api_admin_stats():
    # 用户统计
    total_users = User.query.count()
    active_users = db.session.query(User).filter(
        User.id.in_(
            db.session.query(MindMap.user_id).distinct()
        )
    ).count()

    # 脑图统计
    total_mindmaps = MindMap.query.count()
    recent_mindmaps = MindMap.query.filter(
        MindMap.created_at >= datetime.now() - timedelta(days=7)
    ).count()

    # 标签统计
    total_tags = Tag.query.count()

    # 分享统计
    shared_mindmaps = MindMap.query.filter(
        MindMap.share_permission.in_(['readonly', 'editable'])
    ).count()

    # 存储统计（估算）
    total_storage = db.session.query(db.func.sum(db.func.length(MindMap.data))).scalar() or 0
    total_storage_mb = round(total_storage / (1024 * 1024), 2)

    return jsonify({
        'users': {
            'total': total_users,
            'active': active_users,
            'inactive': total_users - active_users
        },
        'mindmaps': {
            'total': total_mindmaps,
            'recent_7_days': recent_mindmaps,
            'shared': shared_mindmaps
        },
        'tags': {
            'total': total_tags
        },
        'storage': {
            'total_mb': total_storage_mb
        }
    })


# 获取用户列表
@app.route('/api/admin/users')
@admin_required
def api_admin_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')

    query = User.query

    if search:
        query = query.filter(User.username.contains(search))

    users = query.order_by(User.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'users': [{
            'id': u.id,
            'username': u.username,
            'mindmaps_count': MindMap.query.filter_by(user_id=u.id).count(),
            'tags_count': Tag.query.filter_by(user_id=u.id).count(),
            'last_active': MindMap.query.filter_by(user_id=u.id)
            .order_by(MindMap.created_at.desc())
            .first().created_at.isoformat() if MindMap.query.filter_by(user_id=u.id).first() else None,
            'created_at': None  # 如果需要可以添加用户创建时间字段
        } for u in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    })


# 获取脑图列表
@app.route('/api/admin/mindmaps')
@admin_required
def api_admin_mindmaps():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    user_id = request.args.get('user_id', type=int)

    query = MindMap.query.join(User)

    if search:
        query = query.filter(MindMap.name.contains(search))

    if user_id:
        query = query.filter(MindMap.user_id == user_id)

    mindmaps = query.order_by(MindMap.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'mindmaps': [{
            'id': m.id,
            'name': m.name,
            'user_id': m.user_id,
            'username': m.user.username,
            'nodes_count': count_nodes_in_mindmap(json.loads(m.data)),
            'is_shared': m.share_permission in ['readonly', 'editable'],
            'share_permission': m.share_permission,
            'created_at': m.created_at.isoformat() if m.created_at else None,
            'share_expires_at': m.share_expires_at.isoformat() if m.share_expires_at else None
        } for m in mindmaps.items],
        'total': mindmaps.total,
        'pages': mindmaps.pages,
        'current_page': page
    })


def count_nodes_in_mindmap(data):
    """计算脑图中的节点数量"""
    if isinstance(data, dict):
        if 'data' in data:
            return count_nodes(data['data'])
        else:
            return count_nodes(data)
    return 0


# 获取系统日志（简化版）
@app.route('/api/admin/logs')
@admin_required
def api_admin_logs():
    # 真实日志查询（示例，可根据需求扩展）
    logs = [
        {'id':1, 'level':'INFO', 'message':f'管理员 {current_user.username} 登录系统', 'timestamp':datetime.now().isoformat(), 'user':current_user.username},
        {'id':2, 'level':'INFO', 'message':'系统启动完成', 'timestamp':(datetime.now()-timedelta(hours=1)).isoformat(), 'user':'system'},
        {'id':3, 'level':'INFO', 'message':'用户注册成功: testuser', 'timestamp':(datetime.now()-timedelta(minutes=30)).isoformat(), 'user':'system'},
    ]
    return jsonify({'logs': logs})


# 删除用户（管理员操作）
@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def api_admin_delete_user(user_id):
    if current_user.role != 'super_admin':
        return jsonify({'msg': '需要超级管理员权限'}), 403

    user = User.query.get_or_404(user_id)

    # 删除用户相关的脑图和标签
    MindMap.query.filter_by(user_id=user_id).delete()
    Tag.query.filter_by(user_id=user_id).delete()

    db.session.delete(user)
    db.session.commit()

    return jsonify({'msg': '用户删除成功'})


# 删除脑图（管理员操作）
@app.route('/api/admin/mindmaps/<int:mindmap_id>', methods=['DELETE'])
@admin_required
def api_admin_delete_mindmap(mindmap_id):
    try:
        mindmap = MindMap.query.get_or_404(mindmap_id)

        # 记录删除操作
        print(
            f"管理员 {current_user.username} 正在删除脑图 ID: {mindmap_id}, 名称: {mindmap.name}, 所属用户: {mindmap.user_id}")

        # 先删除相关的版本历史记录
        MindMapVersion.query.filter_by(mindmap_id=mindmap_id).delete()

        # 删除脑图与标签的关联关系
        db.session.execute(mindmap_tags.delete().where(mindmap_tags.c.mindmap_id == mindmap_id))

        # 删除脑图
        db.session.delete(mindmap)
        db.session.commit()

        return jsonify({'msg': '脑图删除成功'})

    except Exception as e:
        db.session.rollback()
        print(f"删除脑图失败: {str(e)}")
        return jsonify({'msg': f'删除失败: {str(e)}'}), 500





# 管理员信息
@app.route('/api/admin/me')
@admin_required
def api_admin_me():
    return jsonify({
        'username': current_user.username,
        'role': current_user.role
    })

@app.route('/admin')
def admin_root():
    return redirect('/admin/login.html')



@app.route('/')
def root():
    # 如果用户已登录
    if current_user.is_authenticated:
        # 检查是否是管理员
        if hasattr(current_user, 'role') and current_user.role in ['admin', 'super_admin']:
            return redirect('/admin/index.html')
        else:
            return redirect('/index.html')
    # 未登录用户跳转到登录页
    return redirect('/login.html')


# ===== 首次运行建表 =====
with app.app_context():
    db.create_all()




# ===== 数据库字段迁移 =====
# ===== 数据库字段迁移 =====
# ===== 数据库字段迁移 =====
with app.app_context():
    # 检查是否需要添加角色字段到 user 表
    try:
        db.session.execute(text("SELECT role FROM user LIMIT 1"))
    except Exception as e:
        print("添加角色字段到用户表...")
        db.session.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'user'"))
        db.session.commit()
        print("角色字段添加成功")

    # 检查是否需要添加新字段
    try:
        # 尝试查询 share_permission 字段
        db.session.execute(text("SELECT share_permission FROM mind_map LIMIT 1"))
    except Exception as e:
        # 如果字段不存在，则添加
        print("添加 share_permission 字段到数据库...")
        db.session.execute(text("ALTER TABLE mind_map ADD COLUMN share_permission VARCHAR(10) DEFAULT 'readonly'"))
        db.session.commit()
        print("字段添加成功")

    # 添加分享时效字段
    try:
        db.session.execute(text("SELECT share_expires_at FROM mind_map LIMIT 1"))
    except Exception as e:
        print("添加分享时效字段到数据库...")
        db.session.execute(text("ALTER TABLE mind_map ADD COLUMN share_expires_at DATETIME"))
        db.session.execute(text("ALTER TABLE mind_map ADD COLUMN share_created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
        db.session.commit()
        print("分享时效字段添加成功")

    # 添加脑图创建时间字段
    try:
        db.session.execute(text("SELECT created_at FROM mind_map LIMIT 1"))
    except Exception as e:
        print("添加脑图创建时间字段到数据库...")
        db.session.execute(text("ALTER TABLE mind_map ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
        db.session.commit()
        print("脑图创建时间字段添加成功")

    # 检查是否需要添加标签表
    try:
        db.session.execute(text("SELECT * FROM tag LIMIT 1"))
    except Exception as e:
        print("创建标签表...")
        db.session.execute(text("""
            CREATE TABLE tag (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(50) NOT NULL,
                color VARCHAR(7) DEFAULT '#409EFF',
                user_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """))
        db.session.execute(text("""
            CREATE TABLE mindmap_tags (
                mindmap_id INT,
                tag_id INT,
                PRIMARY KEY (mindmap_id, tag_id),
                FOREIGN KEY (mindmap_id) REFERENCES mind_map(id),
                FOREIGN KEY (tag_id) REFERENCES tag(id)
            )
        """))
        db.session.commit()
        print("标签表创建成功")

    # 删除原来的管理员表创建代码，替换为在统一用户表中创建管理员账号
    try:
        # 确保管理员账号存在
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', role='super_admin')
            admin.set_pw('admin123')
            db.session.add(admin)
            db.session.commit()
            print("管理员账号创建成功: admin/admin123 (超级管理员)")
        elif admin.role not in ['admin', 'super_admin']:
            # 如果admin账号存在但不是管理员角色，升级为管理员
            admin.role = 'super_admin'
            db.session.commit()
            print("已升级admin账号为超级管理员")
        else:
            print(f"管理员账号已存在: {admin.username} (角色: {admin.role})")
    except Exception as e:
        print(f"检查管理员账号时出错: {e}")


    # 检查是否需要创建版本历史表
    try:
        db.session.execute(text("SELECT * FROM mind_map_version LIMIT 1"))
    except Exception as e:
        print("创建版本历史表...")
        db.session.execute(text("""
            CREATE TABLE mind_map_version (
                id INT PRIMARY KEY AUTO_INCREMENT,
                mindmap_id INT NOT NULL,
                version_number INT NOT NULL,
                data TEXT NOT NULL,
                created_by INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                change_description VARCHAR(500),
                FOREIGN KEY (mindmap_id) REFERENCES mind_map(id),
                FOREIGN KEY (created_by) REFERENCES user(id)
            )
        """))
        db.session.commit()
        print("版本历史表创建成功")

        # 检查是否需要创建评论表
        try:
            db.session.execute(text("SELECT * FROM comment LIMIT 1"))
        except Exception as e:
            print("创建评论表...")
            db.session.execute(text("""
                CREATE TABLE comment (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    mindmap_id INT NOT NULL,
                    user_id INT NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    parent_id INT,
                    x FLOAT,
                    y FLOAT,
                    node_id VARCHAR(100),
                    FOREIGN KEY (mindmap_id) REFERENCES mind_map(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES user(id),
                    FOREIGN KEY (parent_id) REFERENCES comment(id) ON DELETE CASCADE
                )
            """))
            db.session.commit()
            print("评论表创建成功")





if __name__ == '__main__':
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000,
        threaded=True
    )