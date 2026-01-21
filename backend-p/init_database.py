import pymysql
from pymysql.cursors import DictCursor


def init_database():
    # 首先连接到MySQL（不指定数据库）
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        charset='utf8mb4',
        cursorclass=DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute("CREATE DATABASE IF NOT EXISTS smart_note CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("数据库创建成功")

        # 重新连接到新创建的数据库
        connection.select_db('smart_note')

        with connection.cursor() as cursor:
            # 创建用户表
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

            print("所有表创建成功")

            # 创建默认管理员用户
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = 'admin'")
            admin_exists = cursor.fetchone()['count']
            if not admin_exists:
                import uuid
                cursor.execute(
                    "INSERT INTO users (id, username, password, role) VALUES (%s, %s, %s, %s)",
                    (str(uuid.uuid4()), 'admin', 'admin123', 'admin')
                )
                print("默认管理员用户创建成功")

        connection.commit()
        print("数据库初始化完成！")

    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
        connection.rollback()
    finally:
        connection.close()


if __name__ == '__main__':
    init_database()