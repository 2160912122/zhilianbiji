import os
import json
import uuid
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import pymysql
from pymysql.cursors import DictCursor
# 初始化Flask应用
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key_12345')  # 生产环境需更换为安全密钥

# 启用CORS支持
CORS(app, origins=['http://localhost:5173', 'http://localhost:5175'], supports_credentials=True)

# 数据库配置
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '051204')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'smart_note')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""数据库工具函数"""


def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            charset='utf8mb4',
            cursorclass=DictCursor,
            autocommit=True
        )
        return connection
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        return None


def init_database():
    """初始化数据库表结构"""
    connection = get_db_connection()
    if not connection:
        logger.error("无法连接到数据库，初始化失败")
        return

    try:
        with connection.cursor() as cursor:
            # 用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(36) PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(20) DEFAULT 'user',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME
                )
            ''')

            # 表格文档表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tables (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    columns_data JSON,
                    rows_data JSON,
                    cell_styles JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')

            # 白板文档表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS whiteboards (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    room_key VARCHAR(100),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')

            # 系统设置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_settings (
                    setting_key VARCHAR(100) PRIMARY KEY,
                    setting_value TEXT,
                    description VARCHAR(255),
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')

            # 分享链接表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS share_links (
                    id VARCHAR(36) PRIMARY KEY,
                    doc_id VARCHAR(36) NOT NULL,
                    doc_type ENUM('table', 'whiteboard') NOT NULL,
                    permission ENUM('view', 'edit') DEFAULT 'view',
                    expiry DATETIME NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(36) NOT NULL
                )
            ''')

            # 插入默认系统设置
            cursor.execute('''
                INSERT IGNORE INTO system_settings (setting_key, setting_value, description) VALUES
                ('default_share_expiry', '7d', '默认分享链接有效期'),
                ('auto_save_interval', '30', '自动保存间隔（秒）'),
                ('max_file_size', '10', '最大文件大小（MB）'),
                ('session_timeout', '60', '会话超时时间（分钟）')
            ''')

            # 创建默认管理员
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = 'admin'")
            if not cursor.fetchone()['count']:
                cursor.execute(
                    "INSERT INTO users (id, username, password, role) VALUES (%s, %s, %s, %s)",
                    (str(uuid.uuid4()), 'admin', 'admin123', 'admin')
                )

        connection.commit()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        connection.rollback()
    finally:
        connection.close()


"""认证装饰器"""


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'status': 'error', 'message': '请先登录'}), 401
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'status': 'error', 'message': '请先登录'}), 401
        if session.get('role') != 'admin':
            return jsonify({'status': 'error', 'message': '权限不足'}), 403
        return f(*args, **kwargs)

    return decorated_function


"""用户认证API"""


@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({'status': 'error', 'message': '用户名和密码不能为空'}), 400
        if len(username) < 3:
            return jsonify({'status': 'error', 'message': '用户名至少3个字符'}), 400
        if len(password) < 6:
            return jsonify({'status': 'error', 'message': '密码至少6个字符'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return jsonify({'status': 'error', 'message': '用户名已存在'}), 400

            user_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO users (id, username, password) VALUES (%s, %s, %s)",
                (user_id, username, password)
            )
            connection.commit()

        return jsonify({'status': 'success', 'message': '注册成功'})
    except Exception as e:
        logger.error(f"注册失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '注册失败'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'status': 'error', 'message': '用户名和密码不能为空'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, password, role FROM users WHERE username = %s",
                (username,)
            )
            user = cursor.fetchone()

            if user and user['password'] == password:
                cursor.execute(
                    "UPDATE users SET last_login = %s WHERE id = %s",
                    (datetime.now(), user['id'])
                )
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                connection.commit()

                return jsonify({
                    'status': 'success',
                    'message': '登录成功',
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'role': user['role']
                    }
                })
            else:
                return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '登录失败'}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'success', 'message': '登出成功'})


@app.route('/api/check-login', methods=['GET'])
def check_login():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'username': session['username'],
            'role': session.get('role', 'user')
        })
    return jsonify({'logged_in': False})


@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500
        
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email, role, created_at, last_login FROM users WHERE id = %s",
                (session['user_id'],)
            )
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'status': 'error', 'message': '用户不存在'}), 404
            
            # 格式化日期
            if user['created_at']:
                user['created_at'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if user['last_login']:
                user['last_login'] = user['last_login'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'status': 'success', 'user': user})
    except Exception as e:
        logger.error(f"获取用户资料失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '获取用户资料失败'}), 500


@app.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500
        
        with connection.cursor() as cursor:
            # 检查用户名是否已存在（排除当前用户）
            if username:
                cursor.execute(
                    "SELECT id FROM users WHERE username = %s AND id != %s",
                    (username, session['user_id'])
                )
                if cursor.fetchone():
                    return jsonify({'status': 'error', 'message': '用户名已存在'}), 400
            
            # 更新用户资料
            update_fields = []
            update_values = []
            
            if username:
                update_fields.append("username = %s")
                update_values.append(username)
                session['username'] = username  # 更新session中的用户名
            
            if email:
                update_fields.append("email = %s")
                update_values.append(email)
            
            if not update_fields:
                return jsonify({'status': 'error', 'message': '没有需要更新的字段'}), 400
            
            update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            update_values.append(session['user_id'])
            
            cursor.execute(update_query, tuple(update_values))
            connection.commit()
        
        return jsonify({'status': 'success', 'message': '用户资料更新成功'})
    except Exception as e:
        logger.error(f"更新用户资料失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '更新用户资料失败'}), 500


"""文档管理API"""


@app.route('/api/documents', methods=['GET'])
@login_required
def get_documents():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        with connection.cursor() as cursor:
            documents = []

            # 加载表格文档
            cursor.execute(
                "SELECT id, title, 'table' as type, updated_at FROM tables WHERE user_id = %s",
                (session['user_id'],)
            )
            for table in cursor.fetchall():
                documents.append({
                    'id': table['id'],
                    'name': table['title'],
                    'type': 'table',
                    'modified': table['updated_at'].strftime('%Y-%m-%d %H:%M') if table['updated_at'] else ''
                })

            # 加载白板文档
            cursor.execute(
                "SELECT id, title, 'whiteboard' as type, updated_at FROM whiteboards WHERE user_id = %s",
                (session['user_id'],)
            )
            for whiteboard in cursor.fetchall():
                documents.append({
                    'id': whiteboard['id'],
                    'name': whiteboard['title'],
                    'type': 'whiteboard',
                    'modified': whiteboard['updated_at'].strftime('%Y-%m-%d %H:%M') if whiteboard['updated_at'] else ''
                })

        return jsonify(documents)
    except Exception as e:
        logger.error(f"获取文档列表失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '获取文档列表失败'}), 500


"""表格文档API"""


@app.route('/api/table/new', methods=['POST'])
@login_required
def new_table():
    try:
        data = request.get_json() or {}
        title = data.get('title', '新表格')

        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        with connection.cursor() as cursor:
            # 检查是否已存在相同名称的表格
            cursor.execute(
                "SELECT COUNT(*) as count FROM tables WHERE user_id = %s AND title = %s",
                (session['user_id'], title)
            )
            result = cursor.fetchone()
            if result['count'] > 0:
                return jsonify({'status': 'error', 'message': '该表格名称已存在'}), 400

            # 创建新表格
            table_data = {
                "id": str(uuid.uuid4()),
                "title": title,
                "columns": ["列1", "列2", "列3"],
                "rows": [["", "", ""], ["", "", ""], ["", "", ""]],
                "cellStyles": {}
            }

            cursor.execute(
                "INSERT INTO tables (id, user_id, title, columns_data, rows_data, cell_styles) VALUES (%s, %s, %s, %s, %s, %s)",
                (table_data['id'], session['user_id'], title,
                 json.dumps(table_data['columns']),
                 json.dumps(table_data['rows']),
                 json.dumps(table_data['cellStyles']))
            )
            connection.commit()

        return jsonify({'status': 'success', 'id': table_data['id'], 'data': table_data})
    except Exception as e:
        logger.error(f"创建表格失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '创建表格失败'}), 500


@app.route('/api/table', methods=['GET'])
@login_required
def get_table():
    try:
        table_id = request.args.get('id')
        if not table_id:
            return jsonify({'status': 'error', 'message': '缺少表格ID'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM tables WHERE id = %s AND user_id = %s",
                (table_id, session['user_id'])
            )
            table = cursor.fetchone()

            if not table:
                return jsonify({'status': 'error', 'message': '表格不存在'}), 404

            return jsonify({
                "id": table['id'],
                "title": table['title'],
                "columns": json.loads(table['columns_data']),
                "rows": json.loads(table['rows_data']),
                "cellStyles": json.loads(table['cell_styles']) if table['cell_styles'] else {}
            })
    except Exception as e:
        logger.error(f"获取表格失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '获取表格失败'}), 500


@app.route('/api/table/save', methods=['POST'])
@login_required
def save_table():
    try:
        data = request.get_json()
        if not data or not data.get('id'):
            return jsonify({'status': 'error', 'message': '无效数据或缺少表格ID'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE tables SET title = %s, columns_data = %s, rows_data = %s, cell_styles = %s WHERE id = %s AND user_id = %s",
                (data.get('title'),
                 json.dumps(data.get('columns', [])),
                 json.dumps(data.get('rows', [])),
                 json.dumps(data.get('cellStyles', {})),
                 data.get('id'), session['user_id'])
            )
            connection.commit()

        return jsonify({'status': 'success', 'message': '表格保存成功'})
    except Exception as e:
        logger.error(f"保存表格失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '保存表格失败'}), 500


"""白板文档API"""


@app.route('/api/whiteboard/new', methods=['POST'])
@login_required
def new_whiteboard():
    try:
        data = request.get_json() or {}
        title = data.get('title', '新白板')
        room_key = str(uuid.uuid4())[:22]

        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        with connection.cursor() as cursor:
            # 检查是否已存在相同名称的白板
            cursor.execute(
                "SELECT COUNT(*) as count FROM whiteboards WHERE user_id = %s AND title = %s",
                (session['user_id'], title)
            )
            result = cursor.fetchone()
            if result['count'] > 0:
                return jsonify({'status': 'error', 'message': '该白板名称已存在'}), 400

            # 创建新白板
            whiteboard_data = {
                "id": str(uuid.uuid4()),
                "title": title,
                "room_key": room_key
            }

            cursor.execute(
                "INSERT INTO whiteboards (id, user_id, title, room_key) VALUES (%s, %s, %s, %s)",
                (whiteboard_data['id'], session['user_id'], title, room_key)
            )
            connection.commit()

        return jsonify({'status': 'success', 'id': whiteboard_data['id'], 'data': whiteboard_data})
    except Exception as e:
        logger.error(f"创建白板失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '创建白板失败'}), 500


@app.route('/api/whiteboard', methods=['GET'])
@login_required
def get_whiteboard():
    try:
        whiteboard_id = request.args.get('id')
        if not whiteboard_id:
            return jsonify({'status': 'error', 'message': '缺少白板ID'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM whiteboards WHERE id = %s AND user_id = %s",
                (whiteboard_id, session['user_id'])
            )
            whiteboard = cursor.fetchone()

            if not whiteboard:
                return jsonify({'status': 'error', 'message': '白板不存在'}), 404

            return jsonify({
                "id": whiteboard['id'],
                "title": whiteboard['title'],
                "room_key": whiteboard['room_key'],
                "excalidraw_data": whiteboard['excalidraw_data']
            })
    except Exception as e:
        logger.error(f"获取白板失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '获取白板失败'}), 500


@app.route('/api/whiteboard/save', methods=['POST'])
@login_required
def save_whiteboard():
    try:
        data = request.get_json()
        if not data or not data.get('id'):
            return jsonify({'status': 'error', 'message': '无效数据或缺少白板ID'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        with connection.cursor() as cursor:
            # 验证所有权
            cursor.execute(
                "SELECT id FROM whiteboards WHERE id = %s AND user_id = %s",
                (data['id'], session['user_id'])
            )
            if not cursor.fetchone():
                return jsonify({'status': 'error', 'message': '无权修改此白板'}), 403

            # 更新白板信息
            cursor.execute(
                """UPDATE whiteboards 
                   SET title = %s, room_key = %s, excalidraw_data = %s, updated_at = CURRENT_TIMESTAMP 
                   WHERE id = %s AND user_id = %s""",
                (data.get('title', '未命名白板'),
                 data.get('room_key', str(uuid.uuid4())[:22]),
                 data.get('excalidraw_data'),
                 data['id'],
                 session['user_id'])
            )
            connection.commit()

        return jsonify({'status': 'success', 'message': '白板保存成功'})
    except Exception as e:
        logger.error(f"保存白板失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '保存白板失败'}), 500


"""分享功能API"""


@app.route('/api/share/<shareId>', methods=['GET'])
def get_shared_document(shareId):
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        with connection.cursor() as cursor:
            # 查询分享记录
            cursor.execute(
                "SELECT * FROM share_links WHERE id = %s",
                (shareId,)
            )
            share = cursor.fetchone()

            if not share:
                return jsonify({'status': 'error', 'message': '分享链接不存在'}), 404

            # 检查过期
            if share['expiry'] and share['expiry'] < datetime.now():
                cursor.execute("DELETE FROM share_links WHERE id = %s", (shareId,))
                connection.commit()
                return jsonify({'status': 'error', 'message': '分享链接已过期'}), 404

            doc_id = share['doc_id']
            doc_type = share['doc_type']
            permission = share['permission']

            # 查询文档内容
            if doc_type == 'table':
                cursor.execute(
                    "SELECT id, title, columns_data, rows_data, cell_styles FROM tables WHERE id = %s",
                    (doc_id,)
                )
                doc = cursor.fetchone()
                if not doc:
                    return jsonify({'status': 'error', 'message': '文档已被删除'}), 404

                return jsonify({
                    'id': doc['id'],
                    'type': 'table',
                    'title': doc['title'],
                    'columns': json.loads(doc['columns_data']),
                    'rows': json.loads(doc['rows_data']),
                    'cellStyles': json.loads(doc['cell_styles']) if doc['cell_styles'] else {},
                    'permission': permission
                })

            elif doc_type == 'whiteboard':
                cursor.execute(
                    "SELECT id, title, room_key FROM whiteboards WHERE id = %s",
                    (doc_id,)
                )
                doc = cursor.fetchone()
                if not doc:
                    return jsonify({'status': 'error', 'message': '文档已被删除'}), 404

                return jsonify({
                    'id': doc['id'],
                    'type': 'whiteboard',
                    'title': doc['title'],
                    'room_key': doc['room_key'],
                    'permission': permission
                })

            else:
                return jsonify({'status': 'error', 'message': '不支持的文档类型'}), 400

    except Exception as e:
        logger.error(f"获取分享文档失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '获取分享文档失败'}), 500


@app.route('/api/share/create', methods=['POST'])
@login_required
def create_share():
    try:
        data = request.get_json()
        if not data or not data.get('doc_id') or not data.get('doc_type'):
            return jsonify({'status': 'error', 'message': '缺少文档ID或类型'}), 400

        doc_id = data['doc_id']
        doc_type = data['doc_type']
        permission = data.get('permission', 'view')
        expiry = data.get('expiry', '7d')

        # 计算过期时间
        expiry_time = None
        if expiry != 'never':
            days = int(expiry.replace('d', ''))
            expiry_time = datetime.now() + timedelta(days=days)

        # 生成分享ID
        share_id = str(uuid.uuid4())

        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        with connection.cursor() as cursor:
            # 验证文档所有权
            table = "tables" if doc_type == 'table' else "whiteboards"
            cursor.execute(
                f"SELECT id FROM {table} WHERE id = %s AND user_id = %s",
                (doc_id, session['user_id'])
            )
            if not cursor.fetchone():
                return jsonify({'status': 'error', 'message': '无权分享此文档'}), 403

            # 创建分享记录
            cursor.execute(
                """INSERT INTO share_links 
                   (id, doc_id, doc_type, permission, expiry, created_by) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (share_id, doc_id, doc_type, permission, expiry_time, session['user_id'])
            )
            connection.commit()

        return jsonify({
            'status': 'success',
            'share_id': share_id,
            'share_url': f"{request.host_url}?share={share_id}"
        })
    except Exception as e:
        logger.error(f"创建分享链接失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '创建分享链接失败'}), 500


"""管理后台API"""


@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username, role, created_at, last_login FROM users")
            users = cursor.fetchall()

            for user in users:
                if user['created_at']:
                    user['created_at'] = user['created_at'].strftime('%Y-%m-%d %H:%M')
                if user['last_login']:
                    user['last_login'] = user['last_login'].strftime('%Y-%m-%d %H:%M')

        return jsonify({'status': 'success', 'users': users})
    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '获取用户列表失败'}), 500


@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_stats():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as user_count FROM users")
            user_count = cursor.fetchone()['user_count']

            cursor.execute("SELECT COUNT(*) as table_count FROM tables")
            table_count = cursor.fetchone()['table_count']

            cursor.execute("SELECT COUNT(*) as whiteboard_count FROM whiteboards")
            whiteboard_count = cursor.fetchone()['whiteboard_count']

        return jsonify({
            'status': 'success',
            'stats': {
                'user_count': user_count,
                'table_count': table_count,
                'whiteboard_count': whiteboard_count,
                'total_documents': table_count + whiteboard_count
            }
        })
    except Exception as e:
        logger.error(f"获取统计数据失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '获取统计数据失败'}), 500


@app.route('/api/admin/users/<user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    try:
        data = request.get_json()
        if not data or not data.get('role'):
            return jsonify({'status': 'error', 'message': '缺少角色信息'}), 400

        role = data['role']
        if role not in ['user', 'admin']:
            return jsonify({'status': 'error', 'message': '无效的角色'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        with connection.cursor() as cursor:
            # 检查用户是否存在
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cursor.fetchone():
                return jsonify({'status': 'error', 'message': '用户不存在'}), 404

            # 更新用户角色
            cursor.execute(
                "UPDATE users SET role = %s WHERE id = %s",
                (role, user_id)
            )
            connection.commit()

        return jsonify({'status': 'success', 'message': '用户角色更新成功'})
    except Exception as e:
        logger.error(f"更新用户角色失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '更新用户角色失败'}), 500


"""静态文件服务 - 前后端分离后不再需要"""

# 根路径返回主页面
@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')



"""应用入口"""
# 临时端点：更新数据库结构
@app.route('/api/update-db', methods=['GET'])
def update_db():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        with connection.cursor() as cursor:
            # 添加excalidraw_data字段到whiteboards表
            cursor.execute(
                'ALTER TABLE whiteboards ADD COLUMN excalidraw_data JSON NULL AFTER room_key'
            )
            connection.commit()

        return jsonify({'status': 'success', 'message': '数据库表更新成功：已添加excalidraw_data字段'})
    except Exception as e:
        logger.error(f"更新数据库失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'更新数据库失败: {str(e)}'}), 500

if __name__ == '__main__':
    init_database()  # 初始化数据库
    app.run(host='0.0.0.0', port=5000, debug=True)  # 生产环境需关闭debug