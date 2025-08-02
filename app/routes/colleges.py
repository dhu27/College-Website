from flask import Blueprint, render_template, request
from sqlalchemy import or_, and_
from app.models import College
from app import db

colleges_bp = Blueprint('colleges', __name__)

@colleges_bp.route('/colleges')
def college_list():
    query = College.query
    filters_applied = []

    # Search by name
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(College.name.ilike(f"%{search}%"))
        filters_applied.append(f"Search: {search}")

    # State
    state = request.args.get('state')
    if state:
        query = query.filter(College.state == state)
        filters_applied.append(f"State: {state}")

    # Control type
    control_map = {'public': 1, 'private': 2}
    control_filters = request.args.getlist('control')
    if control_filters:
        values = [control_map[c] for c in control_filters if c in control_map]
        query = query.filter(College.control.in_(values))
        filters_applied.append(f"Control: {control_filters}")

    # Max Cost of Attendance
    max_cost = request.args.get('max_cost', type=float)
    if max_cost is not None:
        query = query.filter(College.cost_of_attendance <= max_cost)
        filters_applied.append(f"Max Cost: {max_cost}")

    # Student Body Size
    sizes = request.args.getlist('size')
    size_conditions = []
    for s in sizes:
        if s == 'small':
            size_conditions.append(College.undergrad_population < 5000)
        elif s == 'medium':
            size_conditions.append(College.undergrad_population.between(5000, 15000))
        elif s == 'large':
            size_conditions.append(College.undergrad_population > 15000)
    if size_conditions:
        query = query.filter(or_(*size_conditions))
        filters_applied.append(f"Size: {sizes}")

    # Specialties
    specialty_map = {
        'All-Women': College.is_women_only,
        'All-Men': College.is_men_only,
        'AANAPISI': College.is_annhi,
        'HBCU': College.is_hbcu,
        'NATIVE AMERICAN': College.is_tribal
    }
    specialties = request.args.getlist('specialties')
    for spec in specialties:
        column = specialty_map.get(spec)
        if column is not None:
            query = query.filter(column.is_(True))
    if specialties:
        filters_applied.append(f"Specialties: {specialties}")

    # Selectivity by admission rate
    selectivity_map = {
        'Extremely Selective': College.admission_rate <= 0.10,
        'Very Selective': College.admission_rate.between(0.10, 0.25),
        'Selective': College.admission_rate.between(0.25, 0.50),
        'Average': College.admission_rate.between(0.50, 0.75),
        'Safety': College.admission_rate > 0.75
    }
    selectivity_levels = request.args.getlist('selectivity')
    selectivity_filters = [selectivity_map[s] for s in selectivity_levels if s in selectivity_map]
    if selectivity_filters:
        query = query.filter(or_(*selectivity_filters))
        filters_applied.append(f"Selectivity: {selectivity_levels}")

    # Final Query
    colleges = query.order_by(College.name).all()

    # Debug Output (for development only)
    if filters_applied:
        print("Filters applied:")
        for f in filters_applied:
            print(f"- {f}")
        print(f"Total colleges returned: {len(colleges)}")

    return render_template('colleges_list.html', colleges=colleges)

@colleges_bp.route('/college/<int:college_id>', endpoint='college_detail')
def college_detail(college_id):
    college = College.query.get_or_404(college_id)
    return render_template('college_detail.html', college=college)




