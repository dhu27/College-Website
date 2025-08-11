from datetime import datetime, timezone as dt_timezone
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
    __tablename__ = 'college'
    id = db.Column(db.Integer, primary_key=True)

    unitid = db.Column(db.Integer)
    name = db.Column(db.String(255))  # INSTNM
    website = db.Column(db.String(255))  # INSTURL
    net_price_url = db.Column(db.String(255))  # NPCURL
    city = db.Column(db.String(255))  # CITY
    state = db.Column(db.String(255))  # STABBR
    zip = db.Column(db.String(255))  # ZIP

    latitude = db.Column(db.Float)  # LATITUDE
    longitude = db.Column(db.Float)  # LONGITUDE

    accrediting_agency = db.Column(db.String(255))  # ACCREDAGENCY

    school_degree = db.Column(db.Integer)  # SCH_DEG
    highest_degree = db.Column(db.Integer)  # HIGHDEG
    predominant_degree = db.Column(db.Integer)  # PREDDEG

    control = db.Column(db.Integer)  # CONTROL
    num_branches = db.Column(db.Integer)  # NUMBRANCH
    is_main_campus = db.Column(db.Boolean)  # MAIN

    locale = db.Column(db.Integer)  # LOCALE
    region = db.Column(db.Integer)  # REGION
    carnegie_basic_class = db.Column(db.Integer)  # CCBASIC
    carnegie_size_class = db.Column(db.Integer)  # CCSIZSET

    is_hbcu = db.Column(db.Boolean)  # HBCU
    is_annhi = db.Column(db.Boolean)  # ANNHI
    is_hsi = db.Column(db.Boolean)  # HSI
    is_men_only = db.Column(db.Boolean)  # MENONLY
    is_women_only = db.Column(db.Boolean)  # WOMENONLY
    is_tribal = db.Column(db.Boolean)  # HBCU.1 (possibly tribal colleges — confirm context)

    cost_of_attendance = db.Column(db.Float)  # COSTT4_A
    tuition_in_state = db.Column(db.Float)  # TUITIONFEE_IN
    tuition_out_of_state = db.Column(db.Float)  # TUITIONFEE_OUT

    median_grad_debt = db.Column(db.Float)  # GRAD_DEBT_MDN_SUPP
    median_debt = db.Column(db.Float)  # DEBT_MDN

    earnings_income1 = db.Column(db.Float)  # MD_EARN_WNE_INC1_P11
    earnings_income2 = db.Column(db.Float)  # MD_EARN_WNE_INC2_P11
    earnings_income3 = db.Column(db.Float)  # MD_EARN_WNE_INC3_P11

    retention_rate_ft = db.Column(db.Float)  # RET_FT4
    retention_rate_part_time = db.Column(db.Float)  # RET_PT4
    retention_rate = db.Column(db.Float)  # RET_FTL4

    graduation_rate_150 = db.Column(db.Float)  # C150_4
    graduation_rate_less_than_4 = db.Column(db.Float)  # C150_L4
    graduation_rate_200 = db.Column(db.Float)  # C200_4

    admission_rate = db.Column(db.Float)  # ADM_RATE
    sat_avg = db.Column(db.Float)  # SAT_AVG
    sat_verbal_25 = db.Column(db.Float)  # SATVR25
    sat_math_25 = db.Column(db.Float)  # SATMT25
    act_math_25 = db.Column(db.Float)  # ACTMT25
    act_composite_25 = db.Column(db.Float)  # ACTCM25

    undergrad_population = db.Column(db.Integer)  # UGDS
    pct_white = db.Column(db.Float)  # UGDS_WHITE
    pct_black = db.Column(db.Float)  # UGDS_BLACK
    pct_hispanic = db.Column(db.Float)  # UGDS_HISP
    pct_asian = db.Column(db.Float)  # UGDS_ASIAN
    pct_aian = db.Column(db.Float)  # UGDS_AIAN
    pct_nhpi = db.Column(db.Float)  # UGDS_NHPI
    pct_two_or_more = db.Column(db.Float)  # UGDS_2MOR
    pct_unknown = db.Column(db.Float)  # UGDS_UNKN
    pct_nonresident_alien = db.Column(db.Float)  # UGDS_NRA

    pct_pell = db.Column(db.Float)  # PELL_EVER
    avg_faculty_salary = db.Column(db.Float)

    #wiki api
    description = db.Column(db.Text) # college description
    photo_url = db.Column(db.Text) # image URL


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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(dt_timezone.utc))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)

    def __repr__(self):
        return f"<Review {self.rating}★ for College ID {self.college_id}>"
    
class CollegeList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(dt_timezone.utc))
    colleges = db.relationship('CollegeListEntry', backref='list', lazy=True)

class CollegeListEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('college_list.id'))
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'))
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(dt_timezone.utc))
    notes = db.Column(db.Text)