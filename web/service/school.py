from web.config import MongoDB_CONFIG
from web.utils.mongo_operator import MongoOperator


def get_schools_institutions(cur_school=None, mongo=None):
    """
    获取目前的所有的学校和cur_school对应的所有学院
    :param cur_school: 当前选中的学校，如为None则默认获取第一个
    :param mongo: 为空则自己创建一个mongo
    :return: (学校数组,学院列表)
    """
    pass
    if mongo is None:
        mongo = MongoOperator(**MongoDB_CONFIG)
    # 获取学校
    collection = mongo.get_collection('school')
    generator = collection.find({}, {'_id': 0, 'name': 1})
    schools = [school['name'] for school in generator]
    # 确定当前选择的学校
    cur_school = schools[0] if cur_school is None else cur_school
    # 获取当前学校的所有院系
    school = collection.find_one({'name': cur_school}, {'_id': 0, 'institutions': 1})
    institutions = [result['name'] for result in school['institutions']]
    return cur_school, schools, institutions

def get_school_info(school_name,mongo=None):
    """
    根据学校名获取学校的简介信息
    :param school_name: 学校名
    :return: school_info: 学校名，学院数量，一流学科数量，重点学科数量，国家重点实验室数量，院士数量，长江学者数量，杰出青年数量
    """
    if mongo is None:
        mongo = MongoOperator(**MongoDB_CONFIG)
    collection = mongo.get_collection("school")
    school_info = collection.find_one({"name":school_name}, {"_id":0,"institutions":1,"dfc_num":1,"nkd_num":1,
                           "skl_num":1,"academician_num":1,"outstanding_num":1,"cjsp_num":1})
    school_info['institutions'] = len(school_info['institutions'])
    return school_info

if __name__ == "__main__":
    #测试
    s = get_school_info("大连理工大学")
    print(s)

