import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. 슬라이딩 윈도우 크기 10 설정 후, 평균 아래 값들을 직전 5개 데이터 중 최대값으로 대체
# 2. z-score 이상치 탐지 기법 적용(threshold = 2)
#   이상치 식별 시 직전 3개 데이터 중 최대값으로 대체
# 3. data smoothing 적용

def replace_outliers_zscore(df, column, threshold=2):
    """Replace outliers based on the Z-Score method with the maximum of the last 3 values."""
    mean = df[column].mean()
    std = df[column].std()
    df['z_score'] = (df[column] - mean) / std

    # Iterate through the dataframe and replace outliers with the maximum of the last 3 values
    for i in range(len(df)):
        if np.abs(df.loc[i, 'z_score']) > threshold:
            # Find the maximum of the last 3 values, ensuring not to go out of bounds
            if i >= 3:
                df.loc[i, column] = df.loc[i-3:i-1, column].max()
            else:
                df.loc[i, column] = df.loc[0:i, column].max()
    
    # Drop the z_score column as it's no longer needed
    df = df.drop(columns=['z_score'])
    return df

def main():
    # Load the CSV file
    file_path = './dataset/전기전도도_유입압력_10분간격_1주일.csv'
    data = pd.read_csv(file_path)
    
    # Convert 'Time' column to datetime for easier manipulation
    data['Time'] = pd.to_datetime(data['Time'])
    
    # Create a copy of the original feed pressure data for visualization
    data['original_feed_pressure'] = data['feed_pressure']
    
    # Create a rolling window of size 10 and calculate the average
    data['rolling_mean'] = data['feed_pressure'].rolling(window=10).mean()

    # Replace values below the rolling mean with the maximum of the last 5 values
    for i in range(len(data)):
        if data.loc[i, 'feed_pressure'] < data.loc[i, 'rolling_mean']:
            data.loc[i, 'feed_pressure'] = data.loc[max(0, i-5):i, 'feed_pressure'].max()

    # Replace Z-Score-based outliers with the maximum of the last 3 values
    data_cleaned = replace_outliers_zscore(data, 'feed_pressure', threshold=2)
    
    # Apply smoothing using a rolling mean with a window size of 5 for further smoothing
    data_cleaned['smoothed_feed_pressure'] = data_cleaned['feed_pressure'].rolling(window=5, min_periods=1).mean()

    # Save the preprocessed data to a new CSV file
    data_cleaned.to_csv('전처리된_전기전도도_유입압력_10분간격_1주일.csv', index=False)

    # Plot the original, modified, and smoothed data
    plt.figure(figsize=(14, 7))
    plt.plot(data_cleaned['Time'], data_cleaned['original_feed_pressure'], label='Original Feed Pressure', color='red', alpha=0.5)
    plt.plot(data_cleaned['Time'], data_cleaned['feed_pressure'], label='Modified Feed Pressure', color='orange', alpha=0.6)
    plt.plot(data_cleaned['Time'], data_cleaned['smoothed_feed_pressure'], label='Smoothed Feed Pressure', color='blue', alpha=0.8)
    
    plt.xlabel('Time')
    plt.ylabel('Feed Pressure')
    plt.title('Feed Pressure with Original, Modified, and Smoothed Data')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
