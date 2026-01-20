from flask import Flask, jsonify, request
from flask_jwt_extended import jwt_required
from config import config
from extensions import db, cors, bcrypt, jwt
from models import User, Flowchart, Tag, FlowchartTag
import uuid
from datetime import datetime, timedelta
from sqlalchemy import or_


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    cors.init_app(app, supports_credentials=True)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # 注册路由
    register_routes(app)

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app


def register_routes(app):
    # 用户认证
    @app.route('/api/register', methods=['POST'])
    def register():
        from flask import request
        data = request.json

        # 验证数据
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'message': '用户名和密码不能为空'}), 400

        # 检查用户是否存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': '用户名已存在'}), 400

        # 创建用户
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = User(
            username=data['username'],
            password_hash=hashed_password,
            email=data.get('email')
        )

        try:
            db.session.add(user)
            db.session.commit()

            # 生成访问令牌
            from flask_jwt_extended import create_access_token
            access_token = create_access_token(identity=str(user.id))

            return jsonify({
                'message': '注册成功',
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            # 直接打印错误信息到控制台
            print(f"注册失败详细错误: {str(e)}")
            import traceback
            traceback.print_exc()
            # 记录详细错误信息
            app.logger.error(f"注册失败: {str(e)}")
            return jsonify({'message': '注册失败', 'error': str(e)}), 500

    @app.route('/api/login', methods=['POST'])
    def login():
        from flask import request
        data = request.json

        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'message': '用户名和密码不能为空'}), 400

        user = User.query.filter_by(username=data['username']).first()

        if user and bcrypt.check_password_hash(user.password_hash, data['password']):
            from flask_jwt_extended import create_access_token
            access_token = create_access_token(identity=str(user.id))

            return jsonify({
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }), 200

        return jsonify({'message': '用户名或密码错误'}), 401

    # 获取所有标签
    @app.route('/api/tags', methods=['GET'])
    @jwt_required()
    def get_tags():
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()

        tags = Tag.query.filter_by(user_id=user_id).all()

        result = []
        for tag in tags:
            # 获取该标签下的流程图数量
            flowchart_count = FlowchartTag.query.filter_by(tag_id=tag.id).count()

            result.append({
                'id': tag.id,
                'name': tag.name,
                'created_at': tag.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'flowchart_count': flowchart_count
            })

        return jsonify(result), 200

    # 创建标签
    @app.route('/api/tags', methods=['POST'])
    @jwt_required()
    def create_tag():
        from flask import request
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        data = request.json

        if not data or 'name' not in data:
            return jsonify({'message': '标签名称不能为空'}), 400

        # 检查是否已存在相同名称的标签（对同一用户）
        existing_tag = Tag.query.filter_by(name=data['name'], user_id=user_id).first()
        if existing_tag:
            return jsonify({'message': '标签已存在', 'tag': {'id': existing_tag.id, 'name': existing_tag.name}}), 200

        # 创建新标签
        tag = Tag(
            name=data['name'],
            user_id=user_id
        )

        try:
            db.session.add(tag)
            db.session.commit()

            return jsonify({
                'id': tag.id,
                'name': tag.name,
                'message': '标签创建成功'
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': '标签创建失败'}), 500

    # 流程图管理 - 支持搜索和标签筛选
    @app.route('/api/flowcharts', methods=['GET'])
    @jwt_required()
    def get_flowcharts():
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()

        # 获取查询参数
        search = request.args.get('search', '').strip()
        tag_ids = request.args.get('tag_ids', '').strip()

        # 基础查询
        query = Flowchart.query.filter_by(user_id=user_id)

        # 搜索功能
        if search:
            query = query.filter(
                or_(
                    Flowchart.title.ilike(f'%{search}%'),
                    Flowchart.description.ilike(f'%{search}%')
                )
            )

        # 标签筛选
        if tag_ids:
            tag_id_list = [int(tag_id) for tag_id in tag_ids.split(',') if tag_id.isdigit()]
            if tag_id_list:
                # 获取包含所有指定标签的流程图ID
                from sqlalchemy import func
                flowchart_ids = db.session.query(FlowchartTag.flowchart_id).filter(
                    FlowchartTag.tag_id.in_(tag_id_list)
                ).group_by(FlowchartTag.flowchart_id).having(
                    func.count(FlowchartTag.tag_id) == len(tag_id_list)
                ).all()

                flowchart_ids = [fid[0] for fid in flowchart_ids]
                if flowchart_ids:
                    query = query.filter(Flowchart.id.in_(flowchart_ids))
                else:
                    # 如果没有匹配的流程图，返回空列表
                    return jsonify([]), 200

        flowcharts = query.order_by(Flowchart.updated_at.desc()).all()

        result = []
        for fc in flowcharts:
            # 获取流程图的标签
            tags = []
            for tag in fc.tags:
                tags.append({
                    'id': tag.id,
                    'name': tag.name
                })

            result.append({
                'id': fc.id,
                'title': fc.title,
                'description': fc.description,
                'thumbnail': fc.thumbnail,
                'created_at': fc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': fc.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_public': fc.is_public,
                'share_token': fc.share_token,
                'tags': tags
            })

        return jsonify(result), 200

    @app.route('/api/flowcharts', methods=['POST'])
    @jwt_required()
    def create_flowchart():
        from flask import request
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        data = request.json

        # 创建流程图
        flowchart = Flowchart(
            user_id=user_id,
            title=data.get('title', '未命名流程图'),
            description=data.get('description', ''),
            flow_data=data.get('flow_data', {}),
            thumbnail=data.get('thumbnail', ''),
            share_token=str(uuid.uuid4())
        )

        try:
            db.session.add(flowchart)
            db.session.flush()  # 获取flowchart.id

            # 处理标签
            if 'tags' in data and data['tags']:
                for tag_data in data['tags']:
                    tag = None

                    # 如果有id，使用现有标签
                    if 'id' in tag_data:
                        tag = Tag.query.filter_by(id=tag_data['id'], user_id=user_id).first()
                    # 如果有name，创建新标签或使用现有标签
                    elif 'name' in tag_data:
                        tag = Tag.query.filter_by(name=tag_data['name'], user_id=user_id).first()
                        if not tag:
                            tag = Tag(name=tag_data['name'], user_id=user_id)
                            db.session.add(tag)
                            db.session.flush()

                    if tag:
                        # 创建关联
                        flowchart_tag = FlowchartTag(flowchart_id=flowchart.id, tag_id=tag.id)
                        db.session.add(flowchart_tag)

            db.session.commit()

            return jsonify({
                'id': flowchart.id,
                'message': '创建成功'
            }), 201
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"创建流程图失败: {str(e)}")
            return jsonify({'message': '创建失败', 'error': str(e)}), 500

    @app.route('/api/flowcharts/<int:flowchart_id>', methods=['GET'])
    def get_flowchart(flowchart_id):
        try:
            flowchart = Flowchart.query.get_or_404(flowchart_id)

            # 检查权限：公开或自己的
            from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
            user_id = None
            try:
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
            except:
                pass

            if not flowchart.is_public and (not user_id or str(flowchart.user_id) != user_id):
                return jsonify({'message': '无权访问'}), 403

            # 获取流程图的标签
            tags = []
            for tag in flowchart.tags:
                tags.append({
                    'id': tag.id,
                    'name': tag.name
                })

            return jsonify({
                'id': flowchart.id,
                'title': flowchart.title,
                'description': flowchart.description,
                'flow_data': flowchart.flow_data,
                'thumbnail': flowchart.thumbnail,
                'is_public': flowchart.is_public,
                'share_token': flowchart.share_token,
                'author': flowchart.author.username if flowchart.author else '未知作者',
                'created_at': flowchart.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': flowchart.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'tags': tags
            }), 200
        except Exception as e:
            app.logger.error(f"获取流程图失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'message': '获取流程图失败', 'error': str(e)}), 500

    @app.route('/api/flowcharts/<int:flowchart_id>', methods=['PUT'])
    @jwt_required()
    def update_flowchart(flowchart_id):
        from flask import request
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()

        flowchart = Flowchart.query.get_or_404(flowchart_id)

        if str(flowchart.user_id) != user_id:
            return jsonify({'message': '无权修改'}), 403

        data = request.json

        # 更新字段
        if 'title' in data:
            flowchart.title = data['title']
        if 'description' in data:
            flowchart.description = data['description']
        if 'flow_data' in data:
            flowchart.flow_data = data['flow_data']
        if 'thumbnail' in data:
            flowchart.thumbnail = data['thumbnail']
        if 'is_public' in data:
            flowchart.is_public = data['is_public']

        # 更新标签
        if 'tags' in data:
            # 清空现有标签
            FlowchartTag.query.filter_by(flowchart_id=flowchart.id).delete()

            # 添加新标签
            for tag_data in data['tags']:
                tag = None

                # 如果有id，使用现有标签
                if 'id' in tag_data:
                    tag = Tag.query.filter_by(id=tag_data['id'], user_id=user_id).first()
                # 如果有name，创建新标签或使用现有标签
                elif 'name' in tag_data:
                    tag = Tag.query.filter_by(name=tag_data['name'], user_id=user_id).first()
                    if not tag:
                        tag = Tag(name=tag_data['name'], user_id=user_id)
                        db.session.add(tag)
                        db.session.flush()

                if tag:
                    flowchart_tag = FlowchartTag(flowchart_id=flowchart.id, tag_id=tag.id)
                    db.session.add(flowchart_tag)

        flowchart.updated_at = datetime.utcnow()

        try:
            db.session.commit()
            return jsonify({'message': '更新成功'}), 200
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"更新流程图失败: {str(e)}")
            return jsonify({'message': '更新失败', 'error': str(e)}), 500

    @app.route('/api/flowcharts/<int:flowchart_id>', methods=['DELETE'])
    @jwt_required()
    def delete_flowchart(flowchart_id):
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()

        flowchart = Flowchart.query.get_or_404(flowchart_id)

        if str(flowchart.user_id) != user_id:
            return jsonify({'message': '无权删除'}), 403

        try:
            db.session.delete(flowchart)
            db.session.commit()
            return jsonify({'message': '删除成功'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': '删除失败'}), 500

    # 复制流程图
    @app.route('/api/flowcharts/<int:flowchart_id>/duplicate', methods=['POST'])
    @jwt_required()
    def duplicate_flowchart(flowchart_id):
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()

        original_flowchart = Flowchart.query.get_or_404(flowchart_id)

        if str(original_flowchart.user_id) != user_id:
            return jsonify({'message': '无权复制'}), 403

        # 创建副本
        new_flowchart = Flowchart(
            user_id=user_id,
            title=f"{original_flowchart.title} (副本)",
            description=original_flowchart.description,
            flow_data=original_flowchart.flow_data,
            thumbnail=original_flowchart.thumbnail,
            share_token=str(uuid.uuid4()),
            is_public=False
        )

        try:
            db.session.add(new_flowchart)
            db.session.flush()

            # 复制标签
            for tag in original_flowchart.tags:
                flowchart_tag = FlowchartTag(flowchart_id=new_flowchart.id, tag_id=tag.id)
                db.session.add(flowchart_tag)

            db.session.commit()

            return jsonify({
                'id': new_flowchart.id,
                'message': '复制成功'
            }), 201
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"复制流程图失败: {str(e)}")
            return jsonify({'message': '复制失败', 'error': str(e)}), 500

    # 获取当前用户信息
    @app.route('/api/user', methods=['GET'])
    @jwt_required()
    def get_current_user():
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()

        user = User.query.get_or_404(user_id)

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200

    # 分享相关
    @app.route('/api/flowcharts/<int:flowchart_id>/share', methods=['POST'])
    @jwt_required()
    def share_flowchart(flowchart_id):
        from flask import request
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()

        flowchart = Flowchart.query.get_or_404(flowchart_id)

        if str(flowchart.user_id) != user_id:
            return jsonify({'message': '无权分享'}), 403

        data = request.json
        days = data.get('days', 7)

        # 生成分享链接
        share_url = f'/share/{flowchart.share_token}'

        return jsonify({
            'share_url': share_url,
            'share_token': flowchart.share_token,
            'expires_in': f'{days}天'
        }), 200

    @app.route('/api/share/<share_token>', methods=['GET'])
    def get_shared_flowchart(share_token):
        flowchart = Flowchart.query.filter_by(share_token=share_token).first()

        if not flowchart:
            return jsonify({'message': '分享不存在或已过期'}), 404

        # 获取流程图的标签
        tags = []
        for tag in flowchart.tags:
            tags.append({
                'id': tag.id,
                'name': tag.name
            })

        return jsonify({
            'id': flowchart.id,
            'title': flowchart.title,
            'flow_data': flowchart.flow_data,
            'thumbnail': flowchart.thumbnail,
            'is_public': flowchart.is_public,
            'readonly': True,
            'tags': tags
        }), 200


# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)