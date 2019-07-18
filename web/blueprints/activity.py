from flask import Blueprint, render_template


from web.forms import ActivityForm


activity_bp = Blueprint('activity', __name__)


@activity_bp.route('/', methods=['GET', 'POST'])
def add_activity():
    form = ActivityForm()
    if form.validate_on_submit():
        pass

    return render_template('activity/new_activity.html', form=form)
