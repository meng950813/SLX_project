from web.utils.neo4j_operator import NeoOperator
from web.config import NEO4J_CONFIG


def get_teacher_central_network(teacher_id, school=None):
    """
    获取某一教师社交网络
    :param teacher_id: int
    :param school: 学校名，限定关系网的范围
    :return: [] or [
                {
                    "source": {id: teacher_id, name, shcool, institution, code},
                    "r" : {paper:xxx, patent:xxx, project:xxx}
                    "target":{id: xxx, name, school, institution, code}
                }, ...
            ]
    """
    try:
        if school:
            cql = "Match(source:Teacher{id:%d})-[r:学术合作]-(target:Teacher{school:%s}) " \
                  "return source, r, target" % (teacher_id, school)
        else:
            cql = "Match(source:Teacher{id:%d})-[r:学术合作]-(target:Teacher) " \
                  "return source, r, target" % teacher_id

        neo = NeoOperator(**NEO4J_CONFIG).get_connection()
        result = neo.run(cql).data()
        return result
    except Exception as e:
        print(e)
        return []


def get_teacher_central_network_with_agent(agent_id, teacher_id):
    """
    获取某教师的个人中心网络及商务在该教师的个人网络中的位置
    :param agent_id: int
    :param teacher_id: int
    :return: {
        "relation": [
            {
                source: {id, name, school, institution, code},
                r:{paper, patent, project},
                target: {id, name, school, institution, code}
            }, ... ],
        "agent_relation": [{agent_id: xxx, visited: xxx, activity: xxx, t_id:13213},...]
    }
    """
    try:
        neo = NeoOperator(**NEO4J_CONFIG).get_connection()
        cql = "Match(source:Teacher{id:%d})-[r:学术合作]-(target:Teacher) return source,r, target" % teacher_id
        back = neo.run(cql).data()

        cql = "Match(agent:Agent{id:%d})-[r:knows]-(t:Teacher)-[:学术合作]-(s:Teacher{id:%d})" \
              " return agent.id as agent_id, r.visited as visited, r.activity as activity, t.id as t_id " \
              % (agent_id, teacher_id)

        agent_relation = neo.run(cql).data()
        # return neo.run(cql).data()
        return {"relation": back, "agent_relation": agent_relation}
    except Exception as e:
        print("in get_personal_relation_with_agent and reason is: %s" % e)
        return []


def get_institution_relation_with_agent(agent_id, school, institution):
    """
    获取当前商务在该学院中的社交网络 --> 学院内部社交数据已有文件
    :param agent_id: int
    :param school: str
    :param institution: str
    :return:[{visited: xxx, activity: xxx, id:13213},...]
    """
    try:
        neo = NeoOperator(**NEO4J_CONFIG).get_connection()
        # s_id ==> source_id, t_id ==> target_id
        # cql = """Match(t1:Teacher{school:'%s', institution:'%s'})-[r]-(t2 :Teacher{school:'%s', institution:'%s'})
        #     return t1.id as s_id, t1.name as s_name,
        #     r.paper as paper, r.patent as patent, r.project as project,
        #     t2.id as t_id, t2.name as t_name"""\
        #     % (school, institution, school, institution)
        #
        # # list ==> [{s_id: xxx, s_name: xxx, t_id: 99332, t_name: xxx, paper:0, patent:0, project:0},...] or []
        # institution_relation = neo.run(cql).data()

        agent_cql = """Match(ag:Agent{id:%d})-[r:knows]->(t:Teacher{school:'%s', institution:'%s'})
            return r.visited as visited, r.activity as activity, t.id as id""" \
                    % (agent_id, school, institution)

        # list ==> [{agent_id: xxx, visited: xxx, activity: xxx, t_id:13213},...] or []
        agent_relation = neo.run(agent_cql).data()
        # return {"relation": institution_relation, "agent_relation": agent_relation}
        return agent_relation

    except Exception as e:
        print("in get_institution_relation_with_agent and reason is: %s" % e)
        return []
    pass


def get_school_relation_with_agent(agent_id, school):
    """
    获取当前商务在该学校中建立的关系
    :param agent_id: int
    :param school: int
    :return: [] or [{'visited': 1, 'activity': 0, 't_id': 001, 'name':xxx, 'institution': xxx}, ...]
    """
    try:
        cql = "Match(agent:Agent{id:%d})-[r:knows]->(teacher:Teacher{school:'%s'}) " \
              "return r.visited as visited, r.activity as activity, teacher.id as t_id, " \
              "teacher.name as name, teacher.institution as institution" % (agent_id, school)
        
        neo = NeoOperator(**NEO4J_CONFIG).get_connection()
        return neo.run(cql).data()
    except Exception as e:
        print("in get_school_relation_with_agent and reason is: %s" % e)
        return []


def create_agent_node(agent_id, name, agent_type, charge=None):
    """
    插入商务信息到图数据库中
    :param agent_id: 商务id
    :param name: str 商务名
    :param agent_type: int 商务类型 0 -> 高校商务， 1 -> 企业商务
    :param charge: string 负责区域，高校商务为 具体学校， 企业商务为 所负责地区
    :return: dict {success: True / False, message: xxx}
    """
    if agent_id and name and agent_type and charge:
        return NeoOperator(**NEO4J_CONFIG).create_node("Agent", id=agent_id, name=name, type=agent_type, charge=charge)
    
    return {"success": False, "message": "缺少必要参数"}


def modify_agent_node(id=None, **data):
    """
    修改商务数据
    :param id: teacher_id
    :param data: dict 要修改的属性
    :return: dict {success: True / False, message: xxx}
    """
    # 允许修改的属性
    allowed_key = {"name", "charge", "type"}
    
    return NeoOperator(**NEO4J_CONFIG).modify_node("Teacher", id=id, allowed_keys=allowed_key, **data)


def create_teacher_node(teacher_id=None, name=None, school=None, institution=None, dept=None, code=None):
    """
    创建教师节点
    :param teacher_id:
    :param name:
    :param school:
    :param institution:
    :param dept: 所属 系 / 研究所
    :param code: 所属学科
    :return: {success: True/ False, messgage: xxx}
    """

    if not (teacher_id and name and school and institution):
        return {"success": False, "message": "必要数据不能为空"}
    return NeoOperator(**NEO4J_CONFIG).create_node("Teacher", id=teacher_id, name=name, school=school, 
                        institution=institution, dept=dept,code=code)


def modify_teacher_node(id=None, **data):
    """
    修改教师数据
    :param id: teacher_id
    :param data: dict 要修改的属性
    :return: dict {success: True / False, message: xxx}
    """
    # 允许修改的属性
    allowed_key = {"school", "institution", "dept", "code", "name"}
    
    return NeoOperator(**NEO4J_CONFIG).modify_node("Teacher", id=id, allowed_keys=allowed_key, **data)


def create_company_node(company_id=None, name=None, location=None):
    """
    创建/修改 企业节点数据
    :param company_id: int 企业id
    :param name: string 企业名
    :param location: string 企业所在地 eg: 昆山
    :param create: 创建(True)/ 修改(False) 节点
    :return: {success: True/False, message: xxx}
    """
    if company_id and name and location:
        
        return NeoOperator(**NEO4J_CONFIG).create_node("Company", id=company_id, name=name, location=location)
    return {"success": False, "message": "缺少必要参数"}


def modify_company_node(company_id=None, **data):
    """
    修改企业节点属性
    :param company_id: int
    :param data: dict 要修改的属性
    :return: dict {success: True / False, message: xxx}
    """
    # 允许修改的属性
    allowed_key = {"location", "name"}
    return NeoOperator(**NEO4J_CONFIG).modify_node("Company", id=company_id, allowed_keys=allowed_key, **data)


def upsert_relation_of_agent2agent(source_id, target_id):
    """
    商务间的关系类型: 协作 -> cooperation
    创建/更新 商务与 其他商务 间的关系
    :param source_id: int 商务id
    :param target_id: int 商务id
    :return: dict {success: True / False, message: xxx}
    """
    
    return NeoOperator(**NEO4J_CONFIG).upsert_relation("Agent", source_id, "Agent", target_id, "knows", cooperation=1)


def upsert_relation_of_agent2teacher(agent_id, teacher_id, is_visit=True):
    """
    创建/更新 商务与教师间的关系
    :param agent_id: int 商务id
    :param teacher_id: int 教师id
    :param is_visit: bool 关系类型，True ==> 拜访（默认）， False ==> 参与活动
    :return: dict {success: True / False, message: xxx}
    """
    visited, activity = 0, 0

    if is_visit:
        visited = 1
    else:
        activity = 1
    return NeoOperator(**NEO4J_CONFIG).upsert_relation("Agent", agent_id, "Teacher", teacher_id, "knows", 
                    visited=visited, activity=activity)


def upsert_relation_of_agent2company(agent_id, company_id, rel_type=1):
    """
    创建/更新 商务与企业间的关系
    :param agent_id: int 商务id
    :param teacher_id: int 企业id
    :param rel_type: int 关系类型, 1 ==> 拜访(默认), 2 ==> 陪同教师拜访, 3==> 参与活动
    :return: dict {success: True / False, message: xxx}
    """
    visited, accompany, activity = 0, 0, 0
    # 拜访
    if rel_type == 1:
        visited = 1
    # 陪同拜访
    elif rel_type == 2:
        accompany = 1
    # 组织参与活动
    else:
        activity = 1

    return NeoOperator(**NEO4J_CONFIG).upsert_relation("Agent", agent_id, "Company", company_id, "knows", 
                    visited=visited, accompany=accompany, activity=activity)


def upsert_relation_of_teacher2teacher(source_id, target_id, paper=0, patent=0, project=0, award=0):
    """
    创建/修改 老师与老师的关系，其关系名为: 学术合作
        属性包括: paper(论文合作数据), patent(专利合作次数), project(项目合作次数), award(合作获奖次数)
    :param source_id: int 教师id
    :param target_id: int 企业id
    :param paper, patent, project, award 属性值
    :return: {"success": True / False}
    """

    return NeoOperator(**NEO4J_CONFIG).upsert_relation(label_s="Teacher", source_id=source_id, label_t="Teacher", 
                        target_id=target_id, rel_type="学术合作", paper=paper, patent=patent, project=project, award=award)


def upsert_relation_of_teacher2company(teacher_id, company_id, is_visit=True):
    """
    创建/修改 老师与企业的关系，其中关系分为： 商业合作， 参观/交流， 两类， 重要性依次降低， 点头之交则忽略
    :param teacher_id: int 教师id
    :param company_id: int 企业id
    :param is_visit: 关系类型： False ==> 商业合作，True ==> 参观/交流
    :return: {"success": True / False}
    """

    if is_visit:
        cooperation = 0
        visited = 1
    else:
        cooperation = 1
        visited = 0

    return NeoOperator(**NEO4J_CONFIG).upsert_relation(label_s="Teacher", source_id=teacher_id, label_t="Company", 
                        target_id=company_id, rel_type="knows", cooperation=cooperation, visited=visited)


if __name__ == '__main__':
    # get_teacher_central_network(153727)

    pass