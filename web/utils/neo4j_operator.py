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
                " return agent.id as agent_id, r.visited as visited, r.activity as activity, t.id as t_id "\
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
                return r.visited as visited, r.activity as activity, t.id as id"""\
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
                  "return r.visited as visited, r.activity as activity, teacher.id as t_id, "\
                  "teacher.name as name, teacher.institution as institution" % (agent_id, school)
            return self.neo.run(cql).data()
        except Exception as e:
            print("in get_school_relation_with_agent and reason is: %s" % e)
            return []

    def create_agent(self, agent_id, name, agent_type):
        """
        插入商务信息到图数据库中
        :param agent_id: 商务id
        :param name: str 商务名
        :param agent_type: int 商务类型 0 -> 高校商务， 1 -> 企业商务
        :return: dict {success: True / False, message: xxx}
        """
        try:
            agent_node = Node("Agent", id=agent_id, name=name, type=agent_type)
            # create 函数无返回值 ==> 执行成功返回 None, 失败进入 except
            self.neo.create(agent_node)
            return {"success": True}
        except Exception as e:
            print(e)
            return {"success": False, "message": "用户 %d 已存在，请不要重复" % agent_id}

    def upsert_agent_relation(self, agent_id, teacher_id, is_visit=True):
        """
        创建/更新 商务与教师间的关系 => TODO：创建/更新商务与企业的关系 & 创建/更新教师与企业的关系
        :param agent_id: int 商务id
        :param teacher_id: int 教师id
        :param is_visit: bool 关系类型，True ==> 拜访（默认）， False ==> 参与活动
        :return: dict {success: True / False, message: xxx}
        """
        try:
            # 查找节点，若无，返回 None
            agent = self.neo.nodes.match("Agent", id=agent_id).first()
            if agent is None:
                return {"success": False, "message": "%d 商务不存在" % agent_id}

            teacher = self.neo.nodes.match("Teacher", id=teacher_id).first()
            if teacher is None:
                return {"success": False, "message": "%d 教师不存在" % teacher_id}

            # 查找现有关系，若无，返回 None
            match = self.neo.match(nodes=(agent, teacher), r_type="knows").first()
            # 在已有关系上修改
            if match:
                if is_visit == 1:
                    match['visited'] += 1
                else:
                    match["activity"] += 1
                # 更新数据，无返回值
                self.neo.push(match)
            else:
                if is_visit == 1:
                    match = Relationship(agent, "knows", teacher, visited=1, activity=0)
                else:
                    match = Relationship(agent, "knows", teacher, visited=0, activity=1)
                # 创建关系，无返回值
                self.neo.create(match)

            return {"success": True}
        except Exception as e:
            print(e)
            return {"success": False, "message": ""}


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
    obj.get_personal_relation_with_agent(100000, 90147)
    # obj.get_personal_relation_with_agent(100000, 90021)