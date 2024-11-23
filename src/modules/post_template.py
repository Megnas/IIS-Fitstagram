from flask import Blueprint, render_template, flash, redirect, url_for, abort
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import login_required, current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, Regexp
from wtforms_alchemy import QuerySelectMultipleField
from .groups_manager import get_user_member_groups
from .tag_manager import get_valid_tag
from .user_manager import get_user_from_uid, get_user
from .post_manager import create_new_post, get_post_by_id, can_see_post
from wtforms import widgets

from .db import Post

bp = Blueprint('post', __name__)

class QuerySelectMultipleFieldWithCheckboxes(QuerySelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class PostForm(FlaskForm):
    post_photo = FileField('Picture', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only!')])
    description = StringField('Description', validators=[Length(min=0, max=256)])
    tags = StringField('Tags', validators=[ 
        Length(min=0, max=512), 
        Regexp(r'^[a-z0-9_ ]*$', message="Tags must not contain spaces or uppercase letters and can only include lowercase letters, numbers, and underscores.")
    ])
    visibility = BooleanField('Public', default=True)  # Add visibility toggle
    user = StringField('User UIDs', validators=[ 
        Length(min=0, max=512), 
        Regexp(r'^[a-z0-9_ ]*$', message="User IDs must not contain spaces or uppercase letters and can only include lowercase letters, numbers, and underscores.")
    ])
    groups = QuerySelectMultipleFieldWithCheckboxes("Groups", query_factory=lambda: get_user_member_groups(current_user.id))
    submit = SubmitField('Post')

@bp.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    form.groups.query = get_user_member_groups(current_user.id)

    if form.validate_on_submit():
        #Tags
        tag_tokens = form.tags.data.split()
        tag_ids = []
        for tag in tag_tokens:
            tag_id: int = get_valid_tag(tag)
            if tag_id:
                tag_ids.append(tag_id)
            else:
                flash(f'Invalid tag: {tag}', 'danger')
                return render_template('create_post.html', form=form)

        #Get Groups
        group_ids = []
        for group in form.groups.data:
            if (current_user.id == group.owner_id or current_user.id in group.users):
                group_ids.append(group)
            else:
                flash(f'Invalid group: {group.name}', 'danger')
                return render_template('create_post.html', form=form)
            
        #Public and users
        user_ids = []
        if not form.visibility.data:
            user_tokens = form.user.data.split()
            for user in user_tokens:
                usr = get_user_from_uid(user)
                if usr:
                    if usr.id == current_user.id:
                        flash('Cannot add your self to list', 'danger')
                        return render_template('create_post.html', form=form)
                    user_ids.append(usr)
                else:
                    flash(f'Invalid user uid: {user}', 'danger')
                    return render_template('create_post.html', form=form)
                
        try:
            create_new_post(user_id=current_user.id, post_image=form.post_photo.data, post_decs=form.description.data or "", post_tags=tag_ids, groups=group_ids, visibility=form.visibility.data, allow_users=user_ids)
            return redirect(url_for('view.index'))
        except:
            flash(f'Failed to create Post', 'danger')
            return render_template('create_post.html', form=form)

    return render_template('create_post.html', form=form)

@bp.route("/post/<int:post_id>")
def post(post_id):
    post: Post = get_post_by_id(post_id)
    if(post):
        if not post.visibility:
            if not current_user.is_authenticated:
                abort(401, description="Not authorized!")
            if not can_see_post(current_user, post):
                abort(401, description="Not authorized!")
        return render_template("post.html", post=post, p_user=get_user(post.owner_id))
    else:
        abort(404, description="User does not exists.")

@bp.route("/edit_post/<int:post_id>")
def edit_post(post_id):
    abort(404, description="Post does not exists.")