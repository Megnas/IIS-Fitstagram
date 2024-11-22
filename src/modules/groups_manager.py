from .db import db, User, Group

def get_user_groups(user_id: int) -> [Group]:
    user = db.session.query(User).filter(User.id == user_id)
    return user.groups

def get_all_groups() -> [Group]:
    return db.session.query(Group).all()
    
def create_new_group(creator_id: int):
    group = Group(owner_id = creator_id)
    db.session.add(group)
    db.session.commit()

def delete_group(group_id: int):
    group = db.session.query(Group).filter(Group.id == group_id).first()
    db.session.delete(group)
    
def add_user_to_group(group_id: int, user_id: int):
    group = db.session.query(Group).filter(Group.id == group_id).first()
    group.users.append(user_id)
    db.session.commit()

def invite_user_to_group(group_id: int, user_id: int):
    group = db.session.query(Group).filter(Group.id == group_id).first()
    group.invited_users.append(user_id)
    db.session.commit()

def reject_user_invitation_to_group(group_id: int, user_id: int):
    group = db.session.query(Group).filter(Group.id == group_id).first()
    group.invited_users.remove(user_id)
    db.session.commit()

def approve_invitation_to_group(group_id: int, user_id: int):
    group = db.session.query(Group).filter(Group.id == group_id).first()
    group.invited_users.remove(user_id)
    group.users.append(user_id)
    db.session.commit()

def remove_user_from_group(group_id: int, user_id: int):
    group = db.session.query(Group).filter(Group.id == group_id).first()
    group.users.remove(user_id)
    db.session.commit()
    
def change_group_description(group_id: int, description: str):
    group = db.session.query(Group).filter(Group.id == group_id).first()
    group.description = description
    db.session.commit()

def change_group_name(group_id: int, name: str):
    group = db.session.query(Group).filter(Group.id == group_id).first()
    group.name = name
    db.session.commit()

def change_group_image(group_id: int, image):
    photo_id = upload_image(image)
    group = db.session.query(Group).filter(Group.id == group_id).first()
    group.photo_id = photo_id
    db.session.commit()