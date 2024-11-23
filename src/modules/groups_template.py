from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import groups_manager
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from .groups_manager import create_new_group, get_all_groups

bp = Blueprint("groups", __name__)

class EditGroupForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=1, max=64)])
    description = StringField("Description")
    photo = FileField(
        "Group Image",
        validators=[FileAllowed(["jpg", "jpeg", "png"], "Images only!")]
    )
    visibility = BooleanField("Public")
    invite_user = SelectField("Users",choices = [("Tonda", 1)])
    submit = SubmitField("Save changes")

class CreateGroupForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=1, max=64)])
    description = StringField("Description")
    photo = FileField(
        "Group Image",
        validators=[FileAllowed(["jpg", "jpeg", "png"], "Images only!")]
    )
    visibility = BooleanField("Public")
    submit = SubmitField("Save changes")

@bp.route("/groups", methods=['GET'])
@login_required
def groups():
    try:
        groups = get_all_groups()        
    except Exception as e:
        flash("Could not get all groups", "danger")
        print("get_all_groups() failed")
    return render_template("groups.html", groups=groups)

@bp.route("/edit_group/<int:group_id>", methods=['GET', 'POST'])
@login_required
def edit_group():
    form = EditGroupForm()
    return render_template("edit_group.html")

@bp.route("/create_group", methods=['GET', 'POST'])
@login_required
def create_group():
    form = CreateGroupForm()
    user = current_user
    
    if form.validate_on_submit():
        #try:
        create_new_group(
            user.id,
            form.name.data,
            form.visibility.data,
            form.photo.data,
            form.description.data
        )
        #except Exception as e:
        #    flash("Could not create group", "danger")
        #    print(f"Could not create group {e}")
            
    if form.errors:
        flash(f"{form.errors}", "danger")

    return render_template("create_group.html", form=form)