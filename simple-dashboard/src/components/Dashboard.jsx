import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const [chartData, setChartData] = useState({ normal: [], anomalous: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/anomalies')
      .then(response => response.json())
      .then(data => {
        // Группируем данные по пользователям
        const userTraffic = data.reduce((acc, item) => {
          if (!acc[item.IdSubscriber]) {
            acc[item.IdSubscriber] = [];
          }
          acc[item.IdSubscriber].push({
            time: new Date(item.Start10mPeriod),
            uploadGB: item.UpTx / (1024 * 1024 * 1024),
            downloadGB: item.DownTx / (1024 * 1024 * 1024),
            totalTraffic: (item.UpTx + item.DownTx) / (1024 * 1024 * 1024)
          });
          return acc;
        }, {});

        // Анализируем резкие изменения трафика для каждого пользователя
        const userStats = Object.entries(userTraffic).map(([userId, traffic]) => {
          const sorted = traffic.sort((a, b) => a.time - b.time);
          
          // Ищем резкие скачки в трафике
          let maxJump = 0;
          let avgTraffic = 0;
          let trafficSpikes = 0;
          
          for (let i = 1; i < sorted.length; i++) {
            const prevTotal = sorted[i-1].totalTraffic;
            const currentTotal = sorted[i].totalTraffic;
            const jump = currentTotal / (prevTotal || 1); // Во сколько раз изменился трафик
            maxJump = Math.max(maxJump, jump);
            
            // Если трафик вырос более чем в 5 раз - считаем это резким скачком
            if (jump > 5) {
              trafficSpikes++;
            }
            
            avgTraffic += currentTotal;
          }
          avgTraffic /= sorted.length;
          
          return {
            userId,
            traffic: sorted,
            maxJump,
            trafficSpikes,
            avgTraffic,
            dataPoints: traffic.length
          };
        });

        // Фильтруем пользователей с достаточным количеством данных
        const validUsers = userStats.filter(user => user.dataPoints >= 5);

        // Находим пользователя с самым резким скачком трафика
        const anomalousUser = validUsers
          .sort((a, b) => b.maxJump - a.maxJump)[0];

        // Находим пользователя со стабильным трафиком
        const normalUser = validUsers
          .filter(user => 
            user.userId !== anomalousUser.userId && 
            user.maxJump < 2 && // Изменения трафика не более чем в 2 раза
            user.trafficSpikes === 0 // Нет резких скачков
          )
          .sort((a, b) => a.maxJump - b.maxJump)[0];

        setChartData({
          normal: normalUser.traffic.map(t => ({
            time: t.time.toLocaleTimeString(),
            upload: t.uploadGB,
            download: t.downloadGB
          })),
          anomalous: anomalousUser.traffic.map(t => ({
            time: t.time.toLocaleTimeString(),
            upload: t.uploadGB,
            download: t.downloadGB
          })),
          normalUserId: normalUser.userId,
          anomalousUserId: anomalousUser.userId,
          normalMaxJump: normalUser.maxJump.toFixed(1),
          anomalousMaxJump: anomalousUser.maxJump.toFixed(1)
        });
        setLoading(false);
      })
      .catch(error => {
        console.error('Error:', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div style={{ padding: '20px', color: '#333' }}>Загрузка данных...</div>;
  }

  return (
    <div style={{ 
      width: '1200px', 
      padding: '20px', 
      margin: '20px auto',
      background: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <h2 style={{ 
        color: '#333', 
        marginBottom: '20px', 
        textAlign: 'center' 
      }}>
        Сравнение нормального и аномального трафика
      </h2>
      
      <div style={{ 
        marginBottom: '20px',
        padding: '10px',
        background: '#f5f5f5',
        borderRadius: '4px'
      }}>
        <div>Нормальный трафик: Пользователь ID {chartData.normalUserId} (макс. изменение в {chartData.normalMaxJump} раз)</div>
        <div>Аномальный трафик: Пользователь ID {chartData.anomalousUserId} (макс. изменение в {chartData.anomalousMaxJump} раз)</div>
      </div>

      <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
        {/* График нормального трафика */}
        <div style={{ flex: 1, height: '400px', background: '#f8f9fa', padding: '20px', borderRadius: '8px' }}>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>Нормальный трафик</h3>
          <ResponsiveContainer>
            <LineChart data={chartData.normal}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="time"
                tick={{ fill: '#333' }}
              />
              <YAxis 
                tick={{ fill: '#333' }}
                label={{ 
                  value: 'Трафик (GB)', 
                  angle: -90, 
                  position: 'insideLeft',
                  fill: '#333'
                }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #ccc'
                }}
                formatter={(value) => `${value.toFixed(2)} GB`}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="upload"
                name="Выгрузка"
                stroke="#2196F3"
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
              <Line
                type="monotone"
                dataKey="download"
                name="Скачивание"
                stroke="#4CAF50"
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* График аномального трафика */}
        <div style={{ flex: 1, height: '400px', background: '#f8f9fa', padding: '20px', borderRadius: '8px' }}>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>Аномальный трафик</h3>
          <ResponsiveContainer>
            <LineChart data={chartData.anomalous}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="time"
                tick={{ fill: '#333' }}
              />
              <YAxis 
                tick={{ fill: '#333' }}
                label={{ 
                  value: 'Трафик (GB)', 
                  angle: -90, 
                  position: 'insideLeft',
                  fill: '#333'
                }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #ccc'
                }}
                formatter={(value) => `${value.toFixed(2)} GB`}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="upload"
                name="Выгрузка"
                stroke="#F44336"
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
              <Line
                type="monotone"
                dataKey="download"
                name="Скачивание"
                stroke="#FF9800"
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;