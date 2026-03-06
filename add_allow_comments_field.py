"""
数据库迁移脚本：为 posts 表添加 allow_comments 字段
运行方式：python add_allow_comments_field.py
"""
import sqlite3

def migrate():
    # 连接数据库
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(posts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'allow_comments' not in columns:
            # 添加 allow_comments 字段，默认值为 TRUE
            cursor.execute('''
                ALTER TABLE posts 
                ADD COLUMN allow_comments BOOLEAN DEFAULT TRUE
            ''')
            conn.commit()
            print("✅ 成功添加 allow_comments 字段到 posts 表")
        else:
            print("ℹ️  allow_comments 字段已存在，无需迁移")
            
    except Exception as e:
        print(f"❌ 迁移失败：{e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("🚀 开始数据库迁移...")
    migrate()
    print("✨ 迁移完成！")
