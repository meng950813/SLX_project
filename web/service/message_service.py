"""
2019.7.9
by df
"""

from web.config import MongoDB_CONFIG
from web.utils.mongo_operator import MongoOperator

def search_message_num(user_id):
    """
    根据用户的id获取到未读信息的数量
    :param user_id:
    :return: 未读信息数量num
    """
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 指定集合
    message_num = mongo_operator.find({"user_id": user_id,"state" : 0},"message").count()
    return message_num

def search_message_info(user_id):
    """
    根据用户id获取数据中其他用户发送给他的消息
    :param user_id:
    :return: 其他用户的姓名from_name，发送的时间date， 消息的内容detail
    """
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 指定集合
    message_dict = mongo_operator.find({"user_id": user_id}, "message")
    return message_dict

def update_massgae_state(user_id):
    """
    根据用户id改变消息的状态，将未读消息改为已读
    :param user_id:
    :return:
    """
    mongo_operator = MongoOperator(**MongoDB_CONFIG).get_collection("message")

    mongo_operator.update_many({"user_id" : user_id},{"$set":{"state":1}})

def get_user_id(user_name):
    """
    根据用户名获取用户id
    :param user_id:
    :return: 用户id,user_id
    """
    mongo_operator = MongoOperator(**MongoDB_CONFIG).get_collection("user")
    user_id = mongo_operator.find_one({"name" : user_name})['id']
    return user_id

def insert_message(message):
    """
    将发送的接受者，消息，发送时间插入数据库
    :param user_id:
    :param detail:
    :param date:
    :return:
    """
    mongo_operator = MongoOperator(**MongoDB_CONFIG).get_collection("message")
    mongo_operator.insert({"state" : message['state'], "from_id" : message['from_id'], "from_name" : message['from_name'],
                           "user_id" : message['user_id'],"date" : message['date'], "detail" : message['detail']})

if __name__ == "__main__":
    # message = {"state" : 0,
    # "from_id" : 100006,
    # "from_name" : "段旭扬",
    # "user_id" : 100000,
    # "date" : "2019-07-09 12:11",
    # "detail" : "去高一（21）拜访陈彦熹"}
    # insert_message(message)
    id = get_user_id("杨秀宁")
    print(id)
