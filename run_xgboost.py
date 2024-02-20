import pandas as pd
import os
import nibabel as nib
from nibabel import freesurfer as nfs
import numpy as np

import matplotlib.pyplot as plt
from tqdm import tqdm

# myscript.py
import sys

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report

if len(sys.argv) > 1:
    outcomes_doc = sys.argv[1]
else:
    print("No input list provided.")
    exit()

# run a basic gradient boost classifier if there is a outcomes file

if not os.path.isfile(outcomes_doc):
    print('missing outcomes file; no ML run')
    exit()

df = pd.read_pickle('freesurfer_features.p')
# fill in nans with 0 -- CHANGE
df = df.fillna(0)

outcomes = pd.read_csv(outcomes_doc)
outcomes = outcomes[['Subject', 'Outcome']]

df_w_outcomes = df.merge(outcomes, how='inner', on='Subject')

# Assume 'X' is your feature matrix, and 'y' is your target variable
X = df_w_outcomes[df_w_outcomes.columns.difference(['Subject', 'Outcome'])]
y = df_w_outcomes['Outcome']

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the Gradient Boosting Classifier
gb_classifier = GradientBoostingClassifier(random_state=42)

# Define the hyperparameter grid for tuning
param_grid = {
    'n_estimators': [50, 100, 150],
    'learning_rate': [0.01, 0.1, 0.2],
    'max_depth': [4, 6, 8],
}

# Create the GridSearchCV object
print('Running CV grid search.')
grid_search = GridSearchCV(estimator=gb_classifier, param_grid=param_grid, scoring='accuracy', cv=5)

# Fit the model to the training data
grid_search.fit(X_train, y_train)

# Get the best hyperparameters
best_params = grid_search.best_params_

# Instantiate the model with the best hyperparameters
print('Building model.')
best_gb_classifier = GradientBoostingClassifier(**best_params, random_state=42)

# Train the model on the full training set
best_gb_classifier.fit(X_train, y_train)

# Make predictions on the test set
y_pred = best_gb_classifier.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)

print(f'Best Hyperparameters: {best_params}')
print(f'Tuned Gradient Boosting Classifier Accuracy: {accuracy}')


