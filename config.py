# 页面设置
STARTPAGE = 0     # 开始页面
ENDPAGE   = 1     # 结束页面
PAGESIZE  = 10000    # 分页读取行数

# 线程数量设置
THREAD_NUM = 10

# MYSQL 配置
HOST      = "139.9.52.22"
PORT      = 6789
USER      = "jrj"
PASSWORD  = "jrjwu"
DATABASE  = "youshua"
TABLE     = "test"
COLUMN    = "mobile"

# 保存结果表名
SAVE_TABLE = "fangtx_registered_from_test"

# 打印设置 1: 只显示成功结果  0: 显示所有结果
PRINT = 1

"""

git clone https://github.com/Juaran/Fangtx.git
cd Fangtx
vi config.py

screen python3 fangtx_pro.py
"""
