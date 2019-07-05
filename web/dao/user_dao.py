import pymongo
from web.config import MongoDB_CONFIG


def do_login(telephone=None, email=None, u_id=None, pwd=""):
    """
    根据 账号信息 及 密码 查询用户信息
    :param telephone: 手机号
    :param email: 邮箱
    :param u_id: 用户id
    :param pwd: 密码（32位字符串）
    :return: 用户信息 ： （ID,NAME,TYPE）or None
    """
    # 连接服务器
    client = pymongo.MongoClient("mongodb://" + MongoDB_CONFIG["ip"] + ":" + MongoDB_CONFIG["port"])
    # 指定远程库
    db = client["new_db"]
    # 指定集合
    collection = db['user']
    # 条件
    condition = {'password': pwd}

    if telephone:
        condition['tel_number'] = telephone
    elif email:
        condition['email'] = email
    elif u_id:
        condition['id'] = u_id

    result = collection.find_one(condition)
    # 删除mongo的id
    if result:
        del result['_id']

    return result


if __name__ == "__main__":
    # 测试：
    # success with telphone
    print(do_login(telephone="12345678901", pwd="3b86247f12fa88a116e8e446614b3eae"))
    # success with email
    print(do_login(email="c@m.com", pwd="3b86247f12fa88a116e8e446614b3eae"))
    # success with user_id
    print(do_login(u_id=100000, pwd="3b86247f12fa88a116e8e446614b3eae"))
    # fail to login
    print(do_login(telephone="12345678901", pwd="3b86247f12fa88a116e8e"))
