
# =============================================================================
# FREIGHT FORECASTING MODEL - PERFORMANCE EVALUATION
# =============================================================================
#
# Purpose:
#   Evaluate the trained Random Forest freight forecasting model.
#
# Input:
#   data/processed/training/test.parquet
#   models/freight_random_forest.pkl
#
# Output:
#   - Actual vs Predicted comparison
#   - Error analysis
#   - Worst predictions
#   - Year-wise performance
#   - Volatility/error analysis
#   - Feature importance
#   - Evaluation report
#
# =============================================================================

import os
# import pickle
import joblib
import numpy as np
import pandas as pd


# =============================================================================
# PATH CONFIGURATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEST_DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "training",
    "test.parquet"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "freight_random_forest.pkl"
)

RESULTS_PATH = os.path.join(
    BASE_DIR,
    "models",
    "model_evaluation_report.txt"
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_metrics(actual, predicted):
    """
    Calculate common regression evaluation metrics.
    """

    actual = np.asarray(actual)
    predicted = np.asarray(predicted)

    errors = actual - predicted

    mae = np.mean(np.abs(errors))

    rmse = np.sqrt(np.mean(errors ** 2))

    ss_res = np.sum(errors ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)

    r2 = 1 - (ss_res / ss_tot)

    # Avoid division by zero
    non_zero_actual = actual != 0

    mape = np.mean(
        np.abs(
            (actual[non_zero_actual] - predicted[non_zero_actual])
            / actual[non_zero_actual]
        )
    ) * 100

    return mae, rmse, r2, mape


def print_separator():
    print("=" * 80)


# =============================================================================
# MAIN PROGRAM
# =============================================================================

def main():

    print_separator()
    print("FREIGHT FORECASTING MODEL EVALUATION")
    print_separator()

    # =========================================================================
    # 1. CHECK FILES
    # =========================================================================

    print("\nChecking required files...")

    if not os.path.exists(TEST_DATA_PATH):
        print("\nERROR: Test dataset not found.")
        print(TEST_DATA_PATH)
        return

    if not os.path.exists(MODEL_PATH):
        print("\nERROR: Trained model not found.")
        print(MODEL_PATH)
        return

    print("Test dataset found.")
    print("Model found.")

    # =========================================================================
    # 2. LOAD TEST DATA
    # =========================================================================

    print("\n" + "=" * 80)
    print("1. LOADING TEST DATA")
    print("=" * 80)

    test_df = pd.read_parquet(TEST_DATA_PATH)

    print(f"Test dataset shape: {test_df.shape}")

    print("\nTest columns:")
    for column in test_df.columns:
        print(f"- {column}")

    # =========================================================================
    # 3. LOAD MODEL
    # =========================================================================

    print("\n" + "=" * 80)
    print("2. LOADING TRAINED MODEL")
    print("=" * 80)

    # with open(MODEL_PATH, "rb") as file:
    #     model = pickle.load(file)
    model = joblib.load(MODEL_PATH)

    print("Random Forest model loaded successfully.")

    # =========================================================================
    # 4. IDENTIFY FEATURES AND TARGET
    # =========================================================================

    print("\n" + "=" * 80)
    print("3. PREPARING TEST DATA")
    print("=" * 80)

    target_column = "Target_Price"

    if target_column not in test_df.columns:
        print(f"\nERROR: {target_column} not found in test dataset.")
        return

    # Date is not used as a direct model feature.
    # Target_Price is the value we are trying to predict.

    feature_columns = [
        column
        for column in test_df.columns
        if column not in ["Date", target_column]
    ]

    X_test = test_df[feature_columns]
    y_test = test_df[target_column]

    print(f"Number of features: {len(feature_columns)}")
    print(f"Number of test samples: {len(X_test)}")

    print("\nFeatures used:")
    for feature in feature_columns:
        print(f"- {feature}")

    # =========================================================================
    # 5. GENERATE PREDICTIONS
    # =========================================================================

    print("\n" + "=" * 80)
    print("4. GENERATING TEST PREDICTIONS")
    print("=" * 80)

    predictions = model.predict(X_test)

    print("Predictions generated successfully.")

    # =========================================================================
    # 6. CALCULATE OVERALL METRICS
    # =========================================================================

    print("\n" + "=" * 80)
    print("5. OVERALL MODEL PERFORMANCE")
    print("=" * 80)

    mae, rmse, r2, mape = calculate_metrics(
        y_test.values,
        predictions
    )

    print(f"\nMAE :  {mae:.2f}")
    print(f"RMSE:  {rmse:.2f}")
    print(f"R²  :  {r2:.4f}")
    print(f"MAPE:  {mape:.2f}%")

    # =========================================================================
    # 7. CREATE PREDICTION DATAFRAME
    # =========================================================================

    results_df = pd.DataFrame({
        "Date": test_df["Date"].values,
        "Actual_Price": y_test.values,
        "Predicted_Price": predictions
    })

    results_df["Error"] = (
        results_df["Actual_Price"]
        - results_df["Predicted_Price"]
    )

    results_df["Absolute_Error"] = (
        results_df["Error"].abs()
    )

    results_df["Percentage_Error"] = (
        results_df["Absolute_Error"]
        / results_df["Actual_Price"].replace(0, np.nan)
    ) * 100

    # =========================================================================
    # 8. SAMPLE PREDICTIONS
    # =========================================================================

    print("\n" + "=" * 80)
    print("6. SAMPLE PREDICTIONS")
    print("=" * 80)

    sample_predictions = results_df.head(10).copy()

    print("\nFirst 10 predictions:")

    print(
        sample_predictions[
            [
                "Date",
                "Actual_Price",
                "Predicted_Price",
                "Error"
            ]
        ].to_string(index=False)
    )

    # =========================================================================
    # 9. BEST PREDICTIONS
    # =========================================================================

    print("\n" + "=" * 80)
    print("7. MOST ACCURATE PREDICTIONS")
    print("=" * 80)

    best_predictions = (
        results_df
        .sort_values("Absolute_Error")
        .head(10)
    )

    print("\n10 predictions with the smallest absolute error:")

    print(
        best_predictions[
            [
                "Date",
                "Actual_Price",
                "Predicted_Price",
                "Error",
                "Absolute_Error"
            ]
        ].to_string(index=False)
    )

    # =========================================================================
    # 10. WORST PREDICTIONS
    # =========================================================================

    print("\n" + "=" * 80)
    print("8. WORST PREDICTIONS")
    print("=" * 80)

    worst_predictions = (
        results_df
        .sort_values("Absolute_Error", ascending=False)
        .head(10)
    )

    print("\n10 predictions with the largest absolute error:")

    print(
        worst_predictions[
            [
                "Date",
                "Actual_Price",
                "Predicted_Price",
                "Error",
                "Absolute_Error",
                "Percentage_Error"
            ]
        ].to_string(index=False)
    )

    # =========================================================================
    # 11. ERROR DISTRIBUTION
    # =========================================================================

    print("\n" + "=" * 80)
    print("9. ERROR DISTRIBUTION")
    print("=" * 80)

    print(
        f"\nAverage Error: "
        f"{results_df['Error'].mean():.2f}"
    )

    print(
        f"Median Error: "
        f"{results_df['Error'].median():.2f}"
    )

    print(
        f"Minimum Error: "
        f"{results_df['Error'].min():.2f}"
    )

    print(
        f"Maximum Error: "
        f"{results_df['Error'].max():.2f}"
    )

    print(
        f"Average Absolute Error: "
        f"{results_df['Absolute_Error'].mean():.2f}"
    )

    # =========================================================================
    # 12. ERROR RANGES
    # =========================================================================

    print("\n" + "=" * 80)
    print("10. PREDICTION ERROR RANGES")
    print("=" * 80)

    total_predictions = len(results_df)

    within_25 = (
        results_df["Absolute_Error"] <= 25
    ).sum()

    within_50 = (
        results_df["Absolute_Error"] <= 50
    ).sum()

    within_100 = (
        results_df["Absolute_Error"] <= 100
    ).sum()

    print(
        f"\nPredictions within ±25 price units : "
        f"{within_25} / {total_predictions} "
        f"({within_25 / total_predictions * 100:.2f}%)"
    )

    print(
        f"Predictions within ±50 price units : "
        f"{within_50} / {total_predictions} "
        f"({within_50 / total_predictions * 100:.2f}%)"
    )

    print(
        f"Predictions within ±100 price units: "
        f"{within_100} / {total_predictions} "
        f"({within_100 / total_predictions * 100:.2f}%)"
    )

    # =========================================================================
    # 13. YEAR-WISE PERFORMANCE
    # =========================================================================

    print("\n" + "=" * 80)
    print("11. YEAR-WISE MODEL PERFORMANCE")
    print("=" * 80)

    results_df["Year"] = pd.to_datetime(
        results_df["Date"]
    ).dt.year

    yearly_results = []

    for year, group in results_df.groupby("Year"):

        year_mae, year_rmse, year_r2, year_mape = calculate_metrics(
            group["Actual_Price"].values,
            group["Predicted_Price"].values
        )

        yearly_results.append({
            "Year": year,
            "Records": len(group),
            "MAE": year_mae,
            "RMSE": year_rmse,
            "R2": year_r2,
            "MAPE": year_mape
        })

    yearly_df = pd.DataFrame(yearly_results)

    print("\n")
    print(
        yearly_df.to_string(
            index=False,
            formatters={
                "MAE": "{:.2f}".format,
                "RMSE": "{:.2f}".format,
                "R2": "{:.4f}".format,
                "MAPE": "{:.2f}%".format
            }
        )
    )

    # =========================================================================
    # 14. VOLATILITY / ERROR ANALYSIS
    # =========================================================================

    print("\n" + "=" * 80)
    print("12. VOLATILITY AND ERROR ANALYSIS")
    print("=" * 80)

    # Volatility_7 exists in the original test dataset.
    if "Volatility_7" in test_df.columns:

        results_df["Volatility_7"] = (
            test_df["Volatility_7"].values
        )

        # Remove missing volatility values
        volatility_df = results_df.dropna(
            subset=["Volatility_7"]
        ).copy()

        if len(volatility_df) > 0:

            median_volatility = (
                volatility_df["Volatility_7"].median()
            )

            low_volatility = volatility_df[
                volatility_df["Volatility_7"]
                <= median_volatility
            ]

            high_volatility = volatility_df[
                volatility_df["Volatility_7"]
                > median_volatility
            ]

            print(
                f"\nMedian 7-day volatility: "
                f"{median_volatility:.2f}"
            )

            if len(low_volatility) > 0:
                low_mae = low_volatility[
                    "Absolute_Error"
                ].mean()

                print(
                    f"Low-volatility average error: "
                    f"{low_mae:.2f}"
                )

            if len(high_volatility) > 0:
                high_mae = high_volatility[
                    "Absolute_Error"
                ].mean()

                print(
                    f"High-volatility average error: "
                    f"{high_mae:.2f}"
                )

            if (
                len(low_volatility) > 0
                and len(high_volatility) > 0
            ):
                print("\nInterpretation:")

                if high_mae > low_mae:
                    print(
                        "The model has larger errors during "
                        "higher-volatility periods."
                    )
                else:
                    print(
                        "The model does not show larger average "
                        "errors during higher-volatility periods."
                    )

    else:
        print("\nVolatility_7 feature not available.")

    # =========================================================================
    # 15. FEATURE IMPORTANCE
    # =========================================================================

    print("\n" + "=" * 80)
    print("13. FEATURE IMPORTANCE")
    print("=" * 80)

    if hasattr(model, "feature_importances_"):

        importance_df = pd.DataFrame({
            "Feature": feature_columns,
            "Importance": model.feature_importances_
        })

        importance_df = (
            importance_df
            .sort_values(
                "Importance",
                ascending=False
            )
            .reset_index(drop=True)
        )

        print("\nFeature importance ranking:")

        print(
            importance_df.head(15).to_string(
                index=False,
                formatters={
                    "Importance": "{:.6f}".format
                }
            )
        )

    else:
        importance_df = pd.DataFrame()

        print(
            "\nFeature importance is not available "
            "for this model."
        )

    # =========================================================================
    # 16. CURRENT PRICE VS PREDICTION
    # =========================================================================

    print("\n" + "=" * 80)
    print("14. CURRENT PRICE VS NEXT-DAY PREDICTION")
    print("=" * 80)

    if "Price" in test_df.columns:

        latest_row = test_df.iloc[-1]

        latest_features = test_df[
            feature_columns
        ].iloc[[-1]]

        next_prediction = model.predict(
            latest_features
        )[0]

        current_price = latest_row["Price"]

        difference = next_prediction - current_price

        percentage_difference = (
            difference / current_price
        ) * 100

        print(
            f"\nLatest available date: "
            f"{latest_row['Date']}"
        )

        print(
            f"Latest actual price: "
            f"{current_price:.2f}"
        )

        print(
            f"Predicted next-day price: "
            f"{next_prediction:.2f}"
        )

        print(
            f"Expected change: "
            f"{difference:.2f}"
        )

        print(
            f"Expected percentage change: "
            f"{percentage_difference:.2f}%"
        )

    # =========================================================================
    # 17. MODEL INTERPRETATION
    # =========================================================================

    print("\n" + "=" * 80)
    print("15. MODEL INTERPRETATION")
    print("=" * 80)

    print("\nOverall interpretation:")

    if mape < 5:
        print(
            f"- MAPE of {mape:.2f}% indicates very low "
            "average percentage prediction error."
        )
    elif mape < 10:
        print(
            f"- MAPE of {mape:.2f}% indicates good "
            "prediction accuracy."
        )
    else:
        print(
            f"- MAPE of {mape:.2f}% indicates the model "
            "has room for improvement."
        )

    if r2 >= 0.90:
        print(
            f"- R² of {r2:.4f} indicates that the model "
            "explains most of the variation in the test prices."
        )
    elif r2 >= 0.70:
        print(
            f"- R² of {r2:.4f} indicates a reasonably "
            "strong relationship between predictions and actual prices."
        )
    else:
        print(
            f"- R² of {r2:.4f} indicates that the model "
            "has significant unexplained variation."
        )

    print(
        f"- The model's average absolute prediction error "
        f"is {mae:.2f} price units."
    )

    # =========================================================================
    # 18. SAVE DETAILED REPORT
    # =========================================================================

    print("\n" + "=" * 80)
    print("16. SAVING EVALUATION REPORT")
    print("=" * 80)

    report_lines = []

    report_lines.append(
        "FREIGHT FORECASTING MODEL EVALUATION REPORT"
    )
    report_lines.append("=" * 80)

    report_lines.append(
        "\nMODEL"
    )
    report_lines.append(
        "Algorithm: Random Forest Regression"
    )

    report_lines.append(
        "\nDATASET"
    )
    report_lines.append(
        f"Test samples: {len(test_df)}"
    )
    report_lines.append(
        f"Test start: {test_df['Date'].min()}"
    )
    report_lines.append(
        f"Test end: {test_df['Date'].max()}"
    )

    report_lines.append(
        "\nOVERALL PERFORMANCE"
    )
    report_lines.append(
        f"MAE:  {mae:.2f}"
    )
    report_lines.append(
        f"RMSE: {rmse:.2f}"
    )
    report_lines.append(
        f"R²:   {r2:.4f}"
    )
    report_lines.append(
        f"MAPE: {mape:.2f}%"
    )

    report_lines.append(
        "\nPREDICTION ACCURACY"
    )
    report_lines.append(
        f"Within ±25 units: "
        f"{within_25 / total_predictions * 100:.2f}%"
    )
    report_lines.append(
        f"Within ±50 units: "
        f"{within_50 / total_predictions * 100:.2f}%"
    )
    report_lines.append(
        f"Within ±100 units: "
        f"{within_100 / total_predictions * 100:.2f}%"
    )

    report_lines.append(
        "\nYEAR-WISE PERFORMANCE"
    )

    for _, row in yearly_df.iterrows():

        report_lines.append(
            f"{int(row['Year'])}: "
            f"MAE={row['MAE']:.2f}, "
            f"RMSE={row['RMSE']:.2f}, "
            f"R²={row['R2']:.4f}, "
            f"MAPE={row['MAPE']:.2f}%"
        )

    report_lines.append(
        "\nTOP FEATURE IMPORTANCE"
    )

    if not importance_df.empty:

        for _, row in importance_df.head(10).iterrows():

            report_lines.append(
                f"{row['Feature']}: "
                f"{row['Importance']:.6f}"
            )

    report_lines.append(
        "\nMODEL INTERPRETATION"
    )

    report_lines.append(
        f"The Random Forest model achieved a test MAE "
        f"of {mae:.2f}."
    )

    report_lines.append(
        f"The test RMSE was {rmse:.2f}."
    )

    report_lines.append(
        f"The test R² score was {r2:.4f}."
    )

    report_lines.append(
        f"The test MAPE was {mape:.2f}%."
    )

    report_lines.append(
        "\nThis evaluation represents the baseline "
        "performance of the current freight forecasting model."
    )

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n".join(report_lines)
        )

    print(
        f"\nEvaluation report saved to:"
    )

    print(RESULTS_PATH)

    # =========================================================================
    # 19. SAVE PREDICTIONS
    # =========================================================================

    predictions_path = os.path.join(
        BASE_DIR,
        "data",
        "processed",
        "freight_predictions.csv"
    )

    results_df.to_csv(
        predictions_path,
        index=False
    )

    print(
        "\nPredictions saved to:"
    )

    print(predictions_path)

    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================

    print("\n")
    print_separator()
    print("MODEL EVALUATION COMPLETE")
    print_separator()

    print("\nFinal Test Performance:")
    print(f"MAE :  {mae:.2f}")
    print(f"RMSE:  {rmse:.2f}")
    print(f"R²  :  {r2:.4f}")
    print(f"MAPE:  {mape:.2f}%")

    print("\nGenerated files:")
    print(f"- {RESULTS_PATH}")
    print(f"- {predictions_path}")

    print("\nNext step:")
    print(
        "Use the evaluation results to validate the model "
        "and then build the freight forecasting prediction pipeline."
    )

    print_separator()


# =============================================================================
# PROGRAM ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
