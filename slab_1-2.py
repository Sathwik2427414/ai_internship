import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np
import os

try:
    import kaggle
except ImportError:
    print("Kaggle API not found. Please install it using 'pip install kaggle' and configure your API key.")
    print("Refer to https://www.kaggle.com/docs/api for instructions.")
    exit()

dataset_name = "altruistfv/abr-housing-data"
download_path = "./housing_data"
csv_file_name = "ABR_Housing_Data.csv"

if not os.path.exists(download_path):
    os.makedirs(download_path)

try:
    print(f"Attempting to download dataset: {dataset_name} to {download_path}")
    kaggle.api.dataset_download_files(dataset_name, path=download_path, unzip=True)
    print("Dataset downloaded and unzipped successfully.")
except Exception as e:
    print(f"Error downloading dataset: {e}")
    print("Please ensure you have configured your Kaggle API key correctly.")
    exit()

file_path = os.path.join(download_path, csv_file_name)

try:
    df = pd.read_csv(file_path)
    print("\nCSV file loaded successfully!")
    print("\nFirst 5 rows of the DataFrame:")
    print(df.head())
    print("\nDataFrame Info:")
    df.info()
except FileNotFoundError:
    print(f"Error: The file '{csv_file_name}' was not found in '{download_path}'.")
    exit()
except Exception as e:
    print(f"An error occurred while reading the CSV file: {e}")
    exit()

target_column = 'SalePrice'
if target_column not in df.columns:
    print(f"Error: Target column '{target_column}' not found in the dataset.")
    print("Available columns:", df.columns.tolist())
    exit()

numerical_features = df.select_dtypes(include=np.number).columns.tolist()
numerical_features.remove(target_column)

if 'Id' in numerical_features:
    numerical_features.remove('Id')

categorical_features = df.select_dtypes(include='object').columns.tolist()

for col in numerical_features + categorical_features:
    if df[col].isnull().any():
        if df[col].dtype == 'object':
            df[col].fillna(df[col].mode()[0], inplace=True)
        else:
            df[col].fillna(df[col].median(), inplace=True)

X = df.drop(columns=[target_column])
y = df[target_column]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

model = Pipeline(steps=[('preprocessor', preprocessor),
                        ('regressor', LinearRegression())])

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"\nModel Performance:")
print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
print(f"R-squared (R2): {r2:.2f}")

sample_prediction_df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred}).head(10)
print("\nSample Actual vs. Predicted Prices (First 10):")
print(sample_prediction_df)