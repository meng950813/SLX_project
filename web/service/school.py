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
