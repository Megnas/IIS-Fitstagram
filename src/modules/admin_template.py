from flask import Blueprint, abort
from flask_login import login_required, current_user

from .db import Roles

bp = Blueprint('admin', __name__)

@bp.route('/admin')
@login_required
def admin():
    if not(current_user.role == Roles.MODERATOR or current_user.role == Roles.ADMIN):
        abort(401, description="Not allowed")
    return "hello"