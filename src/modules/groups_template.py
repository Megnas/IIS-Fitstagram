from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import groups_manager
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

bp = Blueprint("groups", __name__)

class GroupForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=1, max=64)])
    description = StringField("Description")
    photo = FileField(
        "Group Image",
        validators=[FileAllowed(["jpg", "jpeg", "png"], "Images only!")]
    )
    visibility = BooleanField("Public")
    invite_user = SelectField("Users",choices = [("Tonda", 1)])
    submit = SubmitField("Save changes")

@bp.route("/groups", methods=['GET'])
@login_required
def groups():
    try:
        groups = groups_manager.get_all_groups()        
    except Exception as e:
        flash("Could not get all groups", "danger")
        print("get_all_groups() failed")
    return render_template("groups.html")

@bp.route("/edit_group/<int:group_id>", methods=['GET', 'POST'])
@login_required
def create_group():
    form = GroupForm()
    return render_template("edit_group.html")