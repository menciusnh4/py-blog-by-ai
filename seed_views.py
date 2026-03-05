"""
测试脚本：为现有文章添加随机的浏览次数
"""
import sqlite3
import random

def seed_views():
    db_name = 'blog.db'
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # 获取所有文章
    cursor.execute('SELECT id FROM posts')
    posts = cursor.fetchall()
    
    print(f'找到 {len(posts)} 篇文章')
    
    # 为每篇文章设置随机浏览量
    for post in posts:
        post_id = post[0]
        # 生成一个合理的随机浏览量（10-500 之间）
        view_count = random.randint(10, 500)
        
        cursor.execute('''
            UPDATE posts 
            SET view_count = ? 
            WHERE id = ?
        ''', (view_count, post_id))
        print(f'文章 ID {post_id}: 设置浏览量为 {view_count}')
    
    conn.commit()
    conn.close()
    print('\n✓ 所有文章的浏览量已更新！')

if __name__ == '__main__':
    seed_views()
