// 修复主题切换功能 - 安全版本
function updateThemeIcon(isDark) {
    try {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            if (isDark) {
                themeToggle.textContent = '☀️ 浅色';
            } else {
                themeToggle.textContent = '🌙 暗黑';
            }
        }
    } catch (e) {
        console.error('更新主题图标时出错:', e);
    }
}

// 主题切换功能
function initThemeToggle() {
    try {
        const themeToggle = document.getElementById('theme-toggle');
        const html = document.documentElement;
        const body = document.body;
        
        // 检查本地存储的主题设置
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            html.classList.add('dark-mode');
            body.classList.add('dark-mode');
            updateThemeIcon(true);
        }
        
        // 添加点击事件监听器
        if (themeToggle) {
            themeToggle.addEventListener('click', function(e) {
                e.preventDefault();
                try {
                    // 切换主题
                    if (body.classList.contains('dark-mode')) {
                        // 切换到浅色模式
                        html.classList.remove('dark-mode');
                        body.classList.remove('dark-mode');
                        localStorage.setItem('theme', 'light');
                        updateThemeIcon(false);
                    } else {
                        // 切换到暗色模式
                        html.classList.add('dark-mode');
                        body.classList.add('dark-mode');
                        localStorage.setItem('theme', 'dark');
                        updateThemeIcon(true);
                    }
                } catch (error) {
                    console.error('主题切换时出错:', error);
                }
            });
        }
    } catch (e) {
        console.error('初始化主题切换时出错:', e);
    }
}

// 通用点赞功能（支持动态加载的内容）
function initLikeButtons() {
    // 使用事件委托处理所有点赞按钮
    document.addEventListener('click', function(e) {
        const likeBtn = e.target.closest('.like-btn');
        if (!likeBtn) return;
        
        e.preventDefault();
        const postId = likeBtn.getAttribute('data-post-id');
        const countSpan = likeBtn.querySelector('.like-count');
        
        // 发送点赞请求
        fetch(`/api/like/${postId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 根据返回的状态设置按钮样式
                if (data.liked) {
                    // 点赞成功
                    likeBtn.classList.add('liked');
                    likeBtn.style.background = 'linear-gradient(45deg, #ff4757, #ff3742)';
                } else {
                    // 取消点赞
                    likeBtn.classList.remove('liked');
                    likeBtn.style.background = '';
                }
                // 直接使用后端返回的准确数量
                countSpan.textContent = data.count;
            }
        })
        .catch(error => {
            console.error('点赞失败:', error);
            alert('点赞失败，请稍后再试');
        });
    });
}

// 页面加载完成后初始化
window.addEventListener('load', function() {
    try {
        initThemeToggle();
        initLikeButtons();
        initNotifications(); // 初始化通知
        initComments(); // 初始化评论
    } catch (error) {
        console.error('初始化功能时出错:', error);
    }
});

// ========== 通知相关功能 ==========

function initNotifications() {
    const icon = document.getElementById('notification-icon');
    const badge = document.getElementById('notification-badge');
    const dropdown = document.getElementById('notification-dropdown');
    
    // 如果没有通知图标元素，说明用户未登录，不初始化
    if (!icon) return;
    
    // 点击图标显示/隐藏下拉列表
    icon.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleNotificationDropdown();
    });
    
    // 点击页面其他地方关闭下拉列表
    document.addEventListener('click', function() {
        dropdown.style.display = 'none';
    });
    
    // 阻止点击下拉列表时关闭
    dropdown.addEventListener('click', function(e) {
        e.stopPropagation();
    });
    
    // 页面加载时获取一次通知
    loadNotifications();
}

function toggleNotificationDropdown() {
    const dropdown = document.getElementById('notification-dropdown');
    if (dropdown) {
        const isVisible = dropdown.style.display === 'block';
        dropdown.style.display = isVisible ? 'none' : 'block';
        
        if (!isVisible) {
            loadNotifications();
        }
    }
}

async function loadNotifications() {
    try {
        const response = await fetch('/api/notifications', {
            credentials: 'same-origin' // 携带 cookie
        });
        
        // 检查是否未登录（401）
        if (response.status === 401) {
            console.log('用户未登录，跳过通知加载');
            return;
        }
        
        const data = await response.json();
        
        if (data.success) {
            renderNotifications(data.notifications);
            updateNotificationBadge(data.unread_count);
        } else {
            console.log('通知加载失败:', data.message);
        }
    } catch (error) {
        // 静默失败，可能是未登录
        console.log('通知加载失败或用户未登录');
    }
}

function renderNotifications(notifications) {
    const container = document.getElementById('notification-list');
    if (!container) return;
    
    if (notifications.length === 0) {
        container.innerHTML = '<p style="color: rgba(255,255,255,0.6); text-align: center; padding: 20px;">🍃 暂无通知</p>';
        return;
    }
    
    let html = '';
    notifications.forEach(notif => {
        const typeText = notif.type === 'reply' ? '回复了你的评论' : '新通知';
        const timeAgo = formatNotificationTime(notif.created_at);
        const isUnread = !notif.is_read;
        
        html += `
            <div class="notification-item ${isUnread ? 'unread' : ''}" 
                 style="padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); cursor: pointer; transition: all 0.2s ease;" 
                 onclick="viewNotification(${notif.post_id})">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <p style="margin: 0 0 5px 0; color: #fff; font-size: 0.9rem;">
                            <span style="color: #4ecdc4; font-weight: 600;">${escapeHtml(notif.from_username || '某人')}</span>
                            ${typeText}
                        </p>
                        <p style="margin: 0; color: rgba(255,255,255,0.5); font-size: 0.8rem;">
                            文章：${escapeHtml(notif.post_title || '已删除')}
                        </p>
                    </div>
                    <span style="color: rgba(255,255,255,0.4); font-size: 0.75rem;">${timeAgo}</span>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function updateNotificationBadge(count) {
    const badge = document.getElementById('notification-badge');
    if (!badge) return;
    
    if (count > 0) {
        badge.textContent = count > 99 ? '99+' : count;
        badge.style.display = 'inline-block';
    } else {
        badge.style.display = 'none';
    }
}

// 查看通知（跳转到文章详情页）
async function viewNotification(postId) {
    if (postId) {
        // 先标记为已读
        const response = await fetch('/api/notifications/mark-read', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        // 跳转到文章详情页
        window.location.href = `/post/${postId}`;
    }
}

function formatNotificationTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    if (days < 7) return `${days}天前`;
    
    return date.toLocaleDateString('zh-CN');
}

// 工具函数：转义 HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 分享功能
function sharePost() {
    const titleElement = document.querySelector('h1');
    const contentElement = document.querySelector('.post-content');
    
    const title = titleElement ? titleElement.textContent : '文章分享';
    const content = contentElement ? contentElement.textContent.substring(0, 100) + '...' : '';
    const url = window.location.href;
    
    if (navigator.share) {
        navigator.share({
            title: title,
            text: content,
            url: url
        }).catch(error => {
            console.log('分享取消或失败:', error);
        });
    } else {
        navigator.clipboard.writeText(url).then(() => {
            alert('链接已复制到剪贴板！');
        }).catch(error => {
            console.error('复制失败:', error);
            prompt('请手动复制以下链接:', url);
        });
    }
}

// ========== 评论相关功能 ==========

// 页面加载时根据页面类型加载评论
function initComments() {
    // 检查是否存在评论输入框（只在文章详情页）
    const commentContent = document.getElementById('comment-content');
    if (commentContent) {
        // 绑定字符计数事件
        commentContent.addEventListener('input', function() {
            const count = this.value.length;
            const charCurrent = document.getElementById('char-current');
            if (charCurrent) {
                charCurrent.textContent = count;
            }
            
            if (count > 1000) {
                this.style.borderColor = '#ff4757';
            } else {
                this.style.borderColor = '';
            }
        });
        
        // 获取文章 ID 并加载评论
        const postDetail = document.querySelector('.post-detail');
        if (postDetail) {
            const likeBtn = postDetail.querySelector('[data-post-id]');
            if (likeBtn) {
                const postId = likeBtn.getAttribute('data-post-id');
                loadComments(postId);
            }
        }
    }
}

// 发表评论
async function submitComment(postId) {
    const contentInput = document.getElementById('comment-content');
    const content = contentInput.value.trim();
    
    if (!content) {
        alert('评论内容不能为空！');
        return;
    }
    
    if (content.length > 1000) {
        alert('评论内容过长！');
        return;
    }
    
    try {
        const response = await fetch('/api/comments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                post_id: postId,
                content: content
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            contentInput.value = '';
            const charCurrent = document.getElementById('char-current');
            if (charCurrent) {
                charCurrent.textContent = '0';
            }
            loadComments(postId);
        } else {
            alert(data.message || '评论失败');
        }
    } catch (error) {
        console.error('评论失败:', error);
        alert('评论失败，请稍后再试');
    }
}

// 加载评论列表
async function loadComments(postId) {
    try {
        const response = await fetch(`/api/posts/${postId}/comments`);
        const data = await response.json();
        
        if (data.success) {
            renderComments(data.comments);
            const commentCount = document.getElementById('comment-count');
            if (commentCount) {
                commentCount.textContent = data.total;
            }
        }
    } catch (error) {
        console.error('加载评论失败:', error);
    }
}

// 渲染评论
function renderComments(comments) {
    const container = document.getElementById('comments-list');
    if (!container) return;
    
    if (comments.length === 0) {
        container.innerHTML = '<div class="empty-comments"><p>🍃 还没有评论，快来抢沙发吧！</p></div>';
        return;
    }
    
    let html = '';
    comments.forEach(comment => {
        html += renderComment(comment, false);
    });
    
    container.innerHTML = html;
}

// 渲染单条评论
function renderComment(comment, isReply = false) {
    const replies = comment.replies || [];
    
    // 判断当前用户是否有删除权限
    const currentUserId = window.currentUserId;
    const isAdmin = window.isAdmin;
    const canDelete = currentUserId && (parseInt(comment.user_id) === parseInt(currentUserId) || isAdmin);
    
    return `
        <div class="comment-item ${isReply ? 'comment-reply' : ''}" id="comment-${comment.id}">
            <div class="comment-avatar">
                <span class="avatar-icon">👤</span>
            </div>
            <div class="comment-body">
                <div class="comment-header">
                    <span class="comment-author">${escapeHtml(comment.username || '匿名')}</span>
                    ${comment.parent_id && comment.reply_to_username ? `<span style="color: rgba(255,255,255,0.5); font-size: 0.9rem;">回复 ${escapeHtml(comment.reply_to_username)}</span>` : ''}
                    <span class="comment-date">${formatDate(comment.created_at)}</span>
                </div>
                <div class="comment-content">${escapeHtml(comment.content)}</div>
                <div class="comment-actions">
                    <button class="btn-reply" onclick="showReplyForm(${comment.id}, '${escapeHtml(comment.username)}')">
                        💬 回复
                    </button>
                    ${canDelete ? `
                    <button class="btn-delete" data-comment-id="${comment.id}" data-user-id="${comment.user_id}" onclick="checkDeletePermission(this)">🗑️ 删除</button>
                    ` : ''}
                </div>
                
                <!-- 回复表单（隐藏） -->
                <div class="reply-form-container" id="reply-form-${comment.id}" style="display: none;">
                    <textarea id="reply-content-${comment.id}" placeholder="写下你的回复..." rows="3"></textarea>
                    <div class="reply-form-actions">
                        <button class="btn-submit-reply" onclick="submitReply(${comment.id}, ${comment.post_id})">✅ 提交回复</button>
                        <button class="btn-cancel-reply" onclick="cancelReply(${comment.id})">❌ 取消</button>
                    </div>
                </div>
                
                <!-- 回复列表（在父评论内部渲染） -->
                ${!isReply && replies.length > 0 ? `
                    <div class="comment-replies">
                        ${replies.map(reply => renderComment(reply, true)).join('')}
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

// 显示回复表单
function showReplyForm(commentId, username) {
    const form = document.getElementById(`reply-form-${commentId}`);
    if (form) {
        form.style.display = 'block';
        const textarea = document.getElementById(`reply-content-${commentId}`);
        if (textarea) {
            textarea.placeholder = `回复 @${username}...`;
            textarea.focus();
        }
    }
}

// 取消回复
function cancelReply(commentId) {
    const form = document.getElementById(`reply-form-${commentId}`);
    if (form) {
        form.style.display = 'none';
        const textarea = document.getElementById(`reply-content-${commentId}`);
        if (textarea) {
            textarea.value = '';
        }
    }
}

// 提交回复
async function submitReply(parentCommentId, postId) {
    const contentInput = document.getElementById(`reply-content-${parentCommentId}`);
    const content = contentInput.value.trim();
    
    if (!content) {
        alert('回复内容不能为空！');
        return;
    }
    
    try {
        const response = await fetch('/api/comments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                post_id: postId,
                content: content,
                parent_id: parentCommentId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            contentInput.value = '';
            cancelReply(parentCommentId);
            await loadComments(postId);
        } else {
            alert(data.message || '回复失败');
        }
    } catch (error) {
        console.error('回复失败:', error);
        alert('回复失败，请稍后再试');
    }
}

// 删除评论
async function deleteComment(commentId, postId) {
    console.log('准备删除评论:', { commentId, postId });
    
    if (!confirm('确定要删除这条评论吗？')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/comments/${commentId}`, {
            method: 'DELETE'
        });
        
        console.log('删除评论响应:', response.status);
        
        const data = await response.json();
        console.log('删除评论结果:', data);
        
        if (data.success) {
            alert('评论已删除');
            loadComments(postId);
        } else {
            alert(data.message || '删除失败');
        }
    } catch (error) {
        console.error('删除失败:', error);
        alert('删除失败，请稍后再试');
    }
}

// 检查删除权限
function checkDeletePermission(button) {
    const commentId = button.getAttribute('data-comment-id');
    const commentUserId = button.getAttribute('data-user-id');
    
    // 从全局变量获取当前用户信息
    const currentUserId = window.currentUserId;
    const isAdmin = window.isAdmin;
    
    console.log('检查删除权限:', {
        commentId,
        commentUserId,
        currentUserId,
        isAdmin
    });
    
    // 类型转换后比较
    if (parseInt(commentUserId) === parseInt(currentUserId) || isAdmin) {
        // 从页面中获取文章 ID
        const likeBtn = document.querySelector('[data-post-id]');
        const postId = likeBtn ? likeBtn.getAttribute('data-post-id') : null;
        
        console.log('文章 ID:', postId);
        
        if (postId) {
            deleteComment(commentId, postId);
        } else {
            alert('无法获取文章 ID，删除失败');
        }
    } else {
        console.log('权限不足：评论作者 ID=', commentUserId, '当前用户 ID=', currentUserId);
        alert('您没有权限删除此评论！');
    }
}

// 工具函数：格式化日期
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    if (days < 7) return `${days}天前`;
    
    return date.toLocaleDateString('zh-CN');
}