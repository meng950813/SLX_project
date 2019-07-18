from flask_login import UserMixin


class User(dict, UserMixin):
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
