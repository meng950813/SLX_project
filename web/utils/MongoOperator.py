"""
将Mongo的常用操作封装
"""

import pymongo as pm


class MongoOperator:
    def __init__(self, host, port, db_name, username, password, default_collection):
        """
        设置mongodb的地址，端口，用户名，密码 以及要访问的默认集合，
        :param host: 地址
        :param port: 端口
        :param db_name: 数据库名字
        :param default_collection: 默认的集合
        """

        # 建立数据库连接
        self.client = pm.MongoClient(host=host, port=port, username=username, password=password)
        # 选择相应的数据库名称
        self.db = self.client.get_database(db_name)
        # 设置默认的集合
        self.collection = self.db.get_collection(default_collection)

    def insert(self, item, collection_name=None):
        """
        插入数据，这里的数据可以是一个，也可以是多个
        :param item: 需要插入的数据
        :param collection_name:  可选，需要访问哪个集合
        :return:
        """

        if collection_name != None:
            collection = self.db.get_collection(self.db)
            collection.insert(item)
        else:
            self.collection.insert(item)

    def find(self, expression =None, collection_name=None):
        """
        进行简单查询，可以指定条件和集合
        :param expression: 查询条件，可以为空
        :param collection_name: 集合名称
        :return: 所有结果
        """

        if collection_name != None:
            collection = self.db.get_collection(self.db)
            if expression == None:
                return collection.find()
            else:
                return collection.find(expression)
        else:
            if expression == None:
                return self.collection.find()
            else:
                return self.collection.find(expression)

    def get_collection(self, collection_name=None):
        """
        很多时候单纯的查询不能够通过这个类封装的方法执行，这时候就可以直接获取到对应的collection进行操作
        :param collection_name: 集合名称
        :return: collection
        """

        if collection_name == None:
            return self.collection
        else:
            return self.get_collection(collection_name)


    def get_user_relations(self, u_id):
        # TODO
        try:
            back = self.db.user.find({"id":u_id}).aggregate([{
                "$lookup":
                    {
                        "from": "university",
                        "localField": "charge_school",
                        "foreignField": "name",
                        "as": "school"
                    }
                }])
            print("back data : ",back)
        except Exception as e:
            print("^" * 89)
            print(e)



if __name__ == '__main__':

    # funds_col = db.get_collection()
    # print(funds_col.find_one({"id": 73927}))
    
    # db.get_user_relations(100000)