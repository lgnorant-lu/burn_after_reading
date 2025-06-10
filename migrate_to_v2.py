#!/usr/bin/env python
"""
---------------------------------------------------------------
File name:          migrate_to_v2.py
Author:             Ignorant-lu
Date created:       2025/06/11
Last modified:      2025/06/11
Python Version:     3.x
Description:        Database migration script from v1 to v2 schema
                    Adds password protection, expiration, and file support
---------------------------------------------------------------
"""

import sqlite3
from pathlib import Path
from src.models import ExpirationType

def migrate_database_to_v2(db_path: str = "burn_after_reading.db"):
    """
    Migrate database from v1 to v2 schema
    
    v1 Schema:
    - id (UUID)
    - content (String)
    - created_at (DateTime)
    
    v2 Schema adds:
    - password_hash (String, nullable)
    - expiration_type (Enum, default READ_ONCE)
    - expires_at (DateTime, nullable)
    - filename (String, nullable)
    - file_data (LargeBinary, nullable)
    - content_type (String, nullable)
    - file_size (String, nullable)
    """
    
    db_file = Path(db_path)
    if not db_file.exists():
        print(f"数据库文件 {db_path} 不存在，跳过迁移")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查是否已经迁移过了
        cursor.execute("PRAGMA table_info(notes)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'password_hash' in columns:
            print("数据库已经是v2版本，无需迁移")
            return
        
        print("开始迁移数据库到v2版本...")
        
        # 备份现有数据
        cursor.execute("SELECT * FROM notes")
        existing_notes = cursor.fetchall()
        print(f"找到 {len(existing_notes)} 条现有笔记")
        
        # 重命名旧表
        cursor.execute("ALTER TABLE notes RENAME TO notes_v1_backup")
        
        # 创建新表结构
        cursor.execute("""
        CREATE TABLE notes (
            id CHAR(36) PRIMARY KEY,
            content TEXT,
            password_hash VARCHAR(255),
            expiration_type VARCHAR(20) NOT NULL DEFAULT 'read_once',
            expires_at TIMESTAMP,
            filename VARCHAR(255),
            file_data BLOB,
            content_type VARCHAR(100),
            file_size VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 迁移现有数据（为新字段设置默认值）
        for note in existing_notes:
            cursor.execute("""
            INSERT INTO notes (id, content, password_hash, expiration_type, expires_at, 
                             filename, file_data, content_type, file_size, created_at)
            VALUES (?, ?, NULL, 'read_once', NULL, NULL, NULL, NULL, NULL, ?)
            """, (note[0], note[1], note[2]))  # id, content, created_at
        
        # 提交更改
        conn.commit()
        print(f"成功迁移 {len(existing_notes)} 条笔记")
        
        # 验证迁移结果
        cursor.execute("SELECT COUNT(*) FROM notes")
        new_count = cursor.fetchone()[0]
        print(f"迁移后笔记数量: {new_count}")
        
        print("数据库迁移完成！")
        print("备份表 'notes_v1_backup' 已保留，如需删除请手动执行：")
        print("  sqlite3 notes.db 'DROP TABLE notes_v1_backup;'")
        
    except sqlite3.Error as e:
        print(f"迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def check_migration_status(db_path: str = "burn_after_reading.db"):
    """检查数据库迁移状态"""
    db_file = Path(db_path)
    if not db_file.exists():
        print(f"数据库文件 {db_path} 不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(notes)")
        columns = [row[1] for row in cursor.fetchall()]
        
        v2_columns = ['password_hash', 'expiration_type', 'expires_at', 
                     'filename', 'file_data', 'content_type', 'file_size']
        
        missing_columns = [col for col in v2_columns if col not in columns]
        
        if not missing_columns:
            print("✅ 数据库已升级到v2版本")
            
            cursor.execute("SELECT COUNT(*) FROM notes")
            count = cursor.fetchone()[0]
            print(f"当前笔记数量: {count}")
            
            # 检查是否有备份表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes_v1_backup'")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM notes_v1_backup")
                backup_count = cursor.fetchone()[0]
                print(f"v1备份表中的笔记数量: {backup_count}")
        else:
            print("❌ 数据库仍为v1版本")
            print(f"缺少字段: {missing_columns}")
            
    except sqlite3.Error as e:
        print(f"检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            check_migration_status()
        elif sys.argv[1] == "migrate":
            migrate_database_to_v2()
        else:
            print("用法: python migrate_to_v2.py [check|migrate]")
    else:
        print("数据库迁移工具 v1 → v2")
        print("用法:")
        print("  python migrate_to_v2.py check    - 检查迁移状态")
        print("  python migrate_to_v2.py migrate  - 执行迁移") 