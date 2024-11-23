from .db import db, Post, Tag, Group, User, user_group
from datetime import datetime
from .photo_manager import upload_image_to_webg, upload_image_to_webg_resized
from sqlalchemy import or_

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

def get_accessible_posts(user: User, page: int = 1, per_page: int = 50):
    if not user.is_authenticated:
        # Return only public posts for unauthenticated users
        return (
            db.session.query(Post)
            .filter(Post.visibility == True)
            .order_by(Post.post_date.desc())
            .all()
        )

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