from flask import Blueprint, abort, render_template, redirect, url_for
from flask_login import login_required, current_user

from .db import Roles, User, db

bp = Blueprint('admin', __name__)

@bp.route('/admin')
@login_required
def admin():
    if not(current_user.role == Roles.MODERATOR or current_user.role == Roles.ADMIN):
        abort(401, description="Not allowed")
    return render_template("admin.html")

@bp.route('/admin/users')
@login_required
def admin_users():
    if not(current_user.role == Roles.MODERATOR or current_user.role == Roles.ADMIN):
        abort(401, description="Not allowed")

    blocked_users = User.query.filter_by(blocked=True).all()
    not_blocked_users = User.query.filter_by(blocked=False).all()

    return render_template("admin_users.html", blocked_users=blocked_users, not_blocked_users=not_blocked_users)

@bp.route('/admin_block/<int:user_id>', methods=['POST'])
def admin_block(user_id):
    if not(current_user.role == Roles.MODERATOR or current_user.role == Roles.ADMIN):
        abort(401, description="Not allowed")
    user = User.query.get_or_404(user_id)
    user.blocked = not user.blocked
    db.session.commit()
    return redirect(url_for('admin.admin_users'))