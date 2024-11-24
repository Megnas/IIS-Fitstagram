from .groups_manager import (
    get_user_requested_groups,
    get_user_invited_groups,
)
from .invites_manager import (
    approve_group_invite,
    cancel_group_invite,
)
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for
)
from flask_login import login_required, current_user

bp = Blueprint("invites", __name__)

@bp.route("/accept_invite/<int:group_id>")
@login_required
def accept_invite(group_id):
    approve_group_invite(user_id=current_user.id, group_id=group_id)
    return redirect(url_for("invites.invites"))

@bp.route("/cancel_invite/<int:group_id>")
@login_required
def cancel_invite(group_id):
    cancel_group_invite(user_id=current_user.id, group_id=group_id)
    return redirect(url_for("invites.invites"))


@bp.route("/invites")
@login_required
def invites():
    invites = get_user_invited_groups(current_user.id)
    requests = get_user_requested_groups(current_user.id)

    return render_template("invites.html", invites=invites, requests=requests)