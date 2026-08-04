"""
Model Training and Evaluation Script for MovieMeter.
Trains multiple classifiers (Logistic Regression, Decision Tree, Random Forest,
Gradient Boosting, XGBoost), compares their performance, and saves the best model.
Also generates and saves evaluation plots.
"""

import os
import sys
# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, classification_report,
    confusion_matrix, roc_auc_score, roc_curve, auc
)
from xgboost import XGBClassifier

# Import utilities
from utilities.data_loader import load_dataset
from utilities.preprocessor import (
    clean_raw_data, get_rating_category, target_encode_train_test,
    engineer_features, get_preprocessor_pipeline
)

def save_plots(y_test_encoded, y_pred_encoded, y_prob, label_encoder, best_model_name):
    """
    Generates and saves the Confusion Matrix and ROC Curve plots in assets/eda_plots.
    """
    os.makedirs(os.path.join("assets", "eda_plots"), exist_ok=True)
    
    # 1. Confusion Matrix
    cm = confusion_matrix(y_test_encoded, y_pred_encoded)
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=label_encoder.classes_,
        yticklabels=label_encoder.classes_
    )
    plt.title(f"Confusion Matrix - {best_model_name} (Best Model)")
    plt.ylabel("Actual Category")
    plt.xlabel("Predicted Category")
    plt.tight_layout()
    cm_path = os.path.join("assets", "eda_plots", "confusion_matrix.png")
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"Confusion Matrix saved to {cm_path}")
    
    # 2. ROC Curve
    n_classes = len(label_encoder.classes_)
    y_test_onehot = pd.get_dummies(y_test_encoded).values
    
    plt.figure(figsize=(10, 8))
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    
    for i in range(n_classes):
        fpr, tpr, _ = roc_curve(y_test_onehot[:, i], y_prob[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(
            fpr, tpr, color=colors[i], lw=2,
            label=f"ROC curve of class {label_encoder.classes_[i]} (area = {roc_auc:.2f})"
        )
        
    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"Receiver Operating Characteristic (ROC) - {best_model_name}")
    plt.legend(loc="lower right")
    plt.tight_layout()
    roc_path = os.path.join("assets", "eda_plots", "roc_curve.png")
    plt.savefig(roc_path, dpi=300)
    plt.close()
    print(f"ROC Curve saved to {roc_path}")

def run_training_pipeline():
    # Make sure folders exist
    os.makedirs("models", exist_ok=True)
    os.makedirs(os.path.join("assets", "eda_plots"), exist_ok=True)
    
    # 1. Load Data
    print("Loading raw dataset...")
    df_raw = load_dataset()
    print(f"Raw shape: {df_raw.shape}")
    
    # 2. Clean Data
    print("Cleaning dataset...")
    df_clean = clean_raw_data(df_raw)
    print(f"Cleaned shape: {df_clean.shape}")
    
    # Plot IMDb score distribution
    plt.figure(figsize=(8, 5))
    sns.histplot(df_clean['imdb_score'], kde=True, bins=30, color='royalblue')
    plt.axvline(6.0, color='red', linestyle='--', label='Low / Medium threshold (6.0)')
    plt.axvline(7.5, color='green', linestyle='--', label='Medium / High threshold (7.5)')
    plt.title("Distribution of IMDb Scores")
    plt.xlabel("IMDb Score")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join("assets", "eda_plots", "imdb_score_distribution.png"), dpi=300)
    plt.close()
    
    # Create target column
    df_clean['rating_category'] = df_clean['imdb_score'].apply(get_rating_category)
    
    # Plot Class Balance
    plt.figure(figsize=(6, 4))
    sns.countplot(x='rating_category', data=df_clean, order=['Low', 'Medium', 'High'], palette='viridis')
    plt.title("IMDb Rating Category Distribution (Class Balance)")
    plt.xlabel("Rating Category")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join("assets", "eda_plots", "class_balance.png"), dpi=300)
    plt.close()
    
    # 3. Train Test Split
    X = df_clean.copy()
    y = df_clean['rating_category']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 4. Feature Engineering
    # Identify top genres on training set
    print("Engineering features...")
    X_train_eng, top_genres = engineer_features(X_train)
    X_test_eng, _ = engineer_features(X_test, top_genres=top_genres)
    
    # Target Encoding
    print("Applying target encoding to high-cardinality features...")
    X_train_encoded, X_test_encoded, meta_maps = target_encode_train_test(
        X_train_eng, X_test_eng, target_col='imdb_score'
    )
    
    # Save meta maps containing smoothed values for Streamlit inference
    meta_maps['top_genres'] = top_genres
    joblib.dump(meta_maps, os.path.join("models", "director_actor_maps.joblib"))
    print("Director/Actor mappings and metadata saved.")
    
    # Define features
    features = [
        'duration', 'title_year', 'director_facebook_likes', 'cast_total_facebook_likes',
        'facenumber_in_poster', 'is_english', 'country_grouped', 'content_rating_grouped',
        'director_avg_score', 'actor_1_avg_score'
    ] + [f'genre_{g}' for g in top_genres]
    
    X_train_final = X_train_encoded[features]
    X_test_final = X_test_encoded[features]
    
    # Numeric, Categorical, Binary listings
    numeric_features = [
        'duration', 'title_year', 'director_facebook_likes', 'cast_total_facebook_likes',
        'facenumber_in_poster', 'director_avg_score', 'actor_1_avg_score'
    ]
    categorical_features = ['country_grouped', 'content_rating_grouped']
    binary_features = ['is_english'] + [f'genre_{g}' for g in top_genres]
    
    # Label encoding target variable
    # We want order: Low, Medium, High -> XGBoost needs 0, 1, 2
    label_encoder = LabelEncoder()
    # Fit encoder on High, Medium, Low
    label_encoder.fit(['Low', 'Medium', 'High'])
    y_train_encoded = label_encoder.transform(y_train)
    y_test_encoded = label_encoder.transform(y_test)
    
    # Build preprocessor pipeline
    preprocessor = get_preprocessor_pipeline(numeric_features, categorical_features, binary_features)
    
    # Fit and transform training features
    print("Fitting and transforming features...")
    X_train_trans = preprocessor.fit_transform(X_train_final)
    X_test_trans = preprocessor.transform(X_test_final)
    
    # Save fitted preprocessor
    joblib.dump(preprocessor, os.path.join("models", "preprocessor.joblib"))
    print("Fitted preprocessor saved.")
    
    # Define models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'),
        'Decision Tree': DecisionTreeClassifier(max_depth=6, random_state=42, class_weight='balanced'),
        'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, class_weight='balanced'),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42),
        'XGBoost': XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42, eval_metric='mlogloss')
    }
    
    results = {}
    
    print("\nTraining and comparing models:")
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_trans_inputs := X_train_trans, y_train_encoded)
        y_pred = model.predict(X_test_trans)
        
        # Calculate metrics
        acc = accuracy_score(y_test_encoded, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test_encoded, y_pred, average='weighted')
        
        # Calculate ROC-AUC (OvR)
        if hasattr(model, "predict_proba"):
            y_prob = model.predict_proba(X_test_trans)
            roc_auc = roc_auc_score(y_test_encoded, y_prob, multi_class='ovr', average='weighted')
        else:
            roc_auc = np.nan
            y_prob = None
            
        results[name] = {
            'model': model,
            'accuracy': acc,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'roc_auc': roc_auc,
            'y_pred': y_pred,
            'y_prob': y_prob
        }
        print(f"{name} - Accuracy: {acc:.4f}, Weighted F1: {f1:.4f}, ROC-AUC: {roc_auc:.4f}")
        
    # Compare and select best model based on F1-Score
    best_model_name = max(results, key=lambda k: results[k]['f1_score'])
    best_result = results[best_model_name]
    print(f"\n*** Best model chosen: {best_model_name} with F1-Score: {best_result['f1_score']:.4f} ***")
    
    # Save best model
    best_model_path = os.path.join("models", "movie_meter_model.joblib")
    joblib.dump(best_result['model'], best_model_path)
    print(f"Saved best model to {best_model_path}")
    
    # Save label encoder
    joblib.dump(label_encoder, os.path.join("models", "label_encoder.joblib"))
    print("Label encoder saved.")
    
    # Save metrics in a summary dataframe
    summary_data = []
    for name, res in results.items():
        summary_data.append({
            'Model': name,
            'Accuracy': res['accuracy'],
            'Precision': res['precision'],
            'Recall': res['recall'],
            'F1-Score': res['f1_score'],
            'ROC-AUC': res['roc_auc']
        })
    df_metrics = pd.DataFrame(summary_data)
    metrics_path = os.path.join("models", "model_comparison_metrics.csv")
    df_metrics.to_csv(metrics_path, index=False)
    print(f"\nModel metrics saved to {metrics_path}")
    print(df_metrics.to_string(index=False))
    
    # Print detailed classification report for the best model
    print(f"\nClassification Report for Best Model ({best_model_name}):")
    y_pred_labels = label_encoder.inverse_transform(best_result['y_pred'])
    y_test_labels = label_encoder.inverse_transform(y_test_encoded)
    print(classification_report(y_test_labels, y_pred_labels))
    
    # Generate and save evaluation plots for the best model
    save_plots(
        y_test_encoded, best_result['y_pred'],
        best_result['y_prob'], label_encoder, best_model_name
    )

if __name__ == "__main__":
    run_training_pipeline()
