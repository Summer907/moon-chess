# 月亮棋（Moon Chess）

《原神》月亮棋规则演示：三子连线是表象，第四子触发旧子消失才是本征。

前端有两套界面：
- **银月茶会（首页 /）**——玩家对玩家 / 玩家对 AI 对弈界面。
- **月轨推演（/lunar-orbit）**——单步回溯、局面分析的沙盒模式。

AI 对手支持 **easy / medium / hard** 三种难度，可获取落子提示或自动走棋。

## 目录结构

```text
backend/
  app/
    ai/            # AI 对手（提示与自动走棋）
    game.py        # 月亮棋规则引擎与内存棋局管理
    main.py        # FastAPI API
    models.py      # Pydantic 数据模型
  tests/           # pytest 规则测试
frontend/
  src/
    api/           # 后端 API 客户端
    components/    # Vue 单文件组件
    router.ts      # 路由定义
    styles/        # 全局样式
    types/         # TypeScript 类型
    utils/         # 工具函数
    views/         # 页面级组件
```

## 单服务启动

```bash
cd frontend
npm install
npm run build

cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

访问：

```text
http://localhost:8000
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| POST | `/api/games` | 新建对局 |
| GET | `/api/games/{id}` | 查询棋局状态 |
| POST | `/api/games/{id}/moves` | 落子 |
| POST | `/api/games/{id}/undo` | 悔棋 |
| POST | `/api/games/{id}/reset` | 重置棋局 |
| GET | `/api/games/{id}/hint?level=medium` | 获取 AI 落子建议 |
| POST | `/api/games/{id}/ai-move` | AI 自动走棋 |

运行测试：

```bash
cd backend
python -m pytest -q
```

## 前端独立开发

```bash
cd frontend
npm install
npm run dev
```

前端默认使用同源 `/api`。Vite 开发服务器会把 `/api` 代理到：

```text
http://localhost:8000
```

如需修改后端地址，在 `frontend/.env` 中设置，例如：

```text
VITE_API_BASE_URL=http://localhost:8000
```

生产构建会输出到 `frontend/dist`，FastAPI 会直接 serve 这个目录：

```bash
cd frontend
npm run build
```

## 规则边界

- 后端负责所有规则判断、合法落子、消子、胜负、平局、AI 走棋和分析说明。
- 前端只展示后端返回的 `GameState`，不自行推导 `pending_removal`、`upcoming_removal`、`legal_moves`、`winner`、`winning_line`、`current_winning_moves` 或 `opponent_real_threats`。
- 第 14 手，也就是后手第 7 手结束后，如果仍未分出胜负，则判平局；胜利判断优先于第 14 手平局。
- `POST /api/games` 的 `max_moves` 保留为兼容字段，但当前规则固定为 14。
- `GET /api/games/{id}/hint` 返回 AI 建议但不修改棋局；`POST /api/games/{id}/ai-move` 可自动落子。
