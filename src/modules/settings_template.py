from flask import Blueprint, render_template, redirect, url_for, flash
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .db import db
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp

from .user_manager import update_user

bp = Blueprint('settings', __name__)

class SettingsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=32)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=5, max=128)])
    unique_id = StringField('UID', validators=[
        DataRequired(), 
        Length(min=5, max=128), 
        Regexp(r'^[a-z0-9_]+$', message="UID must not contain spaces or uppercase letters and can only include lowercase letters, numbers, and underscores.")
    ])
    password = PasswordField('New Password')
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Save Changes')

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    user = current_user  # Get the logged-in user

    if form.validate_on_submit():
        try:
            update_user(user, form.username.data, form.email.data, form.password.data, form.profile_picture.data, form.unique_id.data)
            flash('Your settings have been updated!', 'success')
        except:
            flash('Your settings have not been updated!', 'danger')
        return redirect(url_for('settings.settings'))

    if form.unique_id.errors:
        flash("User ID must not contain spaces or uppercase letters and can only include lowercase letters, numbers, and underscores.", 'danger')

    if form.email.errors:
        flash("Email format invalid", 'danger')

    # Prepopulate the form with the current user's data
    if not form.is_submitted():
        form.username.data = user.username
        form.email.data = user.email
        form.unique_id.data = user.unique_id

    return render_template('settings.html', form=form)