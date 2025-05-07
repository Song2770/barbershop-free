import sys
import re
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTableWidget, QTableWidgetItem, QPushButton, 
                            QLineEdit, QLabel, QMessageBox, QDialog, 
                            QFormLayout, QSpinBox, QDialogButtonBox, QComboBox,
                            QHeaderView)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QColor
from debug_console import DebugConsole

class MemberEditDialog(QDialog):
    def __init__(self, member=None, is_new=False, card_type=None, parent=None):
        super().__init__(parent)
        self.member = member
        self.is_new = is_new
        self.card_type = card_type
        
        if is_new:
            self.setWindowTitle("添加新会员")
        else:
            self.setWindowTitle("编辑会员信息")
        
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout(self)
        
        # 姓名输入
        self.name_edit = QLineEdit()
        layout.addRow("姓名 (2-10个汉字):", self.name_edit)
        
        # 手机号输入
        self.phone_edit = QLineEdit()
        layout.addRow("手机号 (11位):", self.phone_edit)
        
        # 剩余次数
        self.times_spin = QSpinBox()
        self.times_spin.setRange(0, 99)
        layout.addRow("剩余次数 (0-99):", self.times_spin)
        
        # 余额
        self.balance_spin = QSpinBox()
        self.balance_spin.setRange(0, 9999)
        layout.addRow("余额 (0-9999):", self.balance_spin)
        
        # 如果是新建并且没有指定卡类型
        if self.is_new and not self.card_type:
            self.card_type_combo = QComboBox()
            self.card_type_combo.addItems(["剪发卡", "洗吹卡"])
            layout.addRow("卡类型:", self.card_type_combo)
        
        # 按钮
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)
        
        # 如果是编辑模式，填充已有数据
        if not self.is_new and self.member:
            self.name_edit.setText(self.member['name'])
            self.phone_edit.setText(self.member['phone'])
            self.times_spin.setValue(self.member['remaining_times'])
            self.balance_spin.setValue(self.member['balance'])
    
    def get_data(self):
        data = {
            'name': self.name_edit.text(),
            'phone': self.phone_edit.text(),
            'remaining_times': self.times_spin.value(),
            'balance': self.balance_spin.value()
        }
        
        if self.is_new and not self.card_type and hasattr(self, 'card_type_combo'):
            if self.card_type_combo.currentText() == "剪发卡":
                data['card_type'] = 'haircut_card'
            else:
                data['card_type'] = 'wash_blow_card'
        
        return data
    
    def accept(self):
        # 验证数据
        data = self.get_data()
        
        # 验证姓名
        if not re.match(r'^[\u4e00-\u9fa5]{2,10}$', data['name']):
            QMessageBox.warning(self, "输入错误", "姓名必须是2-10个汉字")
            return
        
        # 验证手机号
        if not re.match(r'^\d{11}$', data['phone']):
            QMessageBox.warning(self, "输入错误", "手机号必须是11位数字")
            return
        
        super().accept()


class MemberManagementUI(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.db_manager.data_updated.connect(self.refresh_table)
        self.debug_console = None
        
        self.init_ui()
        self.refresh_table()
    
    def init_ui(self):
        self.setWindowTitle("理发店会员管理系统")
        self.setGeometry(100, 100, 900, 650)  # 增大窗口大小
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # 顶部搜索区域 - 增加搜索框高度
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入姓名或手机号搜索...")
        self.search_input.setMinimumHeight(40)  # 设置搜索框最小高度
        font = QFont()
        font.setPointSize(11)  # 增大字体
        self.search_input.setFont(font)
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)
        
        # 会员列表表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # 姓名、手机号、剩余次数、余额、操作
        self.table.setHorizontalHeaderLabels(["姓名", "手机号", "剩余次数", "余额", "操作"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 不允许直接编辑
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # 设置表格自适应占满区域
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 操作列设置固定宽度
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 100)  # 设置操作列宽度
        
        # 设置表格字体
        table_font = QFont()
        table_font.setPointSize(10)
        self.table.setFont(table_font)
        
        main_layout.addWidget(self.table)
        
        # 底部按钮区域 - 增大按钮大小
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 10, 0, 0)  # 增加顶部边距
        
        # 左侧按钮组
        left_buttons = QHBoxLayout()
        self.add_btn = QPushButton("新建")
        self.add_btn.setMinimumSize(120, 50)  # 增大按钮尺寸
        self.add_btn.setFont(font)  # 使用之前定义的字体
        self.add_btn.clicked.connect(self.on_add)
        left_buttons.addWidget(self.add_btn)
        
        self.debug_btn = QPushButton("调试模式")
        self.debug_btn.setMinimumSize(120, 50)  # 增大按钮尺寸
        self.debug_btn.setFont(font)
        self.debug_btn.clicked.connect(self.toggle_debug)
        left_buttons.addWidget(self.debug_btn)
        
        bottom_layout.addLayout(left_buttons)
        
        bottom_layout.addStretch()
        
        # 右侧切换卡种按钮 - 增大选项按钮
        right_buttons = QHBoxLayout()
        
        table_label = QLabel("当前显示:")
        table_label.setFont(font)  # 增大标签字体
        right_buttons.addWidget(table_label)
        
        self.table_selector = QComboBox()
        self.table_selector.addItems(["剪发卡", "洗吹卡"])
        self.table_selector.setMinimumSize(150, 50)  # 增大下拉框尺寸
        self.table_selector.setFont(font)  # 增大下拉框字体
        self.table_selector.currentIndexChanged.connect(self.on_switch_table)
        right_buttons.addWidget(self.table_selector)
        
        bottom_layout.addLayout(right_buttons)
        
        main_layout.addLayout(bottom_layout)
    
    @pyqtSlot()
    def refresh_table(self):
        """刷新整个表格数据"""
        members = self.db_manager.get_all_members()
        self.populate_table(members)
    
    def update_row(self, row, data):
        """只更新表格中的一行"""
        self.table.setItem(row, 0, QTableWidgetItem(data['name']))
        self.table.setItem(row, 1, QTableWidgetItem(data['phone']))
        self.table.setItem(row, 2, QTableWidgetItem(str(data['remaining_times'])))
        self.table.setItem(row, 3, QTableWidgetItem(str(data['balance'])))
    
    def populate_table(self, members):
        """填充表格数据"""
        self.table.setRowCount(0)  # 清空表格
        
        for member in members:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # 添加数据
            self.table.setItem(row, 0, QTableWidgetItem(member[0]))  # 姓名
            self.table.setItem(row, 1, QTableWidgetItem(member[1]))  # 手机号
            self.table.setItem(row, 2, QTableWidgetItem(str(member[2])))  # 剩余次数
            self.table.setItem(row, 3, QTableWidgetItem(str(member[3])))  # 余额
            
            # 设置隔行变色
            if row % 2 == 1:  # 奇数行
                for col in range(4):  # 不包括操作列
                    self.table.item(row, col).setBackground(QColor('#eaeaea'))    
            # 添加编辑按钮
            edit_btn = QPushButton("修改")
            # 设置按钮字体和样式
            btn_font = QFont()
            btn_font.setPointSize(10)
            edit_btn.setFont(btn_font)
            edit_btn.setMinimumHeight(30)  # 增加按钮高度
            edit_btn.clicked.connect(lambda checked, r=row: self.on_edit(r))
            self.table.setCellWidget(row, 4, edit_btn)
        
        # 表格行高设置
        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, 40)
    
    @pyqtSlot(str)
    def on_search(self, text):
        """搜索会员"""
        if text.strip() == "":
            members = self.db_manager.get_all_members()
        else:
            members = self.db_manager.search_members(text)
        
        self.populate_table(members)
    
    @pyqtSlot(int)
    def on_edit(self, row):
        """编辑会员信息"""
        phone = self.table.item(row, 1).text()
        member = self.db_manager.get_member_by_phone(phone)
        
        if member:
            dialog = MemberEditDialog(member, False, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                new_data = dialog.get_data()
                success, message = self.db_manager.update_member(phone, new_data)
                
                if success:
                    # 只更新这一行
                    self.update_row(row, new_data)
                    self.log(f"已更新会员: {new_data['name']}")
                else:
                    QMessageBox.warning(self, "更新失败", message)
                    self.log(f"更新失败: {message}")
    
    @pyqtSlot()
    def on_add(self):
        """添加新会员"""
        card_type = 'haircut_card' if self.table_selector.currentIndex() == 0 else 'wash_blow_card'
        dialog = MemberEditDialog(is_new=True, card_type=card_type, parent=self)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            # 如果对话框中选择了卡类型，则使用
            if 'card_type' in data:
                # 临时切换表
                current_table = self.db_manager.current_table
                self.db_manager.switch_table(data['card_type'])
                del data['card_type']
                
                success, message = self.db_manager.add_member(data)
                
                # 恢复原表
                self.db_manager.switch_table(current_table)
            else:
                success, message = self.db_manager.add_member(data)
            
            if success:
                self.log(f"已添加新会员: {data['name']}")
                QMessageBox.information(self, "成功", message)
            else:
                QMessageBox.warning(self, "添加失败", message)
                self.log(f"添加失败: {message}")
    
    @pyqtSlot(int)
    def on_switch_table(self, index):
        """切换表格"""
        if index == 0:
            self.db_manager.switch_table('haircut_card')
            self.log("已切换到剪发卡表")
        else:
            self.db_manager.switch_table('wash_blow_card')
            self.log("已切换到洗吹卡表")
    
    @pyqtSlot()
    def toggle_debug(self):
        """切换调试模式"""
        if not self.debug_console or not self.debug_console.isVisible():
            self.debug_console = DebugConsole()
            self.debug_console.show()
            self.debug_btn.setText("关闭调试")
        else:
            self.debug_console.close()
            self.debug_btn.setText("调试模式")
    
    def log(self, message):
        """记录日志信息"""
        print(message)
        if self.debug_console and self.debug_console.isVisible():
            self.debug_console.append_text(message)