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

def migrate_share_link_nullable():
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
            cursor.execute("SHOW COLUMNS FROM share_link WHERE Field = 'note_id'")
            note_id_info = cursor.fetchone()
            
            if note_id_info and note_id_info['Null'] == 'NO':
                cursor.execute("ALTER TABLE share_link MODIFY COLUMN note_id INT NULL")
                print("✓ 已修改 note_id 列为可空")
            else:
                print("✓ note_id 列已允许为空")
            
            cursor.execute("SHOW COLUMNS FROM share_link WHERE Field = 'flowchart_id'")
            flowchart_id_info = cursor.fetchone()
            
            if flowchart_id_info and flowchart_id_info['Null'] == 'NO':
                cursor.execute("ALTER TABLE share_link MODIFY COLUMN flowchart_id INT NULL")
                print("✓ 已修改 flowchart_id 列为可空")
            else:
                print("✓ flowchart_id 列已允许为空")
            
            cursor.execute("SHOW COLUMNS FROM share_link WHERE Field = 'mindmap_id'")
            mindmap_id_info = cursor.fetchone()
            
            if mindmap_id_info and mindmap_id_info['Null'] == 'NO':
                cursor.execute("ALTER TABLE share_link MODIFY COLUMN mindmap_id INT NULL")
                print("✓ 已修改 mindmap_id 列为可空")
            else:
                print("✓ mindmap_id 列已允许为空")
            
            conn.commit()
            print("\n数据库迁移完成！")
            
    except Exception as e:
        conn.rollback()
        print(f"迁移失败: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_share_link_nullable()
