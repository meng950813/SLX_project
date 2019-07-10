from flask import Blueprint, render_template, session

from web.blueprints.auth import login_required


reminder_bp = Blueprint("reminder", __name__)


@reminder_bp.route('/info_reminder')
@login_required
def info_reminder():
    """
    进入消息提醒页面
    :return:
    """
    session['info_num'] = ""
    return render_template("info_reminder.html")
