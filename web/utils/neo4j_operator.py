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
