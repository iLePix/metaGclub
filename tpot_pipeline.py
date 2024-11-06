import pandas as pd
import os
from functools import reduce
import pandas as pd
from sklearn.impute import SimpleImputer
from tpot import TPOTClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
current_dir = os.getcwd()
path = os.path.join(current_dir, 'res/Source_Data_24Oct2022.xlsx')
print(f"looking at data in: {path}")

dfs = pd.read_excel(path, sheet_name=None)

subject_metadata = dfs['subject_metadata']
subject_metadata = subject_metadata.set_index('sample_name')

def process_df(df, feature_name):
    df = df.set_index(feature_name).transpose()
    df.index.name = 'sample_name'
    return df

metaphlan_counts_T = process_df(dfs['metaphlan_counts'], 'clade_name')
metaphlan_rel_ab_T = process_df(dfs['metaphlan_rel_ab'], 'clade_name')
humann_KO_group_counts_T = process_df(dfs['humann_KO_group_counts'], 'Gene Family')
humann_pathway_counts_T = process_df(dfs['humann_pathway_counts'], 'Pathway')

data_frames = [
    subject_metadata,
    metaphlan_counts_T,
    metaphlan_rel_ab_T,
    humann_KO_group_counts_T,
    humann_pathway_counts_T
]

tpot_df = reduce(
    lambda left, right: pd.merge(left, right, left_index=True, right_index=True, how='inner'),
    data_frames
)

control_count = tpot_df[tpot_df["Case_status"] == "Control"].shape[0]

# Count rows with 'PD' in 'Case_status' column
pd_count = tpot_df[tpot_df["Case_status"] == "PD"].shape[0]

# Print statement combining both counts with descriptions
print(f"{pd_count} patients with Parkinson's (PD) | {control_count} healthy control patients.")


X = tpot_df.drop('Case_status', axis=1)
y = tpot_df['Case_status']

# Step 2: Identify numeric and categorical columns
numeric_cols = X.select_dtypes(include=['number']).columns
categorical_cols = X.select_dtypes(include=['object']).columns

# Step 3: Impute missing values
# Impute numeric columns with the mean
numeric_imputer = SimpleImputer(strategy='mean')
X[numeric_cols] = numeric_imputer.fit_transform(X[numeric_cols])

# Impute categorical columns with the most frequent value
categorical_imputer = SimpleImputer(strategy='most_frequent')
X[categorical_cols] = categorical_imputer.fit_transform(X[categorical_cols])

# Step 4: Encode categorical variables (One-Hot Encoding or Label Encoding)
# For simplicity, let's use One-Hot Encoding for categorical variables
X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

# Step 5: Encode target labels (if not already numeric)
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)  # Convert 'Control'/'PD' to 0/1

# Step 6: Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Step 7: TPOT setup and training
tpot = TPOTClassifier(generations=5, population_size=20, verbosity=2, random_state=42, scoring='f1')

# Fit TPOT to training data
tpot.fit(X_train, y_train)

# Evaluate TPOT on test data
print(f"TPOT Test Accuracy: {tpot.score(X_test, y_test)}")

# Export the best pipeline
tpot.export('best_pipeline.py')