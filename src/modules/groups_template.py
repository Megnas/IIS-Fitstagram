from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import groups_manager

bp = Blueprint("groups", __name__)

@bp.route("/groups", methods=['GET'])
@login_required
def groups():
    try:
        groups = groups_manager.get_all_groups()        
    except Exception as e:
        flash("Could not get all groups", "danger")
        print("get_all_groups() failed")
    return render_template("groups.html")