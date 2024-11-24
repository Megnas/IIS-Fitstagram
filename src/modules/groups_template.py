from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from . import groups_manager
from .db import Roles, User
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from .groups_manager import (
    create_new_group, 
    get_user_accesible_groups, 
    get_group, 
    get_user_owned_groups, 
    get_public_groups, 
    user_is_member, 
    get_group_owner
)
from .invites_manager import (
    get_users_with_group_pending_invites, 
    get_users_with_user_pending_invites,
    invite_user_to_group,
    cancel_group_invite
)
from .user_manager import get_users_for_invite, get_user_from_uid
from . import groups_manager
from .post_manager import get_posts_based_on_filters
from wtforms import widgets

from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp
from wtforms.validators import Length, Optional
from flask_wtf import FlaskForm

bp = Blueprint("groups", __name__)

class GroupForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=1, max=64)])
    description = StringField("Description", widget=widgets.TextArea())
    photo = FileField(
        "Group Image",
        validators=[FileAllowed(["jpg", "jpeg", "png"], "Images only!")]
    )
    visibility = BooleanField("Public")
    submit = SubmitField("Save changes")
    
def invite_user_form(users, **kwargs):
    class InviteUserForm(FlaskForm):
        user = StringField(
            "User",
            validators=[DataRequired()]
            )
        submit = SubmitField("Invite")
        
        def validate_input_field(form, field):
            if (field.data) not in form.allowed_values:
                raise ValidationError("Invalid input, please choose from the suggestions")

    allowed_values = [user.unique_id for user in users]
    setattr(InviteUserForm, "allowed_values", allowed_values)
    return InviteUserForm()

@bp.route("/group_invite_user/<int:group_id>", methods=['POST'])
@login_required
def group_invite_user(group_id):
    group = get_group(group_id)
    if (group == None):
        return abort(404, "Could not find group")
    if (group.owner_id != current_user.id):
        return abort(401, "User does not have acces to this group")
    
    form = invite_user_form(get_users_for_invite(group_id=group_id))

    if form.validate_on_submit():
        user = get_user_from_uid(form.user.data)
        if (user != None):
            invite_user_to_group(group_id=group_id, user_id=user.id)
        else:
            flash("User does not exist", "warn")

    if not form.is_submitted:
        form.user.data = ""
            
            
    if form.errors:
        flash("Could not invite user", "warn")

    return redirect(url_for("groups.group_users", group_id=group_id))

@bp.route("/group_cancel_invite/<int:group_id>/<int:user_id>", methods=['GET'])
@login_required
def cancel_invite(group_id, user_id):
    group = get_group(group_id)
    if (group == None):
        return abort(404, "Could not find group")
    if (group.owner_id != current_user.id):
        return abort(401, "User does not have acces to this group")
    
    cancel_group_invite(group_id=group_id, user_id=user_id)

    return redirect(url_for("groups.group_users", group_id=group_id))

@bp.route("/group_request_join/<int:group_id>", methods=['GET'])
@login_required
def request_join(group_id, user_id):
    group = get_group(group_id)
    if (group == None):
        return abort(404, "Could not find group")
    

    return redirect(url_for("groups.group_homepage", group_id=group_id))

@bp.route("/group_approve_user/<int:group_id>/<int:user_id>", methods=['GET'])
@login_required
def approve_join(group_id, user_id):
    group = get_group(group_id)
    if (group == None):
        return abort(404, "Could not find group")
    if (group.owner_id != current_user.id):
        return abort(401, "User does not have acces to this group")
    return redirect(url_for("groups.group_users", group_id=group_id))

@bp.route("/group_reject_user/<int:group_id>/<int:user_id>", methods=['GET'])
@login_required
def reject_join(group_id, user_id):
    group = get_group(group_id)
    if (group == None):
        return abort(404, "Could not find group")
    if (group.owner_id != current_user.id):
        return abort(401, "User does not have acces to this group")
    return redirect(url_for("groups.group_users", group_id=group_id))

@bp.route("/group_kick_user/<int:group_id>/<int:user_id>", methods=['GET'])
@login_required
def group_kick_user(group_id, user_id):
    group = get_group(group_id)
    if (group == None):
        return abort(404, "Could not find group")
    if (group.owner_id != current_user.id):
        return abort(401, "User does not have acces to this group")

    remove_user_from_group(group_id=group_id, user_id=user_id)
    return redirect(url_for("groups.group_users", group_id=group_id))

    
@bp.route("/group_users/<int:group_id>", methods=['GET'])
def group_users(group_id):
    group = get_group(group_id=group_id)       
    owner = get_group_owner(group_id=group_id)

    if (current_user.is_authenticated):
        if (current_user.id == group.owner_id or
            current_user.role == Roles.MODERATOR or
             current_user.role == Roles.ADMIN
        ):
            form = invite_user_form(get_users_for_invite(group_id=group_id))
            if not form.is_submitted:
                form.user.data = ""
            return render_template(
                "group_users_management.html", 
                group=group,
                user_pending=get_users_with_user_pending_invites(group_id=group_id),
                group_pending=get_users_with_group_pending_invites(group_id=group_id),
                invite_user_form=form
            )
        if ( user_is_member(user_id=current_user.id, group_id=group.id)):
            return render_template(
                "group_users.html", 
                group=group, 
                owner=owner
            )

    if (group.visibility):
        return render_template(
            "group_users.html", 
            group=group, 
            owner=owner
        )

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

class PostFilterForm(FlaskForm):
    tags = StringField('Tags', validators=[ 
        Length(min=0, max=512), 
        Regexp(r'^[a-z0-9_ -]*$', message="Tags must not contain spaces or uppercase letters and can only include lowercase letters, numbers, and underscores.")
    ])
    users = StringField('Users', validators=[ 
        Length(min=0, max=512), 
        Regexp(r'^[a-z0-9_ ]*$', message="Tags must not contain spaces or uppercase letters and can only include lowercase letters, numbers, and underscores.")
    ])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    order_by = SelectField('Order By', choices=[('time', 'Time'), ('score', 'Score'), ('comments', 'Number of Comments')], default='time')  # Dropdown for ordering
    submit = SubmitField('Apply Filters')

@bp.route("/group_homepage/<int:group_id>", methods=['GET'])
def group_homepage(group_id):
    group = get_group(group_id=group_id)       

    if (group == None):
        return abort(404, "Could not find group")

    page = request.args.get('page', 1, type=int)

    form = PostFilterForm()

    tags = request.args.get('tags', None ,type=str)
    users = request.args.get('users', None ,type=str)
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    order_by = request.args.get('order_by', 'time')

    posts, tototal, pages = get_posts_based_on_filters(
        current_user, 
        page=page, 
        per_page=24, 
        order_by=order_by, 
        start_date=start_date, 
        end_date=end_date, 
        filter_tag_string=tags, 
        filter_user_string=users,
        specific_group=group.id
    )
    
    form.order_by.data = order_by

    if (current_user.is_authenticated):
        if (current_user.id == group.owner_id or
            current_user.role == Roles.MODERATOR or current_user.role == Roles.ADMIN
        ):
            return render_template(
                "group_homepage.html",
                group=group, owner=True,
                posts=posts,
                page=page,
                pages=pages,
                form=form
            )
        if ( user_is_member(user_id=current_user.id, group_id=group.id)):
            return render_template(
                "group_homepage.html", 
                group=group, 
                owner=False, 
                posts=posts, 
                page=page, 
                pages=pages,
                form=form
            )

    if (group.visibility):
        return render_template(
            "group_homepage.html",
            group=group,
            owner=False, 
            posts=posts, 
            page=page, 
            pages=pages,
            form=form
        )

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
            group = create_new_group(
                creator_id = user.id,
                name = form.name.data,
                visibility = form.visibility.data,
                description = form.description.data,
                photo = form.photo.data
            )
            return redirect(url_for("groups.group_homepage", group_id=group.id))
        except Exception as e:
            flash("Could not create group", "danger")
            print(f"Could not create group {e}")
            
    if form.errors:
        flash(f"{form.errors}", "danger")

    return render_template("create_group.html", form=form)



#vypis pozvanek a pozadavku pro joinuti groupy
#@bp.route("/groups/requests_invites", methods=['GET'])
#@login_required
#def requests_invites():
