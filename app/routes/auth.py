from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.db import db
from app.models import User
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['login']  # could be email OR username
        password = request.form['password']

        user = User.query.filter(
            or_(User.email == login_input, User.username == login_input)
        ).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('main.home'))

        flash('Invalid username/email or password.')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
        elif User.query.filter_by(username=username).first():
            flash('Username already taken.')
        else:
            user = User(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                password_hash=password
            )
            db.session.add(user)
            db.session.commit()
            flash('Account created! You can now log in.')
            return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))
