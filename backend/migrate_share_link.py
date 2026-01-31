import pymysql
import re
from config import Config

def parse_db_uri(uri):
    pattern = r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/([^?]+)'
    match = re.match(pattern, uri)
    if match:
        return {
            'user': match.group(1),
            'password': match.group(2),
            'host': match.group(3),
            'port': int(match.group(4)),
            'database': match.group(5)
        }
    return None

def migrate_share_link_table():
    db_config = parse_db_uri(Config.SQLALCHEMY_DATABASE_URI)
    if not db_config:
        print("无法解析数据库连接字符串")
        return
    
    conn = pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM share_link LIKE 'flowchart_id'")
            flowchart_exists = cursor.fetchone()
            
            if not flowchart_exists:
                cursor.execute("""
                    ALTER TABLE share_link 
                    ADD COLUMN flowchart_id INT NULL AFTER note_id,
                    ADD CONSTRAINT fk_share_link_flowchart 
                    FOREIGN KEY (flowchart_id) REFERENCES flowchart(id) ON DELETE CASCADE
                """)
                print("✓ 已添加 flowchart_id 列")
            else:
                print("✓ flowchart_id 列已存在")
            
            cursor.execute("SHOW COLUMNS FROM share_link LIKE 'mindmap_id'")
            mindmap_exists = cursor.fetchone()
            
            if not mindmap_exists:
                cursor.execute("""
                    ALTER TABLE share_link 
                    ADD COLUMN mindmap_id INT NULL AFTER flowchart_id,
                    ADD CONSTRAINT fk_share_link_mindmap 
                    FOREIGN KEY (mindmap_id) REFERENCES mindmap(id) ON DELETE CASCADE
                """)
                print("✓ 已添加 mindmap_id 列")
            else:
                print("✓ mindmap_id 列已存在")
            
            conn.commit()
            print("\n数据库迁移完成！")
            
    except Exception as e:
        conn.rollback()
        print(f"迁移失败: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_share_link_table()
