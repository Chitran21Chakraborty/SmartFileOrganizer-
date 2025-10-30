import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np

def scan_directory(base_path):
    """Scans directory and returns a DataFrame with file info."""
    data = []
    for root, dirs, files in os.walk(base_path):
        for f in files:
            try:
                path = os.path.join(root, f)
                size = os.path.getsize(path) / (1024 * 1024)  # MB
                ext = os.path.splitext(f)[1].lower()
                created = datetime.fromtimestamp(os.path.getctime(path))
                data.append([f, path, size, ext, created])
            except Exception:
                continue
    df = pd.DataFrame(data, columns=["Name", "Path", "Size_MB", "Extension", "Created_At"])
    return df

def get_file_type_distribution(df):
    return df['Extension'].value_counts()

def get_folder_size_distribution(df):
    df['Folder'] = df['Path'].apply(lambda x: os.path.dirname(x))
    return df.groupby('Folder')['Size_MB'].sum().sort_values(ascending=False)

def get_file_growth_over_time(df):
    df['Month'] = df['Created_At'].dt.to_period('M')
    return df.groupby('Month').size()

def forecast_storage_growth(df):
    """Predicts future file growth (simple linear regression)."""
    df['Timestamp'] = df['Created_At'].map(datetime.timestamp)
    monthly = df.groupby(df['Created_At'].dt.to_period('M')).size().reset_index(name='Count')
    monthly['MonthNum'] = np.arange(len(monthly))
    model = LinearRegression()
    model.fit(monthly[['MonthNum']], monthly['Count'])
    future = np.arange(len(monthly), len(monthly) + 3)
    prediction = model.predict(future.reshape(-1, 1))
    return monthly, prediction
