from flask_login import UserMixin


class User(dict, UserMixin):
    """
    登录用户类，赋值会在登录或者从cookie中赋值
    得到的数据目前为用户集合中的所有数据,在修改该用户的相关数据注意级联
    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'User' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        """
        以Unicode形式返回用户的唯一标识符
        :return: str
        """
        return str(self.id)
