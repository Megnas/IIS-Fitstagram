from flask import Blueprint, render_template, abort, request
from flask_login import current_user

from .user_manager import get_user
from .post_manager import get_accessible_posts, get_accessible_posts_tag, get_accessible_posts_user

bp = Blueprint('view', __name__)

@bp.route("/")
def index():
    page = request.args.get('page', 1, type=int)

    posts, tototal, pages = get_accessible_posts(current_user, page=page, per_page=(4 * 6))
    return render_template("index.html", posts=posts, page=page, pages=pages)

@bp.route("/tag")
def tag():
    page = request.args.get('page', 1, type=int)
    tag = request.args.get('tag', None, type=str)
    posts, tototal, pages = get_accessible_posts_tag(current_user, page=page, per_page=(4 * 6), tag=tag)
    return render_template("tag.html", posts=posts, page=page, pages=pages, tag_name=tag)

@bp.route("/profile/<int:user_id>")
def profile(user_id):
    user = get_user(user_id)
    if(user):
        page = request.args.get('page', 1, type=int)

        posts, tototal, pages = get_accessible_posts_user(current_user, page=page, per_page=(4 * 6), profile_id=user.id)
        return render_template("profile.html", p_user=user, posts=posts, page=page, pages=pages)
    else:
        abort(404, description="User does not exists.")