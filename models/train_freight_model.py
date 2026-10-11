
import os
import polars as pl
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# =============================================================================
# FREIGHT FORECASTING MODEL TRAINING
# =============================================================================

print("=" * 80)
print("FREIGHT FORECASTING MODEL TRAINING")
print("=" * 80)


# =============================================================================
# 1. PATHS
# =============================================================================

BASE_DIR = r"C:\intelligentfrieghtforecast"

TRAIN_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "training",
    "train.parquet"
)

VALIDATION_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "training",
    "validation.parquet"
)

TEST_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "training",
    "test.parquet"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "freight_random_forest.pkl"
)

RESULTS_PATH = os.path.join(
    MODEL_DIR,
    "model_results.txt"
)


# Create models directory if it does not exist
os.makedirs(MODEL_DIR, exist_ok=True)


# =============================================================================
# 2. READ DATA
# =============================================================================

print("\nReading training data...")

train = pl.read_parquet(TRAIN_PATH)
validation = pl.read_parquet(VALIDATION_PATH)
test = pl.read_parquet(TEST_PATH)

print(f"Training shape:   {train.shape}")
print(f"Validation shape: {validation.shape}")
print(f"Test shape:       {test.shape}")


# =============================================================================
# 3. DEFINE TARGET
# =============================================================================

TARGET = "Target_Price"

print("\nTarget variable:")
print(f"- {TARGET}")


# =============================================================================
# 4. SELECT FEATURES
# =============================================================================

# Date is not directly given to the model.
# Year, Month, Quarter and Day_of_Week already represent time information.

FEATURES = [
    "Price",
    "Open",
    "High",
    "Low",
    "Change %",
    "Year",
    "Month",
    "Quarter",
    "Day_of_Week",
    "Price_Lag_1",
    "Price_Lag_7",
    "Price_Lag_30",
    "Price_MA_7",
    "Price_MA_30",
    "Price_MA_90",
    "Volatility_7",
    "Volatility_30",
    "Price_Change_7",
    "Price_Change_30",
    "Price_Range",
    "Price_Range_Pct"
]

print(f"\nNumber of features: {len(FEATURES)}")

print("\nFeatures:")
for feature in FEATURES:
    print(f"- {feature}")


# =============================================================================
# 5. CONVERT TO PANDAS
# =============================================================================

X_train = train.select(FEATURES).to_pandas()
y_train = train.select(TARGET).to_pandas().values.ravel()

X_validation = validation.select(FEATURES).to_pandas()
y_validation = validation.select(TARGET).to_pandas().values.ravel()

X_test = test.select(FEATURES).to_pandas()
y_test = test.select(TARGET).to_pandas().values.ravel()


# =============================================================================
# 6. CHECK DATA
# =============================================================================

print("\nChecking training data...")

print(f"Training samples:   {len(X_train)}")
print(f"Validation samples: {len(X_validation)}")
print(f"Test samples:       {len(X_test)}")

print(f"\nTraining features: {X_train.shape[1]}")


# =============================================================================
# 7. CREATE RANDOM FOREST MODEL
# =============================================================================

print("\n" + "=" * 80)
print("CREATING RANDOM FOREST MODEL")
print("=" * 80)

model = RandomForestRegressor(
    n_estimators=300,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

print("\nModel configuration:")
print("Algorithm: Random Forest Regression")
print("Number of trees: 300")
print("Maximum depth: 15")
print("Minimum samples split: 5")
print("Minimum samples leaf: 2")


# =============================================================================
# 8. TRAIN MODEL
# =============================================================================

print("\nTraining model...")

model.fit(X_train, y_train)

print("Model training completed.")


# =============================================================================
# 9. VALIDATION PREDICTIONS
# =============================================================================

print("\n" + "=" * 80)
print("VALIDATION EVALUATION")
print("=" * 80)

validation_predictions = model.predict(X_validation)


# =============================================================================
# 10. EVALUATION FUNCTION
# =============================================================================

def calculate_metrics(actual, predicted):

    mae = mean_absolute_error(actual, predicted)

    rmse = mean_squared_error(
        actual,
        predicted
    ) ** 0.5

    r2 = r2_score(
        actual,
        predicted
    )

    # Avoid division by zero
    non_zero = actual != 0

    mape = (
        abs(
            (actual[non_zero] - predicted[non_zero])
            / actual[non_zero]
        ).mean()
        * 100
    )

    return mae, rmse, r2, mape


validation_mae, validation_rmse, validation_r2, validation_mape = (
    calculate_metrics(
        y_validation,
        validation_predictions
    )
)


print("\nValidation Results:")
print(f"MAE:  {validation_mae:.2f}")
print(f"RMSE: {validation_rmse:.2f}")
print(f"R²:   {validation_r2:.4f}")
print(f"MAPE: {validation_mape:.2f}%")


# =============================================================================
# 11. TEST PREDICTIONS
# =============================================================================

print("\n" + "=" * 80)
print("FINAL TEST EVALUATION")
print("=" * 80)

test_predictions = model.predict(X_test)

test_mae, test_rmse, test_r2, test_mape = calculate_metrics(
    y_test,
    test_predictions
)


print("\nTest Results:")
print(f"MAE:  {test_mae:.2f}")
print(f"RMSE: {test_rmse:.2f}")
print(f"R²:   {test_r2:.4f}")
print(f"MAPE: {test_mape:.2f}%")


# =============================================================================
# 12. SHOW SAMPLE PREDICTIONS
# =============================================================================

print("\n" + "=" * 80)
print("SAMPLE TEST PREDICTIONS")
print("=" * 80)

test_dates = test.select("Date").to_pandas()["Date"]

sample_predictions = pd.DataFrame({
    "Date": test_dates,
    "Actual_Price": y_test,
    "Predicted_Price": test_predictions
})

sample_predictions["Error"] = (
    sample_predictions["Actual_Price"]
    - sample_predictions["Predicted_Price"]
)

print("\nFirst 10 predictions:")

print(
    sample_predictions
    .head(10)
    .to_string(index=False)
)


# =============================================================================
# 13. FEATURE IMPORTANCE
# =============================================================================

print("\n" + "=" * 80)
print("FEATURE IMPORTANCE")
print("=" * 80)

importance_df = pd.DataFrame({
    "Feature": FEATURES,
    "Importance": model.feature_importances_
})

importance_df = importance_df.sort_values(
    by="Importance",
    ascending=False
)

print("\nMost important features:")

print(
    importance_df
    .head(10)
    .to_string(index=False)
)


# =============================================================================
# 14. SAVE MODEL
# =============================================================================

print("\n" + "=" * 80)
print("SAVING MODEL")
print("=" * 80)

joblib.dump(
    model,
    MODEL_PATH
)

print(f"\nModel saved to:")
print(MODEL_PATH)


# =============================================================================
# 15. SAVE RESULTS
# =============================================================================

with open(RESULTS_PATH, "w") as file:

    file.write("FREIGHT FORECASTING MODEL RESULTS\n")
    file.write("=" * 60 + "\n\n")

    file.write("MODEL\n")
    file.write("Random Forest Regression\n\n")

    file.write("DATASET\n")
    file.write(f"Training samples: {len(X_train)}\n")
    file.write(f"Validation samples: {len(X_validation)}\n")
    file.write(f"Test samples: {len(X_test)}\n\n")

    file.write("VALIDATION RESULTS\n")
    file.write(f"MAE: {validation_mae:.4f}\n")
    file.write(f"RMSE: {validation_rmse:.4f}\n")
    file.write(f"R2: {validation_r2:.4f}\n")
    file.write(f"MAPE: {validation_mape:.4f}%\n\n")

    file.write("TEST RESULTS\n")
    file.write(f"MAE: {test_mae:.4f}\n")
    file.write(f"RMSE: {test_rmse:.4f}\n")
    file.write(f"R2: {test_r2:.4f}\n")
    file.write(f"MAPE: {test_mape:.4f}%\n\n")

    file.write("FEATURE IMPORTANCE\n")
    file.write(importance_df.to_string(index=False))


# =============================================================================
# 16. FINAL SUMMARY
# =============================================================================

print("\n" + "=" * 80)
print("MODEL TRAINING COMPLETE")
print("=" * 80)

print("\nFinal Test Performance:")
print(f"MAE:  {test_mae:.2f}")
print(f"RMSE: {test_rmse:.2f}")
print(f"R²:   {test_r2:.4f}")
print(f"MAPE: {test_mape:.2f}%")

print("\nSaved files:")
print(f"- {MODEL_PATH}")
print(f"- {RESULTS_PATH}")

print("\nNext step:")
print("Analyze model performance and compare predicted prices")
print("with actual freight prices.")

print("=" * 80)
