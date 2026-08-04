# Data Flow

This document details the real-time data flow inside the MovieMeter web application.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Streamlit Frontend
    participant App as app.py (Inference Engine)
    participant Maps as models/director_actor_maps.joblib
    participant Prep as models/preprocessor.joblib
    participant Model as models/movie_meter_model.joblib

    User->>UI: Input Movie Metadata (Wes Anderson, Ralph Fiennes, Comedy|Drama, 99 min)
    UI->>App: Trigger Prediction Event
    App->>Maps: Fetch Director and Lead Actor stats
    Maps-->>App: Returns historical mean score & likes count
    Note over App: pre-fill likes and ratings; construct inputs dataframe
    App->>Prep: Feed inputs dataframe
    Prep-->>App: Return preprocessed scaled matrix
    App->>Model: Run model.predict_proba(matrix)
    Model-->>App: Returns probability array for classes [Low, Medium, High]
    Note over App: Parse highest-probability class and confidence score
    App->>UI: Render styled card, bar charts, and strategic content suggestions
    UI->>User: Display Category, Confidence, and Strategic suggestion
```

### Explanation of Steps:
1. **User Interaction**: User fills out the movie form.
2. **Reputation lookup**: The engine resolves names to historical parameters to populate `director_avg_score` and `actor_1_avg_score`.
3. **Pipeline transformation**: Inputs are scaled and encoded using the exact pipeline fitted during training.
4. **Classification**: Model outputs class scores.
5. **UI Rendering**: Styled components render visual outputs dynamically.
