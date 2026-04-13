from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import json
import os
import time
import random
from collections import defaultdict

# 白板数据管理类
class BoardData:
    def __init__(self, name):
        self.name = name
        self.data = []
        self.users = set()
        self.last_save = time.time()
        self.load()
    
    def load(self):
        # 从文件加载白板数据
        data_dir = 'server-data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        file_path = os.path.join(data_dir, f'{self.name}.json')
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"加载白板数据失败: {e}")
    
    def save(self):
        # 保存白板数据到文件
        data_dir = 'server-data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        file_path = os.path.join(data_dir, f'{self.name}.json')
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            self.last_save = time.time()
        except Exception as e:
            print(f"保存白板数据失败: {e}")
    
    def getAll(self):
        return self.data
    
    def processMessage(self, message):
        # 处理收到的消息
        self.data.append(message)
        # 定期保存
        if time.time() - self.last_save > 30:  # 每30秒保存一次
            self.save()

# 白板管理
boards = {}

# 生成唯一ID
def generate_uid(prefix='', suffix=''):
    uid = str(int(time.time() * 1000))
    uid += str(random.randint(0, 999)).zfill(3)
    if prefix:
        uid = prefix + uid
    if suffix:
        uid = uid + suffix
    return uid

# 初始化 SocketIO
def init_socketio(app):
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    @socketio.on('connect')
    def handle_connect():
        print(f"客户端连接: {request.sid}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"客户端断开连接: {request.sid}")
        # 从所有房间中移除用户
        for board_name, board in boards.items():
            if request.sid in board.users:
                board.users.remove(request.sid)
                print(f"用户 {request.sid} 从白板 {board_name} 断开连接，当前用户数: {len(board.users)}")
                if len(board.users) == 0:
                    # 保存并卸载白板
                    board.save()
                    del boards[board_name]
                    print(f"白板 {board_name} 已卸载")
    
    @socketio.on('getboard')
    def handle_getboard(board_name):
        if not board_name:
            board_name = 'anonymous'
        
        # 加入房间
        join_room(board_name)
        
        # 获取或创建白板
        if board_name not in boards:
            boards[board_name] = BoardData(board_name)
        
        board = boards[board_name]
        board.users.add(request.sid)
        print(f"用户 {request.sid} 加入白板 {board_name}，当前用户数: {len(board.users)}")
        
        # 发送白板数据
        emit('broadcast', {'_children': board.getAll()})
    
    @socketio.on('joinboard')
    def handle_joinboard(board_name):
        if not board_name:
            board_name = 'anonymous'
        
        # 加入房间
        join_room(board_name)
        
        # 获取或创建白板
        if board_name not in boards:
            boards[board_name] = BoardData(board_name)
        
        board = boards[board_name]
        board.users.add(request.sid)
        print(f"用户 {request.sid} 加入白板 {board_name}，当前用户数: {len(board.users)}")
    
    @socketio.on('broadcast')
    def handle_broadcast(message):
        board_name = message.get('board', 'anonymous')
        data = message.get('data')
        
        if not data:
            print("收到无效消息: 缺少数据")
            return
        
        # 确保用户在房间中
        if board_name not in request.namespace.rooms:
            join_room(board_name)
        
        # 检查消息类型
        if not (data.get('tool') or data.get('type') == 'child'):
            print("收到无效消息: 缺少工具或类型")
            return
        
        # 处理消息
        if board_name not in boards:
            boards[board_name] = BoardData(board_name)
        
        board = boards[board_name]
        
        # 处理光标消息
        if data.get('tool') == 'Cursor':
            data['socket'] = request.sid
        else:
            # 保存历史记录
            board.processMessage(data)
        
        # 广播消息给房间中的其他用户
        emit('broadcast', data, room=board_name, include_self=False)
    
    return socketio