from flask import Blueprint, render_template, flash, redirect, url_for, abort, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import login_required, current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, Regexp
from wtforms_alchemy import QuerySelectMultipleField
from .groups_manager import get_user_member_groups
from .tag_manager import get_valid_tag
from .user_manager import get_user_from_uid, get_user
from .post_manager import create_new_post, get_post_by_id, can_see_post, get_like_status, change_like_status, get_post_score, create_comment, get_comments, get_comment
from .post_manager import delete_comment as delete_comment_from_db
from .post_manager import delete_post as delete_post_from_db
from .post_manager import edit_post as edit_post_in_db
from wtforms import widgets
from wtforms.validators import ValidationError

from .db import Post, Comment, Roles

bp = Blueprint('post', __name__)

# Custom validator for max file size
def FileMaxSize(max_size):
    def _file_max_size(form, field):
        if field.data:
            # Get the size of the uploaded file
            file_size = len(field.data.read())
            field.data.seek(0)  # Rewind the file pointer after reading it
            if file_size > max_size:
                raise ValidationError(f"File size must not exceed {max_size / 1024 / 1024} MB")
    return _file_max_size

class QuerySelectMultipleFieldWithCheckboxes(QuerySelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class PostForm(FlaskForm):
    post_photo = FileField('Picture', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only!'), FileMaxSize(5 * 1024 * 1024)])
    description = StringField('Description', validators=[Length(min=0, max=256)], widget=widgets.TextArea())
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

class PostLike(FlaskForm):
    submit = SubmitField('Like')

class PostDislike(FlaskForm):
    submit = SubmitField('Dislike')

class CreateComment(FlaskForm):
    description = StringField('Comment', validators=[Length(min=1, max=256)], widget=widgets.TextArea())
    submit = SubmitField('Create Comment')

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
        
    else:
        # Form is invalid, check errors
        if request.method == 'POST':
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in field {field}: {error}", 'error')

    return render_template('create_post.html', form=form)

@bp.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post: Post = get_post_by_id(post_id)

    if not post:
        abort(404, description="User does not exists.")

    if not post.visibility:
        if not current_user.is_authenticated:
            abort(401, description="Not authorized!")
        if not can_see_post(current_user, post):
            abort(401, description="Not authorized!")
    
    like = None
    dislike = None
    comment=None
    score = None
    score_val, score_per = get_post_score(post)
    if current_user.is_authenticated:

        like = PostLike()
        dislike = PostDislike()
        comment = CreateComment()

        score = get_like_status(post, current_user)

        if comment.validate_on_submit():
            create_comment(post, current_user, comment.description.data)

    comments = get_comments(post)

    return render_template("post.html", post=post, p_user=get_user(post.owner_id), like_form=like, dislike_form=dislike, score=score, score_total=score_val, score_per=score_per, comment=comment, comments=comments)

@bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like(post_id):
    post: Post = get_post_by_id(post_id)
    if not post:
        abort(404, description="Post does not exists.")
    
    change_like_status(post, current_user, True)

    return redirect(url_for('post.post', post_id=post_id))

@bp.route('/dislike/<int:post_id>', methods=['POST'])
@login_required
def dislike(post_id):
    post: Post = get_post_by_id(post_id)
    if not post:
        abort(404, description="Post does not exists.")

    change_like_status(post, current_user, False)

    return redirect(url_for('post.post', post_id=post_id))

@bp.route('/delete_comment/<int:commet_id>/<int:post_id>', methods=['POST'])
@login_required
def delete_comment(commet_id, post_id):
    post: Post = get_post_by_id(post_id)
    if not post:
        abort(404, description="Post does not exists.")

    comment: Comment = get_comment(commet_id)
    if not comment:
        abort(404, description="Comment does not exists.")

    if not (comment.user_id == current_user.id or current_user.role == Roles.MODERATOR or current_user.role == Roles.ADMIN):
        abort(401, description="You dont have permissions")

    delete_comment_from_db(comment)

    return redirect(url_for('post.post', post_id=post_id))

@bp.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post: Post = get_post_by_id(post_id)
    if not post:
        abort(404, description="Post does not exists.")

    if not (post.owner_id == current_user.id or current_user.role == Roles.MODERATOR or current_user.role == Roles.ADMIN):
        abort(401, description="You dont have permissions")

    delete_post_from_db(post)

    return redirect(url_for('view.galery'))

class PostEditForm(FlaskForm):
    description = StringField('Description', validators=[Length(min=0, max=256)], widget=widgets.TextArea())
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
    submit = SubmitField('Save')

@bp.route("/edit_post/<int:post_id>", methods=['GET', 'POST'])
def edit_post(post_id):
    post: Post = get_post_by_id(post_id)
    if not post:
        abort(404, description="Post does not exists.")

    if not (post.owner_id == current_user.id):
        abort(401, description="You dont have permissions")

    form = PostEditForm()

    if form.validate_on_submit():
        #Tags
        tag_tokens = form.tags.data.split()
        new_tags = []
        for tag in tag_tokens:
            new_tag = get_valid_tag(tag)
            if new_tag:
                new_tags.append(new_tag)
            else:
                flash(f'Invalid tag: {tag}', 'danger')
                return render_template("edit_post.html", form=form, post=post)
            
        #Public and users
        new_users = []
        if not form.visibility.data:
            user_tokens = form.user.data.split()
            for user in user_tokens:
                usr = get_user_from_uid(user)
                if usr:
                    if usr.id == current_user.id:
                        flash('Cannot add your self to list', 'danger')
                        return render_template('edit_post.html', form=form, post=post)
                    new_users.append(usr)
                else:
                    flash(f'Invalid user uid: {user}', 'danger')
                    return render_template('edit_post.html', form=form, post=post)
        try:
            edit_post_in_db(post=post, description=form.description.data, tags=new_tags, groups=form.groups.data, visibiliy=form.visibility.data, users=new_users)
            flash(f'Post updated', 'info')
        except:
            flash(f'Post updated failed', 'warn')
        return render_template("edit_post.html", form=form, post=post)

    if form.tags.errors:
        flash(f'Invalid tag format (only user lower character of numbers)', 'danger')
        return render_template("edit_post.html", form=form, post=post)
    
    if form.user.errors:
        flash(f'Invalid user format (only user lower character of numbers)', 'danger')
        return render_template("edit_post.html", form=form, post=post)


    #load form with data
    form.description.data = post.description
    form.visibility.data = post.visibility
    form.groups.data = post.groups

    form.tags.data = ""
    for tag in post.tags:
        if not tag.blocked:
            form.tags.data += tag.name
            form.tags.data += " " 

    form.user.data = ""
    for user in post.users:
        form.user.data += user.unique_id
        form.user.data += " " 

    return render_template("edit_post.html", form=form, post=post)