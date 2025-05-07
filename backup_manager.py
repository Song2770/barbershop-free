import os
import shutil
import time
from datetime import datetime
from PyQt5.QtCore import QTimer, QObject

class BackupManager(QObject):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.backup_folder = 'database'
        self.timer = QTimer()
        self.timer.timeout.connect(self.create_backup)

    def start_backup_timer(self):
        """启动定时备份 - 每24小时备份一次"""
        # 设置为24小时
        self.timer.start(24 * 60 * 60 * 1000)
        # 立即执行一次备份
        self.create_backup()

    def create_backup(self):
        """创建数据库和Excel的备份"""
        current_date = datetime.now().strftime('%Y%m%d')

        # 备份SQLite数据库
        db_source = self.db_manager.db_path
        db_backup = os.path.join(self.backup_folder, f"{current_date}_db.bak")

        # 备份Excel文件
        excel_source = self.db_manager.excel_path
        excel_backup = os.path.join(self.backup_folder, f"{current_date}_excel.bak")

        try:
            # 确保数据库是最新的
            self.db_manager.sync_db_to_excel()

            # 复制文件
            if os.path.exists(db_source):
                shutil.copy2(db_source, db_backup)

            if os.path.exists(excel_source):
                shutil.copy2(excel_source, excel_backup)

            print(f"备份已创建: {db_backup} 和 {excel_backup}")
            return True

        except Exception as e:
            print(f"备份失败: {str(e)}")
            return False

    def restore_backup(self, backup_date):
        """从备份恢复数据"""
        db_backup = os.path.join(self.backup_folder, f"{backup_date}_db.bak")
        excel_backup = os.path.join(self.backup_folder, f"{backup_date}_excel.bak")

        try:
            # 恢复SQLite数据库
            if os.path.exists(db_backup):
                shutil.copy2(db_backup, self.db_manager.db_path)

            # 恢复Excel文件
            if os.path.exists(excel_backup):
                shutil.copy2(excel_backup, self.db_manager.excel_path)

            # 刷新数据
            self.db_manager.sync_excel_to_db()
            self.db_manager.data_updated.emit()

            print(f"已从 {backup_date} 的备份恢复")
            return True

        except Exception as e:
            print(f"恢复失败: {str(e)}")
            return False
