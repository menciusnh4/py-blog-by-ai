"""
后台管理系统数据库迁移脚本
添加以下功能：
1. 用户表新增字段：is_active, register_ip, last_login_ip, last_login_at
2. 文章表新增字段：is_pinned
3. 创建底部导航表：footer_links
"""

import sqlite3

db_name = 'blog.db'
conn = sqlite3.connect(db_name)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

print("=" * 60)
print("后台管理系统数据库迁移")
print("=" * 60)

# ========== 1. 修改用户表 ===========
print("\n1. 扩展用户表...")

# 检查字段是否存在
cursor.execute("PRAGMA table_info(users)")
users_columns = [col[1] for col in cursor.fetchall()]

# 添加 is_active 字段
if 'is_active' not in users_columns:
    print("   - 添加 is_active 字段...")
    cursor.execute('''
        ALTER TABLE users 
        ADD COLUMN is_active BOOLEAN DEFAULT TRUE
    ''')
else:
    print("   ✓ is_active 字段已存在")

# 添加 register_ip 字段
if 'register_ip' not in users_columns:
    print("   - 添加 register_ip 字段...")
    cursor.execute('''
        ALTER TABLE users 
        ADD COLUMN register_ip TEXT
    ''')
else:
    print("   ✓ register_ip 字段已存在")

# 添加 last_login_ip 字段
if 'last_login_ip' not in users_columns:
    print("   - 添加 last_login_ip 字段...")
    cursor.execute('''
        ALTER TABLE users 
        ADD COLUMN last_login_ip TEXT
    ''')
else:
    print("   ✓ last_login_ip 字段已存在")

# 添加 last_login_at 字段
if 'last_login_at' not in users_columns:
    print("   - 添加 last_login_at 字段...")
    cursor.execute('''
        ALTER TABLE users 
        ADD COLUMN last_login_at TIMESTAMP
    ''')
else:
    print("   ✓ last_login_at 字段已存在")

conn.commit()
print("✅ 用户表扩展完成")

# ========== 2. 修改文章表 ===========
print("\n2. 扩展文章表...")

cursor.execute("PRAGMA table_info(posts)")
posts_columns = [col[1] for col in cursor.fetchall()]

# 添加 is_pinned 字段
if 'is_pinned' not in posts_columns:
    print("   - 添加 is_pinned 字段...")
    cursor.execute('''
        ALTER TABLE posts 
        ADD COLUMN is_pinned BOOLEAN DEFAULT FALSE
    ''')
else:
    print("   ✓ is_pinned 字段已存在")

conn.commit()
print("✅ 文章表扩展完成")

# ========== 3. 创建底部导航表 ===========
print("\n3. 创建底部导航表...")

cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='footer_links'
""")
if not cursor.fetchone():
    print("   - 创建 footer_links 表...")
    cursor.execute('''
        CREATE TABLE footer_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link_text TEXT NOT NULL,
            url TEXT NOT NULL,
            new_tab BOOLEAN DEFAULT FALSE,
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 插入默认链接
    print("   - 插入默认链接...")
    default_links = [
        ('关于我们', '/about', False, 0),
        ('联系方式', '/contact', False, 1),
        ('隐私政策', '/privacy', False, 2),
    ]
    
    for link_text, url, new_tab, sort_order in default_links:
        cursor.execute('''
            INSERT INTO footer_links (link_text, url, new_tab, sort_order)
            VALUES (?, ?, ?, ?)
        ''', (link_text, url, new_tab, sort_order))
else:
    print("   ✓ footer_links 表已存在")

conn.commit()
print("✅ 底部导航表创建完成")

# ========== 验证结果 ===========
print("\n4. 验证迁移结果...")

# 验证用户表字段
cursor.execute("PRAGMA table_info(users)")
users_columns = [col[1] for col in cursor.fetchall()]
required_user_columns = ['is_active', 'register_ip', 'last_login_ip', 'last_login_at']
missing_user_columns = [col for col in required_user_columns if col not in users_columns]

if missing_user_columns:
    print(f"   ❌ 用户表缺少字段：{missing_user_columns}")
else:
    print("   ✅ 用户表字段完整")

# 验证文章表字段
cursor.execute("PRAGMA table_info(posts)")
posts_columns = [col[1] for col in cursor.fetchall()]
if 'is_pinned' in posts_columns:
    print("   ✅ 文章表字段完整")
else:
    print("   ❌ 文章表缺少 is_pinned 字段")

# 验证底部导航表
cursor.execute("SELECT COUNT(*) FROM footer_links")
link_count = cursor.fetchone()[0]
print(f"   ✅ 底部导航链接数量：{link_count}")

conn.close()

print("\n" + "=" * 60)
print("迁移完成！")
print("=" * 60)
print("\n新增功能:")
print("✅ 用户启用/禁用控制")
print("✅ 用户注册 IP 记录")
print("✅ 用户最后登录 IP 和时间记录")
print("✅ 文章置顶功能")
print("✅ 底部导航配置管理")
print("\n下一步:")
print("1. 重启 Flask 应用")
print("2. 使用管理员账号登录")
print("3. 点击右上角的'⚙️ 后台'按钮进入后台管理")
print("=" * 60)
