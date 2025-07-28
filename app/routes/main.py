# app/routes/main.py
from flask_login import login_required
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/my-colleges')
@login_required
def my_colleges():
    return render_template('my_colleges.html')
