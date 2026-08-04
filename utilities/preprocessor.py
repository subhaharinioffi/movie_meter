"""
Data Preprocessing Utility for MovieMeter.
Handles cleaning, target creation, feature engineering (including out-of-fold target encoding),
and training/testing preprocessing pipelines.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# Define class thresholds
def get_rating_category(score):
    if score < 6.0:
        return 'Low'
    elif score < 7.5:
        return 'Medium'
    else:
        return 'High'

def clean_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw DataFrame: removes duplicates, drops rows with missing target.
    """
    # Drop duplicates based on title, year, and director
    df_clean = df.drop_duplicates(subset=['movie_title', 'title_year', 'director_name']).copy()
    
    # Drop missing target scores
    df_clean = df_clean.dropna(subset=['imdb_score'])
    
    # Reset index
    df_clean = df_clean.reset_index(drop=True)
    return df_clean

def target_encode_train_test(train_df: pd.DataFrame, test_df: pd.DataFrame, target_col: str = 'imdb_score'):
    """
    Computes smoothed target encoding for director_name and actor_1_name.
    Uses K-Fold on training set to avoid target leakage, and maps the final full training
    averages to the test set.
    """
    train_encoded = train_df.copy()
    test_encoded = test_df.copy()
    
    global_mean = train_df[target_col].mean()
    m = 5  # smoothing parameter (prior weight)
    
    # Mappings to save for inference
    director_stats = {}
    actor_stats = {}
    
    # 1. Director Encoding
    # Initialize with global mean
    train_encoded['director_avg_score'] = global_mean
    
    # Out-of-fold encoding on train set
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    for fold_train_idx, fold_val_idx in kf.split(train_encoded):
        fold_train = train_encoded.iloc[fold_train_idx]
        
        # Calculate stats on fold training
        grp = fold_train.groupby('director_name')[target_col].agg(['mean', 'count'])
        smoothed = (grp['mean'] * grp['count'] + global_mean * m) / (grp['count'] + m)
        
        val_directors = train_encoded.iloc[fold_val_idx]['director_name']
        train_encoded.iloc[fold_val_idx, train_encoded.columns.get_loc('director_avg_score')] = val_directors.map(smoothed).fillna(global_mean)
        
    # Fit final model mapper on entire training set
    grp_full_dir = train_df.groupby('director_name')[target_col].agg(['mean', 'count'])
    smoothed_full_dir = (grp_full_dir['mean'] * grp_full_dir['count'] + global_mean * m) / (grp_full_dir['count'] + m)
    test_encoded['director_avg_score'] = test_encoded['director_name'].map(smoothed_full_dir).fillna(global_mean)
    
    # Store for deployment
    director_stats = smoothed_full_dir.to_dict()
    
    # 2. Lead Actor Encoding
    train_encoded['actor_1_avg_score'] = global_mean
    for fold_train_idx, fold_val_idx in kf.split(train_encoded):
        fold_train = train_encoded.iloc[fold_train_idx]
        
        grp = fold_train.groupby('actor_1_name')[target_col].agg(['mean', 'count'])
        smoothed = (grp['mean'] * grp['count'] + global_mean * m) / (grp['count'] + m)
        
        val_actors = train_encoded.iloc[fold_val_idx]['actor_1_name']
        train_encoded.iloc[fold_val_idx, train_encoded.columns.get_loc('actor_1_avg_score')] = val_actors.map(smoothed).fillna(global_mean)
        
    grp_full_act = train_df.groupby('actor_1_name')[target_col].agg(['mean', 'count'])
    smoothed_full_act = (grp_full_act['mean'] * grp_full_act['count'] + global_mean * m) / (grp_full_act['count'] + m)
    test_encoded['actor_1_avg_score'] = test_encoded['actor_1_name'].map(smoothed_full_act).fillna(global_mean)
    
    # Store for deployment
    actor_stats = smoothed_full_act.to_dict()
    
    # Get mean Facebook likes for known directors/actors as defaults for inference
    director_likes_map = train_df.groupby('director_name')['director_facebook_likes'].first().dropna().to_dict()
    actor_likes_map = train_df.groupby('actor_1_name')['actor_1_facebook_likes'].first().dropna().to_dict()
    
    meta_maps = {
        'global_mean': global_mean,
        'director_avg_score_map': director_stats,
        'actor_1_avg_score_map': actor_stats,
        'director_likes_map': director_likes_map,
        'actor_likes_map': actor_likes_map,
        'median_duration': train_df['duration'].median(),
        'median_director_likes': train_df['director_facebook_likes'].median(),
        'median_actor_likes': train_df['actor_1_facebook_likes'].median(),
        'median_cast_likes': train_df['cast_total_facebook_likes'].median(),
        'median_facenumber': train_df['facenumber_in_poster'].median(),
        'median_year': train_df['title_year'].median(),
    }
    
    return train_encoded, test_encoded, meta_maps

def engineer_features(df: pd.DataFrame, top_genres=None) -> tuple[pd.DataFrame, list]:
    """
    Engineers features like parsing genres, binarizing language/country, and categorizing content rating.
    """
    df = df.copy()
    
    # Genres parsing
    if top_genres is None:
        all_genres = []
        for g in df['genres'].dropna():
            all_genres.extend(g.split('|'))
        top_genres = pd.Series(all_genres).value_counts().index[:10].tolist()
        
    for genre in top_genres:
        df[f'genre_{genre}'] = df['genres'].apply(lambda x: 1 if isinstance(x, str) and genre in x.split('|') else 0)
        
    # Language: English vs. Other
    df['is_english'] = df['language'].apply(lambda x: 1 if x == 'English' else 0)
    
    # Country USA, UK, or Other
    df['country_grouped'] = df['country'].apply(lambda x: x if x in ['USA', 'UK'] else 'Other')
    
    # Content rating
    df['content_rating_grouped'] = df['content_rating'].apply(lambda x: x if x in ['G', 'PG', 'PG-13', 'R'] else 'Other')
    
    return df, top_genres

def get_preprocessor_pipeline(numeric_features, categorical_features, binary_features):
    """
    Returns a ColumnTransformer mapping numeric, categorical, and binary columns to standard steps.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ]), numeric_features),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
            ]), categorical_features),
            ('bin', SimpleImputer(strategy='most_frequent'), binary_features)
        ])
    return preprocessor
