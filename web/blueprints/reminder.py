from flask import Blueprint, render_template, session, request

from web.blueprints.auth import login_required
from web.service import message_service

import json, time

reminder_bp = Blueprint("reminder", __name__)



@reminder_bp.route('/info_reminder')
@login_required
def info_reminder():
    import datetime
    """
    进入消息提醒页面
    :return:
    """
    session['message_num'] = 0
    message = message_service.search_message_info(session['uid'])
    unchecked_message = []
    checked_message = []
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    message1 = []
    for i in message:
        message1.append(i)
    for i in range(0,len(message1)):
        if message1[i]['date'][0:10] == str(yesterday):
            message1[i]['date'] = '昨天 '+ message1[i]['date'][11:]
    for i in message1:
        if i['state'] == 1:
            checked_message.append(i)
        else:
            unchecked_message.append(i)
    message_service.update_massgae_state(session['uid'])
    return render_template("info_reminder.html",checked_message=checked_message[0:5],unchecked_message=unchecked_message)

@reminder_bp.route('/add_message')
@login_required
def insert_message():
    state = 0
    date = str(time.strftime("%Y-%m-%d %H:%M:%S"))
    from_id = session['uid']
    from_name = session['username']
    username = request.form.get("receiver")
    detail = request.form.get("content")
    user_id = message_service.get_user_id(username)
    message = {
        'state': state,
        'date': date,
        'from_id': from_id,
        'from_name' : from_name,
        'user_id' : user_id,
        'detail': detail
    }
    try:
        message_service.insert_message(message)
        return json.dumps({"success": True, "message": "操作成功"})
    except BaseException:
        return json.dumps({"success": False, "message": "操作失败"})
