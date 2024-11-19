import string
from .db import db, User, Roles
from hashlib import sha224

def create_user(username: string, pwd: string, mail: string):
    hashed_pwd = sha224(pwd.encode('utf-8')).hexdigest()
    new_user = User(username=username, email=mail, password_hash=hashed_pwd, role=Roles.USER, blocked=False, photo_id=None)
    db.session.add(new_user)
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


def get_username(user_id: int) -> string:
    user = db.session.query(User).filter(User.id == user_id).first()
    return user.username

def get_user(user_id: int) -> User:
    user = db.session.query(User).filter(User.id == user_id).first()
    return user

def update_pfp(user_id: int, filename: string):
    user = db.session.query(User).filter(User.id == user_id).first()
    user.avatar_path = filename
    db.session.commit()