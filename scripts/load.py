# scripts/load_colleges.py

import csv
from app import create_app
from app.db import db
from app.models import College
import os


app = create_app()

CSV_PATH = os.path.join("data", "college_data_filtered.csv")

def parse_float(value):
    try:
        if not value or value.strip().lower() in ("null", "privacySuppressed", "privacysuppressed"):
            return None
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_bool(value):
    return str(value).strip() == "1"

with app.app_context():
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # Skip if required fields are missing
            if not row.get("UNITID") or not row.get("INSTNM"):
                continue

            # Check for existing college (by UNITID)
            if College.query.filter_by(unitid=row["UNITID"]).first():
                continue  # Skip duplicates

            college = College(
                unitid=int(row["UNITID"]),
                name=row["INSTNM"],
                city=row["CITY"],
                state=row["STABBR"],
                zip_code=row["ZIP"],
                latitude=parse_float(row["LATITUDE"]),
                longitude=parse_float(row["LONGITUDE"]),
                website_url=row["INSTURL"],
                net_price_url=row["NPCURL"],
                accrediting_agency=row["ACCREDAGENCY"],
                control=int(float(row["CONTROL"])) if row.get("CONTROL") else None,
                locale=int(float(row["LOCALE"])) if row.get("LOCALE") else None,
                region=int(float(row["REGION"])) if row.get("REGION") else None,
                is_hbcu=parse_bool(row.get("HBCU")),
                is_tribal=parse_bool(row.get("TRIBAL")),
                cost_of_attendance=parse_float(row.get("COSTT4_A")),
                tuition_in_state=parse_float(row.get("TUITIONFEE_IN")),
                tuition_out_of_state=parse_float(row.get("TUITIONFEE_OUT")),
                median_debt=parse_float(row.get("DEBT_MDN")),
                earnings_income1=parse_float(row.get("MD_EARN_WNE_INC1_P11")),
                earnings_income2=parse_float(row.get("MD_EARN_WNE_INC2_P11")),
                earnings_income3=parse_float(row.get("MD_EARN_WNE_INC3_P11")),
                retention_rate_ft=parse_float(row.get("RET_FT4")),
                graduation_rate_150=parse_float(row.get("C150_4")),
                admission_rate=parse_float(row.get("ADM_RATE")),
                sat_average=parse_float(row.get("SAT_AVG")),
                act_composite_25=parse_float(row.get("ACTCM25")),
                undergrad_population=parse_float(row.get("UGDS")),
                pct_white=parse_float(row.get("UGDS_WHITE")),
                pct_black=parse_float(row.get("UGDS_BLACK")),
                pct_hispanic=parse_float(row.get("UGDS_HISP")),
                pct_asian=parse_float(row.get("UGDS_ASIAN")),
                pct_pell_eligible=parse_float(row.get("PELL_EVER")),
                avg_faculty_salary=parse_float(row.get("AVGFACSAL"))
            )

            db.session.add(college)

        db.session.commit()
        print("✅ Colleges successfully loaded into the database.")
