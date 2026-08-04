"""
Streamlit Web Application for MovieMeter.
Transforms the movie rating category predictor into a premium AI-powered Movie Success Analytics Dashboard.
Features:
- Premium dark Netflix/IMDb theme (no sidebar).
- Circular Plotly gauges for Success Probability, Market Potential, and Production Readiness.
- Box Office / OTT Revenue & ROI Estimator.
- Genre Popularity & Runtime Distribution charts driven by the training dataset.
- Target Audience & OTT Platform recommendation models.
- Fixed the float32 type casting error in progress values.
"""

import os
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="MovieMeter – AI Movie Intelligence Dashboard",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for dark-themed, premium UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&family=Space+Grotesk:wght@400;500;700&display=swap');
    
    /* General body override for dark theme */
    html, body, [class*="st-"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #0c0c0e;
        color: #e4e4e7;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        color: #ffffff;
    }

    /* Container for header card */
    .header-card {
        background: linear-gradient(135deg, #1e0b0b 0%, #0e0e12 100%);
        border: 1px solid #d50000;
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(213, 0, 0, 0.15);
        margin-bottom: 2rem;
    }
    
    .header-title {
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0.2rem;
        background: linear-gradient(to right, #ff2a2a, #ff7b7b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
    }
    
    .header-sub {
        font-size: 1.2rem;
        font-weight: 400;
        color: #a1a1aa;
    }
    
    /* Clean glass card design */
    .glass-card {
        background: #121216;
        border: 1px solid #27272a;
        border-radius: 16px;
        padding: 1.8rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: #3f3f46;
    }

    /* Custom visual results banners */
    .banner-High {
        background: linear-gradient(135deg, #062f1a 0%, #09130f 100%);
        border: 2px dashed #00e676;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 4px 25px rgba(0, 230, 118, 0.15);
    }
    
    .banner-Medium {
        background: linear-gradient(135deg, #2f2506 0%, #131109 100%);
        border: 2px dashed #ffab00;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 4px 25px rgba(255, 171, 0, 0.15);
    }
    
    .banner-Low {
        background: linear-gradient(135deg, #2f0606 0%, #130909 100%);
        border: 2px dashed #d50000;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 4px 25px rgba(213, 0, 0, 0.15);
    }

    .banner-class-title {
        font-size: 2.5rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0.5rem 0;
    }
    .text-High { color: #00e676; text-shadow: 0 0 12px rgba(0,230,118,0.4); }
    .text-Medium { color: #ffab00; text-shadow: 0 0 12px rgba(255,171,0,0.4); }
    .text-Low { color: #ff1744; text-shadow: 0 0 12px rgba(255,23,68,0.4); }
    
    .metric-value-large {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    .metric-label-small {
        font-size: 0.85rem;
        color: #a1a1aa;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Recommendations styling */
    .rec-item {
        background: #181820;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff2a2a;
        margin-bottom: 0.8rem;
    }
    
    /* Styled labels */
    .parameter-pill {
        background-color: #27272a;
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
        margin-right: 5px;
        margin-bottom: 5px;
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
    data_path = os.path.join(base_dir, "data", "raw", "movie_metadata.csv")
    
    if not (os.path.exists(maps_path) and os.path.exists(prep_path) and os.path.exists(model_path) and os.path.exists(le_path)):
        return None
        
    meta_maps = joblib.load(maps_path)
    preprocessor = joblib.load(prep_path)
    model = joblib.load(model_path)
    label_encoder = joblib.load(le_path)
    
    # Load dataset if available for chart generation
    df_raw = None
    if os.path.exists(data_path):
        df_raw = pd.read_csv(data_path)
        
    return meta_maps, preprocessor, model, label_encoder, df_raw

assets = load_ml_assets()

if assets is None:
    st.error("⚠️ Machine Learning model assets not found! Please run the training pipeline first: `python utilities/model_trainer.py`.")
    st.stop()

meta_maps, preprocessor, model, label_encoder, df_raw = assets

# Header
st.markdown("""
<div class="header-card">
    <div class="header-title">MovieMeter Success Analytics</div>
    <div class="header-sub">Executive AI Intelligence Platform for Production Houses & OTT Distributors</div>
</div>
""", unsafe_allow_html=True)

# Main Grid for Forms & Inputs
st.markdown("### 🎬 Production Design Parameters")
st.write("Provide details of the movie project to predict rating category, revenue, ROI, and target audiences.")

# Movie entry Form
with st.form("movie_input_form"):
    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        title = st.text_input("Movie Title / Script Project Name", "The Grand Budapest Hotel")
        genres = st.multiselect(
            "Target Genres",
            meta_maps['top_genres'],
            default=["Comedy", "Drama"]
        )
    with col_b:
        director = st.text_input("Director Name", "Wes Anderson")
        release_year = st.number_input("Target Release Year", min_value=1900, max_value=2030, value=2014)
    with col_c:
        actor = st.text_input("Lead Actor (Actor 1)", "Ralph Fiennes")
        duration = st.number_input("Target Runtime (Minutes)", min_value=10, max_value=360, value=99)
        
    col_d, col_e, col_f, col_g = st.columns(4)
    with col_d:
        language = st.selectbox("Original Language", ["English", "Other"])
    with col_e:
        country = st.selectbox("Production Country", ["USA", "UK", "Other"])
    with col_f:
        content_rating = st.selectbox("Target Content Rating", ["G", "PG", "PG-13", "R", "Other"])
    with col_g:
        faces = st.slider("Number of Faces on Poster", min_value=0, max_value=20, value=2)
        
    submit_button = st.form_submit_button("🚀 GENERATE COMPLETE MOVIE SUCCESS ANALYTICS", use_container_width=True)

# Run Prediction Logic upon submission
if submit_button:
    # 1. Lookup reputation stats
    cleaned_dir = director.strip()
    if cleaned_dir in meta_maps['director_avg_score_map']:
        dir_score = meta_maps['director_avg_score_map'][cleaned_dir]
        dir_likes = meta_maps['director_likes_map'].get(cleaned_dir, meta_maps['median_director_likes'])
        is_dir_known = True
    else:
        dir_score = meta_maps['global_mean']
        dir_likes = meta_maps['median_director_likes']
        is_dir_known = False
        
    cleaned_act = actor.strip()
    if cleaned_act in meta_maps['actor_1_avg_score_map']:
        act_score = meta_maps['actor_1_avg_score_map'][cleaned_act]
        act_likes = meta_maps['actor_likes_map'].get(cleaned_act, meta_maps['median_actor_likes'])
        is_act_known = True
    else:
        act_score = meta_maps['global_mean']
        act_likes = meta_maps['median_actor_likes']
        is_act_known = False
        
    # Cast likes calculation
    cast_likes = act_likes + dir_likes + 2000
    
    # 2. Build feature dictionary
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
    
    # Fill top genres binary columns
    for g in meta_maps['top_genres']:
        record[f'genre_{g}'] = 1 if g in genres else 0
        
    df_input = pd.DataFrame([record])
    
    try:
        # Preprocessing transformation
        X_trans = preprocessor.transform(df_input)
        
        # Predictions
        pred_idx = model.predict(X_trans)[0]
        prob = model.predict_proba(X_trans)[0]
        
        # Class names mapping
        pred_label = label_encoder.inverse_transform([pred_idx])[0]
        confidence = prob[pred_idx] * 100
        
        low_prob = prob[label_encoder.transform(['Low'])[0]] * 100
        med_prob = prob[label_encoder.transform(['Medium'])[0]] * 100
        high_prob = prob[label_encoder.transform(['High'])[0]] * 100
        
        # Calculate Success Probability: 1 - Low Category Probability
        success_prob = float(high_prob + med_prob)
        
        # Calculate Market Potential Score (Formula based on star-likes, language, and genre coefficients)
        genre_bonus = sum([15 for g in genres if g in ['Action', 'Adventure', 'Sci-Fi', 'Thriller']])
        genre_bonus = min(30, genre_bonus)
        star_power = np.log1p(cast_likes) / 12 * 40 # Up to 40 points
        loc_bonus = 20 if (country == 'USA' or language == 'English') else 10
        market_potential = min(100, int(30 + star_power + loc_bonus + genre_bonus))
        
        # Calculate Production Readiness Score (Based on standard lengths, content rating, and face counts)
        dur_score = 30 if (90 <= duration <= 120) else 15
        rating_score = 30 if content_rating in ['PG-13', 'R'] else 20
        details_score = 40
        prod_readiness = int(dur_score + rating_score + details_score)
        
        # Dynamic Revenue & ROI estimation
        star_mult = 1.0 + (cast_likes / 100000.0)
        star_mult = min(3.0, star_mult)
        if pred_label == 'High':
            rev_min = 150 * star_mult
            rev_max = 500 * star_mult
            roi_min, roi_max = 180, 500
        elif pred_label == 'Medium':
            rev_min = 40 * star_mult
            rev_max = 150 * star_mult
            roi_min, roi_max = 40, 180
        else:
            rev_min = 5 * star_mult
            rev_max = 40 * star_mult
            roi_min, roi_max = -60, 30
            
        st.markdown("---")
        st.markdown(f"## 📊 Executive Analysis Report: *{title}*")
        
        # Dashboard Row 1: Banner & Circular Guages
        col_banner, col_gauge = st.columns([1.5, 2.5])
        
        with col_banner:
            st.markdown(f"""
            <div class="banner-{pred_label}">
                <div class="metric-label-small">AI Prediction Result</div>
                <div class="banner-class-title text-{pred_label}">{pred_label}</div>
                <div class="metric-label-small">IMDb Quality Tier</div>
                <hr style="border-top: 1px solid rgba(255,255,255,0.1); margin: 1rem 0;">
                <div style="font-size: 1rem;">Confidence Score: <strong>{confidence:.1f}%</strong></div>
                <div style="font-size: 0.9rem; color: #a1a1aa; margin-top: 0.5rem;">
                    Target Class probability under XGBoost Classifier
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Simple indicator values
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="glass-card">
                <div class="metric-label-small">Director Profile ({director})</div>
                <div style="font-size: 1.1rem; font-weight:700; margin-top:0.3rem;">
                    {'Known Director' if is_dir_known else 'New/Independent'}
                </div>
                <div style="font-size:0.85rem; color:#888;">Avg Rating: {dir_score:.2f} | Likes: {int(dir_likes):,}</div>
            </div>
            <div class="glass-card">
                <div class="metric-label-small">Lead Actor Profile ({actor})</div>
                <div style="font-size: 1.1rem; font-weight:700; margin-top:0.3rem;">
                    {'Known Star' if is_act_known else 'New Actor'}
                </div>
                <div style="font-size:0.85rem; color:#888;">Avg Rating: {act_score:.2f} | Likes: {int(act_likes):,}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_gauge:
            # 3 Gauge indicators side-by-side using Plotly
            fig_gauges = go.Figure()
            
            # 1. Success Gauge
            fig_gauges.add_trace(go.Indicator(
                mode = "gauge+number",
                value = success_prob,
                title = {'text': "Success Probability", 'font': {'size': 16, 'family': 'Space Grotesk'}},
                domain = {'x': [0, 0.3], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#27272a"},
                    'bar': {'color': "#00e676" if success_prob >= 70 else "#ffab00" if success_prob >= 40 else "#ff1744"},
                    'bgcolor': "#181820",
                    'borderwidth': 2,
                    'bordercolor': "#27272a",
                    'steps': [
                        {'range': [0, 40], 'color': 'rgba(255, 23, 68, 0.1)'},
                        {'range': [40, 70], 'color': 'rgba(255, 171, 0, 0.1)'},
                        {'range': [70, 100], 'color': 'rgba(0, 230, 118, 0.1)'}
                    ]
                }
            ))
            
            # 2. Market Potential
            fig_gauges.add_trace(go.Indicator(
                mode = "gauge+number",
                value = market_potential,
                title = {'text': "Market Potential Score", 'font': {'size': 16, 'family': 'Space Grotesk'}},
                domain = {'x': [0.35, 0.65], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#27272a"},
                    'bar': {'color': "#ffab00"},
                    'bgcolor': "#181820",
                    'borderwidth': 2,
                    'bordercolor': "#27272a",
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(255,255,255,0.05)'},
                        {'range': [50, 100], 'color': 'rgba(255, 171, 0, 0.05)'}
                    ]
                }
            ))
            
            # 3. Production Readiness
            fig_gauges.add_trace(go.Indicator(
                mode = "gauge+number",
                value = prod_readiness,
                title = {'text': "Production Readiness", 'font': {'size': 16, 'family': 'Space Grotesk'}},
                domain = {'x': [0.7, 1.0], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#27272a"},
                    'bar': {'color': "#66b3ff"},
                    'bgcolor': "#181820",
                    'borderwidth': 2,
                    'bordercolor': "#27272a",
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(255,255,255,0.05)'},
                        {'range': [50, 100], 'color': 'rgba(102, 179, 255, 0.05)'}
                    ]
                }
            ))
            
            fig_gauges.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': "#ffffff"},
                height=320,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            
            st.plotly_chart(fig_gauges, use_container_width=True)
            
            # Category Probabilities breakdown in cards
            col_l, col_m, col_h = st.columns(3)
            with col_l:
                st.markdown(f"""
                <div class="glass-card" style="text-align: center; border-left: 4px solid #ff1744;">
                    <div class="metric-label-small">Low Probability</div>
                    <div style="font-size:1.8rem; font-weight:700; color:#ff1744;">{low_prob:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with col_m:
                st.markdown(f"""
                <div class="glass-card" style="text-align: center; border-left: 4px solid #ffab00;">
                    <div class="metric-label-small">Medium Probability</div>
                    <div style="font-size:1.8rem; font-weight:700; color:#ffab00;">{med_prob:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with col_h:
                st.markdown(f"""
                <div class="glass-card" style="text-align: center; border-left: 4px solid #00e676;">
                    <div class="metric-label-small">High Probability</div>
                    <div style="font-size:1.8rem; font-weight:700; color:#00e676;">{high_prob:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

        # Dashboard Row 2: Revenue Estimation & Recommendations
        col_rev, col_rec = st.columns(2)
        
        with col_rev:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### 💰 Financial & ROI Projection")
            st.write("Estimated Box Office / OTT revenue projection ranges calculated dynamically based on audience reception tier and director star-power coefficient.")
            
            st.markdown(f"""
            <div style="margin: 1.5rem 0;">
                <div class="metric-label-small">Projected Global Gross Range</div>
                <div class="metric-value-large" style="color: #ffab00;">${rev_min:.1f}M – ${rev_max:.1f}M</div>
            </div>
            <div style="margin: 1.5rem 0;">
                <div class="metric-label-small">Estimated ROI Range</div>
                <div class="metric-value-large" style="color: #00e676;">{roi_min}% – {roi_max}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Draw ROI bar indicators
            st.write("**ROI Status indicator:**")
            if roi_min < 0:
                st.error("📉 High Risk of Loss - Revise production budgets or cast combinations.")
            elif roi_min < 100:
                st.warning("📈 Moderate Returns expected - Ideal for catalog licensing.")
            else:
                st.success("💎 Premium Yield asset - Greenlight candidate.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_rec:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### 🎯 Distribution & Audience Analytics")
            st.write("Dynamic recommendation engine results matching features to target distribution vectors.")
            
            # OTT Recommendation logic
            ott_platforms = []
            if pred_label == 'High':
                ott_platforms = ["Netflix (Original Acquisition Premium)", "Apple TV+ (Prestige Cinephile Content)"]
            elif pred_label == 'Medium':
                if "Action" in genres or "Sci-Fi" in genres:
                    ott_platforms = ["Prime Video (Action Blockbuster catalog)", "Disney+ (Visual FX / Teen-friendly focus)"]
                else:
                    ott_platforms = ["Netflix (Drama/Romance acquisition)", "Prime Video (Drama library catalog)"]
            else:
                ott_platforms = ["Sony LIV / Zee5 (Regional Catalog licensing)", "Free Ad-supported Streaming TV (FAST) Channels"]
                
            if country != 'USA' and country != 'UK':
                ott_platforms.append("Hotstar / local OTT distributors")
                
            # Audience logic
            audiences = []
            if "Animation" in genres or "Family" in genres:
                audiences.append("Kids & Family (G/PG rating affinity)")
            if "Action" in genres or "Sci-Fi" in genres or "Adventure" in genres:
                audiences.append("Action & Sci-Fi Fans (Blockbuster interest)")
            if "Horror" in genres or "Thriller" in genres:
                audiences.append("Genre Thrill Seekers (Late night / Teen demographic)")
            if "Drama" in genres or "Biography" in genres:
                audiences.append("Film Enthusiasts & Mature Adults (Prestige story seekers)")
            
            if language == "Other":
                audiences.append("Regional & Cultured Subtitle Audiences")
            else:
                audiences.append("Global Mass-Market Audiences")
                
            st.markdown("#### Recommended Distribution Platforms:")
            for platform in ott_platforms:
                st.markdown(f"<div class='rec-item'>📡 <strong>{platform}</strong></div>", unsafe_allow_html=True)
                
            st.markdown("#### Primary Target Audience Segments:")
            for aud in audiences:
                st.markdown(f"<div class='rec-item' style='border-left-color: #00e676;'>👥 <strong>{aud}</strong></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Dashboard Row 3: Genre Popularity & Market Trends Section (Dataset Driven)
        st.markdown("---")
        st.markdown("### 📈 Genre Popularity & Market Trends (Database Insights)")
        
        if df_raw is not None:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # 1. Parse genres from full dataset to draw live Plotly chart
                raw_genres = []
                for g in df_raw['genres'].dropna():
                    raw_genres.extend(g.split('|'))
                df_genres = pd.Series(raw_genres).value_counts().reset_index()
                df_genres.columns = ['Genre', 'Total Movies']
                
                fig_genres = px.bar(
                    df_genres.head(12), x='Genre', y='Total Movies',
                    title='Database Movie Counts by Genre (Market Density)',
                    color='Total Movies',
                    color_continuous_scale='Reds',
                    template='plotly_dark'
                )
                fig_genres.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_genres, use_container_width=True)
                
            with col_chart2:
                # 2. Runtime distribution histogram
                fig_dur = px.histogram(
                    df_raw.dropna(subset=['duration']), x='duration',
                    title='Global Runtime Distribution (User Selection Highlighted)',
                    nbins=50,
                    color_discrete_sequence=['#ff2a2a'],
                    template='plotly_dark'
                )
                # Add vertical line for user selection
                fig_dur.add_vline(x=duration, line_width=3, line_dash="dash", line_color="#00e676", 
                                  annotation_text=f"Your Movie ({duration}m)", annotation_position="top right")
                fig_dur.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_dur, use_container_width=True)
        else:
            st.info("Additional historical charts will render here once the raw movie dataset is downloaded to data/raw/movie_metadata.csv.")
            
    except Exception as e:
        st.error(f"Prediction failed with error: {e}")
        st.info("Please verify that you entered valid numerical inputs and fields.")
