from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import user_manager
from flask_login import login_required, logout_user, login_user, current_user

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        try:
            user_manager.create_user(username=username, pwd=password, mail=email)
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Registration Failed.', 'danger')
            print("Registration failed!", e)
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = user_manager.login_user(mail=email, pwd=password)
        if user:
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('view.index'))
        flash('Invalid credentials, please try again.', 'danger')
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('view.index'))