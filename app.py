"""
Streamlit Web Application for MovieMeter.
Provides a professional, modern, and beautiful user interface for predicting
IMDb movie rating categories before release.
"""

import os
import joblib
import numpy as np
import pandas as pd
import streamlit as tf # Using standard imports

# Set page config
import streamlit as st
st.set_page_config(
    page_title="MovieMeter – AI-Powered IMDb Predictor",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark-themed, glassmorphism UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
    
    /* General styles */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
    }
    
    /* Custom main title styling */
    .title-container {
        padding: 1.5rem;
        background: linear-gradient(135deg, #1f1c2c 0%, #928dab 100%);
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .title-main {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        background: linear-gradient(to right, #ff7e5f, #feb47b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    .title-sub {
        font-size: 1.1rem;
        font-weight: 300;
        opacity: 0.9;
    }
    
    /* Card design system */
    .metric-card {
        background: #1e1e24;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #2d2d34;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        margin-bottom: 1rem;
    }
    
    /* Result card styling depending on class */
    .result-card-High {
        background: radial-gradient(circle at top left, #0e2e1e, #131b17);
        border: 2px solid #00c853;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 200, 83, 0.2);
        color: white;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .result-card-Medium {
        background: radial-gradient(circle at top left, #2e280e, #1b1913);
        border: 2px solid #ffab00;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(255, 171, 0, 0.2);
        color: white;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .result-card-Low {
        background: radial-gradient(circle at top left, #2e0e0e, #1b1313);
        border: 2px solid #d50000;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(213, 0, 0, 0.2);
        color: white;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .result-badge {
        font-size: 2.2rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0.5rem 0;
    }
    
    .result-badge-High {
        color: #00c853;
        text-shadow: 0 0 10px rgba(0, 200, 83, 0.5);
    }
    
    .result-badge-Medium {
        color: #ffab00;
        text-shadow: 0 0 10px rgba(255, 171, 0, 0.5);
    }
    
    .result-badge-Low {
        color: #d50000;
        text-shadow: 0 0 10px rgba(213, 0, 0, 0.5);
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #888899;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load model and preprocessors
@st.cache_resource
def load_ml_assets():
    """
    Loads fitted ML artifacts: maps, preprocessor, model, label encoder.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    maps_path = os.path.join(base_dir, "models", "director_actor_maps.joblib")
    prep_path = os.path.join(base_dir, "models", "preprocessor.joblib")
    model_path = os.path.join(base_dir, "models", "movie_meter_model.joblib")
    le_path = os.path.join(base_dir, "models", "label_encoder.joblib")
    
    # Check existence
    if not (os.path.exists(maps_path) and os.path.exists(prep_path) and os.path.exists(model_path) and os.path.exists(le_path)):
        return None
        
    meta_maps = joblib.load(maps_path)
    preprocessor = joblib.load(prep_path)
    model = joblib.load(model_path)
    label_encoder = joblib.load(le_path)
    
    return meta_maps, preprocessor, model, label_encoder

assets = load_ml_assets()

if assets is None:
    st.error("⚠️ Machine Learning model assets not found! Please run the training pipeline first: `python utilities/model_trainer.py`.")
    st.stop()

meta_maps, preprocessor, model, label_encoder = assets

# Sidebar layout
with st.sidebar:
    st.image("https://img.icons8.com/color/144/movie-projector.png", width=100)
    st.markdown("### MovieMeter Dashboard")
    st.markdown("""
    **MovieMeter** uses advanced machine learning to estimate a film's quality category before it is released. 
    By analyzing pre-production metadata (director, cast, duration, country, language, genre mix), the engine classifies the projected audience rating.
    """)
    st.markdown("---")
    st.markdown("#### Classification Thresholds:")
    st.markdown("- **🔴 Low:** IMDb Rating < 6.0")
    st.markdown("- **🟡 Medium:** 6.0 ≤ IMDb Rating < 7.5")
    st.markdown("- **🟢 High:** IMDb Rating ≥ 7.5")
    st.markdown("---")
    st.markdown("#### Evaluation Performance (XGBoost):")
    st.markdown("- **Accuracy:** 62.1%")
    st.markdown("- **Weighted F1:** 0.60")
    st.markdown("- **ROC-AUC (Weighted):** 0.73")
    st.info("💡 Excludes post-release fields like sales, review counts, or votes to prevent data leakage.")

# Header
st.markdown("""
<div class="title-container">
    <div class="title-main">MovieMeter</div>
    <div class="title-sub">AI-Powered IMDb Rating Category Predictor</div>
</div>
""", unsafe_allow_html=True)

# Main Form Split Layout
col_input, col_info = st.columns([2, 1.2])

with col_input:
    st.markdown("### 🎬 Enter Movie Details")
    
    # Text input
    title = st.text_input("Movie Title", "The Grand Budapest Hotel")
    
    # Sub-columns for text search fields
    col_dir, col_act = st.columns(2)
    with col_dir:
        director = st.text_input("Director Name", "Wes Anderson")
    with col_act:
        actor = st.text_input("Lead Actor Name (Actor 1)", "Ralph Fiennes")
        
    # Numerical features
    col_year, col_dur, col_faces = st.columns(3)
    with col_year:
        release_year = st.number_input("Release Year", min_value=1900, max_value=2030, value=2014)
    with col_dur:
        duration = st.number_input("Runtime (Minutes)", min_value=10, max_value=360, value=99)
    with col_faces:
        faces = st.slider("Faces on Poster", min_value=0, max_value=20, value=2)
        
    # Categoricals
    col_lang, col_country, col_content = st.columns(3)
    with col_lang:
        language = st.selectbox("Language", ["English", "Other"])
    with col_country:
        country = st.selectbox("Country", ["USA", "UK", "Other"])
    with col_content:
        content_rating = st.selectbox("Content Rating", ["G", "PG", "PG-13", "R", "Other"])
        
    # Genres selection
    st.markdown("**Select Movie Genres (Select all that apply)**")
    selected_genres = st.multiselect(
        "Genres",
        meta_maps['top_genres'],
        default=["Comedy", "Drama"]
    )

# Information display / Guide in right column
with col_info:
    st.markdown("### 🔍 Model Insights")
    st.markdown("How is the prediction calculated?")
    st.markdown("""
    1. **Reputation Lookup:** The system cross-references the Director and Lead Actor with our database to resolve their average historical IMDb score.
    2. **Facebook Popularity:** Historical Facebook popularity for the Director and Cast is automatically pre-filled.
    3. **Genre & Content Analysis:** Target parameters are scaled, categorized, and fed into our optimized gradient booster.
    """)
    
    # Dynamically show looked-up metrics based on user inputs
    st.markdown("#### Live Lookup Profile:")
    
    # Director Lookup
    cleaned_dir = director.strip()
    if cleaned_dir in meta_maps['director_avg_score_map']:
        dir_score = meta_maps['director_avg_score_map'][cleaned_dir]
        dir_likes = meta_maps['director_likes_map'].get(cleaned_dir, meta_maps['median_director_likes'])
        dir_status = f"🟢 **Known** (Avg Score: {dir_score:.2f}, Likes: {int(dir_likes):,})"
    else:
        dir_score = meta_maps['global_mean']
        dir_likes = meta_maps['median_director_likes']
        dir_status = f"⚪ **New Director** (Uses baseline fallback: {dir_score:.2f})"
        
    # Actor Lookup
    cleaned_act = actor.strip()
    if cleaned_act in meta_maps['actor_1_avg_score_map']:
        act_score = meta_maps['actor_1_avg_score_map'][cleaned_act]
        act_likes = meta_maps['actor_likes_map'].get(cleaned_act, meta_maps['median_actor_likes'])
        act_status = f"🟢 **Known** (Avg Score: {act_score:.2f}, Likes: {int(act_likes):,})"
    else:
        act_score = meta_maps['global_mean']
        act_likes = meta_maps['median_actor_likes']
        act_status = f"⚪ **New Lead Actor** (Uses baseline fallback: {act_score:.2f})"
        
    # Estimated Cast Total Likes
    cast_likes = act_likes + dir_likes + 2000
    
    st.markdown(f"**Director status:** {dir_status}")
    st.markdown(f"**Lead Actor status:** {act_status}")
    st.markdown(f"**Estimated Cast Likes:** {int(cast_likes):,}")

# Button trigger
st.markdown("<br>", unsafe_allow_html=True)
predict_clicked = st.button("🚀 PREDICT IMDB RATING CATEGORY", use_container_width=True)

if predict_clicked:
    # Build feature record
    record = {
        'duration': duration,
        'title_year': release_year,
        'director_facebook_likes': dir_likes,
        'cast_total_facebook_likes': cast_likes,
        'facenumber_in_poster': faces,
        'is_english': 1 if language == "English" else 0,
        'country_grouped': country,
        'content_rating_grouped': content_rating,
        'director_avg_score': dir_score,
        'actor_1_avg_score': act_score
    }
    
    # Top genres flags
    for g in meta_maps['top_genres']:
        record[f'genre_{g}'] = 1 if g in selected_genres else 0
        
    df_input = pd.DataFrame([record])
    
    # Apply transformation
    try:
        X_trans = preprocessor.transform(df_input)
        
        # Predict class & probability
        pred_idx = model.predict(X_trans)[0]
        prob = model.predict_proba(X_trans)[0]
        
        # Inverse transform class label
        pred_label = label_encoder.inverse_transform([pred_idx])[0]
        confidence = prob[pred_idx] * 100
        
        # Map label index
        low_prob = prob[label_encoder.transform(['Low'])[0]] * 100
        med_prob = prob[label_encoder.transform(['Medium'])[0]] * 100
        high_prob = prob[label_encoder.transform(['High'])[0]] * 100
        
        st.markdown("---")
        st.markdown("### 📊 Prediction Result")
        
        # Split results panel
        col_res_card, col_prob_breakdown = st.columns([1, 1])
        
        with col_res_card:
            st.markdown(f"""
            <div class="result-card-{pred_label}">
                <div class="stat-label">Predicted Rating Category</div>
                <div class="result-badge result-badge-{pred_label}">{pred_label}</div>
                <div style="font-size: 1.1rem; font-weight: 600; margin-top: 1rem;">
                    Confidence Score: {confidence:.1f}%
                </div>
                <div style="font-size: 0.9rem; opacity: 0.8; margin-top: 0.5rem;">
                    Movie: <strong>{title}</strong> by {director}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_prob_breakdown:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown("#### Probability Breakdown:")
            
            st.markdown(f"**High (≥ 7.5):** {high_prob:.1f}%")
            st.progress(high_prob / 100)
            
            st.markdown(f"**Medium (6.0 - 7.4):** {med_prob:.1f}%")
            st.progress(med_prob / 100)
            
            st.markdown(f"**Low (< 6.0):** {low_prob:.1f}%")
            st.progress(low_prob / 100)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Advice
            st.markdown("#### 💡 OTT Content Strategic Suggestion:")
            if pred_label == 'High':
                st.success("🏆 **Acclaimed Movie Tier:** Strong candidate for major marketing campaigns, homepage banners, and prestige distribution. High recommendation priority.")
            elif pred_label == 'Medium':
                st.warning("📈 **Reliable Mass Appeal Tier:** Solid watch with decent viewership potential. Best suited for targeted genre recommendation categories and standard marketing budgets.")
            else:
                st.error("📉 **Niche / Low Appeal Tier:** Consider acquiring with caution or placing under generic catalog search. Suggest optimizing marketing spend or revising trailers.")
                
    except Exception as e:
        st.error(f"Prediction failed with error: {e}")
        st.info("Please verify that you entered valid numerical inputs and fields.")
