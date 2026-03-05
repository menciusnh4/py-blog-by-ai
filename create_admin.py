from models import db

# 创建管理员账户
admin_username = "admin"
admin_password = "admin123"
admin_email = "admin@geekblog.com"

print("正在创建管理员账户...")
user_id = db.create_user(admin_username, admin_password, admin_email)

if user_id:
    print("[OK] 管理员账户创建成功！")
    print(f"用户名: {admin_username}")
    print(f"密码: {admin_password}")
    print(f"邮箱: {admin_email}")
else:
    print("[ERROR] 管理员账户已存在或创建失败")

print("")
print("[INFO] 使用说明:")
print("- 访问登录页面: http://127.0.0.1:5000/login")
print("- 访问注册页面: http://127.0.0.1:5000/register")
print("- 默认管理员账户已创建，可以直接登录测试")