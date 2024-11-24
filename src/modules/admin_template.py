from flask import Blueprint, abort, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm

from .user_manager import update_user
from .user_manager import create_user as register_new_user

from .db import Roles, User, db, Tag

bp = Blueprint('admin', __name__)

@bp.route('/admin')
@login_required
def admin():
    if not(current_user.role == Roles.MODERATOR or current_user.role == Roles.ADMIN):
        abort(401, description="Not allowed")
    return render_template("admin.html")

@bp.route('/admin/users')
@login_required
def admin_users():
    if not(current_user.role == Roles.MODERATOR or current_user.role == Roles.ADMIN):
        abort(401, description="Not allowed")

    blocked_users = db.session.query(User).filter(User.blocked == True, User.role == Roles.USER).all()
    not_blocked_users = db.session.query(User).filter(User.blocked == False, User.role == Roles.USER).all()
    moderators = db.session.query(User).filter(User.role == Roles.MODERATOR).all()

    return render_template("admin_users.html", blocked_users=blocked_users, not_blocked_users=not_blocked_users,moderators=moderators)

@bp.route('/admin_block/<int:user_id>', methods=['POST'])
def admin_block(user_id):
    if not(current_user.role == Roles.MODERATOR or current_user.role == Roles.ADMIN):
        abort(401, description="Not allowed")
    user = User.query.get_or_404(user_id)
    user.blocked = not user.blocked
    db.session.commit()
    return redirect(url_for('admin.admin_users'))

@bp.route('/make_mod/<int:user_id>', methods=['POST'])
def make_mod(user_id):
    if not(current_user.role == Roles.ADMIN):
        abort(401, description="Not allowed")
    user: User = User.query.get_or_404(user_id)
    if user.role == Roles.ADMIN or user.blocked:
        abort(401, description="Not allowed")
    if user.role == Roles.USER:
        user.role = Roles.MODERATOR
    elif user.role == Roles.MODERATOR:
        user.role = Roles.USER
    db.session.commit()
    return redirect(url_for('admin.admin_users'))

class SettingsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=32)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=5, max=128)])
    unique_id = StringField('UID', validators=[
        DataRequired(), 
        Length(min=5, max=128), 
        Regexp(r'^[a-z0-9_]+$', message="UID must not contain spaces or uppercase letters and can only include lowercase letters, numbers, and underscores.")
    ])
    password = PasswordField('New Password')
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only!')])
    submit = SubmitField('Save Changes')

@bp.route('/admin_settings/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_settings(user_id):
    if not(current_user.role == Roles.ADMIN):
        abort(401, description="Not allowed")
    user = User.query.get_or_404(user_id)

    form = SettingsForm()

    if form.validate_on_submit():
        try:
            update_user(user, form.username.data, form.email.data, form.password.data, form.profile_picture.data, form.unique_id.data)
            flash('Your settings have been updated!', 'success')
        except:
            flash('Your settings have not been updated!', 'danger')
        return redirect(url_for('admin.admin_settings', user_id=user.id))

    if form.unique_id.errors:
        flash("User ID must not contain spaces or uppercase letters and can only include lowercase letters, numbers, and underscores.", 'danger')

    if form.email.errors:
        flash("Email format invalid", 'danger')

    # Prepopulate the form with the current users data
    if not form.is_submitted():
        form.username.data = user.username
        form.email.data = user.email
        form.unique_id.data = user.unique_id

    return render_template('admin_settings.html', form=form, selected_user=user)

@bp.route('/admin/tags')
@login_required
def admin_tags():
    if not(current_user.role == Roles.MODERATOR or current_user.role == Roles.ADMIN):
        abort(401, description="Not allowed")

    blocked_tags = db.session.query(Tag).filter(Tag.blocked == True).all()
    not_blocked_tags = db.session.query(Tag).filter(Tag.blocked == False).all()

    return render_template("admin_tags.html", blocked_tags=blocked_tags, not_blocked_tags=not_blocked_tags)

@bp.route('/admin_block_tag/<int:tag_id>', methods=['POST'])
def admin_block_tag(tag_id):
    if not(current_user.role == Roles.MODERATOR or current_user.role == Roles.ADMIN):
        abort(401, description="Not allowed")
    tag = Tag.query.get_or_404(tag_id)
    tag.blocked = not tag.blocked
    db.session.commit()
    return redirect(url_for('admin.admin_tags'))

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(), 
        Length(min=5, max=128)
    ])
    unique_id = StringField('UID', validators=[
        DataRequired(), 
        Length(min=5, max=128), 
        Regexp(r'^[a-z0-9_]+$', message="UID must not contain spaces or uppercase letters and can only include lowercase letters, numbers, and underscores.")
    ])
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=32)
    ])
    password = PasswordField('New Password')
    submit = SubmitField('Register')

@bp.route('/admin/create_user', methods=['GET', 'POST'])
def create_user():
    if not(current_user.role == Roles.ADMIN):
        abort(401, description="Not allowed")

    form = RegisterForm()

    if form.validate_on_submit():
        try:
            user = register_new_user(username=form.username.data, pwd=form.password.data, mail=form.email.data, uid=form.unique_id.data)
            flash('User creation succesful', 'danger')
            return redirect(url_for('admin.create_user'))
        except Exception as e:
            db.session.rollback()
            flash('Registration Failed.', 'danger')
            print("Registration failed!", e)

    if form.unique_id.errors:
        flash("User ID must not contain spaces or uppercase letters and can only include lowercase letters, numbers, and underscores.", 'danger')

    if form.email.errors:
        flash("Email format invalid", 'danger')

    return render_template('admin_create_user.html', form=form)