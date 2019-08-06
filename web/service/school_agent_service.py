"""
用于处理 school_agent.py 中需要的数据
by chen
"""
import json
import os

from web.config import MongoDB_CONFIG
from web.settings import basedir
from web.utils.mongo_operator import MongoOperator
from web.utils.neo4jAPI import *


class SchoolAgentService(object):

    def get_institutions_dict(self, school):
        """
        获取学校所有的学院信息，按 visited 排序
        :param school: str 学校名
        :return: [{"name":xxx, "visited": 132},...] or False
        """
        if not school:
            return {}

        back = MongoOperator(**MongoDB_CONFIG).get_collection("school").find_one({"name": school}, {"institutions": 1})
        if not back or not ("institutions" in back):
            return False

        institutions = back['institutions']
        # 按照学院被点击次数排序 ==> [{"visited":xx, "name":xx}, ...]
        institutions.sort(key=lambda k: k.get("visited"), reverse=True)
        # 取出学院名，转为dict
        return institutions

    def get_institutions_list(self, school):
        """
        获取学校所有的学院信息，按 visited 排序
        :param school: str 学校名
        :return: [xxx,xxx,xxx...] or False
        """
        if not school:
            return []

        institutions = self.get_institutions_dict(school)
        # 取出学院名，转为list
        return [item["name"] for item in institutions]

    def get_relations(self, school, institution):
        """
        获取当前用户与某一学院之中的人员关系及其中的内部社区分布
        :param school: 学校名
        :param institution: 学院名
        :param agent_id: 商务自己建立的联系, [{id:xxx, name: xxx, weight: 123},{...},....]
        :return: 可供echarts直接渲染的json文件 or False
        """
        file_path = os.path.join(basedir, 'web', 'static', 'relation_data', '%s%s.txt' % (school, institution))

        # 判断该学院社区网络文件是否存在
        if not os.path.exists(file_path):
            print("%s %s 的社交网络尚未生成！" % (school, institution))
            return False
        with open(file_path, "r") as f:
            data = json.loads(f.read())
            # print(data)
            
            # agent_relation => [{visited: xxx, activity: xxx, id:13213},...] or []
            # agent_relation = self.get_institutions_relation_data(agent_id, school, institution)

            # relation_data = self.format_institution_relation_data(data, agent_relation)
            relation_data = self.format_institution_relation_data(data)
            return json.dumps(relation_data)

    def get_team(self, school, institution, team_index):
        """
        获取院系的某一个团队
        :param school: 学校的名称
        :param institution: 学院名
        :param team_index: 团队id
        :return: 可供echarts直接渲染的json文件 or False
        """
        file_path = os.path.join(basedir, 'web', 'static', 'relation_data', '%s%s.txt' % (school, institution))

        # 判断该学院社区网络文件是否存在
        if not os.path.exists(file_path):
            print("%s %s 的社交网络尚未生成！" % (school, institution))
            return False

        with open(file_path, "r") as f:
            # 获取所有的相关节点
            data = json.loads(f.read())
            nodes = [node for node in data['nodes'] if node['class'] == team_index]
            ids = [node['teacherId'] for node in nodes]
            # 链接
            links = [link for link in data['edges'] if link['source'] in ids and link['target'] in ids]
            # 覆盖
            data['nodes'], data['edges'] = nodes, links

            relation_data = self.format_institution_relation_data(data)
            return json.dumps(relation_data)

    def format_institution_relation_data(self, data):
        """
        将学院关系数据简化为可发送的数据
        :param data: 预处理过的社区网络数据
        :return: 可供echarts直接渲染的json文件 or False
        """
        try:
            """
                nodes 中舍弃 code, school, insititution, centrality, class 属性, 
                添加 label,symbolSize 属性
                class 属性是指节点所属社区, 从 1 开始
            """
            teacher_id_dict = dict()
            class_id_dict = dict()

            for node in data["nodes"]:
                node['label'], node['name'] = node['name'], str(node['teacherId'])
                node['category'], node["draggable"] = node['class'], True
                node['symbolSize'] = int(node['centrality'] * 30 + 5)

                # 核心节点
                if node['teacherId'] in data["core_node"]:
                    node["itemStyle"] = {
                        "normal": {
                            "borderColor": 'yellow',
                            "borderWidth": 2,
                            "shadowBlur": 10,
                            "shadowColor": 'rgba(0, 0, 0, 0.3)'
                        }
                    }

                    # 保存 class 的种类是为了划分社区 ==> 实现这一功能的前提是 class 值不存在断档
                    # 其值为该社区核心节点 id
                    class_id_dict[str(node["class"])] = node["label"]

                # 保存 teacherId => 判定商务创建的所有关系中有哪些属于当前社区;
                # 以其 class 为值是为了更方便的在隐藏非核心节点时, 将商务与其的关系累加到核心节点上
                teacher_id_dict[node['teacherId']] = node["class"]

                del node["teacherId"], node["class"], node["centrality"], node["code"], node["school"], node["insititution"]

            data["links"] = []
            for link in data["edges"]:
                if "source" not in link or "target" not in link:
                    print("缺少 起点 / 终点：", link)
                else:
                    link["source"], link["target"] = str(link["source"]), str(link["target"])
                    link["value"] = link["weight"]
                    if "weight" in link: del link['weight']
                    data["links"].append(link)

            """
                在生成的社区关系文件中, community_data 中的数据应该是每个社区中的对比数据, 即其 key 应当包含每个class的值
                但有部分数据并非如此, community_data 的 key 并未包括所有 class, 因此不能使用其作为分类的标准
                
                前提: nodes中的class连续 ==> 不会出现 1,2,5,...的情况
                传递社区总数
            """
            data["community"] = len(class_id_dict)

            # 添加商务节点
            # data["nodes"].append(self.create_agent_node())

            # 格式化商务创建的社交关系
            # agent_relation_links, core_node = self.create_agent_relation_links(agent_relation, teacher_id_dict, class_id_dict)

            # data["links"].extend(agent_relation_links)

            # data["core_node"] = core_node
            data["core_node"] = class_id_dict

            if "community_data" in data: del data['community_data']
            if "algorithm_compare" in data: del data['algorithm_compare']
            if "edges" in data: del data['edges']

            return data

        except Exception as e:
            print(e)
            return False

    def create_agent_node(self):
        """
        创建商务的节点
        :return: dict {"":}
        """
        return {
            "name": "0",
            "label": "我",
            "category": 0,
            # 'circle', 'rect', 'roundRect', 'triangle', 'diamond', 'pin', 'arrow', 'none'
            "symbol": "diamond",
            "draggable": True,
            "symbolSize": 36,
            "itemStyle": {
                "normal": {
                    "borderColor": 'white',
                    "borderWidth": 2,
                    "shadowBlur": 6,
                    "shadowColor": 'rgba(0, 0, 0, 0.3)'
                }
            }
        }

    def create_agent_relation_links(self, data, teacher_dict, class_dict):
        """
        创建商务与当前学院中老师的关系
        :param data: 商务创建的所有联系, [{id:xxx, visited: 123, activity:123 },{...},....]
        :param teacher_dict: dict 当前学院的教师id列表, 值为其所属社区号
        :param class_dict: dict 当前学院中的社区号, 值为其中核心节点的 teacherId
        :return: tuple (
                [{source:"0",target:"xxx",normal:{lineStyle:{width:...}}}],
                {"core_node_teacherId": totalWeight}
            )
        """
        back = []

        # 用于保存商务与该社区所有老师的关系之和
        # 格式为: {"core_node_teacherId": totalWeight}
        core_node = {}

        for item in data:
            if item.get("id") not in teacher_dict:
                continue

            info = {
                "source": "0",
                "target": str(item['id']),
                "visited": item['visited'],
                "activity": item['activity'],
                "lineStyle": {
                    "normal": {
                        # TODO 根据拜访次数设定连线宽度
                        "width": 5
                    }
                }
            }
            back.append(info)

            # 防止取不到值
            try:
                core_teacher = class_dict[teacher_dict[item['id']]]
                if core_teacher in core_node:
                    core_node[core_teacher]["visited"] += item["visited"]
                    core_node[core_teacher]["activity"] += item["activity"]
                else:
                    core_node[core_teacher] = {
                        "visited" : item["visited"],
                        "activity" : item["activity"]
                    }
            except Exception as e:
                print("取不到正确的值")
                print(e)

        return back, core_node

    def create_agent_relation_with_core_node(self, core_node):
        """
        创建商务与每个社区核心节点的关系, 该关系为商务与该社区中非核心节点关系的总和
        :param core_node: dict 商务与核心节点的关系权重, 格式为: {"teacherId": weight, ...}
        :return: list [{source:"0",target:"xxx", "core": True, normal:{lineStyle:{width:...}}}]
        """
        back = []
        for teacherId, weight in core_node.items():
            back.append({
                "source": "0",
                "target": "-" + str(teacherId),
                "visited": "共" + str(weight),
                "core": True,
                "lineStyle": {
                    "normal": {
                        # TODO 根据拜访次数设定连线宽度
                        "width": 10
                    }
                }
            })

        return back

    def add_institution_click_time(self, school, institution):
        """
        更新指定学院的点击次数 +1
        :param school: 学校名
        :param institution: 学院名
        :return:
        """
        try:
            # back => {'_id': ObjectId('xxx'), 'institutions': [{'visited': 2, 'name': '公共卫生学院'}]}
            back = MongoOperator(**MongoDB_CONFIG).get_collection("school").find_one(
                {"name": school, "institutions.name": institution}, {"institutions.$.visited": 1})
            visited = int(back['institutions'][0]["visited"]) + 1
            # 该学院增加一次点击
            MongoOperator(**MongoDB_CONFIG).get_collection("school").update_one(
                {"name": school, "institutions.name": institution}, {"$set": {"institutions.$.visited": visited}})
        except Exception as e:
            print("点击次数加一失败， visited=%s")
            print(e)

    def format_personal_relation_data(self, data):
        """
        格式化个人中心网络，生成 echarts 能渲染的数据格式
        :param data: {
            "relation": [
                {
                    source: {id, name, school, institution, code},
                    r:{paper, patent, project},
                    target: {id, name, school, institution, code}
                }, ... ],
            "agent_relation": [{agent_id: xxx, visited: xxx, activity: xxx, t_id:13213},...]
        }
        :return:
        """
        back = {
            "nodes": [self.create_agent_node()],
            "links": [],
            "community": 2
        }

        # 若以该教师为核心的网络为空 ==> 只返回商务节点, 教师节点由前端生成
        if len(data['relation']) == 0:
            back['community'] = 1

        teacher_id_set = set()

        for item in data["relation"]:
            source, r, target = item['source'], item['r'], item['target']

            if source['id'] not in teacher_id_set:
                teacher_id_set.add(source[id])
                back['nodes'].append(
                    {"name": str(source['id']), "label": source['name'], "category": 1, "draggable": True})

            if target['id'] not in teacher_id_set:
                teacher_id_set.add(target['id'])
                back['nodes'].append(
                    {"name": str(target['id']), "label": target["name"], "category": 2, "draggable": True})

            back['links'].append({"source": str(source['id']), "target": str(target["id"]), "paper": r['paper'],
                                  "patent": r['patent'], "project": r['project']})

        for item in data['agent_relation']:
            back['links'].append({"source": "0", "target": str(item["t_id"]),
                                  "visited": item['visited'], "activity": item['activity']})

        return back

    def get_agent_relation_in_institution(self, agent_id, school, institution):
        # data ==> [{visited: xxx, activity: xxx, id:13213},...]
        data = get_institution_relation_with_agent(agent_id, school, institution)

        return data
    
    def get_agent_relation_in_school(self, agent_id, school):
        """
        获取商务在该学校建立的社交关系数据
        :param agent_id:
        :param school:
        :return:{
            "nodes": [{name, label, institution}, ...],
            "links": [{source, target, visited, activity}],
             "community": 123
        }
        """
        # data => [] or [{'visited': 1, 'activity': 0, 't_id': 001, 'name':xxx, 'institution': xxx}, ...]
        data = get_school_relation_with_agent(agent_id, school)

        return self.format_school_relation_data(data)

    def format_school_relation_data(self, data):
        """
        格式化商务在该学校建立的社交网络，生成 echarts 能渲染的数据格式
        :param data: list of dict ==>
            [] or [{'visited': 1, 'activity': 0, 't_id': 001, 'name':xxx, 'institution': xxx}, ...]
        :return:
        """
        back = {
            "nodes": [self.create_agent_node()],
            "links": []
        }

        institutions_dict, index = {}, 1
        for item in data:
            node = {"name": str(item['t_id']), "label": item['name'], "symbolSize": 30,
                    "draggable": True, "institution": item['institution']}

            if item['institution'] not in institutions_dict:
                institutions_dict[item['institution']] = index
                index += 1

            node["category"] = institutions_dict[item['institution']]

            back['nodes'].append(node)
            back['links'].append({"source": "0", "target": str(item['t_id']), "visited": item['visited'],
                                  "activity": item['activity']})
        
        back["institutions"] = [k for k in institutions_dict.keys()]
        return back


agent_service = SchoolAgentService()
