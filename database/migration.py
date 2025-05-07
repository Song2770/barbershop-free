import os
import pandas as pd
import sqlite3

class DataMigrator:
    def __init__(self):
        self.old_excel_path = os.path.join('old_db.xlsx')
        self.db_path = 'members.db'

    def migrate_haircut_card(self):
        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            df = pd.read_excel(self.old_excel_path, sheet_name='卡', header=0, usecols='B:D')
            df.columns = ['name', 'phone', 'remaining_times']
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO haircut_card (name, phone, remaining_times, balance)
                    VALUES (?,?,?,0)
                ''', (row['name'], str(row['phone']), row['remaining_times']))
            conn.commit()
        except Exception as e:
            print(f'剪头卡迁移失败: {str(e)}')
        finally:
            conn.close()

    def migrate_wash_blow_card(self):
        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            df = pd.read_excel(self.old_excel_path, sheet_name='洗发卡', header=0, usecols='B:D')
            df.columns = ['name', 'phone', 'remaining_times']
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO wash_blow_card (name, phone, remaining_times, balance)
                    VALUES (?,?,?,0)
                ''', (row['name'], str(row['phone']), row['remaining_times']))
            conn.commit()
        except Exception as e:
            print(f'洗头卡迁移失败: {str(e)}')
        finally:
            conn.close()

if __name__ == '__main__':
    migrator = DataMigrator()
    migrator.migrate_haircut_card()
    migrator.migrate_wash_blow_card()
    print('数据迁移完成')
