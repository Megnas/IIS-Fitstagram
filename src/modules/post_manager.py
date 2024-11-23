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