# Machine Learning Workflow

The workflow outlines the steps taken from raw data ingestion to offline training, cross-validation evaluation, and model serialization.

```mermaid
flowchart TD
    A[Raw IMDb Dataset Download] --> B[Data Cleaning & Duplicate Removal]
    B --> C[Train-Test Split 80/20]
    
    subgraph Feature Engineering on Train Set
        C --> D[Extract Top 10 Genres]
        D --> E[Binarize Language and Country]
        E --> F[5-Fold Out-of-fold Target Encoding for Directors/Actors]
    end
    
    subgraph Model Development & Selection
        F --> G[Impute & Scale Numeric Features]
        G --> H[One-Hot Encode Categorical Features]
        H --> I[Train Classifiers: LogReg, DT, RF, GB, XGBoost]
        I --> J[Evaluate Metrics: Accuracy, Recall, Precision, F1-Score, ROC-AUC]
        J --> K[Identify Best Model: XGBoost Classifier]
    end
    
    K --> L[Serialize Preprocessor, Model, and Metadata maps using Joblib]
    L --> M[Deploy on Streamlit Application]

    style Feature Engineering on Train Set fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    style Model Development & Selection fill:#efebe9,stroke:#5d4037,stroke-width:2px;
```

### Process Detail
1. **Target Encoding Strategy**: High-cardinality nominal variables like `director_name` and `actor_1_name` are target-encoded with smoothing to prevent overfitting.
2. **Label Encoding**: XGBoost target classes are encoded as `Low: 0`, `Medium: 1`, `High: 2`.
3. **Pipeline Construction**: A Scikit-learn `Pipeline` connects preprocessing with estimator logic to ensure no data leakage during cross-validation.
