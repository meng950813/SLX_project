from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from flask_moment import Moment
from flask_mail import Mail

bootstrap = Bootstrap()
csrf = CSRFProtect()
moment = Moment()
mail = Mail()
