from datetime import datetime
from .db import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    reviews = db.relationship('Review', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"

class College(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unitid = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    zip_code = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    website_url = db.Column(db.String(255))
    net_price_url = db.Column(db.String(255))
    accrediting_agency = db.Column(db.String(255))

    control = db.Column(db.Integer)         # 1=Public, 2=Private nonprofit, 3=Private for-profit
    locale = db.Column(db.Integer)          # Urban/rural code
    region = db.Column(db.Integer)
    is_hbcu = db.Column(db.Boolean)
    is_tribal = db.Column(db.Boolean)

    # Cost & Tuition
    cost_of_attendance = db.Column(db.Float)
    tuition_in_state = db.Column(db.Float)
    tuition_out_of_state = db.Column(db.Float)

    # Debt & Earnings
    median_debt = db.Column(db.Float)
    earnings_income1 = db.Column(db.Float)
    earnings_income2 = db.Column(db.Float)
    earnings_income3 = db.Column(db.Float)

    # Outcomes & Admissions
    retention_rate_ft = db.Column(db.Float)
    graduation_rate_150 = db.Column(db.Float)
    admission_rate = db.Column(db.Float)
    sat_average = db.Column(db.Float)
    act_composite_25 = db.Column(db.Float)

    # Enrollment & Demographics
    undergrad_population = db.Column(db.Float)
    pct_white = db.Column(db.Float)
    pct_black = db.Column(db.Float)
    pct_hispanic = db.Column(db.Float)
    pct_asian = db.Column(db.Float)

    # Financial Aid & Faculty
    pct_pell_eligible = db.Column(db.Float)
    avg_faculty_salary = db.Column(db.Float)

    programs = db.relationship('Program', backref='college', lazy=True)
    reviews = db.relationship('Review', backref='college', lazy=True)

    def __repr__(self):
        return f"<College {self.name} ({self.state})>"

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    degree_type = db.Column(db.String(50))  # e.g., "Bachelor's", "Master's", etc.
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)

    def __repr__(self):
        return f"<Program {self.name}>"

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5 stars
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)

    def __repr__(self):
        return f"<Review {self.rating}★ for College ID {self.college_id}>"
