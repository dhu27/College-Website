from typing import List, Optional, Dict
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from app.models import College
from app.db import db


def recommend_colleges_filtered(
    file_path: str,  # kept for signature compatibility; unused when pulling from DB
    states: Optional[List[str]] = None,
    user_sat: Optional[int] = None,
    user_act: Optional[int] = None,
    user_gpa: Optional[float] = None,
    user_priorities: Optional[Dict[str, float]] = None,
    user_cost: Optional[int] = None,
    top_n: int = 10,
    prefer_selectivity: bool = True,  # if True, lower admission_rate => higher score
) -> pd.DataFrame:
    """
    College recommender with key improvements:
      - Robust NA handling with low-coverage feature drop (keeps SAT/ACT/GPA columns for fit scoring).
      - Outlier winsorization before MinMax scaling.
      - Per-priority bucket averaging so each priority weight contributes equally regardless of column count.
      - Explicit direction handling: cost metrics are inverted; admissions rate inversion is controlled by `prefer_selectivity`.
      - Academic fit score (SAT/ACT/GPA bands) is added as its own bucket when user scores are provided.
      - Row-wise, NaN-safe weighted average across buckets (missing buckets don't poison the overall score).

    Returns the top-N schools with overall score and per-bucket subscores for explainability.
    """

    # ---- Column mappings (prefer your DB's lowercase schema)
    cost_col = 'cost_of_attendance'
    feature_map = {
        'academics': ['retention_rate_ft', 'graduation_rate_150'],
        'admissions': ['admission_rate'],
        'cost': [cost_col, 'median_debt'],
        'faculty': ['avg_faculty_salary'],
        'diversity': ['diversity_score'],
        'location': ['urbanicity_score'],
        'prestige': ['admission_rate'],  # Lower admission rate = higher prestige
    }

    # SAT/ACT/GPA columns we want to keep for fit scoring (do not drop for coverage)
    sat_act_gpa_cols = [
        'sat_avg',
        'sat_verbal_25', 'sat_verbal_75',
        'sat_math_25', 'sat_math_75',
        'act_composite_25', 'act_composite_75',
        'act_math_25', 'act_math_75',
        'gpa25', 'gpa75',
        # add more if your DB has different spellings
        # legacy/uppercase variants (handled in logic below too):
        'ACTCM25', 'ACTCM75', 'ACTCMMID', 'GPA25', 'GPA75'
    ]

    # Columns where lower is better (we might add 'admission_rate' below)
    invert_after_norm = {cost_col, 'median_debt'}
    if prefer_selectivity:
        invert_after_norm.add('admission_rate')

    # ---- Load data from DB
    query = College.query
    if states:
        query = query.filter(College.state.in_(states))
    if user_cost is not None:
        query = query.filter(getattr(College, cost_col) <= user_cost)

    colleges = query.all()
    if not colleges:
        raise ValueError("No schools match the selected filters. Try broadening your search.")

    df = pd.DataFrame([c.__dict__ for c in colleges])
    if '_sa_instance_state' in df.columns:
        df = df.drop(columns=['_sa_instance_state'])

    # ---- Collect features from priorities that actually exist in the data
    feats = []
    if user_priorities:
        for k, w in user_priorities.items():
            if k in ('value', 'campus'):
                continue
            if w and w > 0:
                feats.extend(feature_map.get(k, []))
    feats = sorted(set(f for f in feats if f in df.columns))

    # ---- Fallback defaults (lowercase DB names)
    if not feats:
        default_feats = [
            'retention_rate_ft', 'graduation_rate_150', 'admission_rate',
            cost_col, 'median_debt', 'avg_faculty_salary',
            'diversity_score', 'urbanicity_score'
        ]
        feats = [f for f in default_feats if f in df.columns]

    if not feats:
        raise ValueError("No usable features found in the dataset. Check your columns/dataset.")

    # ---- Build ranking frame with meta + selected features + SAT/ACT/GPA (protected from removal)
    meta_cols = [c for c in ['name', 'city', 'state', 'unitid'] if c in df.columns]
    sat_act_present = [c for c in sat_act_gpa_cols if c in df.columns]
    df_rank = df[meta_cols + feats + sat_act_present].copy()

    # ---- Numeric conversion for scoring feats
    num_df = df_rank[feats].apply(pd.to_numeric, errors='coerce')

    # ---- Drop low-coverage features (<60% non-null), but keep at least something
    coverage = num_df.notna().mean()
    keep_feats = [f for f in feats if coverage.get(f, 0) >= 0.60]
    if not keep_feats:
        keep_feats = feats  # fallback: keep and impute

    num_df = num_df[keep_feats]

    # ---- Outlier winsorization (1st–99th percentile) before imputation & scaling
    def winsorize_series(s: pd.Series, lo: float = 0.01, hi: float = 0.99) -> pd.Series:
        s_no_na = s.dropna()
        if s_no_na.empty:
            return s
        ql, qu = s_no_na.quantile(lo), s_no_na.quantile(hi)
        return s.clip(lower=ql, upper=qu)

    for col in num_df.columns:
        num_df[col] = winsorize_series(num_df[col])

    # ---- Median imputation
    num_df = num_df.apply(pd.to_numeric, errors='coerce')
    num_df = num_df.fillna(num_df.median(numeric_only=True))

    # Drop any columns still entirely NaN (extremely sparse)
    non_empty_cols = [c for c in num_df.columns if num_df[c].notna().any()]
    num_df = num_df[non_empty_cols]
    if num_df.empty:
        raise ValueError('No usable numeric features after NA handling. Consider loosening coverage threshold or priorities.')

    # ---- Normalize 0–1
    scaler = MinMaxScaler()
    norm = pd.DataFrame(
        scaler.fit_transform(num_df),
        columns=num_df.columns,
        index=df_rank.index
    )

    # ---- Flip directional features so "lower is better" becomes higher score
    for feat in norm.columns:
        if feat in invert_after_norm:
            norm[feat] = 1 - norm[feat]

    # ---- Build per-priority bucket means (each bucket contributes equally)
    bucket_scores: Dict[str, pd.Series] = {}
    for k, cols in feature_map.items():
        if k in ('value', 'campus'):
            continue
        cols = [c for c in cols if c in norm.columns]
        if cols:
            bucket_scores[k] = norm[cols].mean(axis=1)

    # ---- Academic fit score (SAT/ACT/GPA), independent of normalization
    def band_fit_series(user_val: float, lo: pd.Series, hi: pd.Series) -> pd.Series:
        out = pd.Series(np.nan, index=lo.index, dtype=float)
        width = (hi - lo).where((~lo.isna()) & (~hi.isna()) & ((hi - lo) > 0), np.nan)
        inside = (user_val >= lo) & (user_val <= hi)
        out[inside] = 1.0
        below = (user_val < lo) & (~lo.isna()) & (~width.isna())
        out[below] = np.clip(1 - (lo[below] - user_val) / (width[below].abs() + 1e-6), 0, 1)
        above = (user_val > hi) & (~hi.isna()) & (~width.isna())
        out[above] = np.clip(1 - (user_val - hi[above]) / (width[above].abs() + 1e-6), 0, 1)
        return out

    fit_components = []

    # SAT fit: prefer band if both 25/75 present; else approximate from sat_avg ± 100
    if user_sat is not None:
        # lowercase band variant
        if {'sat_verbal_25', 'sat_verbal_75', 'sat_math_25', 'sat_math_75'}.issubset(df_rank.columns):
            sat_lo = pd.to_numeric(df_rank['sat_verbal_25'], errors='coerce') + pd.to_numeric(df_rank['sat_math_25'], errors='coerce')
            sat_hi = pd.to_numeric(df_rank['sat_verbal_75'], errors='coerce') + pd.to_numeric(df_rank['sat_math_75'], errors='coerce')
            fit_components.append(band_fit_series(user_sat, sat_lo, sat_hi))
        elif 'sat_avg' in df_rank.columns:
            sat_avg = pd.to_numeric(df_rank['sat_avg'], errors='coerce')
            fit_components.append(band_fit_series(user_sat, sat_avg - 100, sat_avg + 100))

    # ACT fit: support lowercase and uppercase variants
    if user_act is not None:
        if {'act_composite_25', 'act_composite_75'}.issubset(df_rank.columns):
            act_lo = pd.to_numeric(df_rank['act_composite_25'], errors='coerce')
            act_hi = pd.to_numeric(df_rank['act_composite_75'], errors='coerce')
            fit_components.append(band_fit_series(user_act, act_lo, act_hi))
        elif {'ACTCM25', 'ACTCM75'}.issubset(df_rank.columns):
            act_lo = pd.to_numeric(df_rank['ACTCM25'], errors='coerce')
            act_hi = pd.to_numeric(df_rank['ACTCM75'], errors='coerce')
            fit_components.append(band_fit_series(user_act, act_lo, act_hi))
        elif 'ACTCMMID' in df_rank.columns:
            act_mid = pd.to_numeric(df_rank['ACTCMMID'], errors='coerce')
            fit_components.append(band_fit_series(user_act, act_mid - 2, act_mid + 2))

    # GPA fit: support lowercase and uppercase variants
    if user_gpa is not None:
        if {'gpa25', 'gpa75'}.issubset(df_rank.columns):
            gpa_lo = pd.to_numeric(df_rank['gpa25'], errors='coerce')
            gpa_hi = pd.to_numeric(df_rank['gpa75'], errors='coerce')
            fit_components.append(band_fit_series(user_gpa, gpa_lo, gpa_hi))
        elif {'GPA25', 'GPA75'}.issubset(df_rank.columns):
            gpa_lo = pd.to_numeric(df_rank['GPA25'], errors='coerce')
            gpa_hi = pd.to_numeric(df_rank['GPA75'], errors='coerce')
            fit_components.append(band_fit_series(user_gpa, gpa_lo, gpa_hi))

    if fit_components:
        fit_score = pd.concat(fit_components, axis=1).mean(axis=1, skipna=True)
        if fit_score.notna().any():
            bucket_scores['fit'] = fit_score

    # ---- Compute weighted score across buckets (NaN-safe, row-wise)
    score_df = pd.DataFrame({k: bucket_scores[k] for k in bucket_scores.keys()})
    if user_priorities:
        weights = {
            k: float(v)
            for k, v in user_priorities.items()
            if k not in ('value', 'campus') and v and v > 0 and k in score_df.columns
        }
        # If we computed 'fit' but no explicit weight, align it to 'admissions' weight or default 1.0
        if 'fit' in score_df.columns and 'fit' not in weights:
            weights['fit'] = float(user_priorities.get('admissions', 1.0))
        if not weights:
            weights = {k: 1.0 for k in score_df.columns}
    else:
        weights = {k: 1.0 for k in score_df.columns}

    w_series = pd.Series(weights).reindex(score_df.columns).fillna(0.0)
    valid_mask = score_df.notna()
    row_den = (valid_mask * w_series).sum(axis=1)
    row_num = (score_df.fillna(0.0) * w_series).sum(axis=1)
    overall = row_num / row_den.replace(0, np.nan)  # NaN if no valid buckets for a row

    # ---- Assemble result with meta + subscores
    out = pd.DataFrame(index=df_rank.index)
    for m in meta_cols:
        out[m] = df_rank[m]

    # Aliases for compatibility
    if 'name' in out.columns:
        out['INSTNM'] = out['name']
    if 'city' in out.columns:
        out['CITY'] = out['city']
    if 'state' in out.columns:
        out['STABBR'] = out['state']
    if 'unitid' in out.columns:
        out['UNITID'] = out['unitid']

    # Include DB primary key if present
    if 'id' in df.columns:
        out['id'] = df['id']

    # Subscores
    for k in sorted(score_df.columns):
        out[f"score_{k}"] = score_df[k]
    out['score'] = overall

    # ---- Sort and return top N
    out = out.sort_values('score', ascending=False).head(top_n)
    if out.empty:
        raise ValueError("No schools match the criteria after ranking. Try broadening filters.")

    return out  # final ranked DataFrame
