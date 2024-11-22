from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import user_manager
from flask_login import login_required, logout_user, login_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

bp = Blueprint('auth', __name__)

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=5, max=128)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=32)])
    password = PasswordField('New Password')
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=5, max=128)])
    password = PasswordField('New Password')
    submit = SubmitField('Login')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        try:
            user_manager.create_user(username=form.username.data, pwd=form.password.data, mail=form.email.data)
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Registration Failed.', 'danger')
            print("Registration failed!", e)
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = user_manager.login_user(mail=form.email.data, pwd=form.password.data)
        if user:
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('view.index'))
        flash('Invalid credentials, please try again.', 'danger')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('view.index'))