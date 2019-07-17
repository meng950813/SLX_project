from web.dao import user_dao
from web.utils import encrypt
import re
from web.config import MongoDB_CONFIG
from web.utils.mongo_operator import MongoOperator


def check_user(username, password):
    """
    根据账户名密码
    :param username:用户名（str）
    :param password: 原始密码（str）
    :return:  字典对象{'ID': 1, 'NAME': '测试账号', 'TYPE': '1'}
            or None
    """
    tel = re.compile(r"^\d{11}$")
    email = re.compile(r"^[\w\d]+@[\w\d]+\.com$")
    u_id = re.compile(r"^\d{6,8}$")
    #  加密出密码
    password = encrypt.encryption(password)

    back = None

    # 利用正则判断用户名是否符合标准，以减少 sql 注入可能性
    if tel.match(username):
        # 以电话登陆
        back = user_dao.do_login(telephone=username, pwd=password)
    elif email.match(username):
        # 以邮件登陆
        back = user_dao.do_login(email=username, pwd=password)
    elif u_id.match(username):
        # 以 id 登陆
        back = user_dao.do_login(u_id=username, pwd=password)

    # 返回查询结果
    return back


def get_user_by_email(email):
    """
    根据email获取对应的用户，如果邮箱不存在则返回None
    :param email:
    :return:
    """
    # 数据库查询
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    collection = mongo_operator.get_collection("user")
    user = collection.find_one({'email': email})

    return user


def set_password(user, new_password):
    """
    为某个用户赋予新的密码
    :param user: 用户字典
    :param new_password: 新的密码
    :return: 操作成功则返回True
    """
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    collection = mongo_operator.get_collection("user")
    # 为密码加密
    password_hash = encrypt.encryption(new_password)
    # 更新数据库
    condition = {'id': user['id']}
    user['password'] = password_hash
    result = collection.update_one(condition, {'$set': user})
    return result.modified_count == 1
