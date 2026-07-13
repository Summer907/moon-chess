# 后端

FastAPI + Pydantic 实现月亮棋规则引擎和 API（含 AI 对手），并 serve `frontend/dist` 静态文件。

```bash
cd ..
uv sync

cd frontend
npm install
npm run build

cd ..
uv run uvicorn --app-dir backend app.main:app --reload --port 8000
```

启动后访问 `http://localhost:8000` 即可打开前端页面。

测试：

```bash
uv run pytest -q
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

## 国际化与 API 文本

后端不根据 `Accept-Language` 生成界面句子。它只返回稳定的规则事实、枚举和错误码；Vue 前端根据用户选择的 `zh-CN` 或 `en-US` 生成所有自然语言。

业务错误使用统一响应格式：

```json
{
  "detail": {
    "code": "invalid_move",
    "params": { "position": 4 }
  }
}
```

`GameError` 使用 `code` 和 `params`，不能通过比较旧中文错误文案判断错误类型。主要错误码包括：`game_not_found`（404）、`game_finished`（409）、`invalid_move`（422）、`no_legal_moves`（409）、`game_capacity_reached`（503）、`rate_limited`（429）、`ai_busy`（503）和 `validation_error`（422）。

响应模型已移除展示文案字段：`MoveEvent.note`、`Analysis.explanation`、`AiMoveResponse.reason` 和 `AiMoveEvaluation.reason`。棋谱使用 `removal_phase`，AI 使用 `confidence` 枚举与 `reason_codes`（每项含 `code`、`params`）表达可本地化的决策信息。
