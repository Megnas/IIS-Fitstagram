import string
from .db import db, User, Roles, Group, GroupInvite
from hashlib import sha224
from sqlalchemy import or_

from .photo_manager import upload_image_to_webg_resized

def get_similar_users(patern: str) -> [User]:
    like_pattern = f"%{patern}%"

    results = User.query.filter(
        or_(
            User.username.ilike(like_pattern),
            User.unique_id.ilike(like_pattern),
            User.email.ilike(like_pattern)
        )
    ).all()

    return results

def create_user(username: str, pwd: str, mail: str, uid: str) -> User:
    hashed_pwd = sha224(pwd.encode('utf-8')).hexdigest()
    new_user = User(username=username, email=mail, password_hash=hashed_pwd, role=Roles.USER, blocked=False, photo_id=None, unique_id=uid)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def get_users(users: [str]):
    users = db.session.query(User).filter(User.unique_id.in_(users)).all()
    return users

def get_users_for_invite(group_id: int):
    group = db.session.query(Group).filter(Group.id == group_id).first()
    do_not_invite = [group.owner_id] + [user.id for user in group.users]
    invites = db.session.query(GroupInvite).filter(
        GroupInvite.group_id == group_id
    ).all()
    do_not_invite += [invite.user_id for invite in invites]
    users = db.session.query(User).filter(
        User.id.not_in(do_not_invite)
    ).all()
    return users

def update_user(user: User, username=None , email=None, pwd=None, pfp=None, uid=None):
    if pfp:
        image_id = upload_image_to_webg_resized(pfp, quality=90)
        user.photo_id = image_id
    if username:
        user.username = username
    if email:
        user.email = email
    if pwd:
        user.password_hash = sha224(pwd.encode('utf-8')).hexdigest()
    if uid:
        user.unique_id = uid

    db.session.commit()


def login_user(mail: string, pwd: string) -> User:
    hashed_pwd = sha224(pwd.encode('utf-8')).hexdigest()
    user = db.session.query(User).filter(User.email == mail, User.password_hash == hashed_pwd, User.blocked == False).first()
    return user


def block_user(mail: string):
    db.session.query(User).filter(User.email == mail).first().blocked = True
    db.session.commit()


def change_role(mail: string, role: Roles):
    db.session.query(User).filter(User.email == mail).first().role = role
    db.session.commit()


def find_users(username: string):
    users = db.session.query(User).filter(User.username.contains(username))
    return users


def delete_user(user_id: int):
    user = db.session.query(User).filter(User.id == user_id).first()
    db.session.delete(user)


def change_username(user_id: int, user_newname):
    user = db.session.query(User).filter(User.id == user_id).first()
    user.username = user_newname
    db.session.commit()

def change_image(user_id: int, image):
    photo_id = upload_image(image)
    user = db.session.query(User).filter(User.id == user_id).first()
    user.photo_id = photo_id
    db.session.commit()

def get_username(user_id: int) -> string:
    user = db.session.query(User).filter(User.id == user_id).first()
    return user.username

def get_user(user_id: int) -> User:
    user = db.session.query(User).filter(User.id == user_id).first()
    return user

def get_all_users(user_id: int) -> User:
    user = db.session.query(User).filter(User.id == user_id).first()
    return user

def get_user_from_uid(uid: str) -> User:
    user = db.session.query(User).filter(User.unique_id == uid).first()
    return user

def update_pfp(user_id: int, filename: string):
    user = db.session.query(User).filter(User.id == user_id).first()
    user.avatar_path = filename
    db.session.commit()