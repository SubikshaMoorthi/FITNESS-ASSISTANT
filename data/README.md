# Data Folder

This folder holds the project datasets and processed outputs.

## Recommended storage layout
- raw/: source datasets and original files
- processed/: cleaned and feature-engineered datasets used by the ML pipeline

## Initial dataset selection strategy
Prioritize a daily user health / activity dataset that includes:
- sleep data
- steps or activity metrics
- calorie information
- workout metadata
- user profile features
- recovery indicators when available

## Data quality expectations
The dataset should be reviewed for:
- missing values
- inconsistent units
- outliers
- invalid dates
- inconsistent categorical labels

## Project data objective
The first ML problem is not a generic recommendation model. It is a structured readiness classification problem based on practical health indicators.
