from web.dao import user_dao
from web.utils import encrypt


def check_user(username, password):
    user = user_dao.select(username)

    if user is None:
        return None
    password_hash = encrypt.encryption(password)

    # 数据存放到session中？
    if password_hash == user['password']:
        return user
    return None
