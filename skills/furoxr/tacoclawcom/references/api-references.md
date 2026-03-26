#### get_kline:
- endpoint: /market/klines
- method: GET
- parameters:
  - query parameters:
    - symbol (required): trading pair symbol, e.g. `BTCUSDT`, `ETHUSDT`
    - interval (required): kline interval. Supported values: `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d`, `3d`, `1w`, `1M`
    - exchange (required): exchange name. Supported values: `Binance`, `Taco`, `Aster`, `Grvt`, `StandX`, `Lighter`
    - start_time (optional): start time in Unix milliseconds. If omitted together with end_time, returns the latest 100 klines.
    - end_time (optional): end time in Unix milliseconds. If omitted together with start_time, returns the latest 100 klines.
- response (example below in json format):
  ```json
  {
    "base_response": {
      "status_code": 200,
      "status_msg": "success",
      "trace_id": "trace tracking id"
    },
    "klines": [
      {
        "symbol": "BTCUSDT",
        "interval": "1h",
        "exchange": "Binance",
        "open_time": 1709251200000,
        "close_time": 1709254800000,
        "open": "62345.50",
        "high": "62890.00",
        "low": "62100.00",
        "close": "62780.30",
        "volume": "1234.567",
        "quote_volume": "77012345.89",
        "trades_count": 45678
      }
    ]
  }
  ```
- notes:
  - Maximum 100 klines per response. If the query range contains more, only the latest 100 are returned.
  - Price and volume fields are returned as strings to preserve decimal precision.


#### open_position
- endpoint: /auth/tacoclaw/trade/open_position
- method: POST
- parameters:
  - query parameters:
     - user_id: tacoclaw user id
  - request body (in json format as below example):
       ```json
       {
         "api_token": "please use taco api key same as authentication bearer token in header",
         "user_id": "same as in query parameter",
         "side": "Short",
         "exchange": "Taco",
         "symbol": "BTCUSDT",
         "notional_position": 100.0,
         "leverage": 3,
         "sl_price": 30000.0,
         "tp_price": 90000.0
       }
       ```

#### close_position
- endpoint: /auth/tacoclaw/trade/close_position
- method: POST
- parameters:
  - query parameters:
     - user_id: tacoclaw user id
  - request body (in json format as below example):
       ```json
       {
         "api_token": "please use taco api key same as authentication bearer token in header",
         "user_id": "same as in query parameter",
         "exchange": "Taco",
         "symbol": "BTCUSDT",
         "notional_position": 100.0,
         "side": "Short"
       }
       ```

#### set_leverage
- endpoint: /auth/tacoclaw/trade/set_leverage
- method: POST
- parameters:
  - query parameters:
     - user_id: tacoclaw user id
  - request body (in json format as below example):
       ```json
       {
         "api_token": "please use taco api key same as authentication bearer token in header",
         "user_id": "same as in query parameter",
         "exchange": "Taco",
         "symbol": "BTCUSDT",
         "leverage": 5
       }
       ```

#### set_margin_mode
- endpoint: /auth/tacoclaw/trade/set_margin_mode
- method: POST
- parameters:
  - query parameters:
     - user_id: tacoclaw user id
  - request body (in json format as below example):
       ```json
       {
         "api_token": "please use taco api key same as authentication bearer token in header",
         "user_id": "same as in query parameter",
         "exchange": "Taco",
         "symbol": "BTCUSDT",
         "is_cross_margin": true
       }
       ```

#### set_stop_loss
- endpoint: /auth/tacoclaw/trade/set_stop_loss
- method: POST
- parameters:
  - query parameters:
     - user_id: tacoclaw user id
  - request body (in json format as below example):
       ```json
       {
         "api_token": "please use taco api key same as authentication bearer token in header",
         "user_id": "same as in query parameter",
         "exchange": "Taco",
         "symbol": "BTCUSDT",
         "side": "Long",
         "notional_position": 100.0,
         "price": 85000.0
       }
       ```

#### set_take_profit
- endpoint: /auth/tacoclaw/trade/set_take_profit
- method: POST
- parameters:
  - query parameters:
     - user_id: tacoclaw user id
  - request body (in json format as below example):
       ```json
       {
         "api_token": "please use taco api key same as authentication bearer token in header",
         "user_id": "same as in query parameter",
         "exchange": "Taco",
         "symbol": "BTCUSDT",
         "side": "Long",
         "notional_position": 100.0,
         "price": 95000.0
       }
       ```

#### cancel_stop_loss_orders
- endpoint: /auth/tacoclaw/trade/cancel_stop_loss_orders
- method: POST
- parameters:
  - query parameters:
     - user_id: tacoclaw user id
  - request body (in json format as below example):
       ```json
       {
         "api_token": "please use taco api key same as authentication bearer token in header",
         "user_id": "same as in query parameter",
         "exchange": "Taco",
         "symbol": "BTCUSDT"
       }
       ```

#### cancel_take_profit_orders
- endpoint: /auth/tacoclaw/trade/cancel_take_profit_orders
- method: POST
- parameters:
  - query parameters:
     - user_id: tacoclaw user id
  - request body (in json format as below example):
       ```json
       {
         "api_token": "please use taco api key same as authentication bearer token in header",
         "user_id": "same as in query parameter",
         "exchange": "Taco",
         "symbol": "BTCUSDT"
       }
       ```

#### cancel_stop_orders
- endpoint: /auth/tacoclaw/trade/cancel_stop_orders
- method: POST
- parameters:
  - query parameters:
     - user_id: tacoclaw user id
  - request body (in json format as below example):
       ```json
       {
         "api_token": "please use taco api key same as authentication bearer token in header",
         "user_id": "same as in query parameter",
         "exchange": "Taco",
         "symbol": "BTCUSDT"
       }
       ```

#### cancel_all_orders
- endpoint: /auth/tacoclaw/trade/cancel_all_orders
- method: POST
- parameters:
  - query parameters:
     - user_id: tacoclaw user id
  - request body (in json format as below example):
       ```json
       {
         "api_token": "please use taco api key same as authentication bearer token in header",
         "user_id": "same as in query parameter",
         "exchange": "Taco",
         "symbol": "BTCUSDT"
       }
       ```

#### cancel_order_by_order_id
- endpoint: /auth/tacoclaw/trade/cancel_order_by_order_id
- method: POST
- parameters:
  - query parameters:
     - user_id: tacoclaw user id
  - request body (in json format as below example):
       ```json
       {
         "api_token": "please use taco api key same as authentication bearer token in header",
         "user_id": "same as in query parameter",
         "exchange": "Taco",
         "symbol": "BTCUSDT",
         "order_id": "123456"
       }
       ```

#### get_positions
- endpoint: /auth/tacoclaw/trade/get_positions
- method: GET
- parameters:
  - query parameters:
     - user_id: tacoclaw user id
     - exchange: Taco

#### get_open_orders
- endpoint: /auth/tacoclaw/trade/get_open_orders
- method: GET
- parameters:
  - query parameters:
     - user_id: tacoclaw user id
     - exchange: Taco