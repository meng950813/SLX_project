from flask import Blueprint, render_template, session, request
from web.service.basic_info_service import search_teacher_basic_info
import datetime
import json

from web.blueprints.auth import login_required
from web.utils.mongo_operator import MongoOperator
from web.config import MongoDB_CONFIG

scholar_bp = Blueprint('scholar', __name__)


@scholar_bp.route('/scholar/<int:teacher_id>')
@login_required
def scholar_info(teacher_id):
    """
    专家个人信息
    :param teacher_id:
    :return:
    """
    # 返回json 序列化后的文件
    teacher_basic_info = search_teacher_basic_info(teacher_id)
    length = [0, 0]

    # 计算该教师所拥有的基金的数目，并将其加到列表中，用以传送给前端
    if "funds" in teacher_basic_info:
        length[0] = len(teacher_basic_info["funds"])

    # 计算该教师所拥有的专利
    if "patent" in teacher_basic_info:
        length[1] = len(teacher_basic_info["patent"])

    # 计算教师年龄
    birth_year = teacher_basic_info["birth_year"]
    if birth_year == " ":
        age = " "
    else:
        year = datetime.datetime.now().year
        age = year - int(birth_year)

    return render_template('detail.html', teacher_basic_info=teacher_basic_info, length=length, age=age)


@scholar_bp.route('/feedback', methods=['POST'])
@login_required
def agent_feedback():
    """
    保存商务反馈的信息
    :return:
    """
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    
    back = mongo_operator.db['agent_feedback'].insert_one(
        {
            "user_id": session['uid'],
            'title': request.form.get('title'),
            'type': request.form.get('type'),
            'target': request.form.get('target'),
            'content': request.form.get('content').replace("\n","<br>"),
            "status": 0
        })
    
    print(back.inserted_id)
    if back.inserted_id:
        return json.dumps({'success': True})
    return json.dumps({"success": False})


if __name__ == '__main__':
    pass
