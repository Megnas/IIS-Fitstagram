from flask import Blueprint, render_template, abort
from flask_login import current_user

from .user_manager import get_user
from .post_manager import get_accessible_posts

bp = Blueprint('view', __name__)

@bp.route("/")
def index():
    posts = get_accessible_posts(current_user)
    return render_template("index.html", posts=posts)

@bp.route("/profile/<int:user_id>")
def profile(user_id):
    user = get_user(user_id)
    if(user):
        return render_template("profile.html", p_user=user)
    else:
        abort(404, description="User does not exists.")