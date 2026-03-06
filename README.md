# 我的博客网站

这是一个使用Python Flask框架开发的简洁美观的博客网站，采用SQLite数据库存储数据。

## 功能特性

- ✨ 现代化响应式设计
- 📝 完整的文章管理功能（增删改查）
- 🎨 优美的 UI 界面
- 📱 移动端适配
- 🔧 简单易用的部署方式
- 💬 完整的评论系统（支持嵌套回复）
- 🔔 通知功能（评论回复提醒）
- 🌙 暗黑模式切换
- ❤️ 点赞功能（支持匿名）
- 👤 用户系统与管理员权限
- 🏠 个人中心（资料编辑、文章管理、评论管理）
- 🔒 文章评论开关控制
- 📊 后台管理系统（用户、文章、评论、导航管理）

## 技术栈

- **后端**: Python 3.12 + Flask
- **数据库**: SQLite
- **前端**: HTML5 + CSS3 + JavaScript
- **模板引擎**: Jinja2

## 快速开始

### 1. 克隆项目
```bash
git clone <项目地址>
cd blog_project
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行应用
```bash
python app.py
```

### 4. 访问网站
打开浏览器访问: http://localhost:5000

## 项目结构

```
blog_project/
├── app.py              # Flask 主应用文件
├── models.py           # 数据库模型
├── add_allow_comments_field.py  # 数据库迁移脚本
├── create_admin.py     # 创建管理员账号
├── requirements.txt    # 依赖包列表
├── blog.db            # SQLite 数据库文件
├── README.md          # 项目文档
├── templates/         # HTML 模板文件
│   ├── base.html      # 基础模板
│   ├── index.html     # 首页模板
│   ├── post.html      # 文章详情模板
│   ├── create.html    # 创作文章模板
│   ├── edit.html      # 编辑文章模板
│   ├── login.html     # 登录页面
│   ├── register.html  # 注册页面
│   ├── loading.html   # 加载页面
│   └── profile/       # 个人中心模板
│       ├── index.html     # 个人资料
│       ├── posts.html     # 我的文章
│       └── comments.html  # 我的评论
│   └── admin_new/     # 后台管理模板
│       ├── base.html      # 管理基础模板
│       ├── dashboard.html # 仪表盘
│       ├── users.html     # 用户管理
│       ├── posts.html     # 文章管理
│       ├── comments.html  # 评论管理
│       └── footer_links.html # 底部导航管理
└── static/            # 静态资源文件
    ├── css/
    │   ├── style.css      # 主样式
    │   ├── dark_mode.css  # 暗黑模式
    │   ├── effects.css    # 特效样式
    │   └── font-fix.css   # 字体修复
    └── js/
        ├── main.js        # 主 JavaScript 文件
        └── cleanup_mouse.js # 清理鼠标效果
```

## 使用说明

### 创建文章
1. 点击导航栏的"写文章"按钮
2. 填写文章标题、作者和内容
3. 点击"发布文章"按钮

### 管理文章
- **查看文章**: 点击文章标题或"阅读更多"按钮
- **编辑文章**: 在文章页面点击"编辑文章"按钮
- **删除文章**: 点击"删除文章"按钮确认删除

### 首页功能
- 显示所有文章列表（瀑布流布局）
- 支持文章搜索和筛选
- 每篇文章显示摘要和基本信息
- 无限滚动加载更多

### 文章详情页
- 完整的文章内容展示
- 点赞功能（支持匿名操作）
- 分享功能（复制到剪贴板）
- 评论系统（支持二级嵌套回复）
- 删除权限控制（作者或管理员）

### 评论系统
- 登录用户可发表评论
- 支持回复其他用户的评论
- 评论通知功能
- 字符数限制（1-1000 字）
- 实时字数统计

### 通知功能
- 新评论提醒
- 回复通知
- 未读消息计数
- 一键标记已读
- 下拉列表查看

### 主题切换
- 暗黑模式/浅色模式切换
- 本地存储偏好设置
- 平滑过渡动画

## 自定义配置

### 修改端口
在 `app.py` 文件中修改：
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # 修改port参数
```

### 修改密钥
在 `app.py` 文件中修改：
```python
app.secret_key = 'your-secret-key-here'  # 使用更安全的密钥
```

## 部署建议

### 生产环境部署
```bash
# 安装gunicorn
pip install gunicorn

# 启动应用
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker部署
可以创建Dockerfile进行容器化部署。

## 开发计划

- [x] 用户注册登录功能
- [x] 文章分类和标签
- [x] 评论系统
- [x] 搜索功能
- [x] 文章浏览统计
- [x] Markdown 支持（富文本编辑器）
- [x] 暗黑模式
- [x] 点赞功能
- [x] 通知系统
- [ ] 文章收藏功能
- [ ] 用户个人主页
- [ ] 评论表情包
- [ ] 文章打赏功能

## 常见问题

### 1. 如何创建管理员账号？
```bash
python create_admin.py
```
按照提示输入用户名和密码即可。

### 2. 如何初始化测试数据？
```bash
# 注意：项目已移除测试数据脚本，建议手动创建文章和评论
```

### 3. 数据库迁移
如果数据库缺少字段，运行迁移脚本：
```bash
python add_allow_comments_field.py
```

### 4. 评论系统如何使用？

### 4. 评论系统如何使用？
- 登录后在文章详情页底部发表评论
- 点击"回复"按钮可以回复其他评论
- 评论后对方会收到通知
- 个人中心可查看和管理自己的评论

### 5. 如何控制文章评论开关？
在创作文章时，勾选或取消“允许评论”复选框即可控制该文章是否开放评论。

### 6. 暗黑模式如何切换？

### 7. 数据库在哪里？
数据库文件为 `blog.db`，使用 SQLite 存储。可以使用 SQLite 客户端工具查看和编辑。

## 技术细节

### 后端架构
- **框架**: Flask (Web 框架)
- **ORM**: SQLAlchemy (数据库操作)
- **认证**: Flask-Login (用户会话管理)
- **密码加密**: Werkzeug (密码哈希)

### 前端架构
- **模板引擎**: Jinja2
- **CSS**: 原生 CSS + CSS Variables
- **JavaScript**: 原生 ES6+
- **富文本编辑器**: Quill.js
- **粒子背景**: particles.js

### 数据库设计
主要数据表：
- `users` - 用户表（含昵称、签名、登录信息）
- `posts` - 文章表（含评论开关字段）
- `comments` - 评论表（支持嵌套回复）
- `notifications` - 通知表
- `sessions` - 会话表
- `likes` - 点赞记录表

### API 接口
- `/api/posts/<id>/comments` - 获取文章评论
- `/api/comments` - 创建评论
- `/api/comments/<id>` - 删除评论
- `/api/notifications` - 获取通知
- `/api/notifications/mark-read` - 标记已读
- `/api/like/<post_id>` - 点赞文章
- `/admin/users` - 用户管理（管理员）
- `/admin/posts` - 文章管理（管理员）
- `/admin/comments` - 评论管理（管理员）

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 许可证

MIT License