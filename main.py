import pandas as pd
import glob
import matplotlib.pyplot as plt

def load_traffic_data(file_pattern):
    all_data = []
    for file in glob.glob(file_pattern):
        if file.endswith('.csv') or file.endswith('.txt'):
            df = pd.read_csv(file) if file.endswith('.csv') else pd.read_csv(file, sep='\t')
            all_data.append(df)
    return pd.concat(all_data, ignore_index=True)

def preprocess_data(df):
    df['StartSession'] = pd.to_datetime(df['StartSession'], errors='coerce')
    df['EndSession'] = pd.to_datetime(df['EndSession'], errors='coerce')
    
    # Обработка ошибок
    df['Duration'] = pd.to_timedelta(df['Duartion'], errors='coerce')
    
    # Убедимся, что UpTx и DownTx являются числовыми
    df['UpTx'] = pd.to_numeric(df['UpTx'], errors='coerce')
    df['DownTx'] = pd.to_numeric(df['DownTx'], errors='coerce')
    
    return df

def plot_traffic(df):
    df_grouped = df.groupby(df['StartSession'].dt.date).agg({'UpTx': 'sum', 'DownTx': 'sum'}).reset_index()

    plt.figure(figsize=(12, 6))
    plt.plot(df_grouped['StartSession'], df_grouped['UpTx'], label='Upload Traffic', marker='o')
    plt.plot(df_grouped['StartSession'], df_grouped['DownTx'], label='Download Traffic', marker='o')
    plt.title('Traffic Dynamics')
    plt.xlabel('Date')
    plt.ylabel('Traffic (bytes)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

file_pattern = 'telecom10k/*'  # Укажите путь к вашим файлам
traffic_data = load_traffic_data(file_pattern)
cleaned_data = preprocess_data(traffic_data)
plot_traffic(cleaned_data)
