import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
import joblib

# 1. Load the dataset
df = pd.read_csv("content_training_data.csv")

# 2. Drop 'content_feedback' if it exists (not needed for training)
if "content_feedback" in df.columns:
    df = df.drop(columns=["content_feedback"])

# 3. Separate features and target
X = df.drop(columns=["content_tag"])
y = df["content_tag"]

# 4. Encode categorical columns
categorical_cols = ["expression", "user_type"]
encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])
    encoders[col] = le  # Save encoder for future decoding

# 5. Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. Create pipeline
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
])

# 7. Train the model
pipeline.fit(X_train, y_train)

# 8. Save model and encoders
joblib.dump(pipeline, "content_recommender_model.pkl")
joblib.dump(encoders, "label_encoders.pkl")

print("✅ Model and encoders saved successfully!")
