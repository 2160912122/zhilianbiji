# -*- coding: utf-8 -*-
import io
import os
import random
import string
import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps

import markdown
import pdfkit
from dotenv import load_dotenv
from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, send_file, session, url_for)
from flask_apscheduler import APScheduler
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import PasswordField, StringField, SubmitField, validators
from wtforms.validators import DataRequired, Length
from zhipuai import ZhipuAI

scheduler = APScheduler()
app = Flask(__name__)
load_dotenv()
CORS(app, supports_credentials=True)  # 必须开启 CORS
login_manager = LoginManager(app)
# 初始化智谱客户端（全局一次即可）


# -------------------- 配置 --------------------
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:123456@localhost:3306/notes_db?charset=utf8mb4"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB
app.config["SECRET_KEY"] = "your-secret-key-here"  # 重要：生产环境请使用强密钥

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "请先登录以访问此页面"


# 修复：兼容旧版 SQLAlchemy 的用户加载器
@login_manager.user_loader
def load_user(user_id):
    # 兼容 SQLAlchemy 1.x 和 2.x
    try:
        # 尝试使用新的 session.get() 方法
        return db.session.get(User, int(user_id))
    except AttributeError:
        # 回退到旧的 query.get() 方法
        return User.query.get(int(user_id))


# 新增：智谱AI调用函数
def call_zhipu(prompt, system_message=""):
    """调用智谱大模型API"""
    try:
        api_key = os.getenv("ZHIPUAI_API_KEY")
        model = os.getenv("ZHIPUAI_MODEL", "glm-4")

        if not api_key:
            print("错误：未设置ZHIPUAI_API_KEY环境变量")
            return None

        client = ZhipuAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2048,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"智谱AI调用失败：{str(e)}")
        return None


# 修改原有AI接口：用call_zhipu替代之前的调用函数
# 1. AI生成笔记接口
@app.route("/api/ai/generate_note", methods=["POST"])
@login_required
def ai_generate_note():
    data = request.json
    topic = data.get("topic", "")
    if not topic:
        return jsonify({"error": "请输入笔记主题"}), 400

    prompt = f"请围绕「{topic}」生成一篇详细笔记，结构清晰（分点或分段），内容详实，适合保存为个人笔记。"
    system_msg = "你是专业的笔记生成助手，生成内容需逻辑连贯、重点突出，避免冗余。"

    content = call_zhipu(prompt, system_msg)
    if not content:
        return jsonify({"error": "AI生成失败，请重试"}), 500

    return jsonify(
        {"content": content, "suggested_title": topic if topic else "AI生成的笔记"}
    )


# 2. AI总结笔记接口
@app.route("/api/ai/summarize", methods=["POST"])
@login_required
def ai_summarize():
    data = request.json
    content = data.get("content", "")
    if not content:
        return jsonify({"error": "请提供需要总结的笔记内容"}), 400

    prompt = (
        f"请总结以下笔记内容（不超过300字，提炼核心观点，分点说明更佳）：\n\n{content}"
    )
    system_msg = "你是专业的内容总结专家，总结需简洁、准确，覆盖笔记关键信息。"

    summary = call_zhipu(prompt, system_msg)
    return jsonify({"summary": summary or "未生成有效总结，请重试"})


# 3. AI推荐标签接口
@app.route("/api/ai/suggest_tags", methods=["POST"])
@login_required
def ai_suggest_tags():
    data = request.json
    content = data.get("content", "")
    if not content:
        return jsonify({"error": "请提供笔记内容"}), 400

    # 限制内容长度，避免API调用过长
    content_preview = content[:500]  # 只取前500字符

    prompt = f"""请为以下笔记内容推荐3-5个相关标签，要求：
    1. 标签简洁明了，1-4个汉字
    2. 覆盖内容的核心主题
    3. 用中文逗号分隔，不要编号和解释

    笔记内容：
    {content_preview}

    推荐标签："""

    system_msg = (
        "你是专业的标签推荐助手，只返回用中文逗号分隔的标签，不要任何其他文字。"
    )

    tags_str = call_zhipu(prompt, system_msg)

    # 更健壮的标签解析
    if tags_str:
        # 清理响应：移除可能的引导词和标点
        tags_str = tags_str.replace("推荐标签：", "").replace("标签：", "")
        tags_str = tags_str.strip("。.，, ")

        # 分割标签
        tags = []
        for tag in tags_str.split(","):
            tag = tag.strip()
            if tag and len(tag) <= 4:  # 限制标签长度
                tags.append(tag)

        # 去重并限制数量
        tags = list(dict.fromkeys(tags))[:5]
    else:
        tags = []

    # 如果没有生成标签，提供默认标签
    if not tags:
        tags = ["学习", "笔记", "知识"]

    return jsonify({"tags": tags})


# -------------------- 表单类（移除邮箱） --------------------
class RegistrationForm(FlaskForm):
    username = StringField(
        "用户名",
        [
            validators.DataRequired(message="用户名不能为空"),
            validators.Length(min=3, max=50, message="用户名长度必须在3-50个字符之间"),
        ],
    )
    password = PasswordField(
        "密码",
        [
            validators.DataRequired(message="密码不能为空"),
            validators.Length(min=6, message="密码长度至少6个字符"),
        ],
    )
    submit = SubmitField("注册")


class LoginForm(FlaskForm):
    username = StringField(
        "用户名", [validators.DataRequired(message="用户名不能为空")]
    )
    password = PasswordField("密码", [validators.DataRequired(message="密码不能为空")])
    submit = SubmitField("登录")


# -------------------- 数据模型（移除邮箱字段） --------------------
class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_admin = db.Column(db.Boolean, default=False)  # 新增：管理员标志

    # 关联用户的笔记
    notes = db.relationship("Note", backref="author", lazy=True, passive_deletes=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Category(db.Model):
    """分类模型：与笔记一对多"""

    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    notes = db.relationship("Note", backref="category", lazy=True, passive_deletes=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
        }


class Tag(db.Model):
    """标签模型：与笔记多对多"""

    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    notes = db.relationship(
        "Note", secondary="note_tag", back_populates="tags", passive_deletes=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
        }


# 版本历史模型
class NoteVersion(db.Model):
    __tablename__ = "note_version"
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(
        db.Integer, db.ForeignKey("note.id", ondelete="CASCADE"), nullable=False
    )
    content = db.Column(db.Text, nullable=False)
    updater_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    # 关联
    note = db.relationship("Note", backref="versions")
    updater = db.relationship("User", backref="version_updates")


# 笔记-标签关联表（多对多）
note_tag = db.Table(
    "note_tag",
    db.Column(
        "note_id",
        db.Integer,
        db.ForeignKey("note.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tag.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Note(db.Model):
    __tablename__ = "note"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(20), nullable=False)  # 'richtext' / 'markdown'
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_public = db.Column(db.Boolean, default=False)  # 是否公开

    # 关联用户
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    # 关联分类
    category_id = db.Column(
        db.Integer, db.ForeignKey("category.id", ondelete="SET NULL"), nullable=True
    )

    # 关联标签
    tags = db.relationship(
        "Tag", secondary="note_tag", back_populates="notes", lazy="dynamic"
    )

    def to_dict(self):
        """列表页用：只返回关键信息"""
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "tag_ids": [tag.id for tag in self.tags],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "content": self.content,  # 添加内容字段以支持搜索功能
        }

    def to_full_dict(self):
        """详情页用：返回完整信息"""
        d = self.to_dict()
        d["content"] = self.content
        d["category"] = self.category.to_dict() if self.category else None
        d["tags"] = [tag.to_dict() for tag in self.tags.all()]
        return d

    def save_version(self, updater_id):
        """保存当前内容为历史版本"""
        version = NoteVersion(
            note_id=self.id, content=self.content or "", updater_id=updater_id
        )
        db.session.add(version)
        return version


class ShareLink(db.Model):
    """分享链接表"""

    __tablename__ = "share_link"
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(
        db.Integer, db.ForeignKey("note.id", ondelete="CASCADE"), nullable=False
    )
    token = db.Column(db.String(36), unique=True, nullable=False)
    permission = db.Column(db.String(10), nullable=False)  # 'view' / 'edit'
    created_at = db.Column(db.DateTime, default=datetime.now)
    expire_at = db.Column(db.DateTime)
    note = db.relationship("Note", backref="share_links")


# -------------------- Flask-Login 配置 --------------------
@login_manager.user_loader
def load_user(user_id):
    # 旧代码：return User.query.get(int(user_id))
    # 新代码（适配SQLAlchemy 2.0+）：
    from sqlalchemy.orm import Session

    with db.session.begin_nested():
        return db.session.get(User, int(user_id))


# -------------------- 工具函数 --------------------
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def generate_token():
    return str(uuid.uuid4())


def get_share_by_token(token):
    link = ShareLink.query.filter_by(token=token).first()
    if not link:
        abort(404, description="分享链接不存在")

    # 检查是否过期 - 使用UTC时间进行比较
    is_expired = False
    if link.expire_at and link.expire_at < datetime.now(timezone.utc).replace(
        tzinfo=None
    ):
        is_expired = True

    return link, is_expired


app.add_template_filter(markdown.markdown, name="markdown")


def init_scheduler(app):
    scheduler.init_app(app)

    @scheduler.task("cron", hour=0)
    def clean_expired_links():
        with app.app_context():
            expired_links = ShareLink.query.filter(
                ShareLink.expire_at < datetime.now()
            ).all()
            for link in expired_links:
                db.session.delete(link)
            db.session.commit()

    scheduler.start()


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403, description="请先登录")
        if not current_user.is_admin:
            abort(403, description="需要管理员权限")
        return f(*args, **kwargs)

    return decorated_function


# -------------------- 认证路由 --------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=form.username.data).first()

        if existing_user:
            flash("用户名已存在", "error")
            return render_template("register.html", form=form)

        # 创建新用户
        user = User(username=form.username.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash("注册成功！请登录", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            flash(f"欢迎回来，{user.username}!", "success")
            return redirect(next_page or url_for("index"))
        else:
            flash("用户名或密码错误", "error")

    return render_template("login.html", form=form)


# 版本历史页面
@app.route("/notes/<int:note_id>/versions")
@login_required
def note_versions(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    versions = (
        NoteVersion.query.filter_by(note_id=note_id)
        .order_by(NoteVersion.updated_at.desc())
        .all()
    )
    return render_template("version_history.html", note=note, versions=versions)


# 获取版本列表API
@app.route("/api/notes/<int:note_id>/versions")
@login_required
def get_note_versions(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    versions = (
        NoteVersion.query.filter_by(note_id=note_id)
        .order_by(NoteVersion.updated_at.desc())
        .all()
    )

    return jsonify(
        [
            {
                "id": version.id,
                "content": version.content,
                "updater": {"username": version.updater.username},
                "updated_at": version.updated_at.isoformat(),
                "content_preview": (
                    version.content[:150] + "..."
                    if len(version.content) > 150
                    else version.content
                ),
            }
            for version in versions
        ]
    )


# 版本回滚API
@app.route(
    "/api/notes/<int:note_id>/versions/<int:version_id>/rollback", methods=["POST"]
)
@login_required
def rollback_note_version(note_id, version_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    version = NoteVersion.query.filter_by(id=version_id, note_id=note_id).first_or_404()

    # 先保存当前内容为历史版本
    note.save_version(current_user.id)

    # 回滚到指定版本
    note.content = version.content
    db.session.commit()

    return jsonify({"message": "回滚成功"})


# 预览版本内容API
@app.route("/api/notes/<int:note_id>/versions/<int:version_id>")
@login_required
def get_note_version(note_id, version_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    version = NoteVersion.query.filter_by(id=version_id, note_id=note_id).first_or_404()

    return jsonify(
        {
            "id": version.id,
            "content": version.content,
            "updater": {"username": version.updater.username},
            "updated_at": version.updated_at.isoformat(),
        }
    )


# ---------- 管理员 API ----------
@app.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    return render_template("admin.html")


@app.route("/api/admin/stats")
@login_required
@admin_required
def get_admin_stats():
    """获取系统统计信息（普通用户也可访问，但只返回基本信息）"""
    if current_user.is_admin:
        # 管理员看到完整统计
        total_users = User.query.count()
        total_notes = Note.query.count()
        total_categories = Category.query.count()
        total_tags = Tag.query.count()
        total_shares = ShareLink.query.count()

        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_users = User.query.filter(User.created_at >= seven_days_ago).count()

        return jsonify(
            {
                "total_users": total_users,
                "total_notes": total_notes,
                "total_categories": total_categories,
                "total_tags": total_tags,
                "total_shares": total_shares,
                "recent_users": recent_users,
                "is_admin": True,
            }
        )
    else:
        # 普通用户只看到自己的统计
        user_notes = Note.query.filter_by(user_id=current_user.id).count()
        user_categories = Category.query.filter_by(user_id=current_user.id).count()
        user_tags = Tag.query.filter_by(user_id=current_user.id).count()

        return jsonify(
            {
                "user_notes": user_notes,
                "user_categories": user_categories,
                "user_tags": user_tags,
                "is_admin": False,
            }
        )


@app.route("/api/admin/users")
@login_required
@admin_required
def get_all_users():
    """获取所有用户列表"""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify(
        [
            {
                "id": user.id,
                "username": user.username,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat(),
                "note_count": Note.query.filter_by(user_id=user.id).count(),
            }
            for user in users
        ]
    )


@app.route("/api/admin/users/<int:user_id>", methods=["DELETE"])
@login_required
@admin_required
def delete_user(user_id):
    """删除用户（管理员操作）"""
    if user_id == current_user.id:
        return jsonify({"error": "不能删除自己的账户"}), 400

    user = User.query.get_or_404(user_id)

    # 删除用户的所有数据
    Note.query.filter_by(user_id=user_id).delete()
    Category.query.filter_by(user_id=user_id).delete()
    Tag.query.filter_by(user_id=user_id).delete()
    ShareLink.query.filter(ShareLink.note.has(user_id=user_id)).delete()

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "用户已删除"})


@app.route("/api/admin/users/<int:user_id>/toggle_admin", methods=["POST"])
@login_required
@admin_required
def toggle_user_admin(user_id):
    """切换用户的管理员状态"""
    if user_id == current_user.id:
        return jsonify({"error": "不能修改自己的管理员状态"}), 400

    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()

    return jsonify(
        {
            "message": f'用户管理员状态已{"启用" if user.is_admin else "禁用"}',
            "is_admin": user.is_admin,
        }
    )


@app.route("/api/admin/notes")
@login_required
@admin_required
def get_all_notes():
    """获取所有笔记列表"""
    notes = Note.query.order_by(Note.updated_at.desc()).limit(100).all()
    return jsonify(
        [
            {
                "id": note.id,
                "title": note.title,
                "type": note.type,
                "user_id": note.user_id,
                "username": note.author.username,
                "created_at": note.created_at.isoformat(),
                "updated_at": note.updated_at.isoformat(),
                "content_preview": (
                    note.content[:100] + "..."
                    if note.content and len(note.content) > 100
                    else note.content
                ),
            }
            for note in notes
        ]
    )


@app.route("/api/admin/notes/<int:note_id>", methods=["DELETE"])
@login_required
@admin_required
def admin_delete_note(note_id):
    """管理员删除笔记"""
    note = Note.query.get_or_404(note_id)
    ShareLink.query.filter_by(note_id=note_id).delete()
    db.session.delete(note)
    db.session.commit()

    return jsonify({"message": "笔记已删除"})


@app.route("/api/admin/cleanup", methods=["POST"])
@login_required
@admin_required
def cleanup_system():
    """系统清理：删除过期分享链接"""
    expired_count = ShareLink.query.filter(
        ShareLink.expire_at < datetime.now()
    ).delete()
    db.session.commit()

    return jsonify(
        {
            "message": f"已清理 {expired_count} 个过期分享链接",
            "cleaned_count": expired_count,
        }
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("您已成功退出登录", "success")
    return redirect(url_for("login"))


# -------------------- 受保护的路由 --------------------
@app.route("/")
@login_required
def index():
    return render_template("index.html")


# ---------- 分类 API ----------
@app.route("/api/categories", methods=["GET"])
@login_required
def get_categories():
    categories = (
        Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    )
    return jsonify([c.to_dict() for c in categories])


@app.route("/api/categories", methods=["POST"])
@login_required
def create_category():
    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "分类名称为必填项"}), 400

    name = data["name"].strip()
    # 检查当前用户是否已有同名分类
    if Category.query.filter_by(name=name, user_id=current_user.id).first():
        return jsonify({"error": "该分类已存在"}), 400

    category = Category(name=name, user_id=current_user.id)
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201


@app.route("/api/categories/<int:category_id>", methods=["DELETE"])
@login_required
def delete_category(category_id):
    category = Category.query.filter_by(
        id=category_id, user_id=current_user.id
    ).first_or_404()
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "分类已删除"}), 200


# 退出登录接口（需要登录才能访问，用 login_required 装饰）
@app.route("/api/logout", methods=["POST"])
@login_required  # 确保只有已登录用户才能调用
def api_logout():
    logout_user()  # 销毁当前用户的会话（Flask-Login 内置方法）
    return jsonify({"message": "退出登录成功"}), 200


# ---------- 标签 API ----------
@app.route("/api/tags", methods=["GET"])
@login_required
def get_tags():
    tags = Tag.query.filter_by(user_id=current_user.id).order_by(Tag.name).all()
    return jsonify([t.to_dict() for t in tags])


@app.route("/api/tags", methods=["POST"])
@login_required
def create_tag():
    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "标签名称为必填项"}), 400

    name = data["name"].strip()
    # 检查当前用户是否已有同名标签
    if Tag.query.filter_by(name=name, user_id=current_user.id).first():
        return jsonify({"error": "该标签已存在"}), 400

    tag = Tag(name=name, user_id=current_user.id)
    db.session.add(tag)
    db.session.commit()
    return jsonify(tag.to_dict()), 201


@app.route("/api/tags/<int:tag_id>", methods=["DELETE"])
@login_required
def delete_tag(tag_id):
    tag = Tag.query.filter_by(id=tag_id, user_id=current_user.id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    return jsonify({"message": "标签已删除"}), 200


# ---------- 笔记 API ----------
@app.route("/api/notes", methods=["GET"])
@login_required
def get_notes():
    notes = (
        Note.query.filter_by(user_id=current_user.id)
        .order_by(Note.updated_at.desc())
        .all()
    )
    return jsonify([n.to_dict() for n in notes])


@app.route("/api/notes/<int:note_id>", methods=["GET"])
@login_required
def get_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    return jsonify(note.to_full_dict())


@app.route("/api/notes", methods=["POST"])
@login_required
def create_note():
    data = request.json
    if not data or not data.get("type"):
        return jsonify({"error": "类型为必填项"}), 400

    base_title = data.get("title", "").strip() or "无标题笔记"
    title = base_title
    counter = 1
    while Note.query.filter_by(title=title, user_id=current_user.id).first():
        title = f"{base_title}({counter})"
        counter += 1

    new_note = Note(
        title=title,
        content=data.get("content", ""),
        type=data["type"],
        category_id=data.get("category_id"),
        user_id=current_user.id,
        is_public=data.get("is_public", False),
    )
    db.session.add(new_note)
    db.session.flush()

    # 处理标签
    tag_ids = data.get("tag_ids", [])
    tags = []
    if tag_ids:
        # 过滤掉临时ID（以'temp-'开头的ID）
        real_tag_ids = [
            id
            for id in tag_ids
            if not isinstance(id, str) or not id.startswith("temp-")
        ]
        if real_tag_ids:
            tags.extend(
                Tag.query.filter(
                    Tag.id.in_(real_tag_ids), Tag.user_id == current_user.id
                ).all()
            )

    # 处理标签名称（用于新标签）
    tag_names = data.get("tags", [])
    if tag_names:
        for tag_name in tag_names:
            # 检查标签是否已存在
            existing_tag = Tag.query.filter_by(
                name=tag_name, user_id=current_user.id
            ).first()
            if existing_tag:
                if existing_tag not in tags:
                    tags.append(existing_tag)
            else:
                # 创建新标签
                new_tag = Tag(name=tag_name, user_id=current_user.id)
                db.session.add(new_tag)
                db.session.flush()
                tags.append(new_tag)

    new_note.tags = tags

    # 保存初始版本
    new_note.save_version(current_user.id)

    db.session.commit()
    return jsonify(new_note.to_dict()), 201


@app.route("/api/notes/<int:note_id>", methods=["PUT"])
@login_required
def update_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()

    token = request.headers.get("X-Share-Token")
    if token:
        link = ShareLink.query.filter_by(token=token, note_id=note_id).first()
        if not link or link.permission != "edit":
            return jsonify({"error": "没有编辑权限"}), 403

    data = request.json
    if not data or not data.get("type"):
        return jsonify({"error": "类型为必填项"}), 400

    # 检查内容是否有变化，有变化则保存版本
    old_content = note.content
    new_content = data.get("content", "")

    if old_content != new_content:
        # 保存历史版本
        note.save_version(current_user.id)

    # 处理标题，支持空标题
    base_title = data.get("title", "").strip() or "无标题笔记"
    title = base_title
    counter = 1
    while (
        Note.query.filter_by(title=title, user_id=current_user.id).first()
        and title != note.title
    ):
        title = f"{base_title}({counter})"
        counter += 1

    note.title = title
    note.content = new_content
    note.type = data["type"]
    note.category_id = data.get("category_id")
    note.is_public = data.get("is_public", False)

    # 处理标签ID
    tags = []
    tag_ids = data.get("tag_ids", [])
    if tag_ids:
        # 过滤掉临时标签ID（前端生成的临时ID）并转换为整数
        real_tag_ids = []
        for id in tag_ids:
            if isinstance(id, str):
                if not id.startswith("temp-"):
                    try:
                        real_tag_ids.append(int(id))
                    except ValueError:
                        pass
            elif isinstance(id, int):
                real_tag_ids.append(id)
        if real_tag_ids:
            tags.extend(
                Tag.query.filter(
                    Tag.id.in_(real_tag_ids), Tag.user_id == current_user.id
                ).all()
            )

    # 处理标签名称（用于新标签）
    tag_names = data.get("tags", [])
    if tag_names:
        for tag_name in tag_names:
            # 检查标签是否已存在
            existing_tag = Tag.query.filter_by(
                name=tag_name, user_id=current_user.id
            ).first()
            if existing_tag:
                if existing_tag not in tags:
                    tags.append(existing_tag)
            else:
                # 创建新标签
                new_tag = Tag(name=tag_name, user_id=current_user.id)
                db.session.add(new_tag)
                db.session.flush()
                tags.append(new_tag)

    note.tags = tags

    db.session.commit()
    return jsonify(note.to_dict())


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
@login_required
def delete_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    ShareLink.query.filter_by(note_id=note_id).delete()
    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "笔记已删除"}), 200


# ---------- 文件上传 ----------
@app.route("/api/upload", methods=["POST"])
@login_required
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "未找到文件"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "未选择文件"}), 400
    if file and allowed_file(file.filename):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = "".join(random.choices(string.ascii_letters + string.digits, k=6))
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"{timestamp}_{random_str}.{ext}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        return jsonify({"url": f"/static/uploads/{filename}"}), 200
    return jsonify({"error": "不支持的文件类型"}), 400


# ---------- 分享 ----------
@app.route("/api/share", methods=["POST"])
@login_required
def create_share():
    data = request.json
    note_id = data.get("note_id")
    permission = data.get("permission", "view")
    expires_at_str = data.get("expire_at")

    if permission not in ("view", "edit"):
        return jsonify({"error": "无效的权限类型"}), 400

    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    token = generate_token()

    # 处理有效期 - 正确处理时区
    expire_at = None
    if expires_at_str:
        try:
            # 直接解析 ISO 格式字符串
            expire_at = datetime.fromisoformat(expires_at_str)
            # 转换为 UTC 时间存储并移除时区信息
            expire_at = expire_at.astimezone(timezone.utc).replace(tzinfo=None)
        except ValueError as e:
            print(f"有效期解析错误: {e}, 输入: {expires_at_str}")
            return jsonify({"error": "无效的有效期格式"}), 400

    link = ShareLink(
        note_id=note.id, token=token, permission=permission, expire_at=expire_at
    )
    db.session.add(link)
    db.session.commit()
    share_url = url_for("share_page", token=token, _external=True)

    return jsonify(
        {
            "share_url": share_url,
            "permission": permission,
            "expire_at": (
                expire_at.replace(tzinfo=timezone.utc).isoformat()
                if expire_at
                else None
            ),
        }
    )


@app.route("/api/notes/<int:note_id>/shares", methods=["GET"])
@login_required
def get_shares(note_id):
    """获取笔记的所有分享链接"""
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    shares = ShareLink.query.filter_by(note_id=note.id).all()

    result = []
    for share in shares:
        result.append(
            {
                "token": share.token,
                "share_url": url_for("share_page", token=share.token, _external=True),
                "permission": share.permission,
                "created_at": share.created_at.replace(tzinfo=timezone.utc).isoformat(),
                "expire_at": (
                    share.expire_at.replace(tzinfo=timezone.utc).isoformat()
                    if share.expire_at
                    else None
                ),
            }
        )

    return jsonify(result)


@app.route("/api/shares/<token>", methods=["DELETE"])
@login_required
def delete_share(token):
    """删除分享链接"""
    share = ShareLink.query.filter_by(token=token).first_or_404()
    note = Note.query.filter_by(
        id=share.note_id, user_id=current_user.id
    ).first_or_404()

    db.session.delete(share)
    db.session.commit()

    return jsonify({"message": "分享链接已删除"})


# 新增：前后端分离专用的 JSON 注册接口（/api/register）
@app.route("/api/register", methods=["POST"])
def api_register():
    # 1. 接收前端 Vue 发送的 JSON 数据
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        # 返回 JSON 错误：参数不完整
        return jsonify({"message": "用户名和密码不能为空"}), 400

    username = data["username"].strip()
    password = data["password"].strip()

    # 2. 数据校验（和前端呼应，双重保障）
    if len(username) < 4 or len(username) > 50:
        return jsonify({"message": "用户名长度必须在4-50位之间"}), 400
    if len(password) < 6:
        return jsonify({"message": "密码不能少于6位"}), 400

    # 3. 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "用户名已存在"}), 400

    # 4. 创建新用户（和原有逻辑一致）
    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    # 5. 返回 JSON 成功响应（前端需要这个来判断注册成功）
    return jsonify({"message": "注册成功，请登录"}), 200


# 同样，修改登录接口为 JSON 版（/api/login），适配前端 Vue
# 后端 app.py 的 api/login 接口（正确写法）
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    username = data.get("username").strip()
    password = data.get("password").strip()

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        # 返回 JSON 错误，状态码 401
        return jsonify({"message": "用户名或密码错误"}), 401

    login_user(user)
    # 返回用户信息
    return (
        jsonify(
            {
                "message": "登录成功",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "is_admin": user.is_admin,
                },
            }
        ),
        200,
    )


@app.route("/api/user", methods=["GET"])
@login_required
def get_current_user():
    return (
        jsonify(
            {
                "id": current_user.id,
                "username": current_user.username,
                "is_admin": current_user.is_admin,
            }
        ),
        200,
    )


@app.route("/api/check-login", methods=["GET"])
def check_login():
    if current_user.is_authenticated:
        return jsonify({"isLogin": True}), 200
    else:
        return jsonify({"isLogin": False}), 200


# ---------- 导出 ----------
@app.route("/api/notes/<int:note_id>/export", methods=["GET"])
@login_required
def export_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    fmt = request.args.get("format", "md").lower()

    # 映射前端格式到后端格式
    format_mapping = {"markdown": "md", "html": "html"}
    fmt = format_mapping.get(fmt, fmt)

    if fmt not in ("md", "pdf", "html"):
        return jsonify({"error": "不支持的导出格式"}), 400

    if fmt == "md":
        md_bytes = (note.content or "").encode("utf-8")
        buffer = io.BytesIO(md_bytes)
        buffer.seek(0)
        filename = f"{note.title or 'note'}.md"
        return send_file(
            buffer, as_attachment=True, download_name=filename, mimetype="text/markdown"
        )
    elif fmt == "html":
        if note.type == "markdown":
            html_content = markdown.markdown(
                note.content or "",
                extensions=[
                    "markdown.extensions.extra",
                    "markdown.extensions.codehilite",
                ],
            )
        else:
            html_content = note.content or ""

        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>{note.title or '无标题笔记'}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }}
                h1, h2, h3 {{ color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
                img {{ max-width: 100%; height: auto; margin: 10px 0; }}
                pre {{ background: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; }}
                code {{ background: #f8f9fa; padding: 2px 4px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <h1>{note.title or '无标题笔记'}</h1>
            <div class="content">{html_content}</div>
            <div style="margin-top: 30px; color: #999; font-size: 12px;">
                导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </body>
        </html>
        """

        html_bytes = html.encode("utf-8")
        buffer = io.BytesIO(html_bytes)
        buffer.seek(0)
        filename = f"{note.title or 'note'}.html"
        return send_file(
            buffer, as_attachment=True, download_name=filename, mimetype="text/html"
        )

    if fmt == "pdf":
        try:
            config = pdfkit.configuration(
                wkhtmltopdf=r"E:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
            )

            if note.type == "markdown":
                html_content = markdown.markdown(
                    note.content or "",
                    extensions=[
                        "markdown.extensions.extra",
                        "markdown.extensions.codehilite",
                    ],
                )
            else:
                base_url = request.host_url
                html_content = (note.content or "").replace(
                    "/static/uploads/", f"{base_url}static/uploads/"
                )

            html = f"""
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <title>{note.title or '无标题笔记'}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
                    h1, h2, h3 {{ color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
                    img {{ max-width: 100%; height: auto; margin: 10px 0; }}
                    pre {{ background: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; }}
                    code {{ background: #f8f9fa; padding: 2px 4px; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <h1>{note.title or '无标题笔记'}</h1>
                <div class="content">{html_content}</div>
                <div style="margin-top: 30px; color: #999; font-size: 12px;">
                    导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
            </body>
            </html>
            """

            pdf_bytes = pdfkit.from_string(
                html,
                output_path=False,
                configuration=config,
                options={
                    "page-size": "A4",
                    "margin-top": "15mm",
                    "margin-right": "15mm",
                    "margin-bottom": "15mm",
                    "margin-left": "15mm",
                    "encoding": "UTF-8",
                    "no-outline": None,
                },
            )

            buffer = io.BytesIO(pdf_bytes)
            buffer.seek(0)
            filename = f"{note.title or 'note'}.pdf"
            return send_file(
                buffer,
                as_attachment=True,
                download_name=filename,
                mimetype="application/pdf",
            )

        except Exception as e:
            print(f"PDF 导出失败：{str(e)}")
            return jsonify({"error": f"PDF 导出失败：{str(e)}"}), 500


# ---------- 分享页面 ----------
@app.route("/share/<token>")
def share_page(token):
    """处理分享链接的访问，验证 token 并显示笔记内容"""
    try:
        link, is_expired = get_share_by_token(token)
        note = link.note
        if not note:
            abort(404, description="分享的笔记不存在")

        # 为过期时间添加时区信息
        expire_at_with_tz = None
        if link.expire_at:
            expire_at_with_tz = link.expire_at.replace(tzinfo=timezone.utc)

        return render_template(
            "share.html",
            note=note,
            token=token,
            permission=link.permission,  # 确保传递权限信息
            expire_at=expire_at_with_tz,
            is_expired=is_expired,  # 使用函数返回的过期状态
            note_id=note.id,  # 确保传递 note_id
        )
    except Exception as e:
        return f"<h1>Forbidden</h1><p>{str(e)}</p>", 403


# -------------------- 启动 --------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # 创建默认管理员用户（如果不存在）
        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(username="admin", is_admin=True)
            admin_user.set_password("admin123")
            db.session.add(admin_user)
            db.session.commit()
            print("默认管理员用户已创建: admin/admin123")

    init_scheduler(app)
    app.run(debug=True, host="0.0.0.0", port=5000)
