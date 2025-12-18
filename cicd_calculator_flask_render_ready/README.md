# CI/CD Calculator (Flask)

四則演算（+ - * /）ができる最小の電卓アプリです。
- **CI**: GitHub Actions で pytest を実行
- **CD**: CI成功時に Render Deploy Hook を叩いて自動デプロイ

## ローカル実行
```bash
pip install -r requirements.txt
PYTHONPATH=src python src/calculator_app/app.py
```
http://localhost:5050

## テスト
```bash
PYTHONPATH=src pytest
```

## Render (CD) 設定
Render の Web Service の **Start Command** にこれを設定：
```bash
PYTHONPATH=src gunicorn -b 0.0.0.0:$PORT calculator_app.app:app
```

GitHub の Secrets に追加：
- Name: `RENDER_DEPLOY_HOOK_URL`
- Value: Render の Deploy Hook URL（https://api.render.com/deploy/...）

## API
- GET `/health` → `{ "status": "ok" }`
- POST `/calc` → `{ "a":2, "op":"+", "b":3 }`
  - 成功: `{ "result": 5.0, ... }`
  - 失敗: `INVALID_OPERATOR` / `INVALID_NUMBER` / `DIVIDE_BY_ZERO`
