import sqlite3
from datetime import datetime
import hashlib

class Database:
    def __init__(self, db_name='blog.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                register_ip TEXT,
                last_login_ip TEXT,
                last_login_at TIMESTAMP,
                nickname TEXT,
                bio TEXT
            )
        ''')
        
        # 创建会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 创建文章表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                author TEXT NOT NULL DEFAULT '匿名',
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                view_count INTEGER DEFAULT 0,
                is_pinned BOOLEAN DEFAULT FALSE,
                allow_comments BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 创建点赞表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(post_id, user_id, ip_address)
            )
        ''')
        
        # 创建评论表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                parent_id INTEGER,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                like_count INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                FOREIGN KEY (post_id) REFERENCES posts (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (parent_id) REFERENCES comments (id) ON DELETE CASCADE
            )
        ''')
        
        # 创建通知表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                comment_id INTEGER,
                post_id INTEGER,
                from_user_id INTEGER,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (comment_id) REFERENCES comments (id) ON DELETE CASCADE,
                FOREIGN KEY (post_id) REFERENCES posts (id),
                FOREIGN KEY (from_user_id) REFERENCES users (id)
            )
        ''')
        
        # 创建底部导航表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS footer_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link_text TEXT NOT NULL,
                url TEXT NOT NULL,
                new_tab BOOLEAN DEFAULT FALSE,
                sort_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password, email=None):
        """创建新用户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            ''', (username, password_hash, email))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def verify_user(self, username, password):
        """验证用户登录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT id, username, email, is_admin FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def create_session(self, user_id):
        """创建用户会话"""
        import secrets
        import datetime as dt
        
        conn = self.get_connection()
        cursor = conn.cursor()
        session_token = secrets.token_hex(32)
        expires_at = dt.datetime.now() + dt.timedelta(days=7)
        
        cursor.execute('''
            INSERT INTO sessions (user_id, session_token, expires_at)
            VALUES (?, ?, ?)
        ''', (user_id, session_token, expires_at))
        conn.commit()
        conn.close()
        return session_token
    
    def verify_session(self, session_token):
        """验证会话"""
        import datetime as dt
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.is_admin, u.is_active,
                   u.register_ip, u.last_login_ip, u.last_login_at
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = ? AND s.expires_at > ?
        ''', (session_token, dt.datetime.now()))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def delete_session(self, session_token):
        """删除会话"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
        conn.commit()
        conn.close()
    
    def create_post(self, title, content, author='匿名', user_id=None, allow_comments=True):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO posts (title, content, author, user_id, allow_comments)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, author, user_id, allow_comments))
        conn.commit()
        post_id = cursor.lastrowid
        conn.close()
        return post_id
    
    def get_posts_paginated(self, offset, limit):
        """分页获取文章"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, u.username as author_name 
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        posts = cursor.fetchall()
        conn.close()
        return posts
    
    def get_post_likes_count(self, post_id):
        """获取文章点赞数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM likes WHERE post_id = ?', (post_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def like_post(self, post_id, user_id=None, ip_address=None):
        """点赞文章"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 检查是否已点赞（需要特殊处理 NULL 值）
        if user_id is None:
            # 未登录用户，只根据 IP 判断
            cursor.execute('''
                SELECT id FROM likes 
                WHERE post_id = ? AND user_id IS NULL AND ip_address = ?
            ''', (post_id, ip_address))
        else:
            # 登录用户，根据用户 ID 判断
            cursor.execute('''
                SELECT id FROM likes 
                WHERE post_id = ? AND user_id = ? AND ip_address = ?
            ''', (post_id, user_id, ip_address))
        
        existing_like = cursor.fetchone()
        
        if existing_like:
            # 已点赞，取消点赞
            cursor.execute('DELETE FROM likes WHERE id = ?', (existing_like[0],))
            conn.commit()
            conn.close()
            return False  # 取消点赞
        else:
            # 点赞
            cursor.execute('INSERT INTO likes (post_id, user_id, ip_address) VALUES (?, ?, ?)',
                          (post_id, user_id, ip_address))
            conn.commit()
            conn.close()
            return True  # 点赞成功
    
    def has_liked_post(self, post_id, user_id=None, ip_address=None):
        """检查用户是否已点赞"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 特殊处理 NULL 值
        if user_id is None:
            # 未登录用户，只根据 IP 判断
            cursor.execute('''
                SELECT id FROM likes 
                WHERE post_id = ? AND user_id IS NULL AND ip_address = ?
            ''', (post_id, ip_address))
        else:
            # 登录用户，根据用户 ID 判断
            cursor.execute('''
                SELECT id FROM likes 
                WHERE post_id = ? AND user_id = ? AND ip_address = ?
            ''', (post_id, user_id, ip_address))
        
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_post_by_id(self, post_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, u.username as author_name 
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.id = ?
        ''', (post_id,))
        post = cursor.fetchone()
        conn.close()
        return post
    
    def increment_view_count(self, post_id):
        """增加文章浏览次数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE posts 
            SET view_count = view_count + 1 
            WHERE id = ?
        ''', (post_id,))
        conn.commit()
        conn.close()
    
    def get_view_count(self, post_id):
        """获取文章浏览次数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT view_count FROM posts WHERE id = ?', (post_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    
    def update_post(self, post_id, title, content, user_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if user_id:
            cursor.execute('''
                UPDATE posts 
                SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP, user_id = ?
                WHERE id = ?
            ''', (title, content, user_id, post_id))
        else:
            cursor.execute('''
                UPDATE posts 
                SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (title, content, post_id))
        conn.commit()
        conn.close()
    
    def delete_post(self, post_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()
    
    # ========== 评论相关方法 ==========
    
    def create_comment(self, post_id, user_id, content, parent_id=None):
        """创建评论"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 计算 level
        level = 1
        if parent_id:
            cursor.execute('SELECT level FROM comments WHERE id = ?', (parent_id,))
            parent_level = cursor.fetchone()
            if parent_level:
                # 父评论是 level 1，子评论就是 level 2
                # 父评论是 level 2 或更高，子评论也是 level 2（扁平显示）
                level = 2 if parent_level[0] >= 1 else parent_level[0] + 1
        
        cursor.execute('''
            INSERT INTO comments (post_id, user_id, parent_id, content, level)
            VALUES (?, ?, ?, ?, ?)
        ''', (post_id, user_id, parent_id, content, level))
        conn.commit()
        comment_id = cursor.lastrowid
        conn.close()
        return comment_id
    
    def get_comments_by_post(self, post_id):
        """获取文章的所有评论（带用户信息）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, u.username, u.email
            FROM comments c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.post_id = ?
            ORDER BY c.created_at DESC
        ''', (post_id,))
        comments = cursor.fetchall()
        conn.close()
        return comments
    
    def get_comment_tree(self, post_id):
        """构建评论树（所有 level 2 的评论都作为父评论的回复）"""
        comments = self.get_comments_by_post(post_id)
        
        # 分离父评论和子评论
        parent_comments = []
        reply_map = {}
        
        for comment in comments:
            comment_dict = dict(comment)
            if comment['parent_id'] is None:
                # 父评论（level 1）
                parent_comments.append(comment_dict)
            else:
                # 子评论（level 2 或 level 3）
                # 查找被回复的用户名
                parent_comment = next((c for c in comments if c['id'] == comment['parent_id']), None)
                if parent_comment:
                    comment_dict['reply_to_username'] = parent_comment['username']
                    
                    # 如果是 level 3（回复 level 2），找到它的祖父评论（level 1）
                    actual_parent_id = comment['parent_id']
                    if parent_comment['parent_id']:  # 父评论本身也是子评论
                        actual_parent_id = parent_comment['parent_id']
                    
                    if actual_parent_id not in reply_map:
                        reply_map[actual_parent_id] = []
                    reply_map[actual_parent_id].append(comment_dict)
        
        # 将回复附加到父评论
        for parent in parent_comments:
            parent['replies'] = reply_map.get(parent['id'], [])
        
        return parent_comments
    
    def delete_comment(self, comment_id, user_id, is_admin=False):
        """删除评论（支持级联删除回复）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 检查权限
        cursor.execute('SELECT user_id FROM comments WHERE id = ?', (comment_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False
        
        # 只有评论作者或管理员可以删除
        if result[0] != user_id and not is_admin:
            conn.close()
            return False
        
        # 删除评论及其所有回复
        cursor.execute('DELETE FROM comments WHERE id = ? OR parent_id = ?', (comment_id, comment_id))
        conn.commit()
        conn.close()
        return True
    
    # ========== 通知相关方法 ==========
    
    def create_notification(self, user_id, type, comment_id=None, post_id=None, from_user_id=None):
        """创建通知"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (user_id, type, comment_id, post_id, from_user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, type, comment_id, post_id, from_user_id))
        conn.commit()
        notification_id = cursor.lastrowid
        conn.close()
        return notification_id
    
    def get_user_notifications(self, user_id):
        """获取用户的通知列表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT n.*, u.username as from_username, p.title as post_title
            FROM notifications n
            LEFT JOIN users u ON n.from_user_id = u.id
            LEFT JOIN posts p ON n.post_id = p.id
            WHERE n.user_id = ?
            ORDER BY n.created_at DESC
            LIMIT 50
        ''', (user_id,))
        notifications = cursor.fetchall()
        conn.close()
        return notifications
    
    def mark_notification_read(self, notification_id, user_id):
        """标记通知为已读"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE notifications 
            SET is_read = TRUE 
            WHERE id = ? AND user_id = ?
        ''', (notification_id, user_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    def get_unread_notification_count(self, user_id):
        """获取未读通知数量"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = FALSE', (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def mark_all_notifications_read(self, user_id):
        """标记所有通知为已读"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE notifications 
            SET is_read = TRUE 
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    # ========== 后台管理相关方法 ==========
    
    def get_all_users(self, page=1, per_page=20):
        """获取所有用户列表（分页）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        offset = (page - 1) * per_page
        cursor.execute('''
            SELECT id, username, email, created_at, is_admin, is_active,
                   register_ip, last_login_ip, last_login_at
            FROM users
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        users = cursor.fetchall()
        conn.close()
        return users
    
    def get_user_count(self):
        """获取用户总数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def update_user_role(self, user_id, is_admin):
        """修改用户角色"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET is_admin = ? WHERE id = ?
        ''', (is_admin, user_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    def toggle_user_active(self, user_id):
        """切换用户启用状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET is_active = NOT is_active WHERE id = ?
        ''', (user_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    def get_all_posts(self, page=1, per_page=20):
        """获取所有文章列表（分页）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        offset = (page - 1) * per_page
        cursor.execute('''
            SELECT p.*, u.username as author_name,
                   (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) as comment_count
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            ORDER BY p.is_pinned DESC, p.created_at DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        posts = cursor.fetchall()
        conn.close()
        return posts
    
    def get_post_count(self):
        """获取文章总数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM posts')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def toggle_post_pinned(self, post_id):
        """切换文章置顶状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE posts SET is_pinned = NOT is_pinned WHERE id = ?
        ''', (post_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    def update_user_login_info(self, user_id, ip_address):
        """更新用户登录信息"""
        import datetime as dt
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET last_login_ip = ?, last_login_at = ?
            WHERE id = ?
        ''', (ip_address, dt.datetime.now(), user_id))
        conn.commit()
        conn.close()
    
    def update_user_register_ip(self, user_id, ip_address):
        """更新用户注册 IP"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET register_ip = ? WHERE id = ?
        ''', (ip_address, user_id))
        conn.commit()
        conn.close()
    
    # ========== 底部导航相关方法 ==========
    
    def get_footer_links(self):
        """获取所有底部导航链接"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM footer_links
            WHERE is_active = TRUE
            ORDER BY sort_order, created_at
        ''')
        links = cursor.fetchall()
        conn.close()
        return links
    
    def get_all_footer_links(self):
        """获取所有底部导航链接（包括未激活的，用于管理）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM footer_links
            ORDER BY sort_order, created_at
        ''')
        links = cursor.fetchall()
        conn.close()
        return links
    
    def create_footer_link(self, link_text, url, new_tab=False, sort_order=0):
        """创建底部导航链接"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO footer_links (link_text, url, new_tab, sort_order)
            VALUES (?, ?, ?, ?)
        ''', (link_text, url, new_tab, sort_order))
        conn.commit()
        link_id = cursor.lastrowid
        conn.close()
        return link_id
    
    def update_footer_link(self, link_id, link_text, url, new_tab, sort_order, is_active):
        """更新底部导航链接"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE footer_links 
            SET link_text = ?, url = ?, new_tab = ?, sort_order = ?, is_active = ?
            WHERE id = ?
        ''', (link_text, url, new_tab, sort_order, is_active, link_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    def delete_footer_link(self, link_id):
        """删除底部导航链接"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM footer_links WHERE id = ?', (link_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    # ========== 个人中心相关方法 ==========
    
    def get_user_profile(self, user_id):
        """获取用户资料"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, email, nickname, bio, created_at, is_admin
            FROM users
            WHERE id = ?
        ''', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def update_user_profile(self, user_id, nickname, bio):
        """更新用户资料"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET nickname = ?, bio = ?
            WHERE id = ?
        ''', (nickname, bio, user_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    def get_user_posts(self, user_id, page=1, per_page=10):
        """获取用户的文章列表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        offset = (page - 1) * per_page
        cursor.execute('''
            SELECT p.*, u.username as author_name
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.user_id = ?
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        ''', (user_id, per_page, offset))
        posts = cursor.fetchall()
        conn.close()
        return [dict(post) for post in posts]
    
    def get_user_post_count(self, user_id):
        """获取用户文章总数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM posts WHERE user_id = ?', (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_user_comments(self, user_id, page=1, per_page=20):
        """获取用户的评论列表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        offset = (page - 1) * per_page
        cursor.execute('''
            SELECT c.*, p.title as post_title, p.id as post_id,
                   u.username as reply_to_username
            FROM comments c
            JOIN posts p ON c.post_id = p.id
            LEFT JOIN comments parent_comment ON c.parent_id = parent_comment.id
            LEFT JOIN users u ON parent_comment.user_id = u.id
            WHERE c.user_id = ?
            ORDER BY c.created_at DESC
            LIMIT ? OFFSET ?
        ''', (user_id, per_page, offset))
        comments = cursor.fetchall()
        conn.close()
        return [dict(comment) for comment in comments]
    
    def get_user_comment_count(self, user_id):
        """获取用户评论总数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM comments WHERE user_id = ?', (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_all_comments(self, page=1, per_page=20):
        """获取所有评论列表（后台管理用）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        offset = (page - 1) * per_page
        cursor.execute('''
            SELECT c.*, u.username as author_name, p.title as post_title, p.id as post_id
            FROM comments c
            JOIN users u ON c.user_id = u.id
            JOIN posts p ON c.post_id = p.id
            ORDER BY c.created_at DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        comments = cursor.fetchall()
        conn.close()
        return [dict(comment) for comment in comments]
    
    def get_comment_count(self):
        """获取评论总数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM comments')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_comment_by_id(self, comment_id):
        """根据 ID 获取评论"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM comments WHERE id = ?
        ''', (comment_id,))
        comment = cursor.fetchone()
        conn.close()
        return dict(comment) if comment else None

# 初始化数据库
db = Database()