from .db import db, Post, Tag, Group, User
from datetime import datetime
from .photo_manager import upload_image

def create_new_post(user_id: int, post_image, post_decs: str, post_tags: list[Tag], groups: list[Group], visibility: bool, allow_users: list[User] = None) -> Post:
    image_id = upload_image(post_image)
    post: Post = Post(owner_id=user_id, description = post_decs, post_date=datetime.now(), photo_id=image_id, visibility=visibility)

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