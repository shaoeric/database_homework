import pymysql

DEBUG = True

# 打开数据库连接  配置项：连接、用户名、密码、数据库名 编码
db = pymysql.connect("localhost", "root", "root", "database_homework", charset='utf8')

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()

