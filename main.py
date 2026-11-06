
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report, confusion_matrix
df = pd.read_csv("data/train.csv")

X = df.drop("PlacementStatus", axis=1)
y = df["PlacementStatus"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Identify text and numeric columns
cat_cols = X.select_dtypes(include=["object", "str"]).columns
num_cols = X.select_dtypes(exclude=["object", "str"]).columns

# Convert text columns into numbers
preprocessor = ColumnTransformer([
    ("text", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ("numbers", "passthrough", num_cols)
])

# Create the model
model = Pipeline([
    ("preprocessing", preprocessor),
    ("classifier", DecisionTreeClassifier(max_depth=5, random_state=42))
])

# Train the model
model.fit(X_train, y_train)

# Predict placement status
y_pred = model.predict(X_test)

# Check accuracy
accuracy = accuracy_score(y_test, y_pred)

print("Model training completed!")
print("Model accuracy:", round(accuracy * 100, 2), "%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Train a Random Forest model
rf_model = Pipeline([
    ("preprocessing", preprocessor),
    ("classifier", RandomForestClassifier(
        n_estimators=100, random_state=42
    ))
])

rf_model.fit(X_train, y_train)

rf_pred = rf_model.predict(X_test)

rf_accuracy = accuracy_score(y_test, rf_pred)

print("\nRandom Forest Results")
print("Accuracy:", round(rf_accuracy * 100, 2), "%")
print(classification_report(y_test, rf_pred))
joblib.dump(rf_model, "placement_model.pkl")
print("Random Forest model saved successfully!")