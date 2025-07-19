import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import Dict, List, Optional

# Load dataset and compute derived features when needed
def load_college_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, low_memory=False)

    # Compute Diversity Score if raw race columns exist and score isn't already present
    race_cols = ['UGDS_WHITE', 'UGDS_BLACK', 'UGDS_HISP', 'UGDS_ASIAN', 'UGDS_UNKN']
    if 'DIVERSITY_SCORE' not in df.columns and all(col in df.columns for col in race_cols):
        for col in race_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        def calc_diversity(row):
            vals = row[race_cols].dropna().astype(float).values
            vals = vals[vals > 0]
            return -np.sum(vals * np.log(vals)) if vals.size > 0 else np.nan
        df['DIVERSITY_SCORE'] = df.apply(calc_diversity, axis=1)

    # Compute Urbanicity Score if not already present and LOCALE exists
    if 'URBANICITY_SCORE' not in df.columns and 'LOCALE' in df.columns:
        def locale_numeric(val):
            try:
                v = int(val)
                if v in (11, 12, 13): return 1.0    # City
                if v in (21, 22, 23): return 0.75   # Suburb
                if v in (31, 32, 33): return 0.5    # Town
                if v in (41, 42, 43): return 0.25   # Rural
            except:
                return np.nan
            return np.nan
        df['URBANICITY_SCORE'] = df['LOCALE'].apply(locale_numeric)

    return df

# Mapping of sliders to dataset features
feature_map = {
    'academics':    ['SAT_AVG', 'RET_FT4', 'C150_4_POOLED', 'ADM_RATE'],
    'value':        ['MD_EARN_WNE_P10', 'TUITIONFEE_IN', 'DEBT_MDN', 'PELL_COMP_ORIG_YR6_RT'],
    'professors':   ['AVGFACSAL'],
    'athletics':    ['PCIP31'],
    'campus':       ['UGDS'],
    'diversity':    ['DIVERSITY_SCORE'],
    'urbanicity':   ['URBANICITY_SCORE']
}

# Reverse cost features so lower is better
def reverse_cost_features(df: pd.DataFrame, cost_features: List[str]) -> pd.DataFrame:
    for feat in cost_features:
        if feat in df.columns:
            df[feat] = 1 - df[feat]
    return df

# Advanced recommendation function
def recommend_colleges_advanced(
    file_path: str,
    states: List[str],
    user_sat: Optional[int],
    user_act: Optional[int],
    user_gpa: Optional[float],
    user_priorities: Dict[str, float],
    top_n: int = 10,
    gpa_column: str = 'GPA'
) -> pd.DataFrame:
    df = load_college_data(file_path)

    # --- Hard filter by state ---
    df = df[df['STABBR'].isin(states)]
    
    # --- Academic qualification filter ---
    def in_range(user, school, tol):
        return abs(school - user) <= tol if pd.notna(school) else True
    df_f = df.copy()
    if user_sat:
        df_f = df_f[df_f['SAT_AVG'].apply(lambda x: in_range(user_sat, x, 100))]
    elif user_act:
        df_f = df_f[df_f['ACTCMMID'].apply(lambda x: in_range(user_act, x, 3))]
    if user_gpa and gpa_column in df_f:
        df_f = df_f[df_f[gpa_column].apply(lambda x: in_range(user_gpa, x, 0.3))]

    # --- Feature selection based on sliders ---
    feats = []
    for key, w in user_priorities.items():
        if w > 0:
            feats.extend(feature_map.get(key, []))
    feats = [f for f in set(feats) if f in df_f.columns]
    
    # Require a minimum number of valid rows per feature
    min_rows = 500
    valid_feats = [f for f in feats if df_f[f].notna().sum() >= min_rows]
    df_rank = df_f[valid_feats + ['INSTNM', 'CITY', 'STABBR']].dropna()
    if df_rank.empty:
        raise ValueError("No schools match criteria.")
    
    # --- Normalize and reverse costs ---
    num_df = df_rank[valid_feats].apply(pd.to_numeric, errors='coerce')
    scaler = MinMaxScaler()
    norm = pd.DataFrame(scaler.fit_transform(num_df), columns=valid_feats)
    norm = reverse_cost_features(norm, ['TUITIONFEE_IN', 'DEBT_MDN'])
    
    # --- Compute weighted score ---
    scores = np.zeros(len(norm))
    for key, w in user_priorities.items():
        for feat in feature_map.get(key, []):
            if feat in norm.columns:
                scores += w * norm[feat].values
    df_rank['score'] = scores
    
    # Return top N
    return df_rank.sort_values('score', ascending=False).head(top_n)[['INSTNM','CITY','STABBR','score']]

# Example usage
if __name__ == "__main__":
    user_input = {
         'states': ['CA','WA','OR'],
         'user_sat': 1250,
         'user_act': None,
         'user_gpa': 3.6,
         'user_priorities': {
             'academics':0.9,
             'value':0.7,
             'professors':0.3,
             'athletics':0.5,
             'campus':0.6,
             'diversity':0.4,
             'urbanicity':0.2
         }
    }
    results = recommend_colleges_advanced("cleaned_college_data.csv", **user_input)
    print(results)
