from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import groups_manager
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from .groups_manager import create_new_group, get_user_accesible_groups, get_group
from . import groups_manager

bp = Blueprint("groups", __name__)

class GroupForm(FlaskForm):
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
    groups = get_user_accesible_groups(current_user.id)       

    return render_template("groups.html", groups=groups)

@bp.route("/edit_group/<int:group_id>", methods=['GET', 'POST'])
@login_required
def edit_group(group_id):
    group = get_group(group_id)
    if (group == None):
        return abort(404, "Could not find group")
    if (group.owner_id != current_user.id):
        return abort(401, "User does not have acces to this group")

    form = GroupForm()

    if form.validate_on_submit():
        try:
            groups_manager.edit_group(
                group_id = group_id,
                name = form.name.data,
                visibility = form.visibility.data,
                description = form.description.data,
                photo = form.photo.data
            )
            return redirect(url_for("groups.groups"))
        except Exception as e:
            flash("Could not create group", "danger")
            print(f"Could not create group {e}")
            
    if form.errors:
        flash(f"{form.errors}", "danger")
        
    if not form.is_submitted():
        form.name.data = group.name
        form.description.data = group.description
        form.visibility.data = group.visibility

    return render_template("edit_group.html", form=form, group=group)

@bp.route("/create_group", methods=['GET', 'POST'])
@login_required
def create_group():
    form = GroupForm()
    user = current_user
    
    if form.validate_on_submit():
        #try:
            create_new_group(
                user.id,
                form.name.data,
                form.visibility.data,
                form.description.data,
                form.photo.data
            )
            return redirect(url_for("groups.groups"))
        #except Exception as e:
            #flash("Could not create group", "danger")
            #print(f"Could not create group {e}")
            
    if form.errors:
        flash(f"{form.errors}", "danger")

    return render_template("create_group.html", form=form)