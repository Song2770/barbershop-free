from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from PyQt5.QtCore import Qt
from datetime import datetime

class DebugConsole(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("调试控制台")
        self.setGeometry(300, 300, 600, 400)

        layout = QVBoxLayout(self)

        # 输出文本区域
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        # 清空按钮
        clear_btn = QPushButton("清空日志")
        clear_btn.clicked.connect(self.clear_text)
        layout.addWidget(clear_btn)

        self.append_text("调试控制台已启动")

    def append_text(self, text):
        """添加文本到调试窗口"""
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_text = f"[{time_stamp}] {text}"
        self.text_area.append(formatted_text)

    def clear_text(self):
        """清空文本区域"""
        self.text_area.clear()
        self.append_text("日志已清空")

    def closeEvent(self, event):
        """窗口关闭时的处理"""
        event.accept()
