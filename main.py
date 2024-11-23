import pandas
import pandas as pd
import glob
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)


def getTimestampFileName(file):
    return (file.split(' ')[0].split('-')[0][-4:]+'-'+file.split(' ')[0].split('-')[1]+'-'+file.split(' ')[0].split('-')[2]\
              +' '+file.split(' ')[1].split('')[0]+':'+file.split(' ')[1].split('')[1]+':'+file.split(' ')[1].split('')[2][:2])
# Функция для обработки файлов
def process_files(file_pattern):
    # Получаем список всех файлов по заданному шаблону
    files = glob.glob(file_pattern)
    if not files:
        print("No files found.")
        return None
    dataframes = []
    hourdf = []
    startPeriod = ''
    #endPeriod = ''
    j = 0
#    for i in range(len(files)):
    for i in range(50):
        file = files[i]
        if j == 0:
            startPeriod = pd.to_datetime(getTimestampFileName(file)) - pd.Timedelta(minutes=10)
            #endPeriod = startPeriod + pd.Timedelta(hours=1)
        # Определяем формат файла и загружаем данные
        try:
            if file.endswith('.csv'):
                df = pd.read_csv(file)

            elif file.endswith('.txt'):
                df = pd.read_csv(file, delimiter='|')
            else:
                continue

            # Преобразуем время в datetime и создаем нужные столбцы

            df['StartSession'] = pd.to_datetime(df['StartSession'], dayfirst=True)
            df['EndSession'] = pd.to_datetime(df['EndSession'], dayfirst=True)
            #df['Start10mPeriod'] = df['StartSession'].replace(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', scanStart,  regex=True)
            df['Start1hPeriod'] = startPeriod
            df['Start10mPeriod'] = startPeriod + pd.Timedelta(minutes=10*j)
            #df['Start1hPeriod'] = pd.to_datetime(df['Start10mPeriod'], dayfirst=True)
            #df['End10mPeriod'] = df['EndSession'].fillna(getTimestampFileName(files[i+1]) if len(files) > i+1 else float('nan'))
            #df['End1hPeriod'] = endPeriod
            # df=df.groupby("IdSubscriber").agg({
            #     'UpTx': lambda x: sum(x),
            #     'DownTx': lambda x: sum(x),
            #     'StartSession': lambda x: min(x),
            #     'EndSession': lambda x: max(x)
            # }).reset_index()



            df['Traffic'] = df['UpTx'] + df['DownTx']  # Общий трафик в байтах

            # Добавляем DataFrame в список
            hourdf.append(df)
            j += 1
            if j == 6 or len(files) - 1 == i:
                #print(hourdf[-1].head(10))
                dataframes.append(pd.concat(hourdf, ignore_index=True))
                hourdf=[]
                j = 0
            #dataframes.append(df)
        except (TypeError, ValueError) as e:
            print(f"Error processing {file}: {e}")
    #print(pd.concat(dataframes, ignore_index=True).head(10))
    #print(dataframes[1])
    return pd.concat(dataframes, ignore_index=True) if dataframes else None
    #return dataframes

# Функция для построения графика
def plot_traffic(data):
    if data is None or data.empty:
        print("No data to plot.")
        return

    # Группируем данные по часу и суммируем трафик
    data.set_index('Start1hPeriod', inplace=True)
    hourly_traffic = data['Traffic'].resample('H').sum().reset_index()
    
    # Преобразуем время в секунды
    hourly_traffic['TimeInSeconds'] = (hourly_traffic['Start1hPeriod'] - hourly_traffic['Start1hPeriod'].min()).dt.total_seconds()
    
    # Построение графика
    plt.figure(figsize=(12, 6))
    plt.plot(hourly_traffic['TimeInSeconds'], hourly_traffic['Traffic'], marker='o')
    plt.title('Traffic Dynamics Over Time')
    plt.xlabel('Time in Seconds')
    plt.ylabel('Traffic (Bytes)')
    plt.grid()
    plt.show()

def plot_subscriber_traffic(data, idSubscriber):
    hoursN = len(data)
    #print(hoursN)
    #subdf = []
    # for i in range(hoursN):
    #     d = data[i].where(data[i]['IdSubscriber']==idSubscriber)
    #     d = d.dropna(axis=0, how='all')
    #     if len(d) > 0:
    #         #subdf.append(d)
    #subdf = pd.concat(subdf, ignore_index=True)
    d = data.where(data['IdSubscriber'] == idSubscriber)
    d = d.dropna(axis=0, how='all')
    plot_traffic(d)

def plot_all_subscribers(data):
    if data is None or data.empty:
        print("No data to plot.")
        return
    subscribers = data['IdSubscriber'].unique()
    plt.figure(figsize=(12, 6))
    for s in subscribers:
        df = data.where(data['IdSubscriber'] == s)
        # Группируем данные по часу и суммируем трафик
        df.set_index('Start1hPeriod', inplace=True)
        hourly_traffic = df['Traffic'].resample('H').sum().reset_index()

        # Преобразуем время в секунды
        hourly_traffic['TimeInSeconds'] = (
                    hourly_traffic['Start1hPeriod'] - hourly_traffic['Start1hPeriod'].min()).dt.total_seconds()
        # Построение графика

        plt.plot(hourly_traffic['TimeInSeconds'], hourly_traffic['Traffic'], marker='o')
    plt.title('Traffic Dynamics Over Time')
    plt.xlabel('Time in Seconds')
    plt.ylabel('Traffic (Bytes)')
    plt.grid()
    plt.show()

#new_df = df.where(df['age'] > 30)

# Основная часть программы
if __name__ == "__main__":
    # Путь к файлам (измените при необходимости)
    file_pattern = 'telecom10k/*'
    
    # Обработка файлов и построение графика
    traffic_data = process_files(file_pattern)
    #plot_subscriber_traffic(traffic_data, 4187)
    #plot_subscriber_traffic(traffic_data, 7560)
    #plot_traffic(traffic_data)
    plot_all_subscribers(traffic_data)
