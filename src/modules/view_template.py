from flask import Blueprint, render_template, abort, request
from flask_login import current_user

from .db import Post, Tag, db, Score, Comment, User
from sqlalchemy import and_, not_


from .user_manager import get_user, get_users
from .post_manager import get_posts_based_on_filters

from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp
from wtforms.validators import Length, Optional
from flask_wtf import FlaskForm

bp = Blueprint('view', __name__)

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

class PostFilterTagForm(FlaskForm):
    users = StringField('Users', validators=[ 
        Length(min=0, max=512), 
        Regexp(r'^[a-z0-9_ ]*$', message="Tags must not contain spaces or uppercase letters and can only include lowercase letters, numbers, and underscores.")
    ])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    order_by = SelectField('Order By', choices=[('time', 'Time'), ('score', 'Score'), ('comments', 'Number of Comments')], default='time')  # Dropdown for ordering
    submit = SubmitField('Apply Filters')

class PostFilterUserForm(FlaskForm):
    tags = StringField('Tags', validators=[ 
        Length(min=0, max=512), 
        Regexp(r'^[a-z0-9_ -]*$', message="Tags must not contain spaces or uppercase letters and can only include lowercase letters, numbers, and underscores.")
    ])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    order_by = SelectField('Order By', choices=[('time', 'Time'), ('score', 'Score'), ('comments', 'Number of Comments')], default='time')  # Dropdown for ordering
    submit = SubmitField('Apply Filters')

@bp.route("/")
def index():
    page = request.args.get('page', 1, type=int)

    posts, tototal, pages = get_posts_based_on_filters(current_user, page=page, per_page=(4 * 6))
    return render_template("index.html", posts=posts, page=page, pages=pages, self_ref='view.index')

@bp.route("/galery")
def galery():
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
        filter_user_string=users
    )
    
    form.order_by.data = order_by

    return render_template("galery.html", posts=posts, page=page, pages=pages,form=form)

@bp.route("/tag")
def tag():
    page = request.args.get('page', 1, type=int)
    tag = request.args.get('tag', None, type=str)
    form = PostFilterForm()

    tags = request.args.get('tags', None ,type=str)
    users = request.args.get('users', None ,type=str)
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    order_by = request.args.get('order_by', 'time')

    posts, tototal, pages = get_posts_based_on_filters(
        current_user, 
        page=page, 
        per_page=(4 * 6), 
        order_by=order_by, 
        start_date=start_date, 
        end_date=end_date, 
        filter_tag_string=tags, 
        filter_user_string=users,
        specific_tag=tag
    )
    
    form.order_by.data = order_by

    return render_template("tag.html", posts=posts, page=page, pages=pages,form=form,tag_name=tag)

@bp.route("/profile/<int:user_id>")
def profile(user_id):
    user = get_user(user_id)
    if(user):
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
            per_page=(4 * 6), 
            order_by=order_by, 
            start_date=start_date, 
            end_date=end_date, 
            filter_tag_string=tags, 
            filter_user_string=users,
            specific_user=user.id
        )
        
        form.order_by.data = order_by

        return render_template("profile.html", p_user=user, posts=posts, page=page, pages=pages,form=form)
    else:
        abort(404, description="User does not exists.")