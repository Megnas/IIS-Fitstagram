from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_login import UserMixin
from enum import Enum

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Roles(Enum):
    ADMIN = 4
    MODERATOR = 3
    USER = 2
    VISITOR = 1

class Photo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(128), nullable=False)  # File name
    data: Mapped[bytes] = mapped_column(db.LargeBinary(length=(2**31 - 1)), nullable=False)  # Binary data
    mimetype: Mapped[str] = mapped_column(db.String(128), nullable=False)  # MIME type (e.g., image/jpeg)

user_group = db.Table("user_group",
    db.Column("group_id", db.Integer, db.ForeignKey("group.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id", primary_key=True)))

user_group_invite = db.Table("user_group_invite",
    db.Column("group_id", db.Integer, db.ForeignKey("group.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id", primary_key=True)))

class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(128), unique=True)
    username: Mapped[str] = mapped_column(db.String(128))
    password_hash: Mapped[str] = mapped_column(db.String(60))
    role: Mapped[int] = mapped_column(db.Enum(Roles))
    photo_id: Mapped[str] = mapped_column(ForeignKey(Photo.id), nullable=True)
    blocked: Mapped[bool] = mapped_column(db.Boolean)
    groups = db.relationship("Group", secondary=user_group, backref="user")
    invited_groups = db.relationship("Group", secondary=user_group_invite, backref="user")

class Group(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(64))
    owner_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    description: Mapped[str] = mapped_column(db.String(256))
    photo_id: Mapped[str] = mapped_column(ForeignKey(Photo.id))
    users = db.relationship("User", secondary=user_group, backref="group")
    invited_users = db.relationship("User", secondary=user_group_invite, backref="group")

class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(db.String(256))
    post_date: Mapped[str] = mapped_column(db.DateTime)
    photo_id: Mapped[str] = mapped_column(ForeignKey(Photo.id))
    visibility: Mapped[bool] = mapped_column(db.Boolean)

class Tag(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(32))
    blocked: Mapped[bool] = mapped_column(db.Boolean)

class PostTag(db.Model):
    post_id: Mapped[int] = mapped_column(ForeignKey(Post.id),primary_key=True,)
    tag_id: Mapped[int] = mapped_column(ForeignKey(Tag.id),primary_key=True,)

class PostGroup(db.Model):
    post_id: Mapped[int] = mapped_column(ForeignKey(Post.id),primary_key=True,)
    group_id: Mapped[int] = mapped_column(ForeignKey(Group.id),primary_key=True,)

class GroupInvite(db.Model):
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), primary_key=True, )
    group_id: Mapped[int] = mapped_column(ForeignKey(Group.id), primary_key=True, )
    user_pending: Mapped[bool] = mapped_column(db.Boolean)
    group_pending: Mapped[bool] = mapped_column(db.Boolean)
    date_created: Mapped[str] = mapped_column(db.DateTime)

class Score(db.Model):
    post_id: Mapped[int] = mapped_column(ForeignKey(Post.id),primary_key=True,)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id),primary_key=True,)
    score: Mapped[bool] = mapped_column(db.Boolean)

class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey(Post.id))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    content: Mapped[str] = mapped_column(db.String(256))
    timestamp: Mapped[str] = mapped_column(db.DateTime)
