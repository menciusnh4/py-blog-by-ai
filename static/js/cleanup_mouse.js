// 清理鼠标跟踪效果的脚本
console.log('正在移除鼠标跟踪效果...');

// 移除鼠标跟随元素
const follower = document.querySelector('.mouse-follower');
if (follower) {
    follower.remove();
    console.log('已移除鼠标跟随元素');
}

// 移除相关事件监听器（如果存在）
document.removeEventListener('mousemove', null);