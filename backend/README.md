# 后端

FastAPI + Pydantic 实现月亮棋规则引擎和 API（含 AI 对手），并 serve `frontend/dist` 静态文件。

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

AI 模块位于 `app/ai/`，支持三种难度（easy / medium / hard），通过以下接口使用：

- `GET /api/games/{game_id}/hint?level=medium` —— 获取 AI 建议，不修改棋局
- `POST /api/games/{game_id}/ai-move` —— AI 自动走棋（可选 auto_apply 控制是否落子）

主要接口：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| POST | `/api/games` | 新建对局 |
| GET | `/api/games/{id}` | 查询棋局 |
| POST | `/api/games/{id}/moves` | 落子 |
| POST | `/api/games/{id}/undo` | 悔棋 |
| POST | `/api/games/{id}/reset` | 重置 |
| GET | `/api/games/{id}/hint` | AI 落子提示 |
| POST | `/api/games/{id}/ai-move` | AI 自动走棋 |

当前规则固定第 14 手未胜即平，`POST /api/games` 的 `max_moves` 只能为 `14`。
