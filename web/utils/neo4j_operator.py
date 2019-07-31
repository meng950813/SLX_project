# -*- coding: UTF-8 -*-

from py2neo import Graph, Relationship, Node


class NeoOperator(object):

    def __init__(self, host, port, username, password):
        """
        创建连接
        :param host:
        :param port:
        :param username:
        :param password:
        :return:
        """
        self.neo = Graph(host=host, port=port, username=username, password=password)

    def get_relation_with_agent(self, agent_id, school=None, institution=None, teacher_id=None):
        """
        根据传入的商务id， 获取对应范围内的关系数据， TODO
        范围包括 学校级， 学院级， 个人级
        :param agent_id: int 商务id
        :param school: str 学校名
        :param institution: str 学院名
        :param teacher_id: int 教师id
        :return: TODO
        """
        # 无商务id
        if not agent_id:
            return False

        # 获取以 teacherId 为核心的关系网络
        if teacher_id and school and institution:
            self.get_personal_relation_with_agent(agent_id, teacher_id)
        # 获取当前学院的关系网络
        elif school and institution:
            self.get_institution_relation_with_agent(agent_id, school, institution)
        # 获取商务在当前学校建立的关系网络
        elif school:
            self.get_school_relation_with_agent(agent_id, school)
        else:
            return False

    def get_personal_relation_with_agent(self, agent_id, teacher_id):
        """
        获取当前商务在该教师的个人网络中的位置
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
            cql = "Match(source:Teacher{id:%d})-[r:学术合作]-(target:Teacher) return source,r, target" % teacher_id
            back = self.neo.run(cql).data()

            cql = "Match(agent:Agent{id:%d})-[r:knows]-(t:Teacher)-[:学术合作]-(s:Teacher{id:%d})" \
                  " return agent.id as agent_id, r.visited as visited, r.activity as activity, t.id as t_id " \
                  % (agent_id, teacher_id)

            agent_relation = self.neo.run(cql).data()
            # return self.neo.run(cql).data()
            return {"relation": back, "agent_relation": agent_relation}
        except Exception as e:
            print("in get_personal_relation_with_agent and reason is: %s" % e)
            return []
        pass

    def get_institution_relation_with_agent(self, agent_id, school, institution):

        """
        获取当前商务在该学院中的社交网络 --> 学院内部社交数据已有文件
        :param agent_id: int
        :param school: str
        :param institution: str
        :return:[{visited: xxx, activity: xxx, id:13213},...]
        """
        try:
            # s_id ==> source_id, t_id ==> target_id
            # cql = """Match(t1:Teacher{school:'%s', institution:'%s'})-[r]-(t2 :Teacher{school:'%s', institution:'%s'})
            #     return t1.id as s_id, t1.name as s_name,
            #     r.paper as paper, r.patent as patent, r.project as project,
            #     t2.id as t_id, t2.name as t_name"""\
            #     % (school, institution, school, institution)
            #
            # # list ==> [{s_id: xxx, s_name: xxx, t_id: 99332, t_name: xxx, paper:0, patent:0, project:0},...] or []
            # institution_relation = self.neo.run(cql).data()

            agent_cql = """Match(ag:Agent{id:%d})-[r:knows]->(t:Teacher{school:'%s', institution:'%s'})
                return r.visited as visited, r.activity as activity, t.id as id""" \
                        % (agent_id, school, institution)

            # list ==> [{agent_id: xxx, visited: xxx, activity: xxx, t_id:13213},...] or []
            agent_relation = self.neo.run(agent_cql).data()
            # return {"relation": institution_relation, "agent_relation": agent_relation}
            return agent_relation

        except Exception as e:
            print("in get_institution_relation_with_agent and reason is: %s" % e)
            return []
        pass

    def get_school_relation_with_agent(self, agent_id, school):
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
            return self.neo.run(cql).data()
        except Exception as e:
            print("in get_school_relation_with_agent and reason is: %s" % e)
            return []

    def get_teacher_central_network(self, teacher_id, school=None):
        """
        获取某一教师社交网络
        :param teacher_id: int
        :param school:
        :return: [] or
        """
        try:
            if school:
                cql = "Match(n:Teacher{id:%d})-[:学术合作]-(m:Teacher{school:%s}) " \
                      "return n.name as s_name, n.school as s_school, n.institution as s_institution," \
                      "r.paper as paper, r.patent as patent, r.project as project," \
                      "m.name as name, m.school as school, m.institution as institution" \
                      % (teacher_id, school)
            else:
                cql = "Match(n:Teacher{id:%d})-[r:学术合作]-(m:Teacher) " \
                      "return n.name as s_name, n.school as s_school, n.institution as s_institution," \
                      "r.paper as paper, r.patent as patent, r.project as project," \
                      "m.name as name, m.school as school, m.institution as institution" % teacher_id

            result = self.neo.run(cql).data()
            return result
        except Exception as e:
            print(e)

    def create_agent_node(self, agent_id, name, agent_type, charge=None):
        """
        插入商务信息到图数据库中
        :param agent_id: 商务id
        :param name: str 商务名
        :param agent_type: int 商务类型 0 -> 高校商务， 1 -> 企业商务
        :param charge: string 负责区域，高校商务为 具体学校， 企业商务为 所负责地区
        :return: dict {success: True / False, message: xxx}
        """
        if agent_id and name and agent_type and charge:
            return self.create_node("Agent", id=agent_id, name=name, type=agent_type, charge=charge)
        return {"success": False, "message": "缺少必要参数"}

    def modify_agent_node(self, id=None, **data):
        """
        修改商务数据
        :param id: teacher_id
        :param data: dict 要修改的属性
        :return: dict {success: True / False, message: xxx}
        """
        # 允许修改的属性
        allowed_key = {"name", "charge"}
        return self.modify_node("Teacher", id=id, allowed_keys=allowed_key, **data)

    def create_teacher_node(self, teacher_id=None, name=None, school=None, institution=None,dept=None, code=None):
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

       return self.create_node("Teacher", id=teacher_id, name=name, school=school,institution=institution, dept=dept, code=code)

    def modify_teacher_node(self, id=None, **data):
        """
        修改教师数据
        :param id: teacher_id
        :param data: dict 要修改的属性
        :return: dict {success: True / False, message: xxx}
        """
        # 允许修改的属性
        allowed_key = {"school", "institution", "dept", "code", "name"}

        return self.modify_node("Teacher", id=id, allowed_keys=allowed_key, **data)

    def create_company_node(self, company_id=None, name=None, location=None):
        """
        创建/修改 企业节点数据
        :param company_id: int 企业id
        :param name: string 企业名
        :param location: string 企业所在地 eg: 昆山
        :param create: 创建(True)/ 修改(False) 节点
        :return: {success: True/False, message: xxx}
        """
        if company_id and name and location:
            return self.create_node("Company", id=company_id, name=name, location=location)
        return {"success": False, "message": "缺少必要参数"}

    def modify_company_node(self, company_id=None, **data):
        """
        修改企业节点属性
        :param company_id: int
        :param data: dict 要修改的属性
        :return: dict {success: True / False, message: xxx}
        """
        # 允许修改的属性
        allowed_key = {"location", "name"}
        return self.modify_node("Company", id=company_id, allowed_keys=allowed_key, **data)

    def upsert_relation_of_agent2agent(self, source_id, target_id, is_visit=True):
        """
        TODO 商务间的关系类型
        创建/更新 商务与 其他商务 间的关系
        :param source_id: int 商务id
        :param target_id: int 商务id
        :param is_visit: bool 关系类型，True ==> 拜访（默认）， False ==> 参与活动
        :return: dict {success: True / False, message: xxx}
        """
        if is_visit:
            visited = 1
            activity = 0
        else:
            visited = 0
            activity = 1
        # TODO
        # return self.upsert_relation("Agent", source_id, "Agent", target_id, "knows", visited=visited, activity=activity)

    def upsert_relation_of_agent2teacher(self, agent_id, teacher_id, is_visit=True):
        """
        创建/更新 商务与教师间的关系
        :param agent_id: int 商务id
        :param teacher_id: int 教师id
        :param is_visit: bool 关系类型，True ==> 拜访（默认）， False ==> 参与活动
        :return: dict {success: True / False, message: xxx}
        """
        if is_visit == 1:
            visited = 1
            activity = 0
        else:
            visited = 0
            activity = 1
        return self.upsert_relation("Agent", agent_id, "Teacher", teacher_id, "knows", visited=visited, activity=activity)

    def upsert_relation_of_teacher2company(self, teacher_id, company_id, is_visit=True):
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

        return self.upsert_relation(label_s="Teacher", source_id=teacher_id, label_t="Company", target_id=company_id,
                                    rel_type="knows", cooperation=cooperation, visited=visited)

    """
     对外接口
     -----------------------------------------------------------------------------------------------------------------
     对内API
    """
    def get_connection(self):
        return self.neo

    def create_node(self, label=None, **data_dict):
        """
        创建节点
        :param label: 表名
        :param data_dict: 具体数据，键值对
        :return: dict {success: True / False, message: xxx}
        """
        try:
            label_set = {"Agent", "Teacher", "Company"}
            if "id" not in data_dict:
                return {"success": False, "message": "缺少关键参数id"}

            if label not in label_set:
                return {"success": False, "message": "表名不正确"}

            # node ==> None or Node type object
            node = self.neo.nodes.match(label, id=data_dict['id']).first()

            if node is not None:
                return {"success": False, "message": "节点已存在"}

            node = Node(label, **data_dict)
            # create 函数无返回值 ==> 执行成功返回 None, 失败进入 except
            self.neo.create(node)
            return {"success": True}
        except Exception as e:
            print(e)
            return {"success": False, "message": "节点创建失败，原因：%s" % e}

    def modify_node(self, label=None, id=None, allowed_keys={}, **data_dict):
        """
        修改节点属性
        :param label: 表名
        :param id: int
        :param allowed_keys: dict / set 允许修改的属性名
        :param data_dict: 要修改的字典数据
        :return:{success: True/ False, message: xxx}
        """
        try:
            label_set = {"Agent", "Teacher", "Company"}
            if not id:
                return {"success": False, "message": "缺少关键参数id"}

            if label not in label_set:
                return {"success": False, "message": "表名不正确"}

            # node ==> None or Node type object
            node = self.neo.nodes.match(label, id=id).first()

            if node is None:
                return {"success": False, "message": "节点不存在"}

            for key, value in data_dict.items():
                if key not in allowed_keys:
                    return {"success": False, "message": "出现错误的属性名 %s" % key, "allowed_keys": allowed_keys}
                node[key] = value
            # 更新数据，无返回值
            self.neo.push(node)

        except Exception as e:
            print(e)
            return {"success": False, "message": "修改节点属性失败，原因：%s" % e}

    def upsert_relation(self, label_s=None, source_id=None, label_t=None, target_id=None, rel_type=None, **data):
        """
        创建/修改两节点间的关系
        :param label_s: 起始节点所在表： Agent / Teacher / Company
        :param source_id: 起始节点 id
        :param label_t: 目标节点所在表： Agent / Teacher / Company
        :param target_id: 目标节点 id
        :param rel_type: str 关系类型
        :param data: dict 具体参数
        :return: dict {success: True/ False, message: xxx}
        """
        try:
            if not(label_s and source_id and label_t and target_id and rel_type and len(data) > 0):
                return {"success": False, "message": "缺少必要参数"}

            source = self.neo.nodes.match(label_s, id=source_id).first()
            if source is None:
                return {"success": False, "message": "source id 有误"}
            target = self.neo.nodes.match(label_t, id=target_id).first()
            if target is None:
                return {"success": False, "message": "target id 有误"}

            rel = self.neo.match(nodes=(source, target), r_type=rel_type).first()
            if rel is None:
                rel = self.neo.match(nodes=(target, source), r_type=rel_type).first()
            if rel is None:
                relation = Relationship(source, rel_type, target, **data)
                self.neo.create(relation)
                return {"success": True, "message": "关系创建成功"}
            else:
                for key, value in data.items():
                    rel[key] += int(value)
                self.neo.push(rel)
                return {"success": True, "message": "关系更新成功"}
        except Exception as e:
            print(e)
            return {"success": False, "message": "创建关系失败"}

    def del_relation(self, label_s=None, source_id=None, label_t=None, target_id=None, rel_type=None):
        """
        删除节点间属性
        :param label_s:
        :param source_id:
        :param label_t:
        :param target_id:
        :param rel_type:
        :return: dict {"success": True/False, "message": "xxx"}
        """
        try:
            if not(label_s and source_id and label_t and target_id and rel_type):
                return {"success": False, "message": "缺少必要参数"}

            # 删除节点间关系
            cql = "Match(:%s{id:%d})-[r:%s]-(:%s{id:%d}) delete r" % (label_s, source_id, rel_type, label_t, target_id)

            self.neo.run(cql)
            return {"success": True, "message": "删除成功"}
        except Exception as e:
            print(e)
            return {"success": False, "message": "删除失败"}


if __name__ == '__main__':
    from web.config import NEO4J_CONFIG

    obj = NeoOperator(**NEO4J_CONFIG)
    # obj.create_agent(100000, "杨秀宁", 0)
    # # obj.upsert_agent_relation(100000, 99331)
    # obj.upsert_agent_relation(100000, 86791)
    # obj.upsert_agent_relation(100000, 86831)
    # obj.upsert_agent_relation(100000, 90147)

    # obj.get_school_relation_with_agent(100000, "南京大学")
    # obj.get_institution_relation_with_agent(100000, "中国科学技术大学", "管理学院")
    # obj.get_personal_relation_with_agent(100000, 90147)
    # obj.get_personal_relation_with_agent(100000, 90021)
    # obj.create_node("Agent", id=100001, name="测试节点", type=0)
    # obj.modify_node("Agent", id=100001, allowed_keys={"name", "type"}, name="测试节点_修改", type=0)
    # obj.modify_teacher_node(id=73965, dept="农学系")

    # obj.upsert_relation("Agent", 163544, "Agent", 100001, rel_type="合作", times=1, visited=0)
    # obj.del_relation("Agent", 163544, "Agent", 100001, rel_type="合作")

    obj.get_teacher_central_network(153727)
