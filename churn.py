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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# -------------------------------
# Data Loading & Preprocessing
# -------------------------------
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# Load data
df = pd.read_csv('WA_Fn-UseC_-Telco-Customer-Churn.csv')

# Remove duplicates
df = df.drop_duplicates()

# Convert TotalCharges to numeric
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')

# Drop unnecessary columns (reconsider keeping Partner, Dependents, MultipleLines later)
df.drop(columns=['customerID'], inplace=True)  # Only drop ID for now

# Convert Churn to numeric
df['Churn'] = df['Churn'].map({'No': 0, 'Yes': 1})

# Handle missing values
df['TotalCharges'] = df['TotalCharges'].fillna(df['TotalCharges'].median())

# Categorical encoding
cat_columns = df.select_dtypes(include=['object']).columns.tolist()
ordinal_columns = ['Contract'] if 'Contract' in cat_columns else []
binary_columns = [col for col in cat_columns if df[col].nunique() == 2 and col != 'Contract']
nominal_columns = [col for col in cat_columns if col not in ordinal_columns + binary_columns]

# Ordinal encoding
contract_mapping = {"Month-to-month": 1, "One year": 2, "Two year": 3}
if 'Contract' in ordinal_columns:
    df['Contract'] = df['Contract'].map(contract_mapping)

# Binary encoding
le = LabelEncoder()
for col in binary_columns:
    df[col] = le.fit_transform(df[col])

# Nominal encoding
if nominal_columns:
    df = pd.get_dummies(df, columns=nominal_columns)

# Feature engineering
df['MonthlyCharges_per_tenure'] = df['MonthlyCharges'] / (df['tenure'] + 1)  # +1 avoids division by 0
df['TotalCharges_per_tenure'] = df['TotalCharges'] / (df['tenure'] + 1)
df['ShortTenure'] = (df['tenure'] < 12).astype(int)
df['EngagementScore'] = df['MonthlyCharges'] * df['Contract']
df['BillingSecurity'] = df['PaperlessBilling'] * df['PaymentMethod_Electronic check']

# Handle NaNs in engineered features
df[['MonthlyCharges_per_tenure', 'TotalCharges_per_tenure']] = df[['MonthlyCharges_per_tenure', 'TotalCharges_per_tenure']].fillna(0)

# Feature selection
corr_matrix = df.corr(method='spearman')
thresh = 0.15
selected_features = corr_matrix['Churn'][abs(corr_matrix['Churn']) > thresh].index.tolist()
selected_features.remove('Churn')

X = df[selected_features]
y = df['Churn']

# Split data
train, val, test = np.split(df.sample(frac=1), [int(0.6*len(df)), int(0.8*len(df))])

def get_data(data):
    X = data[selected_features]
    y = data['Churn']
    return X, y

X_train, y_train = get_data(train)
X_val, y_val = get_data(val)
X_test, y_test = get_data(test)

# Scale features
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

# Check class balance
print("Class distribution for y train :\n", y_train)
print("Class distribution for x train :\n", X_train)


model_baseline = LogisticRegression()


