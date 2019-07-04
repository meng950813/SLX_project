from web.utils import mysql
from werkzeug.security import generate_password_hash, check_password_hash


def select(username):
    # 把密码转换成hash
    sql = "select * from user where tel_number = ?"
    result = mysql.select_one(sql, username)

    return result
