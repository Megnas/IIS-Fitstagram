from .db import db, User, Group, Roles, GroupInvite
from datetime import datetime
from sqlalchemy import and_

def get_users_with_group_pending_invites(group_id: int) -> [User]:
    invites = db.session.query(GroupInvite).filter(
            and_(
                GroupInvite.group_pending == True,
                GroupInvite.group_id == group_id
            )
    ).all()
    user_ids = [invite.user_id for invite in invites]
    
    users = db.session.query(User).filter(
            User.id.in_(user_ids)
    ).all()

    return users

def get_users_with_user_pending_invites(group_id: int) -> [GroupInvite]:
    invites = db.session.query(GroupInvite).filter(
            and_(
                GroupInvite.user_pending == True,
                GroupInvite.group_id == group_id
            )
    ).all()
    user_ids = [invite.user_id for invite in invites]
    
    users = db.session.query(User).filter(
            User.id.in_(user_ids)
    ).all()

    return users

def invite_user_to_group(group_id: int, user_id: int):
    group = db.session.query(Group).filter(Group.id == group_id).first()
    user = db.session.query(User).filter(User.id == user_id).first()

    if (user in group.users):
        return 
    
    invite = db.session.query(GroupInvite).filter(
        and_(
            GroupInvite.user_id == user_id,
            GroupInvite.group_id == group_id
        )
    ).first()
    if (invite != None):
        return
    try:
        invite = GroupInvite(
            user_id=user.id,
            group_id=group.id,
            user_pending=True,
            group_pending=False,
            date_created=datetime.now()
        )
        db.session.add(invite)
        db.session.commit()
    except:
        db.session.rollback()

def request_group_join(group_id: int, user_id: int):
    group = db.session.query(Group).filter(Group.id == group_id).first()
    user = db.session.query(User).filter(User.id == user_id).first()
    
    if (user in group.users):
        return 
    
    invite = db.session.query(GroupInvite).filter(
        and_(
            GroupInvite.user_id == user_id,
            GroupInvite.group_id == group_id
        )
    ).first()
    if (invite != None):
        return
    try:
        invite = GroupInvite(
            user_id=user.id,
            group_id=group.id,
            user_pending=False,
            group_pending=True,
            date_created=datetime.now()
        )
        db.session.add(invite)
        db.session.commit()
    except:
        db.session.rollback()
    
def cancel_group_invite(user_id: int, group_id: int):
    invite = db.session.query(GroupInvite).filter(
        and_(
            GroupInvite.user_id == user_id,
            GroupInvite.group_id == group_id
        )
    ).first()

    if (invite == None):
        return
    
    db.session.delete(invite)
    db.session.commit()

def approve_group_invite(user_id: int, group_id: int):
    invite = db.session.query(GroupInvite).filter(
        and_(
            GroupInvite.user_id == user_id,
            GroupInvite.group_id == group_id
        )
    ).first()

    if (invite == None):
        return
    db.session.delete(invite)
    
    user = db.session.query(User).filter(
        User.id == user_id
    ).first()
    group = db.session.query(Group).filter(
        Group.id == group_id
    ).first()

    if (user in group.users):
        return None
    try:
        group.users.append(user)
        db.session.commit()
    except:
        db.session.rollback()
    
def get_invite(user_id: int, group_id: int) -> GroupInvite:
    invite = db.session.query(GroupInvite).filter(
        and_(
            GroupInvite.user_id == user_id,
            GroupInvite.group_id == group_id
        )
    ).first()
    return invite 

def get_user_group_invitations(user_id: int) -> [GroupInvite]:
    group_invitations = db.session.query(GroupInvite).filter(
        GroupInvite.user_id == user_id, GroupInvite.user_pending == True
    ).order_by(GroupInvite.date_created.desc()).all()
    return group_invitations

def get_group_member_requests(group_id: int) -> [GroupInvite]:
    group_invitations = db.session.query(GroupInvite).filter(
        GroupInvite.group_id == group_id, GroupInvite.group_pending == True
    ).order_by(GroupInvite.date_created.desc()).all()
    return group_invitations