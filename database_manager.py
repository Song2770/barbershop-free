import os
import sqlite3
import pandas as pd
from PyQt5.QtCore import QObject, pyqtSignal

class DatabaseManager(QObject):
    data_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db_path = os.path.join('database', 'members.db')
        self.excel_path = os.path.join('database', 'members.xlsx')
        self.current_table = 'haircut_card'  # 默认显示剪发卡
        self.initialize_database()

    def initialize_database(self):
        """初始化数据库，创建所需表格"""
        # 创建SQLite数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建剪发卡表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS haircut_card (
            name TEXT CHECK(length(name) >= 2 AND length(name) <= 10),
            phone TEXT CHECK(length(phone) = 11),
            remaining_times INTEGER CHECK(remaining_times >= 0 AND remaining_times <= 99),
            balance INTEGER CHECK(balance >= 0 AND balance <= 9999),
            PRIMARY KEY (phone)
        )
        ''')

        # 创建洗吹卡表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS wash_blow_card (
            name TEXT CHECK(length(name) >= 2 AND length(name) <= 10),
            phone TEXT CHECK(length(phone) = 11),
            remaining_times INTEGER CHECK(remaining_times >= 0 AND remaining_times <= 99),
            balance INTEGER CHECK(balance >= 0 AND balance <= 9999),
            PRIMARY KEY (phone)
        )
        ''')

        conn.commit()
        conn.close()

        # 初始化Excel文件
        self.sync_db_to_excel()

    def sync_db_to_excel(self):
        """将SQLite数据同步到Excel"""
        conn = sqlite3.connect(self.db_path)

        # 读取两个表的数据
        haircut_df = pd.read_sql_query("SELECT * FROM haircut_card", conn)
        wash_blow_df = pd.read_sql_query("SELECT * FROM wash_blow_card", conn)

        # 创建Excel写入器
        with pd.ExcelWriter(self.excel_path) as writer:
            haircut_df.to_excel(writer, sheet_name='haircut_card', index=False)
            wash_blow_df.to_excel(writer, sheet_name='wash_blow_card', index=False)

        conn.close()

    def sync_excel_to_db(self):
        """将Excel数据同步到SQLite"""
        if not os.path.exists(self.excel_path):
            return

        try:
            # 读取Excel数据
            haircut_df = pd.read_excel(self.excel_path, sheet_name='haircut_card')
            wash_blow_df = pd.read_excel(self.excel_path, sheet_name='wash_blow_card')

            conn = sqlite3.connect(self.db_path)

            # 清空现有表格
            conn.execute("DELETE FROM haircut_card")
            conn.execute("DELETE FROM wash_blow_card")

            # 写入新数据
            haircut_df.to_sql('haircut_card', conn, if_exists='append', index=False)
            wash_blow_df.to_sql('wash_blow_card', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"同步Excel到数据库出错: {e}")

    def get_all_members(self):
        """获取当前表的所有会员"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {self.current_table}")
        members = cursor.fetchall()
        conn.close()
        return members

    def search_members(self, search_text):
        """根据姓名或手机号搜索会员"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 使用模糊搜索
        cursor.execute(f"""
        SELECT * FROM {self.current_table}
        WHERE name LIKE ? OR phone LIKE ?
        """, (f'%{search_text}%', f'%{search_text}%'))

        results = cursor.fetchall()
        conn.close()
        return results

    def add_member(self, data):
        """添加新会员"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(f"""
            INSERT INTO {self.current_table} (name, phone, remaining_times, balance)
            VALUES (?, ?, ?, ?)
            """, (data['name'], data['phone'], data['remaining_times'], data['balance']))

            conn.commit()
            conn.close()

            # 同步到Excel
            self.sync_db_to_excel()
            self.data_updated.emit()
            return True, "添加成功"

        except sqlite3.IntegrityError:
            conn.close()
            return False, "手机号已存在"

        except Exception as e:
            conn.close()
            return False, f"添加失败: {str(e)}"

    def update_member(self, phone, data):
        """更新会员信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(f"""
            UPDATE {self.current_table}
            SET name = ?, phone = ?, remaining_times = ?, balance = ?
            WHERE phone = ?
            """, (data['name'], data['phone'], data['remaining_times'], data['balance'], phone))

            conn.commit()
            conn.close()

            # 同步到Excel
            self.sync_db_to_excel()
            self.data_updated.emit()
            return True, "更新成功"

        except sqlite3.IntegrityError:
            conn.close()
            return False, "手机号已存在"

        except Exception as e:
            conn.close()
            return False, f"更新失败: {str(e)}"

    def get_member_by_phone(self, phone):
        """根据手机号获取会员信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(f"""
        SELECT name, phone, remaining_times, balance
        FROM {self.current_table}
        WHERE phone = ?
        """, (phone,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'name': result[0],
                'phone': result[1],
                'remaining_times': result[2],
                'balance': result[3]
            }
        else:
            return None

    def switch_table(self, table_name):
        """切换当前操作的表"""
        if table_name in ['haircut_card', 'wash_blow_card']:
            self.current_table = table_name
            self.data_updated.emit()
            return True
        return False
