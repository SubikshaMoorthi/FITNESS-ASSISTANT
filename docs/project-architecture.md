# Project Architecture and System Design

## 1. System Objective
The system aims to select the next-best intervention for a user based on:
- personal profile
- recent health and activity data
- behavioral adherence patterns
- previous outcomes
- contextual constraints

The main decision is not "what workout should I do?" alone, but rather:

> What intervention is most appropriate right now for this user?

## 2. Core Components

### A. User Profiling Module
Collects static and semi-static information such as:
- age
- sex/gender where required
- height
- weight
- BMI
- fitness level
- goals
- preferences
- available workout time
- constraints and limitations

### B. Daily Data Collection Module
Captures event-level data such as:
- sleep hours
- steps
- activity level
- calories
- workout duration and intensity
- fatigue or soreness rating
- recovery markers

### C. Data Preprocessing Module
Handles:
- missing value imputation
- validation and outlier review
- encoding categorical values
- feature engineering
- scaling
- train/test split

### D. ML Prediction Module
Predicts a fitness/readiness state, such as:
- Low
- Moderate
- High

This component supports the personalized decision engine but does not replace it.

### E. Behavioral Pattern Analysis Module
Tracks:
- adherence rate
- completion rate
- preferred exercise duration
- difficulty tolerance
- skip patterns

This produces a user behavior profile that adjusts scoring.

### F. Decision Engine
The decision layer combines:
- goal relevance
- current state compatibility
- sleep and recovery conditions
- recent workload
- historical response
- preference compatibility
- safety/constraint penalties

It produces a transparent intervention score.

### G. Explainability Module
Provides reasons such as:
- limited sleep reduced readiness
- recent intensity was high
- user history suggests low tolerance to heavy sessions

### H. Conversational Assistant
The LLM should not be the main decision-maker. It should explain and personalize the communication layer.

## 3. Data Flow
User
→ Profile + Daily Inputs
→ Data Processing
→ State Prediction
→ Behavioral Profiling
→ Decision Engine
→ Intervention Recommendation
→ Explainability Layer
→ LLM for Natural-Language Response

## 4. Decision Logic Principle
A recommended intervention is selected using a weighted relevance score:

Intervention score =
Goal Relevance
+ Current State Compatibility
+ Context Compatibility
+ Behavioral Compatibility
+ Historical Response
- Constraint / Safety Penalty

## 5. Example Interventions
- Heavy workout
- Light workout
- Recovery session
- Rest
- Walking / movement
- Nutrition guidance
- Lifestyle guidance

## 6. Key Design Principle
This project is intentionally designed around explainable, modular ML rather than opaque end-to-end recommendation generation.
