# barbershop-free

## 运行说明：

1. 在项目根目录下创建虚拟环境：
```bash
python -m venv venv
```

2. 激活虚拟环境：
```bash
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. 安装必要的依赖：
```bash
pip install PyQt5 pandas openpyxl
```

4. 运行程序：
```bash
python main.py
```

## 功能说明：

1. **数据管理**：
   - 使用SQLite和Excel双数据库存储
   - 自动同步两个数据库
   - 每24小时自动备份一次，备份文件名带日期

2. **会员管理**：
   - 可搜索会员（姓名或手机号）
   - 添加新会员
   - 修改现有会员信息
   - 切换不同卡种表格

3. **界面功能**：
   - 搜索框用于快速查找会员
   - 会员列表显示所有会员信息
   - 每行右侧有修改按钮
   - 修改时只更新对应行，不刷新整表
   - 左下角有新建按钮
   - 右下角可切换不同卡种
   - 调试模式按钮可显示系统日志

## 开源协议：
本项目遵循<a href='./LICENSE'>MIT</a>开源协议，在Github托管并开源。
