import pandas as pd
import numpy as np
import missingno as msno
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             roc_curve, auc, roc_auc_score)
from sklearn.impute import SimpleImputer
from xgboost import XGBClassifier
from imblearn.combine import SMOTETomek
import shap

# -------------------------------
# Data Loading & Preprocessing
# -------------------------------
df = pd.read_csv('WA_Fn-UseC_-Telco-Customer-Churn.csv')
df.duplicated()
# Convert TotalCharges to numeric (errors coerced to NaN)
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df.drop(columns=['customerID','Partner','Dependents','MultipleLines'], inplace=True)

# Convert 'Churn' to numeric (target variable)
df['Churn'] = df['Churn'].map({'No': 0, 'Yes': 1})

# Identify categorical columns
cat_columns = df.select_dtypes(include=['object']).columns.tolist()

ordinal_columns = []
binary_columns = []
nominal_columns = []

if 'Contract' in cat_columns:
    ordinal_columns.append('Contract')
    cat_columns.remove('Contract')

for col in cat_columns:
    if df[col].nunique() == 2:
        binary_columns.append(col)
    else:
        nominal_columns.append(col)

if 'Contract' in ordinal_columns:
    contract_mapping = {"Month-to-month": 1, "One year": 2, "Two year": 3}
    df['Contract'] = df['Contract'].map(contract_mapping)

le = LabelEncoder()
for col in binary_columns:
    df[col] = le.fit_transform(df[col])

if nominal_columns:
    df = pd.get_dummies(df, columns=nominal_columns)

# Feature Engineering
df['MonthlyCharges_per_tenure'] = df['MonthlyCharges'] / (df['tenure'] + 1)
df['TotalCharges_per_tenure'] = df['TotalCharges'] / (df['tenure'] + 1)
df['ShortTenure'] = (df['tenure'] < 12).astype(int)
df['EngagementScore'] = df['MonthlyCharges'] * df['Contract']
df['BillingSecurity'] = df['PaperlessBilling'] * df['PaymentMethod_Electronic check']

# -------------------------------
# Feature Selection
# -------------------------------
corr_matrix = df.corr(method='spearman')
thresh = 0.15
# selected_features = corr_matrix['Churn'][abs(corr_matrix['Churn']) > thresh].index.tolist()
selected_features = corr_matrix.index.tolist()
selected_features.remove('Churn')

X = df[selected_features]
y = df['Churn']

# -------------------------------
# Train-Test Split & SMOTETomek
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

imputer = SimpleImputer(strategy='mean')
X_train = imputer.fit_transform(X_train)
X_test = imputer.transform(X_test)

smote_tomek = SMOTETomek(random_state=42)
X_train_res, y_train_res = smote_tomek.fit_resample(X_train, y_train)

scaler = StandardScaler()
X_train_res = scaler.fit_transform(X_train_res)
X_test = scaler.transform(X_test)

# -------------------------------
# Model Training with XGBoost
# -------------------------------
xgb = XGBClassifier(scale_pos_weight=3, 
                     use_label_encoder=False, eval_metric='logloss', random_state=42)
xgb.fit(X_train_res, y_train_res)

y_pred = xgb.predict(X_test)
print("XGBoost Model Accuracy:", accuracy_score(y_test, y_pred))
print("\nXGBoost Classification Report:\n", classification_report(y_test, y_pred))
print("\nXGBoost Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# -------------------------------
# Hyperparameter Tuning
# -------------------------------
param_grid = {
    'max_depth': [5, 7, 10],
    'learning_rate': [0.01, 0.05, 0.1],
    'n_estimators': [100, 200, 300],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.8, 1.0]
}
grid_search = GridSearchCV(XGBClassifier(eval_metric='logloss', random_state=42), param_grid, cv=5, scoring='recall', n_jobs=-1, verbose=1)
grid_search.fit(X_train_res, y_train_res)

best_xgb = grid_search.best_estimator_
y_pred_best = best_xgb.predict(X_test)
print("Tuned XGBoost Accuracy:", accuracy_score(y_test, y_pred_best))
print("\nTuned XGBoost Classification Report:\n", classification_report(y_test, y_pred_best))

# -------------------------------
# AUC-ROC Score
# -------------------------------
y_proba = best_xgb.predict_proba(X_test)[:, 1]
roc_auc = roc_auc_score(y_test, y_proba)
print(f"AUC-ROC Score: {roc_auc:.4f}")

# -------------------------------
# SHAP Feature Importance
# -------------------------------
# explainer = shap.Explainer(best_xgb)
# shap_values = explainer(X_test)
# shap.summary_plot(shap_values, X_test)



