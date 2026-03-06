from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify
from models import db
import os
import re
import html
from datetime import datetime, timedelta

def strip_html_tags(text):
    """安全地移除HTML标签，返回纯文本"""
    if not text:
        return ""
    
    # 移除HTML标签
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # 解码HTML实体
    clean_text = html.unescape(clean_text)
    
    # 清理多余的空白字符
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return clean_text

def get_excerpt(content, max_length=180):
    """获取文章摘要"""
    if not content:
        return ""
    
    # 如果是HTML内容，先提取纯文本
    plain_text = strip_html_tags(content)
    
    # 截取指定长度
    if len(plain_text) > max_length:
        return plain_text[:max_length] + "..."
    else:
        return plain_text

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

def get_current_user():
    """获取当前登录用户（返回字典）"""
    session_token = session.get('session_token')
    if session_token:
        user = db.verify_session(session_token)
        # 将 sqlite3.Row 转换为字典
        if user:
            return dict(user)
    return None

def require_login(f):
    """登录装饰器"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            flash('请先登录后再进行此操作！')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/favicon.ico')
def favicon():
    """返回空的 favicon，避免 404 错误"""
    return '', 204

@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools():
    """处理 Chrome DevTools 请求，避免 404 错误"""
    return '', 204

@app.route('/')
@app.route('/page/<int:page>')
def index(page=1):
    per_page = 6
    offset = (page - 1) * per_page
    
    # 获取总文章数
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM posts')
    total_posts = cursor.fetchone()[0]
    conn.close()
    
    # 获取当前页的文章
    posts = db.get_posts_paginated(offset, per_page)
    
    # 预计算每篇文章的点赞数、摘要和是否已点赞
    posts_with_likes = []
    current_user = get_current_user()
    
    for post in posts:
        post_dict = dict(post)
        post_dict['like_count'] = db.get_post_likes_count(post['id'])
        post_dict['excerpt'] = get_excerpt(post['content'], 180)
        
        # 判断是否已点赞
        if current_user:
            post_dict['has_liked'] = db.has_liked_post(post['id'], current_user['id'], request.remote_addr)
        else:
            post_dict['has_liked'] = db.has_liked_post(post['id'], None, request.remote_addr)
        
        posts_with_likes.append(post_dict)
    
    return render_template('index.html', 
                         posts=posts_with_likes, 
                         current_user=current_user,
                         page=page,
                         per_page=per_page,
                         total_posts=total_posts)

@app.route('/api/posts')
def api_get_posts():
    """API 接口：获取瀑布流文章数据"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int)
    offset = (page - 1) * per_page
    
    # 获取总文章数
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM posts')
    total_posts = cursor.fetchone()[0]
    conn.close()
    
    # 获取文章数据
    posts = db.get_posts_paginated(offset, per_page)
    
    # 获取当前用户并转换为字典
    current_user = get_current_user()
    if current_user:
        current_user_data = {
            'id': current_user['id'],
            'username': current_user['username'],
            'email': current_user['email'],
            'is_admin': current_user['is_admin']
        }
    else:
        current_user_data = None
    
    # 处理文章数据 - 将 Row 对象转换为字典
    posts_data = []
    for post in posts:
        post_dict = {
            'id': post['id'],
            'title': post['title'],
            'content': post['content'],
            'author': post['author'],
            'author_name': post['author_name'],
            'user_id': post['user_id'],
            'created_at': str(post['created_at']),
            'updated_at': str(post['updated_at']),
            'view_count': db.get_view_count(post['id'])
        }
        post_dict['like_count'] = db.get_post_likes_count(post['id'])
        post_dict['excerpt'] = get_excerpt(post['content'], 180)
        
        # 判断是否已点赞
        if current_user_data:
            post_dict['has_liked'] = db.has_liked_post(post['id'], current_user_data['id'], request.remote_addr)
        else:
            post_dict['has_liked'] = db.has_liked_post(post['id'], None, request.remote_addr)
        
        # 添加权限判断
        if current_user_data:
            post_dict['can_edit'] = (post_dict['user_id'] == current_user_data['id'] or current_user_data.get('is_admin'))
        else:
            post_dict['can_edit'] = False
        posts_data.append(post_dict)
    
    return jsonify({
        'posts': posts_data,
        'page': page,
        'per_page': per_page,
        'total_posts': total_posts,
        'has_more': offset + len(posts) < total_posts,
        'current_user': current_user_data
    })

@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = db.get_post_by_id(post_id)
    if post:
        # 增加浏览次数
        db.increment_view_count(post_id)
        
        # 预计算点赞数、浏览量和是否已点赞
        post_dict = dict(post)
        post_dict['like_count'] = db.get_post_likes_count(post['id'])
        post_dict['view_count'] = db.get_view_count(post['id'])
        
        # 判断当前用户是否已点赞
        current_user = get_current_user()
        if current_user:
            post_dict['has_liked'] = db.has_liked_post(post['id'], current_user['id'], request.remote_addr)
        else:
            post_dict['has_liked'] = db.has_liked_post(post['id'], None, request.remote_addr)
        
        return render_template('post.html', post=post_dict, current_user=current_user)
    else:
        flash('文章不存在！')
        return redirect(url_for('index'))

@app.route('/api/like/<int:post_id>', methods=['POST'])
def like_post_api(post_id):
    """点赞 API"""
    # 获取用户信息
    current_user = get_current_user()
    
    # 获取 IP 地址（简化版）
    ip_address = request.remote_addr
    
    # 执行点赞操作
    liked = db.like_post(post_id, current_user['id'] if current_user else None, ip_address)
    
    # 返回点赞状态和数量
    like_count = db.get_post_likes_count(post_id)
    
    return jsonify({
        'success': True,
        'liked': liked,
        'count': like_count,
        'message': '点赞成功' if liked else '已取消点赞'
    })

# ========== 评论相关 API ==========

@app.route('/api/comments', methods=['POST'])
def create_comment():
    """创建评论"""
    current_user = get_current_user()
    
    if not current_user:
        return jsonify({
            'success': False,
            'message': '请先登录后再评论'
        }), 401
    
    data = request.get_json()
    post_id = data.get('post_id')
    content = data.get('content', '').strip()
    parent_id = data.get('parent_id')  # 可选，如果是回复评论则提供
    
    # 验证
    if not post_id:
        return jsonify({
            'success': False,
            'message': '缺少文章 ID'
        }), 400
    
    if not content or len(content) < 1:
        return jsonify({
            'success': False,
            'message': '评论内容不能为空'
        }), 400
    
    if len(content) > 1000:
        return jsonify({
            'success': False,
            'message': '评论内容过长（最多 1000 字）'
        }), 400
    
    # 检查文章是否存在
    post = db.get_post_by_id(post_id)
    if not post:
        return jsonify({
            'success': False,
            'message': '文章不存在'
        }), 404
    
    # 创建评论
    comment_id = db.create_comment(post_id, current_user['id'], content, parent_id)
    
    # 创建通知
    if parent_id:
        # 回复评论：通知被回复的人
        parent_comment = db.get_comments_by_post(post_id)
        parent_comment = next((c for c in parent_comment if c['id'] == parent_id), None)
        
        if parent_comment and parent_comment['user_id'] != current_user['id']:
            db.create_notification(
                user_id=parent_comment['user_id'],
                type='reply',
                comment_id=comment_id,
                post_id=post_id,
                from_user_id=current_user['id']
            )
    else:
        # 首次评论：通知文章作者
        if post['user_id'] != current_user['id']:
            db.create_notification(
                user_id=post['user_id'],
                type='comment',
                comment_id=comment_id,
                post_id=post_id,
                from_user_id=current_user['id']
            )
    
    return jsonify({
        'success': True,
        'message': '评论成功',
        'comment_id': comment_id
    }), 201

@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    """获取文章的评论列表（树形结构）"""
    comments = db.get_comment_tree(post_id)
    
    return jsonify({
        'success': True,
        'comments': comments,
        'total': len(comments)
    })

@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """删除评论"""
    current_user = get_current_user()
    
    if not current_user:
        return jsonify({
            'success': False,
            'message': '请先登录'
        }), 401
    
    # 删除评论
    success = db.delete_comment(comment_id, current_user['id'], current_user.get('is_admin', False))
    
    if success:
        return jsonify({
            'success': True,
            'message': '评论已删除'
        })
    else:
        return jsonify({
            'success': False,
            'message': '无权删除此评论或评论不存在'
        }), 403

# ========== 通知相关 API ==========

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """获取用户的通知列表"""
    current_user = get_current_user()
    
    if not current_user:
        return jsonify({
            'success': False,
            'message': '请先登录'
        }), 401
    
    notifications = db.get_user_notifications(current_user['id'])
    unread_count = db.get_unread_notification_count(current_user['id'])
    
    # 将 Row 对象转换为字典
    notifications_data = []
    for notif in notifications:
        notif_dict = {
            'id': notif['id'],
            'user_id': notif['user_id'],
            'type': notif['type'],
            'comment_id': notif['comment_id'],
            'post_id': notif['post_id'],
            'from_user_id': notif['from_user_id'],
            'from_username': notif['from_username'],
            'post_title': notif['post_title'],
            'is_read': notif['is_read'],
            'created_at': str(notif['created_at'])
        }
        notifications_data.append(notif_dict)
    
    return jsonify({
        'success': True,
        'notifications': notifications_data,
        'unread_count': unread_count
    })

@app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_as_read(notification_id):
    """标记通知为已读"""
    current_user = get_current_user()
    
    if not current_user:
        return jsonify({
            'success': False,
            'message': '请先登录'
        }), 401
    
    success = db.mark_notification_read(notification_id, current_user['id'])
    
    if success:
        return jsonify({
            'success': True,
            'message': '已标记为已读'
        })
    else:
        return jsonify({
            'success': False,
            'message': '标记失败'
        }), 400

@app.route('/api/notifications/mark-read', methods=['POST'])
def mark_all_notifications_read():
    """标记所有通知为已读"""
    current_user = get_current_user()
    
    if not current_user:
        return jsonify({
            'success': False,
            'message': '请先登录'
        }), 401
    
    success = db.mark_all_notifications_read(current_user['id'])
    
    return jsonify({
        'success': True,
        'message': '已标记所有通知为已读'
    })

@app.route('/create', methods=['GET', 'POST'])
@require_login
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form.get('author', '匿名')
        
        if not title or not content:
            flash('标题和内容不能为空！')
            current_user = get_current_user()
            return render_template('create.html', current_user=current_user)
        
        current_user = get_current_user()
        post_id = db.create_post(title, content, author, current_user['id'])
        flash('文章创建成功！')
        return redirect(url_for('view_post', post_id=post_id))
    
    current_user = get_current_user()
    return render_template('create.html', current_user=current_user)

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@require_login
def edit_post(post_id):
    post = db.get_post_by_id(post_id)
    if not post:
        flash('文章不存在！')
        return redirect(url_for('index'))
    
    # 检查权限
    current_user = get_current_user()
    if post['user_id'] != current_user['id'] and not current_user.get('is_admin'):
        flash('您没有权限编辑这篇文章！')
        return redirect(url_for('view_post', post_id=post_id))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if not title or not content:
            flash('标题和内容不能为空！')
            return render_template('edit.html', post=post, current_user=current_user)
        
        db.update_post(post_id, title, content, current_user['id'])
        flash('文章更新成功！')
        return redirect(url_for('view_post', post_id=post_id))
    
    return render_template('edit.html', post=post, current_user=current_user)

@app.route('/delete/<int:post_id>')
@require_login
def delete_post(post_id):
    post = db.get_post_by_id(post_id)
    if post:
        # 检查权限
        current_user = get_current_user()
        if post['user_id'] != current_user['id'] and not current_user.get('is_admin'):
            flash('您没有权限删除这篇文章！')
            return redirect(url_for('view_post', post_id=post_id))
            
        db.delete_post(post_id)
        flash('文章删除成功！')
    else:
        flash('文章不存在！')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.verify_user(username, password)
        if user:
            session_token = db.create_session(user['id'])
            session['session_token'] = session_token
            
            response = make_response(redirect(url_for('index')))
            response.set_cookie('session_token', session_token, 
                              expires=datetime.now() + timedelta(days=7),
                              httponly=True, secure=False)
            flash(f'欢迎回来，{user["username"]}！')
            return response
        else:
            flash('用户名或密码错误！')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email', '')
        
        if len(username) < 3:
            flash('用户名至少需要3个字符！')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('密码至少需要6个字符！')
            return render_template('register.html')
        
        user_id = db.create_user(username, password, email)
        if user_id:
            flash('注册成功！请登录。')
            return redirect(url_for('login'))
        else:
            flash('用户名已存在！')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session_token = session.get('session_token')
    if session_token:
        db.delete_session(session_token)
    
    session.clear()
    
    response = make_response(redirect(url_for('index')))
    response.set_cookie('session_token', '', expires=0)
    flash('已成功退出登录！')
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)