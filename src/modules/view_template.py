from flask import Blueprint, render_template, abort, request
from flask_login import current_user

from .db import Post, Tag, db, Score, Comment, User
from sqlalchemy import and_, not_


from .user_manager import get_user, get_users
from .post_manager import get_accessible_posts, get_accessible_posts_tag, get_accessible_posts_user

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

def get_tokens(data):
    tokens = data.split()
    positive = []
    negative = []
    for token_data in tokens:
        token: str = token_data
        neg = False
        if token_data.startswith("-"):
            token = token_data[1:]
            neg = True
        if "-" in token:
            return [],[],True
        if neg:
            negative.append(token)
        else:
            positive.append(token)
    return positive, negative, False


@bp.route("/")
def index():
    page = request.args.get('page', 1, type=int)

    posts, tototal, pages = get_accessible_posts(current_user, page=page, per_page=(4 * 6))
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

    filters = []

    if tags:
        p, n, err = get_tokens(tags)
        if err:
            pass # Invalid token format
        if not set(p).isdisjoint(n):
            pass # Duplicate tags usage
        if p:
            filters.append(and_(*[Post.tags.any(Tag.name == tag) for tag in p]))
        if n:
            filters.append(not_(Post.tags.any(Tag.name.in_(n))))
        
    if users:
        users = users.split()
        p_user = get_users(users)
        if users:
            user_ids = [user.id for user in p_user]
            filters.append(Post.owner_id.in_(user_ids))

    # Filter for start date
    if start_date:
        filters.append(Post.post_date >= start_date)

    # Filter for end date
    if end_date:
        filters.append(Post.post_date <= end_date)

    query = Post.query.filter(*filters)

    # Apply ordering
    if order_by == 'time':
        query = query.order_by(Post.post_date.desc())
    elif order_by == 'score':
        query = query.outerjoin(Score).group_by(Post.id).order_by(db.func.sum(Score.score).desc())
    elif order_by == 'comments':
        query = query.outerjoin(Comment).group_by(Post.id).order_by(db.func.count(Comment.id).desc())

    pagination = query.paginate(page=page, per_page=10)

    posts = pagination.items  # Current page's posts
    total = pagination.total  # Total number of posts
    pages = pagination.pages  # Total number of pages

    #posts, tototal, pages = get_accessible_posts(current_user, page=page, per_page=(4 * 6))
    return render_template("galery.html", posts=posts, page=page, pages=pages, self_ref='view.galery',form=form)

@bp.route("/tag")
def tag():
    page = request.args.get('page', 1, type=int)
    tag = request.args.get('tag', None, type=str)
    posts, tototal, pages = get_accessible_posts_tag(current_user, page=page, per_page=(4 * 6), tag=tag)
    return render_template("tag.html", posts=posts, page=page, pages=pages, tag_name=tag, self_ref='view.tag')

@bp.route("/profile/<int:user_id>")
def profile(user_id):
    user = get_user(user_id)
    if(user):
        page = request.args.get('page', 1, type=int)

        posts, tototal, pages = get_accessible_posts_user(current_user, page=page, per_page=(4 * 6), profile_id=user.id)
        return render_template("profile.html", p_user=user, posts=posts, page=page, pages=pages, self_ref='view.index')
    else:
        abort(404, description="User does not exists.")