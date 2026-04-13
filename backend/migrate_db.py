import sqlite3

conn = sqlite3.connect('instance/zhilianbiji.db')
cursor = conn.cursor()

# 检查并添加字段
tables = ['note', 'flowchart', 'table_document', 'whiteboard', 'mindmap']
for table in tables:
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [col[1] for col in cursor.fetchall()]
    if 'is_deleted' not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN is_deleted INTEGER DEFAULT 0")
        print(f'Added is_deleted to {table}')
    if 'deleted_at' not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN deleted_at TEXT")
        print(f'Added deleted_at to {table}')

conn.commit()
conn.close()
print('Database updated successfully')
