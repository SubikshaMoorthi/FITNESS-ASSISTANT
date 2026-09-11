# INTELLIGENT PERSONALIZED FITNESS AND HEALTH ASSISTANT

An end-to-end final-year AI/ML project focused on building a context-aware, behavior-aware fitness decision system.

## Project Goal
The system does not simply generate a generic workout plan. It evaluates the user’s current profile, habits, health signals, recent training load, and behavioral history to decide the most appropriate intervention at the right moment.

The primary philosophy is:

> Personalizing the Decision, Not Just the Recommendation.

## Core Architecture
- Frontend: React.js with pages for authentication, profile, daily check-in, dashboard, recommendations, feedback, and AI assistant.
- Backend: Python + FastAPI for APIs, database access, ML integration, and recommendation orchestration.
- ML Layer: tabular classification for fitness state, clustering for behavior patterns, and explainability with SHAP.
- Decision Engine: transparent rule-based scoring layer that combines profile, state, context, and behavior.
- Conversational Layer: LLM-powered natural-language explanation and chat, while keeping the ML/decision engine as the decision authority.

## Project Structure
```text
Intelligent-Fitness-Assistant/
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── README.md
├── ml/
│   ├── preprocessing/
│   ├── models/
│   ├── notebooks/
│   └── requirements.txt
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
├── database/
│   ├── schema.sql
│   └── README.md
├── notebooks/
│   └── README.md
├── models/
│   └── README.md
├── docs/
│   ├── project-architecture.md
│   └── phase-2-dataset-analysis.md
├── .gitignore
├── README.md
└── .env.example
```

## Project Phases
### Phase 1 — Project Setup
- Create GitHub repository
- Create React frontend
- Create FastAPI backend
- Create project folders
- Configure database and environment

### Phase 2 — Dataset and Data Analysis
- Select suitable dataset(s)
- Analyze columns and data quality
- Map data fields to project requirements
- Define the ML target and feature set
- Document the target variable and its derivation

### Phase 3 — Data Preprocessing
- Missing value handling
- Encoding
- Feature engineering
- Scaling
- Train/test split

### Phase 4 — Machine Learning
- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost
- Evaluation with accuracy, precision, recall, and F1 score

### Phase 5 — Behavioral Analysis
- Recommendation adherence tracking
- Behavioral clustering
- Historical pattern modeling

### Phase 6 — Decision Engine
- Transparent rule-based intervention scoring
- Safety and constraint penalty logic
- Recommendation explanation pipeline

### Phase 7 — Backend Integration
- API endpoints
- Model serving
- Recommendation generation
- Feedback persistence

### Phase 8 — Frontend Development
- Profile form
- Daily check-in
- Dashboard
- Recommendation view
- Feedback flow
- AI assistant UI

### Phase 9 — Explainability
- SHAP explanations for ML prediction
- Human-friendly recommendation rationale

### Phase 10 — Conversational AI
- LLM explanation layer only after the core decision engine is stable

## Initial Implementation Scope
This repository currently focuses on the first two phases:
1. project structure and environment setup
2. dataset selection, feature design, and target definition

Model implementation will begin only after the dataset and ML objective are clearly defined.
