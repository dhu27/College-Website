from flask import Blueprint, render_template, request
from app.models import College

colleges_bp = Blueprint('colleges', __name__)

@colleges_bp.route('/colleges')
def college_list():
    query = request.args.get('q', '').strip()

    if query:
        colleges = College.query.filter(College.name.ilike(f"%{query}%")).order_by(College.name).all()
    else:
        colleges = College.query.order_by(College.id).limit(50).all()

    return render_template('colleges_list.html', colleges=colleges)

@colleges_bp.route('/college/<int:college_id>', endpoint='college_detail')
def college_detail(college_id):
    college = College.query.get_or_404(college_id)
    return render_template('college_detail.html', college=college)




