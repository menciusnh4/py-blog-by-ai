from models import db

# 获取管理员用户ID
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT id FROM users WHERE username = 'admin'")
admin_user = cursor.fetchone()
admin_id = admin_user['id'] if admin_user else None
conn.close()

# 创建一些测试文章
test_posts = [
    {
        'title': '欢迎来到我的博客',
        'content': '''这是我博客的第一篇文章！

在这里我会分享我的技术心得、生活感悟和学习笔记。

希望你能喜欢这里的内容，也欢迎留言交流！

让我们一起在这个数字世界里留下美好的印记。''',
        'author': '博主',
        'user_id': admin_id
    },
    {
        'title': 'Python编程之美',
        'content': '''Python是一门优雅的编程语言。

它的设计理念强调代码的可读性和简洁性。
- 语法简洁明了
- 生态系统丰富
- 学习曲线平缓

无论是数据分析、Web开发还是人工智能，Python都有着广泛的应用场景。''',
        'author': '技术分享者',
        'user_id': admin_id
    },
    {
        'title': '生活需要仪式感',
        'content': '''在这个快节奏的时代，
我们常常忽略了生活中那些美好的细节。

一杯咖啡的香气，
一本书的陪伴，
一次深度的思考，

这些看似平凡的时刻，
其实都是生活的馈赠。

让我们慢下来，
用心感受每一个当下。''',
        'author': '生活观察者',
        'user_id': admin_id
    }
]

# 插入测试数据
for post in test_posts:
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO posts (title, content, author, user_id)
        VALUES (?, ?, ?, ?)
    ''', (post['title'], post['content'], post['author'], post['user_id']))
    conn.commit()
    conn.close()

print("测试数据创建完成！")