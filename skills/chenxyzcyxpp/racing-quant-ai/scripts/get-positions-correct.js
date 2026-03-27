const mysql = require('mysql2');

// 数据库连接配置
const dbConfig = {
  host: '47.121.180.199',
  port: 3306,
  user: 'display',
  password: 'display999!',
  database: 'db_strategy'
};

function getLatestPositions(tableName, limit = 20) {
  return new Promise((resolve, reject) => {
    const connection = mysql.createConnection(dbConfig);
    connection.connect((err) => {
      if (err) {
        reject(err);
        connection.end();
        return;
      }
      // 获取最新一期日期
      const dateQuery = `SELECT DISTINCT trade_date FROM ${tableName} ORDER BY trade_date DESC LIMIT 1`;
      connection.query(dateQuery, (err, dateResults) => {
        if (err) {
          reject(err);
          connection.end();
          return;
        }
        if (dateResults.length === 0) {
          resolve({ latestDate: null, positions: [] });
          connection.end();
          return;
        }
        const latestDate = dateResults[0].trade_date;
        // 获取最新一期持仓
        const posQuery = `SELECT trading_info FROM ${tableName} WHERE trade_date = ?`;
        connection.query(posQuery, [latestDate], (err, posResults) => {
          if (err) {
            reject(err);
            connection.end();
            return;
          }
          if (posResults.length === 0) {
            resolve({ latestDate, positions: [] });
            connection.end();
            return;
          }
          // 转成数组: {code: weight} -> [{code, weight}]
          const tradingInfo = posResults[0].trading_info;
          const positions = Object.entries(tradingInfo)
            .map(([code, weight]) => ({ stock_code: code, weight: Number(weight) }))
            .sort((a, b) => b.weight - a.weight)
            .slice(0, limit);
          resolve({
            latestDate,
            positions
          });
          connection.end();
        });
      });
    });
  });
}

// 获取短周期机器学习趋势增强版的持仓
const tableName = 'strategy_train4pdtlag1wadj_stgml0002';
getLatestPositions(tableName, 20)
  .then(result => {
    console.log(`📊 策略: 短周期机器学习趋势增强版`);
    console.log(`📅 最新持仓日期: ${result.latestDate}\n`);
    console.log(`全部持仓 (共 ${result.positions.length} 只，等权重配置):\n`);
    result.positions.forEach((pos, i) => {
      console.log(`${String(i+1).padStart(2)}. ${pos.stock_code} - 权重: ${(pos.weight * 100).toFixed(2)}%`);
    });
  })
  .catch(err => {
    console.error('错误:', err);
  });
