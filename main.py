import pandas as pd
import glob
import matplotlib.pyplot as plt

# Функция для обработки файлов
def process_files(file_pattern):
    # Получаем список всех файлов по заданному шаблону
    files = glob.glob(file_pattern)
    if not files:
        print("No files found.")
        return None

    dataframes = []
    
    for file in files:
        # Определяем формат файла и загружаем данные
        try:
            if file.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.endswith('.txt'):
                df = pd.read_csv(file, delimiter='|')
            else:
                continue
            
            # Преобразуем время в datetime и создаем нужные столбцы
            df['StartSession'] = pd.to_datetime(df['StartSession'])
            df['EndSession'] = pd.to_datetime(df['EndSession'])
            df['Traffic'] = df['UpTx'] + df['DownTx']  # Общий трафик в байтах
            
            # Добавляем DataFrame в список
            dataframes.append(df)
        
        except (TypeError, ValueError) as e:
            print(f"Error processing {file}: {e}")
    
    return pd.concat(dataframes, ignore_index=True) if dataframes else None

# Функция для построения графика
def plot_traffic(data):
    if data is None or data.empty:
        print("No data to plot.")
        return

    # Группируем данные по часу и суммируем трафик
    data.set_index('StartSession', inplace=True)
    hourly_traffic = data['Traffic'].resample('H').sum().reset_index()
    
    # Преобразуем время в секунды
    hourly_traffic['TimeInSeconds'] = (hourly_traffic['StartSession'] - hourly_traffic['StartSession'].min()).dt.total_seconds()
    
    # Построение графика
    plt.figure(figsize=(12, 6))
    plt.plot(hourly_traffic['TimeInSeconds'], hourly_traffic['Traffic'], marker='o')
    plt.title('Traffic Dynamics Over Time')
    plt.xlabel('Time in Seconds')
    plt.ylabel('Traffic (Bytes)')
    plt.grid()
    plt.show()

# Основная часть программы
if __name__ == "__main__":
    # Путь к файлам (измените при необходимости)
    file_pattern = 'telecom10k/*'
    
    # Обработка файлов и построение графика
    traffic_data = process_files(file_pattern)
    plot_traffic(traffic_data)
