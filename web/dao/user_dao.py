from web.utils import mysql



def dologin(telphone = None, email = None , u_id = None , pwd = ""):
    """
    根据 账号信息 及 密码 查询用户信息
    :param telphone: 手机号
    :param email: 邮箱
    :param u_id: 用户id
    :param pwd: 密码（32位字符串）
    :return: 用户信息 ： （ID,NAME,TYPE）or None
    """
    sql_base = "select ID,NAME,TYPE from sys_user where "
    argu = None
    if telphone:
        sql_base += "TEL_NUMBER = ?"
        argu = telphone
    elif email:
        sql_base += "EMAIL = ?"
        argu = email
    elif u_id:
        sql_base += "ID = ?"
        argu = u_id
    else:
        print("error arugments")
        return  None
    sql_base += " and PASSWORD = ?"
    # 调用语句
    result = mysql.select_one(sql_base, argu, pwd )

    return result

if __name__ == "__main__":
    # 测试：
    # success with telphone
    print(dologin(telphone = "12345678901", pwd = "3b86247f12fa88a116e8e446614b3eae"))
    # success with email
    print(dologin(email= "c@m.com", pwd = "3b86247f12fa88a116e8e446614b3eae"))
    # success with user_id
    print(dologin(u_id= "100000", pwd = "3b86247f12fa88a116e8e446614b3eae"))
    # fail to login
    print(dologin(telphone = "12345678901", pwd = "3b86247f12fa88a116e8e"))