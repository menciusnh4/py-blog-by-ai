"""
后台管理系统快速验证脚本
检查所有功能是否正常工作
"""

import sqlite3

db_name = 'blog.db'
conn = sqlite3.connect(db_name)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 70)
print("后台管理系统功能验证")
print("=" * 70)

# ========== 1. 检查数据库表结构 ==========
print("\n【1】数据库表结构检查")

# 检查 users 表字段
cursor.execute("PRAGMA table_info(users)")
users_columns = [col[1] for col in cursor.fetchall()]
required_user_columns = ['id', 'username', 'email', 'is_admin', 'is_active', 
                         'register_ip', 'last_login_ip', 'last_login_at']

print("\n用户表字段:")
for col in required_user_columns:
    status = "✅" if col in users_columns else "❌"
    print(f"   {status} {col}")

# 检查 posts 表字段
cursor.execute("PRAGMA table_info(posts)")
posts_columns = [col[1] for col in cursor.fetchall()]
required_post_columns = ['id', 'title', 'content', 'user_id', 'view_count', 'is_pinned']

print("\n文章表字段:")
for col in required_post_columns:
    status = "✅" if col in posts_columns else "❌"
    print(f"   {status} {col}")

# 检查 footer_links 表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='footer_links'")
has_footer_links = cursor.fetchone() is not None
print(f"\n底部导航表: {'✅ 存在' if has_footer_links else '❌ 不存在'}")

# ========== 2. 检查管理员账号 ==========
print("\n【2】管理员账号检查")
cursor.execute("SELECT id, username, email, is_admin, is_active FROM users WHERE is_admin = TRUE")
admins = cursor.fetchall()
print(f"管理员数量：{len(admins)}")
for admin in admins:
    print(f"   - ID: {admin['id']}, 用户名：{admin['username']}, 邮箱：{admin['email'] or '-'}")

# ========== 3. 检查普通用户 ==========
print("\n【3】普通用户检查")
cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_admin = FALSE")
user_count = cursor.fetchone()['count']
print(f"普通用户数量：{user_count}")

# ========== 4. 检查 IP 记录 ==========
print("\n【4】IP 地址记录检查")
cursor.execute("""
    SELECT id, username, register_ip, last_login_ip, last_login_at 
    FROM users 
    WHERE register_ip IS NOT NULL OR last_login_ip IS NOT NULL
    LIMIT 5
""")
users_with_ip = cursor.fetchall()
if users_with_ip:
    print(f"已记录 IP 的用户：{len(users_with_ip)}")
    for user in users_with_ip:
        reg_ip = user['register_ip'] or '未记录'
        login_ip = user['last_login_ip'] or '未登录'
        print(f"   - {user['username']}: 注册 IP={reg_ip}, 最后登录 IP={login_ip}")
else:
    print("   暂无 IP 记录（需要用户登录或注册）")

# ========== 5. 检查文章置顶状态 ==========
print("\n【5】文章置顶功能检查")
cursor.execute("SELECT COUNT(*) as count FROM posts WHERE is_pinned = TRUE")
pinned_count = cursor.fetchone()['count']
print(f"已置顶文章：{pinned_count}")

cursor.execute("SELECT COUNT(*) as count FROM posts")
total_posts = cursor.fetchone()['count']
print(f"文章总数：{total_posts}")

# ========== 6. 检查底部导航链接 ==========
print("\n【6】底部导航链接检查")
cursor.execute("SELECT id, link_text, url, new_tab, sort_order FROM footer_links ORDER BY sort_order")
links = cursor.fetchall()
if links:
    print(f"导航链接数量：{len(links)}")
    for link in links:
        new_tab_str = "新窗口" if link['new_tab'] else "当前窗口"
        print(f"   - {link['link_text']} → {link['url']} ({new_tab_str}) [排序:{link['sort_order']}]")
else:
    print("   暂无导航链接（可在后台管理中添加）")

# ========== 7. 权限控制检查 ==========
print("\n【7】权限控制检查")
cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_admin = TRUE AND is_active = TRUE")
active_admins = cursor.fetchone()['count']
print(f"活跃管理员：{active_admins}")

cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_active = FALSE")
disabled_users = cursor.fetchone()['count']
print(f"被禁用的用户：{disabled_users}")

conn.close()

# ========== 总结 ==========
print("\n" + "=" * 70)
print("验证完成！")
print("=" * 70)

# 判断是否可以正常使用
issues = []
if active_admins == 0:
    issues.append("⚠️ 没有活跃的管理员账号，请先创建管理员")
if not has_footer_links:
    issues.append("⚠️ footer_links 表不存在，请运行迁移脚本")

if issues:
    print("\n发现问题:")
    for issue in issues:
        print(f"   {issue}")
    print("\n建议操作:")
    if "没有活跃的管理员账号" in str(issues):
        print("   1. 运行：python create_admin.py 创建管理员")
    if "footer_links 表不存在" in str(issues):
        print("   2. 运行：python migrate_admin.py 执行数据库迁移")
else:
    print("\n✅ 所有功能正常！")
    print("\n使用步骤:")
    print("   1. 启动应用：python app.py")
    print("   2. 使用管理员账号登录")
    print("   3. 点击右上角的'⚙️ 后台'按钮")
    print("   4. 开始使用后台管理功能")

print("\n后台管理功能列表:")
print("   📊 仪表盘：/admin")
print("   👥 用户管理：/admin/users")
print("   📝 文章管理：/admin/posts")
print("   🔗 底部导航：/admin/footer-links")
print("=" * 70)
