from .db import db, Post, Tag, Group, User, user_group, Score
from datetime import datetime
from .photo_manager import upload_image_to_webg, upload_image_to_webg_resized
from sqlalchemy import or_, and_
from sqlalchemy import func

def create_new_post(user_id: int, post_image, post_decs: str, post_tags: list[Tag], groups: list[Group], visibility: bool, allow_users: list[User] = None) -> Post:
    image_id = upload_image_to_webg(post_image)
    miniature_id = upload_image_to_webg_resized(post_image)
    post: Post = Post(owner_id=user_id, description = post_decs, post_date=datetime.now(), photo_id=image_id, miniature_id=miniature_id, visibility=visibility)

    for tag in post_tags:
        if tag not in post.tags:
            post.tags.append(tag)

    for group in groups:
        if group not in post.groups:
            post.groups.append(group)

    if not visibility:
        for user in allow_users:
            if user not in post.users:
                post.users.append(user)

    db.session.add(post)
    db.session.commit()

    return post

def get_post_by_id(post_id: int) -> Post:
    post = db.session.query(Post).filter(Post.id == post_id).first()
    return post

def can_see_post(user: User, post: Post) -> bool:
    if post.visibility:
        return True
    if user.id == post.owner_id or user.id in post.users:
        return True
    for group in post.groups:
        if user.id == group.owner_id or user.id in group.users:
            return True
    return False

def get_like_status(post: Post, user: User) -> bool:
    score: Score = db.session.query(Score).filter(and_(Score.post_id == post.id, Score.user_id == user.id)).first()
    if score:
        return score.score
    return None

def change_like_status(post: Post, user: User, score_value: bool) -> Score:
    print("Enter funcs")
    score_obj: Score = db.session.query(Score).filter(and_(Score.post_id == post.id, Score.user_id == user.id)).first()
    if score_obj:
        if score_obj.score == score_value:
            db.session.delete(score_obj)
            db.session.commit()
            return None
        else:
            score_obj.score = not score_obj.score
            db.session.commit()
            return score_obj
    else:
        score_obj = Score(post_id=post.id, user_id=user.id, score=score_value)
        db.session.add(score_obj)
        db.session.commit()
        return score_obj


def get_post_score(post: Post):
    positive_count = (
        db.session.query(func.count(Score.score))
        .filter(Score.post_id == post.id, Score.score == True)
        .scalar()
    )

    negative_count = (
        db.session.query(func.count(Score.score))
        .filter(Score.post_id == post.id, Score.score == False)
        .scalar()
    )

    total = positive_count + negative_count
    score = positive_count - negative_count

    if total == 0:
        return 0, None
    else:
        return score, ((score / total) + 1) / 2

def get_accessible_posts(user: User, page: int = 1, per_page: int = 50):
    if not user.is_authenticated:
        accessible_posts = db.session.query(Post).filter(Post.visibility == True).order_by(Post.post_date.desc()).paginate(page=page, per_page=per_page)

        posts = accessible_posts.items  # Current page's posts
        total = accessible_posts.total  # Total number of posts
        pages = accessible_posts.pages  # Total number of pages

        return posts, total, pages

    # Subquery for groups the user is a member of
    user_groups_subquery = (
        db.session.query(Group.id)
        .join(user_group, user_group.c.group_id == Group.id)
        .filter(user_group.c.user_id == user.id)
        .subquery()
    )

    # Query for posts
    accessible_posts = (
        db.session.query(Post)
        .outerjoin(Post.groups)  # Join the groups associated with the posts
        .filter(
            or_(
                Post.owner_id == user.id,  # Posts owned by the user
                Post.visibility == True,  # Public posts
                Post.users.any(User.id == user.id),  # Posts explicitly shared with the user
                Post.groups.any(Group.id.in_(user_groups_subquery))  # Posts shared with user's groups
            )
        )
        .order_by(Post.post_date.desc())  # Order by post_date in descending order
        .paginate(page=page, per_page=per_page)
    )

    posts = accessible_posts.items  # Current page's posts
    total = accessible_posts.total  # Total number of posts
    pages = accessible_posts.pages  # Total number of pages

    return posts, total, pages

def get_accessible_posts_tag(user: User, page: int = 1, per_page: int = 50, tag: str=None):
    if not user.is_authenticated:
        accessible_posts = db.session.query(Post).filter(and_(Post.visibility == True, Post.tags.any(Tag.name == tag))).order_by(Post.post_date.desc()).paginate(page=page, per_page=per_page)

        posts = accessible_posts.items  # Current page's posts
        total = accessible_posts.total  # Total number of posts
        pages = accessible_posts.pages  # Total number of pages

        return posts, total, pages

    # Subquery for groups the user is a member of
    user_groups_subquery = (
        db.session.query(Group.id)
        .join(user_group, user_group.c.group_id == Group.id)
        .filter(user_group.c.user_id == user.id)
        .subquery()
    )

    # Query for posts
    accessible_posts = (
        db.session.query(Post)
        .outerjoin(Post.groups)  # Join the groups associated with the posts
        .filter(Post.tags.any(Tag.name == tag))
        .filter(
            or_(
                Post.owner_id == user.id,  # Posts owned by the user
                Post.visibility == True,  # Public posts
                Post.users.any(User.id == user.id),  # Posts explicitly shared with the user
                Post.groups.any(Group.id.in_(user_groups_subquery))  # Posts shared with user's groups
            )
        )
        .order_by(Post.post_date.desc())  # Order by post_date in descending order
        .paginate(page=page, per_page=per_page)
    )

    posts = accessible_posts.items  # Current page's posts
    total = accessible_posts.total  # Total number of posts
    pages = accessible_posts.pages  # Total number of pages

    return posts, total, pages

def get_accessible_posts_user(user: User, page: int = 1, per_page: int = 50, profile_id: int=None):
    if not user.is_authenticated:
        accessible_posts = db.session.query(Post).filter(and_(Post.visibility == True, Post.owner_id == profile_id)).order_by(Post.post_date.desc()).paginate(page=page, per_page=per_page)

        posts = accessible_posts.items  # Current page's posts
        total = accessible_posts.total  # Total number of posts
        pages = accessible_posts.pages  # Total number of pages

        return posts, total, pages

    # Subquery for groups the user is a member of
    user_groups_subquery = (
        db.session.query(Group.id)
        .join(user_group, user_group.c.group_id == Group.id)
        .filter(user_group.c.user_id == user.id)
        .subquery()
    )

    # Query for posts
    accessible_posts = (
        db.session.query(Post)
        .outerjoin(Post.groups)  # Join the groups associated with the posts
        .filter(Post.owner_id == profile_id)
        .filter(
            or_(
                Post.owner_id == user.id,  # Posts owned by the user
                Post.visibility == True,  # Public posts
                Post.users.any(User.id == user.id),  # Posts explicitly shared with the user
                Post.groups.any(Group.id.in_(user_groups_subquery))  # Posts shared with user's groups
            )
        )
        .order_by(Post.post_date.desc())  # Order by post_date in descending order
        .paginate(page=page, per_page=per_page)
    )

    posts = accessible_posts.items  # Current page's posts
    total = accessible_posts.total  # Total number of posts
    pages = accessible_posts.pages  # Total number of pages

    return posts, total, pages

def get_accessible_posts_group(user: User, page: int = 1, per_page: int = 50, group_id: int=None):
    if not user.is_authenticated:
        accessible_posts = db.session.query(Post).filter(and_(Post.visibility == True, Post.groups.any(Group.id == group_id))).order_by(Post.post_date.desc()).paginate(page=page, per_page=per_page)

        posts = accessible_posts.items  # Current page's posts
        total = accessible_posts.total  # Total number of posts
        pages = accessible_posts.pages  # Total number of pages

        return posts, total, pages

    # Subquery for groups the user is a member of
    user_groups_subquery = (
        db.session.query(Group.id)
        .join(user_group, user_group.c.group_id == Group.id)
        .filter(user_group.c.user_id == user.id)
        .subquery()
    )

    # Query for posts
    accessible_posts = (
        db.session.query(Post)
        .outerjoin(Post.groups)  # Join the groups associated with the posts
        .filter(Post.groups.any(Group.id == group_id))
        .filter(
            or_(
                Post.owner_id == user.id,  # Posts owned by the user
                Post.visibility == True,  # Public posts
                Post.users.any(User.id == user.id),  # Posts explicitly shared with the user
                Post.groups.any(Group.id.in_(user_groups_subquery))  # Posts shared with user's groups
            )
        )
        .order_by(Post.post_date.desc())  # Order by post_date in descending order
        .paginate(page=page, per_page=per_page)
    )

    posts = accessible_posts.items  # Current page's posts
    total = accessible_posts.total  # Total number of posts
    pages = accessible_posts.pages  # Total number of pages

    return posts, total, pages