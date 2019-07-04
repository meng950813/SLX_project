"""
created by chen

该模块用于密码加密

基本思路为 ： 调用 hashlib 库中的 md5 加密方法，
            将用户密码 与 专门的 key 进行 update 运算
            返回一个 32 位 长的密码

"""
import hashlib

import sys


sys.path.append("..")


from web.config import SECRET_KEY


def encryption(pwd):
    """
    用于加密的函数
    :param pwd: 用户密码 (str)
    :return: 32位长度字符串
    """

    pwd = str(pwd)

    password = hashlib.md5(pwd.encode())
    password.update(SECRET_KEY['KEY'])
    # 第三次加密
    password.update(SECRET_KEY['KEY2'])

    return password.hexdigest()


if __name__ == '__main__':
    print(encryption("a"))
    print(encryption(123))
    print(encryption(None))
