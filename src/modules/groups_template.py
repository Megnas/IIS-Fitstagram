from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import groups_manager
from flask_wtf import FlaskForm

bp = Blueprint("groups", __name__)

class GroupsForm(FlaskForm):
    name = ""

@bp.route("/groups", methods=['GET'])
@login_required
def groups():
    try:
        groups = groups_manager.get_all_groups()        
    except Exception as e:
        flash("Could not get all groups", "danger")
        print("get_all_groups() failed")
    return render_template("groups.html")

@bp.route("/create_group", methods=['GET', 'POST'])
@login_required
def create_group():
    try:
        groups = groups_manager.get_all_groups()        
    except Exception as e:
        flash("Could not get all groups", "danger")
        print("get_all_groups() failed")
    return render_template("groups.html")