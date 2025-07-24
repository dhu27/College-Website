import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import List, Dict, Optional

# Load and prepare the college dataset
def load_filtered_college_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, low_memory=False)

    # Compute Diversity Score
    race_cols = ['UGDS_WHITE', 'UGDS_BLACK', 'UGDS_HISP', 'UGDS_ASIAN', 'UGDS_UNKN']
    if 'DIVERSITY_SCORE' not in df.columns and all(col in df.columns for col in race_cols):
        for col in race_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        def calc_diversity(row):
            vals = row[race_cols].dropna().astype(float).values
            vals = vals[vals > 0]
            return -np.sum(vals * np.log(vals)) if vals.size > 0 else np.nan
        df['DIVERSITY_SCORE'] = df.apply(calc_diversity, axis=1)

    # Compute Urbanicity Score
    if 'URBANICITY_SCORE' not in df.columns and 'LOCALE' in df.columns:
        def locale_numeric(val):
            try:
                v = int(val)
                if v in (11, 12, 13): return 1.0
                if v in (21, 22, 23): return 0.75
                if v in (31, 32, 33): return 0.5
                if v in (41, 42, 43): return 0.25
            except:
                return np.nan
        df['URBANICITY_SCORE'] = df['LOCALE'].apply(locale_numeric)

    return df

# Feature mappings aligned with user priorities
updated_feature_map = {
    'academics':    ['SAT_AVG', 'RET_FT4', 'C150_4', 'ADM_RATE'],
    'value':        ['MD_EARN_WNE_INC2_P11', 'TUITIONFEE_IN', 'DEBT_MDN'],
    'professors':   ['AVGFACSAL'],
    'campus':       ['UGDS'],
    'diversity':    ['DIVERSITY_SCORE'],
    'urbanicity':   ['URBANICITY_SCORE']
}

# Main recommendation function
def recommend_colleges_filtered(
    file_path: str,
    states: List[str],
    user_sat: Optional[int],
    user_act: Optional[int],
    user_gpa: Optional[float],
    user_priorities: Dict[str, float],
    top_n: int = 10
) -> pd.DataFrame:
    df = load_filtered_college_data(file_path)
    df = df[df['STABBR'].isin(states)]

    def in_range(user, school, tol):
        return abs(school - user) <= tol if pd.notna(school) else True

    df_f = df.copy()
    if user_sat:
        df_f = df_f[df_f['SAT_AVG'].apply(lambda x: in_range(user_sat, x, 100))]
    elif user_act and 'ACTCM25' in df_f.columns:
        df_f = df_f[df_f['ACTCM25'].apply(lambda x: in_range(user_act, x, 3))]

    feats = []
    for key, w in user_priorities.items():
        if w > 0:
            feats.extend(updated_feature_map.get(key, []))
    feats = list(set(f for f in feats if f in df_f.columns))

    valid_feats = [f for f in feats if df_f[f].notna().sum() >= 500]
    df_rank = df_f[valid_feats + ['INSTNM', 'CITY', 'STABBR']].dropna()
    if df_rank.empty:
        raise ValueError("No schools match the criteria.")

    # Normalize and reverse cost features
    num_df = df_rank[valid_feats].apply(pd.to_numeric, errors='coerce')
    scaler = MinMaxScaler()
    norm = pd.DataFrame(scaler.fit_transform(num_df), columns=valid_feats)
    for feat in ['TUITIONFEE_IN', 'DEBT_MDN']:
        if feat in norm.columns:
            norm[feat] = 1 - norm[feat]

    # Compute weighted score
    scores = np.zeros(len(norm))
    for key, w in user_priorities.items():
        for feat in updated_feature_map.get(key, []):
            if feat in norm.columns:
                scores += w * norm[feat].values
    df_rank['score'] = scores

    return df_rank.sort_values('score', ascending=False).head(top_n)[['INSTNM', 'CITY', 'STABBR', 'score']]

# Example usage:
if __name__ == "__main__":
    user_input = {
        'states': ['CA', 'WA', 'OR'],
        'user_sat': 1250,
        'user_act': None,
        'user_gpa': 3.6,
        'user_priorities': {
            'academics': 0.9,
            'value': 0.7,
            'professors': 0.3,
            'campus': 0.6,
            'diversity': 0.4,
            'urbanicity': 0.2
        }
    }
    results = recommend_colleges_filtered("data/college_data_filtered.csv", **user_input)
    print(results)
