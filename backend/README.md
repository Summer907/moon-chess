# 后端

FastAPI + Pydantic 实现月亮棋规则引擎和 API，并 serve `frontend/dist` 静态文件。

```bash
cd ../frontend
npm install
npm run build

cd ../backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

启动后访问 `http://localhost:8000` 即可打开前端页面。

测试：

```bash
python -m pytest -q
```

主要接口：

- `GET /api/health`
- `POST /api/games`
- `GET /api/games/{game_id}`
- `POST /api/games/{game_id}/moves`
- `POST /api/games/{game_id}/undo`
- `POST /api/games/{game_id}/reset`

当前规则固定第 14 手未胜即平，`POST /api/games` 的 `max_moves` 只能为 `14`。
