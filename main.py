import sys
import os
from PyQt5.QtWidgets import QApplication
from member_ui import MemberManagementUI
from database_manager import DatabaseManager
from backup_manager import BackupManager

def main():
    # 确保数据库目录存在
    os.makedirs('database', exist_ok=True)

    # 初始化应用
    app = QApplication(sys.argv)

    # 创建数据库管理器
    db_manager = DatabaseManager()

    # 创建备份管理器
    backup_manager = BackupManager(db_manager)

    # 启动备份定时器
    backup_manager.start_backup_timer()

    # 创建并显示UI
    window = MemberManagementUI(db_manager)
    window.show()

    # 执行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
