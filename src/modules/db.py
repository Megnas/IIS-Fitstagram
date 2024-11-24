from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Column, PrimaryKeyConstraint
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
    db.Column("group_id", db.Integer, db.ForeignKey("group.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    PrimaryKeyConstraint('group_id', 'user_id'))

user_post = db.Table("user_post",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    PrimaryKeyConstraint('post_id', 'user_id'))

class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(128), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(db.String(128), nullable=False)
    unique_id: Mapped[str] = mapped_column(db.String(128), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(db.String(60))
    role: Mapped[int] = mapped_column(db.Enum(Roles), nullable=False)
    photo_id: Mapped[str] = mapped_column(ForeignKey(Photo.id), nullable=True)
    blocked: Mapped[bool] = mapped_column(db.Boolean, nullable=False)
    groups = db.relationship("Group", secondary=user_group, back_populates="users", cascade="all, delete")
    posts = db.relationship("Post", secondary=user_post, back_populates="users", cascade="all, delete")

group_post = db.Table("group_post",
    db.Column("group_id", db.Integer, db.ForeignKey("group.id")),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    PrimaryKeyConstraint('group_id', 'post_id'))

class Group(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(64), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    description: Mapped[str] = mapped_column(db.String(256), nullable=False)
    photo_id: Mapped[int] = mapped_column(ForeignKey(Photo.id), nullable=True)
    visibility: Mapped[bool] = mapped_column(db.Boolean, nullable=False)
    users = db.relationship("User", secondary=user_group, back_populates="groups", cascade="all, delete")
    posts = db.relationship("Post", secondary=group_post, back_populates="groups", cascade="all, delete")

    def __str__(self):
        return self.name
    
post_tag = db.Table("post_tag",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id")),
    PrimaryKeyConstraint('post_id', 'tag_id'))


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    description: Mapped[str] = mapped_column(db.String(256))
    post_date: Mapped[str] = mapped_column(db.DateTime, nullable=False)
    photo_id: Mapped[str] = mapped_column(ForeignKey(Photo.id), nullable=False)
    miniature_id: Mapped[str] = mapped_column(ForeignKey(Photo.id), nullable=False)
    visibility: Mapped[bool] = mapped_column(db.Boolean, nullable=False)
    tags = db.relationship("Tag", secondary=post_tag, back_populates="posts", cascade="all, delete")
    groups = db.relationship("Group", secondary=group_post, back_populates="posts", cascade="all, delete")
    users = db.relationship("User", secondary=user_post, back_populates="posts", cascade="all, delete")

class Tag(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(64), nullable=False, unique=True, index=True)
    blocked: Mapped[bool] = mapped_column(db.Boolean, nullable=False)
    posts = db.relationship("Post", secondary=post_tag, back_populates="tags", cascade="all, delete")

class GroupInvite(db.Model):
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), primary_key=True, )
    group_id: Mapped[int] = mapped_column(ForeignKey(Group.id), primary_key=True, )
    user_pending: Mapped[bool] = mapped_column(db.Boolean)
    group_pending: Mapped[bool] = mapped_column(db.Boolean)
    date_created: Mapped[str] = mapped_column(db.DateTime)

class Score(db.Model):
    post_id: Mapped[int] = mapped_column(ForeignKey(Post.id),nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id),nullable=False)
    score: Mapped[bool] = mapped_column(db.Boolean, nullable=False)

    __table_args__ = (
    db.PrimaryKeyConstraint(
        post_id, user_id,
        ),
    )

class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey(Post.id))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    content: Mapped[str] = mapped_column(db.String(256), nullable=False)
    timestamp: Mapped[str] = mapped_column(db.DateTime, nullable=False)
