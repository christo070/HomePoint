from flask import Blueprint, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from functools import wraps

main = Blueprint("main", __name__)
auth = Blueprint("auth", __name__)
user = Blueprint("user", __name__)
admin = Blueprint("admin", __name__)
professional = Blueprint("professional", __name__)
customer = Blueprint("customer", __name__)

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Decorators to make sure the user is of the correct role
def admin_user(f):
    @wraps(f)
    def assign_user_role(*args, **kwargs):
        if current_user.role != "admin":
            return redirect(url_for("user.dashboard"))
        return f(*args, **kwargs)

    return assign_user_role


def professional_user(f):
    @wraps(f)
    def assign_user_role(*args, **kwargs):
        if current_user.role != "professional":
            return redirect(url_for("user.dashboard"))
        return f(*args, **kwargs)

    return assign_user_role


def customer_user(f):
    @wraps(f)
    def assign_user_role(*args, **kwargs):
        if current_user.role != "customer":
            return redirect(url_for("user.dashboard"))
        return f(*args, **kwargs)

    return assign_user_role


from .main import *
from .auth import *
from .user import *
from .admin import *
from .professional import *
from .customer import *
