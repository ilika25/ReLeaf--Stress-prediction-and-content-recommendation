import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib

# Load dataset
df = pd.read_csv("synthetic_stress_data.csv")

# Encode categorical features
le_expression = LabelEncoder()
le_user_type = LabelEncoder()
df["expression_encoded"] = le_expression.fit_transform(df["expression"])
df["user_type_encoded"] = le_user_type.fit_transform(df["user_type"])

# Define features and target
features = ["typing_speed", "typos", "sleep_hours", "screen_hours", "expression_encoded", "user_type_encoded"]
target = "stress_level"
X = df[features]
y = df[target]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("✅ Model training complete.")
print(f"📉 MAE: {mae:.2f}")
print(f"📈 R² Score: {r2:.2f}")

# Save model
joblib.dump(model, "stress_model.pkl")
joblib.dump(le_expression, "label_encoder_expression.pkl")
joblib.dump(le_user_type, "label_encoder_user_type.pkl")
print("💾 Model and label encoders saved.")
