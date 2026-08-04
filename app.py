"""
Movie Meter – AI-Powered South Indian Cinema Intelligence Platform
Complete redesign featuring:
- Premium Netflix/IMDb-inspired dark theme with Navy background, Maroon accents, and Warm Gold highlights.
- Cinematic entrance animations and custom Google Fonts (Cinzel, Space Grotesk, Plus Jakarta Sans).
- Tabbed modular layout (Home, Movie Prediction, Analytics Dashboard, Genre Trends, Revenue Estimation, Audience Insights, OTT Recommendation, About).
- South Indian Cinema Demo pre-fill option simulating a commercial action entertainer ("Vetri: The Conquest").
- Real-time Plotly charts, circular success probability gauges, and dynamic box-office revenue projection in Crores (₹).
- Fixed the float32 casting bug in progress indicators.
"""

import os
import time
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Movie Meter – South Indian Cinema Intelligence Platform",
    page_icon="🎬",
    layout="wide"
)

# Custom premium styling injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=Plus+Jakarta+Sans:wght@300;400;600;700&family=Space+Grotesk:wght@500;700&display=swap');
    
    /* Global Background and Fonts */
    html, body, [class*="st-"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #0b0c10;
        color: #e4e4e7;
    }
    
    /* Heading Styling */
    h1, h2, h3, h4, h5, h6, .cinzel-font {
        font-family: 'Cinzel', serif;
        font-weight: 800;
        color: #ffd700; /* Warm Gold */
        text-shadow: 0 0 10px rgba(212, 175, 55, 0.2);
    }
    
    /* Custom Top Navigation / Tabs styling */
    div[data-baseweb="tab-list"] {
        background-color: #121216 !important;
        border-radius: 12px !important;
        padding: 8px !important;
        border: 1px solid #27272a !important;
        gap: 8px !important;
    }
    div[data-baseweb="tab-list"] button {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        color: #a1a1aa !important;
        background-color: transparent !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #800020 !important; /* Maroon */
        color: #ffd700 !important; /* Gold text */
        box-shadow: 0 4px 20px rgba(128, 0, 32, 0.6) !important;
        transform: scale(1.02);
    }
    div[data-baseweb="tab-list"] button:hover {
        color: #ffd700 !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
    }

    /* Custom Cards and UI panels */
    .hero-container {
        background: linear-gradient(135deg, #1e0b0b 0%, #060814 100%);
        border: 1px solid #800020;
        border-radius: 20px;
        padding: 3.5rem;
        text-align: center;
        box-shadow: 0 10px 40px rgba(128, 0, 32, 0.3);
        margin-bottom: 2.5rem;
        animation: fadeIn 1.2s ease-in-out;
    }
    
    .hero-title {
        font-family: 'Cinzel', serif;
        font-size: 4.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(to right, #ffd700, #ff8c00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
    }
    
    .glass-panel {
        background: rgba(18, 18, 24, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    .glass-panel:hover {
        border-color: #800020; /* Highlight on hover */
        transform: translateY(-3px);
    }

    /* Custom visual results banners */
    .banner-High {
        background: linear-gradient(135deg, #0a2517 0%, #030a06 100%);
        border: 2px solid #00e676;
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 8px 30px rgba(0, 230, 118, 0.2);
    }
    
    .banner-Medium {
        background: linear-gradient(135deg, #281d05 0%, #0f0b03 100%);
        border: 2px solid #ffab00;
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 8px 30px rgba(255, 171, 0, 0.2);
    }
    
    .banner-Low {
        background: linear-gradient(135deg, #250707 0%, #0a0303 100%);
        border: 2px solid #d50000;
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 8px 30px rgba(213, 0, 0, 0.2);
    }

    .banner-class-title {
        font-family: 'Cinzel', serif;
        font-size: 3rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin: 0.5rem 0;
    }
    .text-High { color: #00e676; }
    .text-Medium { color: #ffab00; }
    .text-Low { color: #ff1744; }

    .rec-item {
        background: #15151e;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #800020;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    .rec-item:hover {
        background: #1c1c28;
    }
    
    /* Footer styles */
    .footer {
        background-color: #08080c;
        border-top: 1px solid #27272a;
        padding: 3rem 2rem;
        text-align: center;
        margin-top: 5rem;
        color: #888899;
    }
    
    /* Fade-in Animation keyframes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animated-section {
        animation: fadeIn 0.8s ease-out;
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
    
    df_raw = None
    if os.path.exists(data_path):
        df_raw = pd.read_csv(data_path)
        
    return meta_maps, preprocessor, model, label_encoder, df_raw

assets = load_ml_assets()

if assets is None:
    st.error("⚠️ Machine Learning model assets not found! Please run the training pipeline first: `python utilities/model_trainer.py`.")
    st.stop()

meta_maps, preprocessor, model, label_encoder, df_raw = assets

# Top Menu Setup using customized Tabs
tab_home, tab_pred, tab_analytics, tab_genres, tab_revenue, tab_audience, tab_ott, tab_about = st.tabs([
    "🏠 HOME", 
    "🎬 MOVIE PREDICTION", 
    "📊 ANALYTICS DASHBOARD", 
    "📈 GENRE TRENDS", 
    "💰 REVENUE ESTIMATION", 
    "👥 AUDIENCE INSIGHTS", 
    "📡 OTT RECOMMENDATIONS",
    "ℹ️ ABOUT ENGINE"
])

# ----------------- 1. HOME TAB -----------------
with tab_home:
    st.markdown("<div class='animated-section'>", unsafe_allow_html=True)
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">MOVIE METER</div>
        <div class="hero-sub">AI-Powered South Indian Cinema Intelligence Platform</div>
        <div style="margin-top: 1.5rem; font-size: 1rem; color: #d4af37; font-weight: 600;">
            📡 ANALYZING KOLLYWOOD, TOLLYWOOD, MOLLYWOOD, & SANDALWOOD BOX OFFICE SUCCESS
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown("""
        <div class="glass-panel">
            <h3>🎬 Platform Intelligence</h3>
            <p>Welcome to <strong>Movie Meter</strong>, a next-generation machine learning engine tailored specifically for the dynamic landscape of South Indian cinema.</p>
            <p>South Indian movies, characterized by their high production standards, rich musical scores, powerful starcast appeal, and massive theatrical distribution networks, require a specialized classification approach. Our model leverages pre-release parameters like director popularity index, lead star rating, genre composition, and script duration to classify movies into IMDb Quality Tiers before the cameras roll.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_h2:
        st.markdown("""
        <div class="glass-panel">
            <h3>💡 Core Analytical Pillars</h3>
            <div style="margin: 0.8rem 0;">⭐ <strong>Reputation Modeling:</strong> Out-of-fold target encoding analyzes historical success maps for over 2,000 directors and actors.</div>
            <div style="margin: 0.8rem 0;">📊 <strong>Market Trend Calibration:</strong> Live database metrics assess genre densities and commercial runtime margins.</div>
            <div style="margin: 0.8rem 0;">📡 <strong>Strategic Content Mapping:</strong> Dynamic ROI estimators and platform matching recommend Netflix, Prime Video, or regional licensing.</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Quick statistics cards
    st.markdown("### 📊 Historical Platform Insights (Dataset Density)")
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.markdown("""
        <div class="glass-panel" style="text-align: center;">
            <div class="metric-label-small">Database Catalog</div>
            <div class="metric-value-large" style="color: #ffd700;">4,919+</div>
            <div style="font-size:0.8rem; color:#888;">Classified Movies</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat2:
        st.markdown("""
        <div class="glass-panel" style="text-align: center;">
            <div class="metric-label-small">Known Directors</div>
            <div class="metric-value-large" style="color: #ffd700;">2,398+</div>
            <div style="font-size:0.8rem; color:#888;">Profiles Mapped</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat3:
        st.markdown("""
        <div class="glass-panel" style="text-align: center;">
            <div class="metric-label-small">Accuracy Score</div>
            <div class="metric-value-large" style="color: #00e676;">62.1%</div>
            <div style="font-size:0.8rem; color:#888;">XGBoost Classifier</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat4:
        st.markdown("""
        <div class="glass-panel" style="text-align: center;">
            <div class="metric-label-small">Weighted ROC-AUC</div>
            <div class="metric-value-large" style="color: #00e676;">73.0%</div>
            <div style="font-size:0.8rem; color:#888;">Precision Margin</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# Initialize session state variables for prediction outputs if not existing
if "prediction_data" not in st.session_state:
    st.session_state["prediction_data"] = None

# ----------------- 2. MOVIE PREDICTION TAB -----------------
with tab_pred:
    st.markdown("<div class='animated-section'>", unsafe_allow_html=True)
    st.markdown("### 🎬 Project Parameter Entry")
    st.write("Fill in the fields below. Use the **South Indian Blockbuster Demo** button to pre-populate with an action entertainer.")
    
    # South Indian Demo Pre-fill Button
    if st.button("🌟 PRE-FILL SOUTH INDIAN CINEMA DEMO (Vetri: The Conquest)", use_container_width=True):
        st.session_state["demo_title"] = "Vetri: The Conquest"
        st.session_state["demo_director"] = "K. R. Rajan"
        st.session_state["demo_actor"] = "Prithviraj Dev"
        st.session_state["demo_genres"] = ["Action", "Drama", "Thriller"]
        st.session_state["demo_duration"] = 145
        st.session_state["demo_year"] = 2026
        st.session_state["demo_lang"] = "Other"
        st.session_state["demo_country"] = "Other"
        st.session_state["demo_rating"] = "PG-13"
        st.session_state["demo_faces"] = 3
        st.toast("Fictional commercial action demo loaded! Click Predict below.", icon="⭐")
        
    # Get values from session state if loaded
    val_title = st.session_state.get("demo_title", "The Grand Budapest Hotel")
    val_director = st.session_state.get("demo_director", "Wes Anderson")
    val_actor = st.session_state.get("demo_actor", "Ralph Fiennes")
    val_genres = st.session_state.get("demo_genres", ["Comedy", "Drama"])
    val_duration = st.session_state.get("demo_duration", 99)
    val_year = st.session_state.get("demo_year", 2014)
    val_lang = st.session_state.get("demo_lang", "English")
    val_country = st.session_state.get("demo_country", "USA")
    val_rating = st.session_state.get("demo_rating", "PG-13")
    val_faces = st.session_state.get("demo_faces", 2)
    
    with st.form("main_pred_form"):
        col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
        with col_p1:
            in_title = st.text_input("Project Name / Title", value=val_title)
            in_genres = st.multiselect("Selected Genres", meta_maps['top_genres'], default=val_genres)
        with col_p2:
            in_director = st.text_input("Director Name", value=val_director)
            in_year = st.number_input("Year of Release", min_value=1900, max_value=2030, value=val_year)
        with col_p3:
            in_actor = st.text_input("Lead Star (Actor 1)", value=val_actor)
            in_duration = st.number_input("Project Runtime (Minutes)", min_value=10, max_value=360, value=val_duration)
            
        col_p4, col_p5, col_p6, col_p7 = st.columns(4)
        with col_p4:
            in_lang = st.selectbox("Language Mode", ["English", "Other"], index=0 if val_lang == "English" else 1)
        with col_p5:
            in_country = st.selectbox("Production Base", ["USA", "UK", "Other"], index=0 if val_country == "USA" else 1 if val_country == "UK" else 2)
        with col_p6:
            in_rating = st.selectbox("Content Certification Rating", ["G", "PG", "PG-13", "R", "Other"], index=["G", "PG", "PG-13", "R", "Other"].index(val_rating))
        with col_p7:
            in_faces = st.slider("Faces on Poster Artwork", min_value=0, max_value=20, value=val_faces)
            
        predict_trigger = st.form_submit_button("🚀 CALCULATE SUCCESS INTELLIGENCE", use_container_width=True)
        
    if predict_trigger:
        # Show progress animation
        with st.status("🎬 Commencing Movie Success Prediction...", expanded=True) as status:
            st.write("Fetching historical database profiles...")
            time.sleep(0.4)
            st.write("Resolving director popularity weightings...")
            time.sleep(0.3)
            st.write("Executing XGBoost classification algorithms...")
            time.sleep(0.4)
            status.update(label="Analysis Ready!", state="complete", expanded=False)
            
        # 1. Lookup logic (and handling fictional commercial demo names)
        cleaned_dir = in_director.strip()
        if cleaned_dir == "K. R. Rajan":
            dir_score = 7.8
            dir_likes = 25000
            is_dir_known = True
        elif cleaned_dir in meta_maps['director_avg_score_map']:
            dir_score = meta_maps['director_avg_score_map'][cleaned_dir]
            dir_likes = meta_maps['director_likes_map'].get(cleaned_dir, meta_maps['median_director_likes'])
            is_dir_known = True
        else:
            dir_score = meta_maps['global_mean']
            dir_likes = meta_maps['median_director_likes']
            is_dir_known = False
            
        cleaned_act = in_actor.strip()
        if cleaned_act == "Prithviraj Dev":
            act_score = 7.6
            act_likes = 50000
            is_act_known = True
        elif cleaned_act in meta_maps['actor_1_avg_score_map']:
            act_score = meta_maps['actor_1_avg_score_map'][cleaned_act]
            act_likes = meta_maps['actor_likes_map'].get(cleaned_act, meta_maps['median_actor_likes'])
            is_act_known = True
        else:
            act_score = meta_maps['global_mean']
            act_likes = meta_maps['median_actor_likes']
            is_act_known = False
            
        cast_likes = act_likes + dir_likes + 2000
        
        # 2. Build feature record
        record = {
            'duration': in_duration,
            'title_year': in_year,
            'director_facebook_likes': dir_likes,
            'cast_total_facebook_likes': cast_likes,
            'facenumber_in_poster': in_faces,
            'is_english': 1 if in_lang == "English" else 0,
            'country_grouped': in_country,
            'content_rating_grouped': in_rating,
            'director_avg_score': dir_score,
            'actor_1_avg_score': act_score
        }
        for g in meta_maps['top_genres']:
            record[f'genre_{g}'] = 1 if g in in_genres else 0
            
        df_input = pd.DataFrame([record])
        
        try:
            # Run transformation and inference
            X_trans = preprocessor.transform(df_input)
            pred_idx = model.predict(X_trans)[0]
            prob = model.predict_proba(X_trans)[0]
            
            pred_label = label_encoder.inverse_transform([pred_idx])[0]
            confidence = prob[pred_idx] * 100
            
            low_prob = prob[label_encoder.transform(['Low'])[0]] * 100
            med_prob = prob[label_encoder.transform(['Medium'])[0]] * 100
            high_prob = prob[label_encoder.transform(['High'])[0]] * 100
            
            # Save all prediction values inside session state
            st.session_state["prediction_data"] = {
                "title": in_title,
                "director": in_director,
                "actor": in_actor,
                "genres": in_genres,
                "duration": in_duration,
                "year": in_year,
                "language": in_lang,
                "country": in_country,
                "rating": in_rating,
                "pred_label": pred_label,
                "confidence": confidence,
                "low_prob": low_prob,
                "med_prob": med_prob,
                "high_prob": high_prob,
                "dir_score": dir_score,
                "dir_likes": dir_likes,
                "is_dir_known": is_dir_known,
                "act_score": act_score,
                "act_likes": act_likes,
                "is_act_known": is_act_known,
                "cast_likes": cast_likes
            }
            st.success("✅ Analytics generated! Open the other tabs to view your reports.")
        except Exception as e:
            st.error(f"Prediction failed with error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)


# Fetch session data for display on the other tabs
p_data = st.session_state["prediction_data"]

# ----------------- 3. ANALYTICS DASHBOARD TAB -----------------
with tab_analytics:
    st.markdown("<div class='animated-section'>", unsafe_allow_html=True)
    if p_data is None:
        st.info("💡 Please complete a prediction inside the 'MOVIE PREDICTION' tab first to generate the executive reports.")
    else:
        st.markdown(f"## 📊 Executive Success Dashboard: *{p_data['title']}*")
        
        col_an1, col_an2 = st.columns([1.5, 2.5])
        with col_an1:
            st.markdown(f"""
            <div class="banner-{p_data['pred_label']}">
                <div class="metric-label-small">AI Prediction Result</div>
                <div class="banner-class-title text-{p_data['pred_label']}">{p_data['pred_label']}</div>
                <div class="metric-label-small">Projected IMDb Quality Tier</div>
                <hr style="border-top: 1px solid rgba(255,255,255,0.1); margin: 1rem 0;">
                <div style="font-size: 1.1rem; font-weight: 600;">Confidence: {p_data['confidence']:.1f}%</div>
                <div style="font-size: 0.85rem; color: #a1a1aa; margin-top: 0.5rem;">
                    Computed via advanced XGBoost Ensemble Model
                </div>
            </div>
            <br>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="glass-panel">
                <div class="metric-label-small">Reputation Ratings Profile</div>
                <div style="margin-top: 0.8rem;">
                    <strong>Director ({p_data['director']}):</strong><br>
                    Average Score: {p_data['dir_score']:.2f} | Facebook Likes: {int(p_data['dir_likes']):,}
                </div>
                <hr style="border-top: 1px solid rgba(255,255,255,0.1); margin: 0.8rem 0;">
                <div>
                    <strong>Lead Actor ({p_data['actor']}):</strong><br>
                    Average Score: {p_data['act_score']:.2f} | Facebook Likes: {int(p_data['act_likes']):,}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_an2:
            # 3 Gauge indicators side-by-side
            success_score = float(p_data['high_prob'] + p_data['med_prob'])
            
            # Market Potential Score
            g_bonus = sum([15 for g in p_data['genres'] if g in ['Action', 'Adventure', 'Sci-Fi', 'Thriller']])
            g_bonus = min(30, g_bonus)
            s_power = np.log1p(p_data['cast_likes']) / 12 * 40
            l_bonus = 20 if (p_data['country'] == 'USA' or p_data['language'] == 'English') else 10
            market_pot = min(100, int(30 + s_power + l_bonus + g_bonus))
            
            # Production Readiness Score
            dur_sc = 30 if (90 <= p_data['duration'] <= 120) else 15
            rat_sc = 30 if p_data['rating'] in ['PG-13', 'R'] else 20
            prod_ready = int(dur_sc + rat_sc + 40)
            
            fig_gauges = go.Figure()
            
            # Success gauge
            fig_gauges.add_trace(go.Indicator(
                mode = "gauge+number",
                value = success_score,
                title = {'text': "Success Rate", 'font': {'size': 15, 'family': 'Space Grotesk'}},
                domain = {'x': [0, 0.3], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [0, 100], 'tickcolor': "#27272a"},
                    'bar': {'color': "#00e676" if success_score >= 70 else "#ffab00" if success_score >= 45 else "#ff1744"},
                    'bgcolor': "#121216",
                    'steps': [
                        {'range': [0, 45], 'color': 'rgba(255, 23, 68, 0.1)'},
                        {'range': [45, 70], 'color': 'rgba(255, 171, 0, 0.1)'},
                        {'range': [70, 100], 'color': 'rgba(0, 230, 118, 0.1)'}
                    ]
                }
            ))
            
            # Market Potential
            fig_gauges.add_trace(go.Indicator(
                mode = "gauge+number",
                value = market_pot,
                title = {'text': "Market potential", 'font': {'size': 15, 'family': 'Space Grotesk'}},
                domain = {'x': [0.35, 0.65], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [0, 100], 'tickcolor': "#27272a"},
                    'bar': {'color': "#ffd700"},
                    'bgcolor': "#121216",
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(255, 255, 255, 0.05)'},
                        {'range': [50, 100], 'color': 'rgba(212, 175, 55, 0.05)'}
                    ]
                }
            ))
            
            # Production Readiness
            fig_gauges.add_trace(go.Indicator(
                mode = "gauge+number",
                value = prod_ready,
                title = {'text': "Production Readiness", 'font': {'size': 15, 'family': 'Space Grotesk'}},
                domain = {'x': [0.7, 1.0], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [0, 100], 'tickcolor': "#27272a"},
                    'bar': {'color': "#66b3ff"},
                    'bgcolor': "#121216",
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(255, 255, 255, 0.05)'},
                        {'range': [50, 100], 'color': 'rgba(102, 179, 255, 0.05)'}
                    ]
                }
            ))
            
            fig_gauges.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': "#ffffff"},
                height=280,
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_gauges, use_container_width=True)
            
            # Class Probabilities breakdown cards
            col_l, col_m, col_h = st.columns(3)
            with col_l:
                st.markdown(f"""
                <div class="glass-panel" style="text-align: center; border-left: 4px solid #ff1744; padding:1.2rem;">
                    <div class="metric-label-small">Low Probability</div>
                    <div style="font-size:1.6rem; font-weight:700; color:#ff1744;">{float(p_data['low_prob']):.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with col_m:
                st.markdown(f"""
                <div class="glass-panel" style="text-align: center; border-left: 4px solid #ffab00; padding:1.2rem;">
                    <div class="metric-label-small">Medium Probability</div>
                    <div style="font-size:1.6rem; font-weight:700; color:#ffab00;">{float(p_data['med_prob']):.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with col_h:
                st.markdown(f"""
                <div class="glass-panel" style="text-align: center; border-left: 4px solid #00e676; padding:1.2rem;">
                    <div class="metric-label-small">High Probability</div>
                    <div style="font-size:1.6rem; font-weight:700; color:#00e676;">{float(p_data['high_prob']):.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------- 4. GENRE TRENDS TAB -----------------
with tab_genres:
    st.markdown("<div class='animated-section'>", unsafe_allow_html=True)
    st.markdown("### 📈 Live Market Genre Distribution & Runtime Analysis")
    st.write("These metrics are calculated from historical movie runs to analyze market saturations.")
    
    if df_raw is not None:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            raw_genres = []
            for g in df_raw['genres'].dropna():
                raw_genres.extend(g.split('|'))
            df_g = pd.Series(raw_genres).value_counts().reset_index()
            df_g.columns = ['Genre', 'Count']
            
            fig_g = px.bar(
                df_g.head(12), x='Genre', y='Count',
                title='Historical Movie Density by Genre',
                color='Count',
                color_continuous_scale='Burg', # Maroon-like theme
                template='plotly_dark'
            )
            fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_g, use_container_width=True)
            
        with col_g2:
            fig_d = px.histogram(
                df_raw.dropna(subset=['duration']), x='duration',
                title='Market Runtime Distributions (Min)',
                nbins=40,
                color_discrete_sequence=['#800020'], # Maroon
                template='plotly_dark'
            )
            if p_data is not None:
                fig_d.add_vline(x=p_data['duration'], line_width=3, line_dash="dash", line_color="#ffd700",
                                annotation_text=f"Your Movie ({p_data['duration']}m)", annotation_position="top right")
            fig_d.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_d, use_container_width=True)
    else:
        st.info("Database files missing. Charts will populate once raw/movie_metadata.csv is fetched.")
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------- 5. REVENUE ESTIMATION TAB -----------------
with tab_revenue:
    st.markdown("<div class='animated-section'>", unsafe_allow_html=True)
    if p_data is None:
        st.info("💡 Please complete a prediction inside the 'MOVIE PREDICTION' tab first to generate the financial report.")
    else:
        st.markdown(f"## 💰 Financial Intelligence Projections: *{p_data['title']}*")
        
        # Calculate dynamic USD ranges based on superstar weights
        star_multiplier = 1.0 + (p_data['cast_likes'] / 100000.0)
        star_multiplier = min(3.0, star_multiplier)
        
        if p_data['pred_label'] == 'High':
            usd_min, usd_max = 150 * star_multiplier, 500 * star_multiplier
            roi_min, roi_max = 180, 500
        elif p_data['pred_label'] == 'Medium':
            usd_min, usd_max = 40 * star_multiplier, 150 * star_multiplier
            roi_min, roi_max = 40, 180
        else:
            usd_min, usd_max = 5 * star_multiplier, 40 * star_multiplier
            roi_min, roi_max = -60, 30
            
        # Convert to Indian Rupee Crores (Fictional conversion representing regional Indian market)
        # 1 USD Million = 8.3 Crores INR roughly
        inr_min = usd_min * 8.3
        inr_max = usd_max * 8.3
        
        col_rev1, col_rev2 = st.columns(2)
        with col_rev1:
            st.markdown(f"""
            <div class="glass-panel" style="border-left: 5px solid #ffd700;">
                <h3>Global Box Office Projections (Fictional Estimates)</h3>
                <div style="margin: 1.5rem 0;">
                    <div class="metric-label-small">Estimated USD Gross Range</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #ffd700;">${usd_min:.1f}M – ${usd_max:.1f}M</div>
                </div>
                <div style="margin: 1.5rem 0;">
                    <div class="metric-label-small">Estimated South Indian Market Conversion (INR)</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #00e676;">₹{inr_min:.1f} Crores – ₹{inr_max:.1f} Crores</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_rev2:
            st.markdown(f"""
            <div class="glass-panel" style="border-left: 5px solid #800020;">
                <h3>Yield and ROI Analysis</h3>
                <div style="margin: 1.5rem 0;">
                    <div class="metric-label-small">Projected Profitability Index (ROI)</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: {'#00e676' if roi_min >= 0 else '#ff1744'};">{roi_min}% – {roi_max}%</div>
                </div>
                <p>ROI calculations are estimated based on distribution rights, digital satellite rights (Sun TV, Star Vijay equivalents), and multiplex ticket sale allocations for commercial theatres in India and overseas markets.</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------- 6. AUDIENCE INSIGHTS TAB -----------------
with tab_audience:
    st.markdown("<div class='animated-section'>", unsafe_allow_html=True)
    if p_data is None:
        st.info("💡 Please complete a prediction inside the 'MOVIE PREDICTION' tab first to generate audience reports.")
    else:
        st.markdown(f"## 👥 Demographics & Audience Analysis: *{p_data['title']}*")
        
        # Audience segmentation logic
        aud_segments = []
        if "Animation" in p_data['genres'] or "Family" in p_data['genres']:
            aud_segments.append({
                "segment": "Kids & Family",
                "percentage": 90,
                "desc": "High appeal for parental groups, G/PG certificate affinity, and holiday release periods."
            })
        if "Action" in p_data['genres'] or "Sci-Fi" in p_data['genres'] or "Adventure" in p_data['genres']:
            aud_segments.append({
                "segment": "Youth & Action Lovers",
                "percentage": 85,
                "desc": "High appeal for teenagers and college demographics. High ticket conversion during opening weekends."
            })
        if "Horror" in p_data['genres'] or "Thriller" in p_data['genres']:
            aud_segments.append({
                "segment": "Teen Genre Fans",
                "percentage": 75,
                "desc": "Late-night show ticket sales, high social media buzz, and trailer engagement."
            })
        if "Drama" in p_data['genres'] or "Biography" in p_data['genres']:
            aud_segments.append({
                "segment": "Prestige Story Seekers",
                "percentage": 65,
                "desc": "Mature demographics, reviews-oriented viewership, and steady long-term box office runs (word of mouth)."
            })
            
        if p_data['language'] == "Other":
            aud_segments.append({
                "segment": "South Indian Regional Audience",
                "percentage": 95,
                "desc": "Fierce local cultural connect. Massive theater attendance across Tamil Nadu, Andhra, Telangana, Kerala, and Karnataka."
            })
        else:
            aud_segments.append({
                "segment": "Global Crossover Audience",
                "percentage": 50,
                "desc": "Requires localized dubs and subtitled releases. Secondary target for international centers."
            })
            
        col_aud1, col_aud2 = st.columns(2)
        with col_aud1:
            st.markdown("### Target Demographics Profile")
            for segment in aud_segments:
                st.markdown(f"""
                <div class="glass-panel" style="margin-bottom:1rem; padding:1.2rem;">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-size:1.1rem; font-weight:700; color:#ffd700;">{segment['segment']}</span>
                        <span style="font-weight:700; color:#00e676;">{segment['percentage']}% Affinity</span>
                    </div>
                    <p style="font-size:0.9rem; color:#a1a1aa; margin-top:0.4rem; margin-bottom:0;">{segment['desc']}</p>
                </div>
                """, unsafe_allow_html=True)
                
        with col_aud2:
            st.markdown("### Market Penetration Insights")
            st.write("We project target marketing strategies based on these parameters:")
            
            # Simple list of suggestions
            st.markdown("""
            <div class="rec-item">💡 <strong>Trailer Launch Strategy:</strong> Prime launch window 3-4 weeks prior to theatrical screen bookings. Focus heavily on action cuts and musical hooks.</div>
            <div class="rec-item">💡 <strong>Social Media Indexing:</strong> Mobilize fan clubs across platforms for superstar hero entry scenes to maximize opening day footprints.</div>
            <div class="rec-item">💡 <strong>Certification Safety:</strong> UA certification enables maximum family demographic attendance, boosting overall box office run duration by ~25%.</div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------- 7. OTT RECOMMENDATIONS TAB -----------------
with tab_ott:
    st.markdown("<div class='animated-section'>", unsafe_allow_html=True)
    if p_data is None:
        st.info("💡 Please complete a prediction inside the 'MOVIE PREDICTION' tab first to generate distribution matches.")
    else:
        st.markdown(f"## 📡 Platform Distribution Strategy: *{p_data['title']}*")
        
        # Recommendations matching
        recs = []
        if p_data['pred_label'] == 'High':
            recs.append({
                "platform": "Netflix Premium Acquisition",
                "details": "High budget acquisition for direct-to-digital post-theatrical window. High subtitle crossing potential globally."
            })
            recs.append({
                "platform": "Amazon Prime Video (Prestige Starcast)",
                "details": "Major focus on starcast titles. Fits Prime's flagship South Indian catalogs."
            })
        elif p_data['pred_label'] == 'Medium':
            if "Action" in p_data['genres'] or "Thriller" in p_data['genres']:
                recs.append({
                    "platform": "Disney+ Hotstar (Mass Action Catalog)",
                    "details": "High affinity for commercial action blockbusters. Attracts wide subscription base in local Indian centers."
                })
            recs.append({
                "platform": "ZEE5 / Sony LIV Acquisitions",
                "details": "Excellent fit for family dramas and mid-budget titles with strong regional viewership indices."
            })
        else:
            recs.append({
                "platform": "Sun NXT / Simply South (Niche Regional Library)",
                "details": "Optimal target for regional low-budget/indie releases. Focus on localized audience libraries."
            })
            recs.append({
                "platform": "Free Ad-supported Streaming TV (FAST) licensing",
                "details": "Yields revenue through programmatic video ads. Recommended for generic back-catalog releases."
            })
            
        col_o1, col_o2 = st.columns(2)
        with col_o1:
            st.markdown("### Recommended Digital Release Windows")
            st.write("These platforms align with the predicted score category and genre composition:")
            for r in recs:
                st.markdown(f"""
                <div class="rec-item">
                    <span style="font-size:1.1rem; font-weight:700; color:#ffd700;">{r['platform']}</span><br>
                    <span style="font-size:0.9rem; color:#a1a1aa; display:block; margin-top:0.4rem;">{r['details']}</span>
                </div>
                """, unsafe_allow_html=True)
                
        with col_o2:
            st.markdown("### Distribution Window Strategy")
            st.write("Recommended distribution timeline after theatrical launch:")
            st.markdown("""
            <div class="glass-panel">
                <div style="margin: 0.8rem 0;">📅 <strong>Theatrical Exclusive Window:</strong> 4 - 6 Weeks (Crucial for South Indian theatrical networks).</div>
                <div style="margin: 0.8rem 0;">📡 <strong>OTT Digital Release:</strong> Week 7+ post-release (Dubbed languages like Hindi, Telugu, Kannada, Malayalam).</div>
                <div style="margin: 0.8rem 0;">📺 <strong>Satellite TV Premiere:</strong> Week 12+ (Traditional television audiences).</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------- 8. ABOUT ENGINE TAB -----------------
with tab_about:
    st.markdown("<div class='animated-section'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Engine Specifications & Modular Design")
    
    col_ab1, col_ab2 = st.columns(2)
    with col_ab1:
        st.markdown("""
        <div class="glass-panel">
            <h3>🛠️ Technology Architecture</h3>
            <p><strong>Movie Meter</strong> is powered by a modular machine learning pipeline:</p>
            <ul>
                <li><strong>Model Estimator:</strong> Extreme Gradient Boosting (XGBoost) Classifier.</li>
                <li><strong>Ensembles:</strong> Comparisons trained with Random Forest and Gradient Boosting.</li>
                <li><strong>Preprocessing:</strong> Dynamic <code>ColumnTransformer</code> applying median imputation, Robust StandardScaler, and categorical one-hot encoding.</li>
                <li><strong>Reputation Mapping:</strong> Out-of-fold cross-validated Target Encoding for high-cardinality nominal parameters (Director/Actor names).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_ab2:
        st.markdown("""
        <div class="glass-panel">
            <h3>💻 Project Integrity</h3>
            <p>The code is fully compliant with PEP-8 guidelines and follows industry best practices:</p>
            <ul>
                <li><strong>Zero Data Leakage:</strong> Post-release indicators like gross revenues, reviews, and voter rating scores are excluded from features.</li>
                <li><strong>Safe Deployment:</strong> Fully integrated dependency management using standard requirements structures.</li>
                <li><strong>Interactive Visualization:</strong> Graphics generated dynamically using responsive Plotly dashboard frameworks.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# --- Visual Footer ---
st.markdown("""
<div class="footer">
    <div style="font-size: 1.2rem; font-weight: 700; color: #ffd700; font-family: 'Cinzel', serif;">MOVIE METER</div>
    <div style="font-size: 0.85rem; margin-top: 0.5rem;">AI-Powered Cinema Intelligence Platform for South Indian Box Office</div>
    <div style="margin-top: 1rem; font-size: 0.85rem;">
        🚀 Developed with Streamlit, Plotly, & XGBoost | 
        📂 <a href="https://github.com/subhaharinioffi/movie_meter" target="_blank" style="color: #ffd700; text-decoration: none; font-weight: 600;">GitHub Repository</a>
    </div>
    <div style="font-size: 0.8rem; margin-top: 1.5rem; color: #555566;">
        © 2026 Movie Meter. Designed for Hackathon presentation. Fictional movie assets are for demo illustration purposes.
    </div>
</div>
""", unsafe_allow_html=True)
