from web.utils import encrypt
import re
from web.config import MongoDB_CONFIG
from web.utils.mongo_operator import MongoOperator
from web.models import User


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
    # 加密密码
    password = encrypt.encryption(password)
    # 查询条件
    condition = {'password': password, "status": "1"}
    # 以电话登陆
    if tel.match(username):
        condition['tel_number'] = username
    # 以邮件登陆
    elif email.match(username):
        condition['email'] = username
    # 以 id 登陆
    elif u_id.match(username):
        condition['id'] = int(username)

    # 连接服务器
    mongo = MongoOperator(**MongoDB_CONFIG)
    # 除_id 外全部获取
    result = mongo.get_collection('user').find_one(condition, {"_id": 0})
    if result:
        return User(**result)
    return None


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


def get_user_by_id(user_id):
    """
    根据user_id 获取对应的用户，如果不存在返回None
    :param user_id:
    :return: User对象或者None
    """
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    collection = mongo_operator.get_collection("user")
    datum = collection.find_one({'id': int(user_id)})
    # 转化成对象
    user = None
    if datum:
        user = User(**datum)

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
    return result.matched_count == 1
