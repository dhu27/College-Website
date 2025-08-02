import pandas as pd
from app import create_app
from app.db import db
from app.models import College

def parse_bool(value):
    truthy = {"1", "1.0", "true", "yes", "y", "True", "Yes", "TRUE", "YES"}
    falsy = {"0", "0.0", "false", "no", "n", "False", "No", "FALSE", "NO", "", "nan"}

    if value is None:
        return False

    val = str(value).strip().lower()

    if val in truthy:
        return True
    elif val in falsy:
        return False

    return False



def parse_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def parse_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

app = create_app()
app.app_context().push()

df = pd.read_csv("data/final_college_data.csv")

for _, row in df.iterrows():
    if College.query.filter_by(unitid=row["UNITID"]).first():
        continue

    college = College(
        unitid=parse_int(row["UNITID"]),
        name=row["INSTNM"],
        website=row["INSTURL"],
        net_price_url=row["NPCURL"],
        city=row["CITY"],
        state=row["STABBR"],
        zip=row["ZIP"],
        latitude=parse_float(row["LATITUDE"]),
        longitude=parse_float(row["LONGITUDE"]),
        accrediting_agency=row["ACCREDAGENCY"],
        school_degree=parse_int(row["SCH_DEG"]),
        highest_degree=parse_int(row["HIGHDEG"]),
        predominant_degree=parse_int(row["PREDDEG"]),
        control=parse_int(row["CONTROL"]),
        num_branches=parse_int(row["NUMBRANCH"]),
        is_main_campus=parse_bool(row["MAIN"]),
        locale=parse_int(row["LOCALE"]),
        region=parse_int(row["REGION"]),
        carnegie_basic_class=parse_int(row["CCBASIC"]),
        carnegie_size_class=parse_int(row["CCSIZSET"]),
        is_hbcu=parse_bool(row["HBCU"]),
        is_annhi=parse_bool(row["ANNHI"]),
        is_tribal=parse_bool(row["HBCU.1"]),
        is_hsi=parse_bool(row["HSI"]),
        is_men_only=parse_bool(row["MENONLY"]),
        is_women_only=parse_bool(row["WOMENONLY"]),
        cost_of_attendance=parse_float(row["COSTT4_A"]),
        tuition_in_state=parse_float(row["TUITIONFEE_IN"]),
        tuition_out_of_state=parse_float(row["TUITIONFEE_OUT"]),
        median_grad_debt=parse_float(row["GRAD_DEBT_MDN_SUPP"]),
        median_debt=parse_float(row["DEBT_MDN"]),
        earnings_income1=parse_float(row["MD_EARN_WNE_INC1_P11"]),
        earnings_income2=parse_float(row["MD_EARN_WNE_INC2_P11"]),
        earnings_income3=parse_float(row["MD_EARN_WNE_INC3_P11"]),
        retention_rate=parse_float(row["RET_FT4"]),
        retention_rate_part_time=parse_float(row["RET_PT4"]),
        graduation_rate_150=parse_float(row["C150_4"]),
        graduation_rate_200=parse_float(row["C200_4"]),
        graduation_rate_less_than_4=parse_float(row["C150_L4"]),
        admission_rate=parse_float(row["ADM_RATE"]),
        sat_avg=parse_float(row["SAT_AVG"]),
        sat_verbal_25=parse_float(row["SATVR25"]),
        sat_math_25=parse_float(row["SATMT25"]),
        act_math_25=parse_float(row["ACTMT25"]),
        act_composite_25=parse_float(row["ACTCM25"]),
        undergrad_population=parse_int(row["UGDS"]),
        pct_white=parse_float(row["UGDS_WHITE"]),
        pct_black=parse_float(row["UGDS_BLACK"]),
        pct_hispanic=parse_float(row["UGDS_HISP"]),
        pct_asian=parse_float(row["UGDS_ASIAN"]),
        pct_aian=parse_float(row["UGDS_AIAN"]),
        pct_nhpi=parse_float(row["UGDS_NHPI"]),
        pct_two_or_more=parse_float(row["UGDS_2MOR"]),
        pct_unknown=parse_float(row["UGDS_UNKN"]),
        pct_nonresident_alien=parse_float(row["UGDS_NRA"]),
        pct_pell=parse_float(row["PELL_EVER"]),
        avg_faculty_salary=parse_float(row["AVGFACSAL"]),
        description=row["wiki_description"],
        photo_url=row["wiki_image"]
    )

    db.session.add(college)

db.session.commit()
print("Data load complete.")
