from flask import Blueprint, render_template, redirect, url_for, flash
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .db import db
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import DataRequired, Email, Length

from .user_manager import update_user

bp = Blueprint('settings', __name__)

class SettingsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=5, max=120)])
    password = PasswordField('New Password')
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Save Changes')

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    user = current_user  # Get the logged-in user

    if form.validate_on_submit():
        update_user(user, form.username.data, form.email.data, form.password.data, form.profile_picture.data)
        flash('Your settings have been updated!', 'success')
        return redirect(url_for('settings.settings'))

    # Prepopulate the form with the current user's data
    if not form.is_submitted():
        form.username.data = user.username
        form.email.data = user.email

    return render_template('settings.html', form=form)