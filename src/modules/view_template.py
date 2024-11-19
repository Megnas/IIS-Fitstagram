from flask import Blueprint, render_template, abort

from .user_manager import get_user

bp = Blueprint('view', __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/profile/<int:user_id>")
def profile(user_id):
    user = get_user(user_id)
    if(user):
        return render_template("profile.html", p_user=user)
    else:
        abort(404, description="User does not exists.")