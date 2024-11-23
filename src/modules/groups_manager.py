from .db import db, User, Group, Roles
from .photo_manager import upload_image_to_webg_resized
from sqlalchemy import or_ 

def get_all_groups() -> [Group]:
    return db.session.query(Group).order_by(Group.name.asc()).all()

def user_is_member(user_id: int, group_id: int) -> bool:
    user = db.session.query(User).filter(User.id == user_id).first()
    group = db.session.query(Group).filter(Group.id == group_id).first()
    if (user.id == group.owner_id or user.id in group.users):
        return True
    return False

def get_user_owned_groups(user_id: int) -> [Group]:
    groups = db.session.query(Group).filter(
        Group.owner_id == user_id
    ).order_by(Group.name.asc()).all()
    return groups

def get_public_groups() -> [Group]:
    groups = db.session.query(Group).filter( 
        Group.visibility == True,
    ).order_by(Group.name.asc()).all()
    return groups

def get_user_accesible_groups(user_id: int) -> [Group]:
    # If user is admin or moderator just return all the groups
    user = db.session.query(User).filter(User.id == user_id).first()
    if (user.role == Roles.MODERATOR or user.role == Roles.ADMIN):
        return get_all_groups()
    # Returns all the groups the user owns, is a member of or are public
    groups = db.session.query(Group).filter( 
        or_(
            Group.owner_id == user_id,
            Group.visibility == True,
            Group.users.any(User.id == user_id)
        )
    ).order_by(Group.name.asc()).all()
    return groups

def get_user_member_groups(user_id: int) -> [Group]:
    # If user is admin or moderator just return all the groups
    user = db.session.query(User).filter(User.id == user_id).first()
    # Returns all the groups the user owns, is a member of or are public
    groups = db.session.query(Group).filter( 
        or_(
            Group.owner_id == user_id,
            Group.users.any(User.id == user_id)
        )
    ).order_by(Group.name.asc()).all()
    return groups

def get_user_groups(user_id: int) -> [Group]:
    user = db.session.query(User).filter(
        User.id == user_id
    ).order_by(Group.name.asc()).all()
    return user.groups

def get_group(group_id: int) -> Group:
    group = db.session.query(Group).filter(Group.id == group_id).first()
    return group
    
def create_new_group(
    creator_id: int,
    name: str,
    visibility: bool,
    description: str,
    photo = None
):
    group = Group(owner_id = creator_id)
    group.name = name
    if (description != None):
        group.description = description
    else:
        group.description = ""
    if (photo):
        print(photo)
        group.photo_id = upload_image_to_webg_resized(photo, quality=90)
    else:
        group.photo_id = None 
    group.visibility = visibility
    db.session.add(group)
    db.session.commit()
    
def edit_group(
    group_id: int,
    name: str = None,
    visibility: bool = None,
    description: str = None,
    photo = None
):
    group = db.session.query(Group).filter(Group.id == group_id).first()
    if (name != None):
        group.name = name
    if (visibility != None):
        group.visibility = visibility
    if (description != None):
        group.description = description
    if (photo != None):
        group.photo_id = upload_image_to_webg_resized(photo, quality=90)

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
    photo_id = upload_image_to_webg_resized(image, quality=90)
    group = db.session.query(Group).filter(Group.id == group_id).first()
    group.photo_id = photo_id
    db.session.commit()