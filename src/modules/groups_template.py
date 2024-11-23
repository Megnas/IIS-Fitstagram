from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from . import groups_manager
from .db import Roles
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from .groups_manager import create_new_group, get_user_accesible_groups, get_group, get_user_owned_groups, get_public_groups, user_is_member, get_group_owner
from . import groups_manager
from .post_manager import get_accessible_posts_group

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
    
class InviteUserForm(FlaskForm):
    pass

@bp.route("/group_kick_user/<int:group_id>/<int:user_id>, methods=['POST']")
@login_required
def group_kick_user(group_id, user_id):
    remove_user_from_group(group_id=group_id, user_id=user_id)

    
@bp.route("/group_users/<int:group_id>", methods=['GET'])
def group_users(group_id):
    group = get_group(group_id=group_id)       
    owner = get_group_owner(group_id=group_id)

    if (current_user.is_authenticated):
        if (current_user.id == group.owner_id or
            current_user.role == Roles.MODERATOR or
             current_user.role == Roles.ADMIN
        ):
            return render_template("group_users_management.html", group=group)
        if ( user_is_member(user_id=current_user.id, group_id=group.id)):
            return render_template("group_users.html", group=group, owner=owner)

    if (group.visibility):
        return render_template("group_users.html", group=group, owner=owner)

    return abort(401, "User does not have acces to this group")

@bp.route("/groups", methods=['GET'])
def groups():
    if (current_user.is_authenticated):
        groups = get_user_accesible_groups(current_user.id)       
        owned_groups = get_user_owned_groups(current_user.id)
    else:
        groups = get_public_groups()
        owned_groups = None
    return render_template("groups.html", groups=groups, owned_groups = owned_groups)

@bp.route("/group_homepage/<int:group_id>", methods=['GET'])
def group_homepage(group_id):
    group = get_group(group_id=group_id)       

    if (group == None):
        return abort(404, "Could not find group")

    page = request.args.get('page', 1, type=int)
    posts, tototal, pages = get_accessible_posts_group(current_user, page=page, per_page=(4 * 6), group_id=group.id)

    if (current_user.is_authenticated):
        if (current_user.id == group.owner_id or
            current_user.role == Roles.MODERATOR or current_user.role == Roles.ADMIN
        ):
            return render_template("group_homepage.html", group=group, owner=True, posts=posts, page=page, pages=pages)
        if ( user_is_member(user_id=current_user.id, group_id=group.id)):
            return render_template("group_homepage.html", group=group, owner=False, posts=posts, page=page, pages=pages)

    if (group.visibility):
        return render_template("group_homepage.html", group=group, owner=False, posts=posts, page=page, pages=pages)

    return abort(401, "User does not have acces to this group")
            

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
            return redirect(url_for("groups.owned_groups"))
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
        try:
            create_new_group(
                creator_id = user.id,
                name = form.name.data,
                visibility = form.visibility.data,
                description = form.description.data,
                photo = form.photo.data
            )
            return redirect(url_for("groups.group_homepage"))
        except Exception as e:
            flash("Could not create group", "danger")
            print(f"Could not create group {e}")
            
    if form.errors:
        flash(f"{form.errors}", "danger")

    return render_template("create_group.html", form=form)