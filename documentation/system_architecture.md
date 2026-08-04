# System Architecture

The architecture of **MovieMeter** is designed to be lightweight, modular, and robust. It follows a decoupled design where the machine learning training pipeline is independent of the real-time inference web application.

Here is the Mermaid system architecture diagram:

```mermaid
graph TD
    %% Define components
    subgraph Data Layer
        A[GitHub Raw IMDb CSV] -->|data_loader.py| B[data/raw/movie_metadata.csv]
    end

    subgraph Offline ML Pipeline
        B -->|preprocessor.py| C[Imputation, Scaling, Target Encoding]
        C -->|model_trainer.py| D[Model Comparison & Selection]
        D -->|Save Assets| E[(models/ preprocessor.joblib, movie_meter_model.joblib, maps.joblib)]
    end

    subgraph Online Web App
        F[Streamlit Frontend User Input] -->|Title, Director, Cast, Runtime, Genre| G[app.py Backend Controller]
        E -->|Load Model & Metadata| G
        G -->|Dynamic Lookup| H[Director/Actor reputation & Facebook likes]
        H -->|Pipeline Transform| I[Predict Class Probabilities]
        I -->|Render Styled Card| F
    end

    classDef layer fill:#f9f,stroke:#333,stroke-width:2px;
    classDef comp fill:#bbf,stroke:#333,stroke-width:1px;
    class Data Layer,Offline ML Pipeline,Online Web App layer;
```

### Component Details
1. **Frontend (Streamlit)**: Reacts to user inputs such as Director name, Cast name, Genres, and Runtime. It provides immediate visual feedback using custom glassmorphic cards and progress bars indicating classification confidence.
2. **Backend Controller (`app.py`)**: Runs Python code to capture web forms, perform memory-cached dictionary lookups for Director/Actor historical metrics, and run sklearn transform operations.
3. **Machine Learning Module**: Consists of:
   - `preprocessor.joblib`: Columns transformer preprocessing pipeline.
   - `movie_meter_model.joblib`: Best classifier (XGBoost).
   - `director_actor_maps.joblib`: Metadata containing historical ratings and likes mappings.
4. **Data flow**: Unidirectional from user inputs -> dynamic mapping injection -> model transformation -> inference -> user interface render.
