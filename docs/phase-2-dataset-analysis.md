# Phase 2: Dataset Recommendation and Analysis

## 1. Recommended Datasets

### Primary recommendation: fitness tracker / lifestyle datasets
Use an individual-level daily tracking dataset with enough rows to represent recurring training, sleep, activity, and recovery patterns. Suitable sources include:

1. Kaggle fitness tracker datasets
   - Fitbit / wearable activity logs
   - daily calorie, step, and sleep data
   - user-level exercise and lifestyle patterns

2. Public health and activity datasets
   - MHEALTH or physical activity monitoring datasets for activity intensity and recovery-related features
   - useful as supplemental data for exercise intensity and movement patterns

3. Exercise / gym dataset (optional support dataset)
   - workout metadata for exercise types, duration, intensity, and user effort

### Why these datasets fit this project
This project is not based on image recognition or video analysis. It depends on structured tabular signals such as:
- sleep
- steps
- active minutes
- calories
- workout frequency
- intensity
- fatigue and recovery
- profile and training goals

This makes daily health and fitness tracker datasets the most suitable starting point.

## 2. Target ML Problem
The most defensible initial ML problem is supervised classification of a user’s current readiness or fitness state.

### Recommended target variable
`readiness_level`

Possible labels:
- Low
- Moderate
- High

This target should be derived from data already present in the dataset, not created artificially without a valid rule.

### Good derivation approach
A target can be derived from a combination of signals such as:
- sleep hours
- daily steps or active minutes
- calories burned
- workout load
- soreness/fatigue
- previous workout intensity

Example rule:
- Low readiness: sleep < 6h, high recent workload, low activity, high fatigue
- Moderate readiness: average sleep, moderate training load
- High readiness: adequate sleep, stable activity, moderate workload, good recovery

This is acceptable if the rule is transparent and documented.

## 3. Input Feature Groups

### A. User profile features
- age
- gender
- height_cm
- weight_kg
- bmi
- fitness_level
- goal
- available_workout_minutes
- physical_constraints

### B. Daily health features
- sleep_hours
- sleep_quality_score
- steps
- active_minutes
- sedentary_minutes
- calories_burned
- resting_heart_rate
- activity_level

### C. Workout features
- workout_frequency
- workout_duration_min
- workout_intensity
- previous_workout_intensity
- last_workout_type
- training_load
- session_rpe

### D. Recovery and fatigue features
- fatigue_score
- soreness_score
- recovery_score
- stress_level

### E. Behavioral features
- adherence_rate
- completion_rate
- preferred_session_duration
- difficulty_rating_history
- skipped_session_count
- previous_recommendation_feedback

## 4. Data Dictionary for the Initial Project

| Column | Type | Description | Use |
|---|---|---|---|
| user_id | categorical/id | unique user identifier | identity |
| date | datetime | date of observation | time axis |
| age | numeric | age in years | profile |
| gender | categorical | sex or gender label | profile |
| height_cm | numeric | user height | profile |
| weight_kg | numeric | user weight | profile |
| bmi | numeric | body mass index | profile |
| fitness_level | categorical | beginner/intermediate/advanced | profile |
| goal | categorical | muscle_gain, fat_loss, endurance, general_health | profile |
| sleep_hours | numeric | total sleep in hours | recovery |
| sleep_quality_score | numeric | perceived or measured sleep quality | recovery |
| steps | numeric | total daily steps | activity |
| active_minutes | numeric | minutes spent active | activity |
| sedentary_minutes | numeric | sedentary minutes | activity |
| calories_burned | numeric | calories expended | energy balance |
| workout_frequency | numeric | workouts in a given period | training load |
| workout_duration_min | numeric | duration of workout | exercise dose |
| workout_intensity | numeric | session intensity | training load |
| previous_workout_intensity | numeric | recent training intensity | load monitoring |
| recovery_score | numeric | short-term recovery state | readiness |
| fatigue_score | numeric | subjective fatigue level | readiness |
| soreness_score | numeric | muscle soreness | recovery |
| adherence_rate | numeric | % of recommendations completed | behavior |
| completion_rate | numeric | app/plan completion rate | behavior |
| preferred_session_duration | numeric | user’s usual preferred session length | behavior |
| difficulty_rating_history | numeric | average session difficulty rating | behavior |
| skipped_session_count | numeric | number of skipped sessions | behavior |
| available_workout_minutes | numeric | free time available for exercise | constraints |
| physical_constraints | categorical/text | limitations or restrictions | safety |
| readiness_level | categorical | Low / Moderate / High | target variable |

## 5. Input Features vs Target Variable

### Input features for readiness model
- age
- bmi
- sleep_hours
- workout_frequency
- workout_intensity
- previous_workout_intensity
- steps
- active_minutes
- calories_burned
- fitness_level
- fatigue_score
- recovery_score
- adherence_rate
- available_workout_minutes

### Target variable
- readiness_level

This is a clean supervised classification problem for a tabular dataset.

## 6. Additional ML Problem: Behavioral Clustering
A second unsupervised task is useful for understanding behavior:

### Candidate clustering variables
- recommendation_completion_rate
- preferred_workout_duration
- average_difficulty_rating
- workout_frequency
- skipped_activity_rate

### Example clusters
- consistent users
- short-session preference users
- low-adherence users
- high-consistency users

This should be used to enrich the decision engine, not as a standalone personalization solution.

## 7. Recommended Initial Modeling Pipeline
The project should follow this order:
1. clean tabular data
2. engineer features
3. define target readiness_level
4. baseline models:
   - Logistic Regression
   - Decision Tree
   - Random Forest
   - XGBoost
5. evaluate using:
   - Accuracy
   - Precision
   - Recall
   - F1-score
6. select the best-performing model for readiness prediction
7. pass its output into the decision engine as a contextual signal

## 8. Important Design Constraint
The model should not directly decide the intervention in a black-box way. Instead, the ML layer should estimate current state or readiness, while the Personalized Decision Engine ranks the interventions transparently.

This preserves explainability, safety, and project clarity.
