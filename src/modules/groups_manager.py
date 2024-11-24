from .db import db, User, Group, Roles, GroupInvite
from .photo_manager import upload_image_to_webg_resized
from sqlalchemy import or_, and_ 
from .invites_manager import get_user_group_invitations

def get_all_groups() -> [Group]:
    return db.session.query(Group).order_by(Group.name.asc()).all()

def get_group_owner(group_id: int) -> User:
    group = db.session.query(Group).filter(Group.id == group_id).first()
    owner = db.session.query(User).filter(User.id == group.owner_id).first()
    return owner

def user_is_member(user_id: int, group_id: int) -> bool:
    user = db.session.query(User).filter(User.id == user_id).first()
    group = db.session.query(Group).filter(Group.id == group_id).first()
    if (user.id == group.owner_id or user in group.users):
        return True
    return False

def get_user_invited_groups(user_id: int) -> [Group]:
    invites = get_user_group_invitations(user_id=user_id)
    group_ids = [invite.group_id for invite in invites]
    groups = db.session.query(Group).filter(
        and_(
            Group.id.in_(group_ids),
            GroupInvite.user_pending == True
        )
    )
    return groups

def get_user_requested_groups(user_id: int) -> [Group]:
    invites = db.session.query(GroupInvite).filter(
        and_(
        GroupInvite.user_id == user_id,
        GroupInvite.group_pending == True
        )
    ).all()
    group_ids = [invite.group_id for invite in invites]
    groups = db.session.query(Group).filter(
        Group.id.in_(group_ids)
    )
    return groups

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
) -> Group:
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

    return group
    
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
    db.session.commit()
    
def add_user_to_group(group_id: int, user_id: int):
    group = db.session.query(Group).filter(Group.id == group_id).first()
    group.users.append(user_id)
    db.session.commit()
    
# The user count excludes the owner
def get_user_count(group_id: int) -> int:
    group = get_group(group_id)
    return len(group.users)
    
def transfer_ownership_to_next(group_id: int):
    owner = get_group_owner(group_id=group_id)
    group = get_group(group_id=group_id)
    if (len(group.users) <= 0):
        print("Ownership transfer impossible")
        return
    new_owner = group.users.pop(0)
    print("New owner "+new_owner.username)
    group.users.append(owner)
    group.owner_id = new_owner.id

    db.session.commit()

def remove_user_from_group(group_id: int, user_id: int):
    group = db.session.query(Group).filter(Group.id == group_id).first()
    user = db.session.query(User).filter(User.id == user_id).first()

    if (user in group.users):
        group.users.remove(user)
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

def get_group_invite_group_pairs(user_id: int):
    results = db.session.query(GroupInvite, Group).join(
        Group,
        GroupInvite.group_id == Group.id
        ).filter(
            and_(
                GroupInvite.user_id == user_id,
                GroupInvite.user_pending == True
            )
        )
    return results

def get_group_request_group_pairs(user_id: int):
    results = db.session.query(GroupInvite, Group).join(
        Group,
        GroupInvite.group_id == Group.id
        ).filter(
            and_(
                GroupInvite.user_id == user_id,
                GroupInvite.group_pending == True
            )
        )
    return results