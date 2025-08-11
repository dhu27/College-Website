from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.db import db
from app.models import CollegeList, CollegeListEntry

lists_bp = Blueprint('lists', __name__)

@lists_bp.route('/my-lists')
@login_required
def my_lists():
    lists = CollegeList.query.filter_by(user_id=current_user.id).all()
    return render_template('my_lists.html', lists=lists)

@lists_bp.route('/lists/create', methods=['POST'])
@login_required
def create_list():
    name = request.form.get('name')
    if not name:
        flash('List name required', 'error')
        return redirect(url_for('lists.my_lists'))
    new_list = CollegeList(name=name, user_id=current_user.id)
    db.session.add(new_list)
    db.session.commit()
    return redirect(url_for('lists.my_lists'))

@lists_bp.route('/lists/<int:list_id>/add', methods=['POST'])
@login_required
def add_to_list(list_id):
    college_id = request.form.get('college_id', type=int)
    if not college_id:
        flash('college_id required', 'error')
        return redirect(url_for('lists.my_lists'))
    entry = CollegeListEntry(list_id=list_id, college_id=college_id)
    db.session.add(entry)
    db.session.commit()
    return redirect(url_for('lists.my_lists'))

