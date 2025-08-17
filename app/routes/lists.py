from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.db import db
from app.models import CollegeList, CollegeListEntry, College

lists_bp = Blueprint('lists', __name__)

@lists_bp.route('/my-lists')
@login_required
# Display all lists for the current user in the UI
def my_lists():
    lists = CollegeList.query.filter_by(user_id=current_user.id).all()
    return render_template('my_lists.html', lists=lists)

@lists_bp.route('/lists/create', methods=['POST'])
@login_required
# Create a new list for the current user (form submission)
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
# Add a college to a specific list (form submission)
def add_to_list(list_id):
    college_id = request.form.get('college_id', type=int)
    if not college_id:
        flash('college_id required', 'error')
        return redirect(url_for('lists.my_lists'))
    entry = CollegeListEntry(list_id=list_id, college_id=college_id)
    db.session.add(entry)
    db.session.commit()
    return redirect(url_for('lists.my_lists'))

############################################################
# RESTful API endpoints for AJAX list management
############################################################

# Get all lists and their colleges for the current user (AJAX)
@lists_bp.route('/api/lists', methods=['GET'])
@login_required
def api_get_lists():
    lists = CollegeList.query.filter_by(user_id=current_user.id).all()
    result = []
    for l in lists:
        colleges = [entry.college_id for entry in l.colleges]
        result.append({'id': l.id, 'name': l.name, 'colleges': colleges})
    return jsonify(result)

# Create a new list for the current user (AJAX)
@lists_bp.route('/api/lists', methods=['POST'])
@login_required
def api_create_list():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'List name required'}), 400
    new_list = CollegeList(name=name, user_id=current_user.id)
    db.session.add(new_list)
    db.session.commit()
    return jsonify({'id': new_list.id, 'name': new_list.name})

# Rename a list (AJAX)
@lists_bp.route('/api/lists/<int:list_id>', methods=['PUT'])
@login_required
def api_rename_list(list_id):
    data = request.get_json()
    name = data.get('name')
    clist = CollegeList.query.filter_by(id=list_id, user_id=current_user.id).first()
    if not clist:
        return jsonify({'error': 'List not found'}), 404
    clist.name = name
    db.session.commit()
    return jsonify({'id': clist.id, 'name': clist.name})

# Delete a list (AJAX)
@lists_bp.route('/api/lists/<int:list_id>', methods=['DELETE'])
@login_required
def api_delete_list(list_id):
    clist = CollegeList.query.filter_by(id=list_id, user_id=current_user.id).first()
    if not clist:
        return jsonify({'error': 'List not found'}), 404
    db.session.delete(clist)
    db.session.commit()
    return jsonify({'success': True})

# Add a college to a list (AJAX)
@lists_bp.route('/api/lists/<int:list_id>/colleges', methods=['POST'])
@login_required
def api_add_college_to_list(list_id):
    data = request.get_json()
    college_id = data.get('college_id')
    clist = CollegeList.query.filter_by(id=list_id, user_id=current_user.id).first()
    college = College.query.get(college_id)
    if not clist or not college:
        return jsonify({'error': 'List or college not found'}), 404
    entry = CollegeListEntry.query.filter_by(list_id=list_id, college_id=college_id).first()
    if entry:
        return jsonify({'error': 'College already in list'}), 400
    new_entry = CollegeListEntry(list_id=list_id, college_id=college_id)
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({'success': True})

# Remove a college from a list (AJAX)
@lists_bp.route('/api/lists/<int:list_id>/colleges/<int:college_id>', methods=['DELETE'])
@login_required
def api_remove_college_from_list(list_id, college_id):
    entry = CollegeListEntry.query.filter_by(list_id=list_id, college_id=college_id).first()
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'success': True})

