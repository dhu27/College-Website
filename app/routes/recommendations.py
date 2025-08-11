from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import CollegeList
from app.ml.recommendations import recommend_colleges_filtered
from flask import current_app

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/recommendations', methods=['GET', 'POST'])
@login_required
def get_recommendations():
    user_lists = CollegeList.query.filter_by(user_id=current_user.id).all()
    results = []
    if request.method == 'POST':
        states = request.form.getlist('states')
        user_sat = request.form.get('sat', type=int)
        user_act = request.form.get('act', type=int)
        priorities = {
            'academics': float(request.form.get('academics', 0) or 0),
            'value': float(request.form.get('value', 0) or 0),
            'diversity': float(request.form.get('diversity', 0) or 0),
            'urbanicity': float(request.form.get('urbanicity', 0) or 0),
            'campus': float(request.form.get('campus', 0) or 0),
        }
        data_path = current_app.config.get('COLLEGE_DATA_PATH', 'data/college_data_filtered.csv')
        results = recommend_colleges_filtered(data_path, states, user_sat, user_act, None, priorities, top_n=12).to_dict('records')
    return render_template('recommendations.html', user_lists=user_lists, results=results)