<p align="center">
  <img src="assets/hero.png" alt="月亮棋 Moon Chess 界面预览" width="880">
</p>

<h1 align="center">月亮棋 Moon Chess</h1>

<p align="center">
  三子连线是表象，第四子触发旧子消失才是本征。
</p>

<p align="center">
  <a href="https://moon-chess.onrender.com/">
    <img src="https://img.shields.io/badge/在线体验-moon--chess.onrender.com-8ddcff?style=for-the-badge" alt="在线体验">
  </a>
  <a href="https://github.com/Summer907/moon-chess">
    <img src="https://img.shields.io/badge/GitHub-Summer907%2Fmoon--chess-0b1220?style=for-the-badge&logo=github" alt="GitHub 仓库">
  </a>
  <img src="https://img.shields.io/badge/License-MIT-a7f3d0?style=for-the-badge" alt="MIT License">
</p>

《原神》月亮棋规则演示工具：在九宫格中轮流落子，形成横、竖、斜三子连线即可获胜；但每方场上最多稳定保留三枚棋子，第四次行动会先让最早落下的旧子消失。

前端包含一个模式大厅和两套对弈界面：

- **银月之庭（/）**——模式选择大厅，可进入银月茶会或月轨推演。
- **银月茶会（/tea-party）**——玩家对 AI 对弈界面，支持三档 AI 难度。
- **月轨推演（/lunar-orbit）**——单步回溯、局面分析的沙盒模式。

AI 对手支持 **easy / medium / hard** 三种难度，可获取落子提示或自动走棋。

界面针对桌面端和移动端自适应：窄屏下状态、分析和开局配置会收纳为可展开面板。银月茶会的执子方与 AI 难度、月轨推演的执子方会在当前浏览器会话中分别保留；页面标题和图标也会随模式切换。

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
    components/    # Vue 单文件组件与响应式折叠面板
    router.ts      # 路由、页面标题与图标定义
    styles/        # 全局样式
    types/         # TypeScript 类型
    utils/         # 工具函数与会话偏好持久化
    views/         # 页面级组件
assets/            # README 图片与各模式页面图标
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

| 方法 | 路径                                  | 说明             |
| ---- | ------------------------------------- | ---------------- |
| GET  | `/api/health`                       | 健康检查         |
| POST | `/api/games`                        | 新建对局         |
| GET  | `/api/games/{id}`                   | 查询棋局状态     |
| POST | `/api/games/{id}/moves`             | 落子             |
| POST | `/api/games/{id}/undo`              | 悔棋             |
| POST | `/api/games/{id}/reset`             | 重置棋局         |
| GET  | `/api/games/{id}/hint?level=medium` | 获取 AI 落子建议 |
| POST | `/api/games/{id}/ai-move`           | AI 自动走棋      |

## 公开部署保护

后端默认启用单实例、进程内的资源保护：创建棋局、普通操作和 AI 请求分别限流；困难 AI 同时只执行一个搜索；棋局会按活跃状态过期，并限制单 IP 与实例总量。超限请求返回 `429` 和 `Retry-After`。

可用环境变量：`RATE_LIMIT_CREATE_PER_MINUTE`（5）、`RATE_LIMIT_CREATE_PER_HOUR`（30）、`RATE_LIMIT_GENERAL_PER_MINUTE`（60）、`RATE_LIMIT_AI_PER_MINUTE`（20）、`RATE_LIMIT_HARD_AI_PER_MINUTE`（5）、`AI_STANDARD_CONCURRENCY`（4）、`AI_HARD_CONCURRENCY`（1）、`AI_MEMO_CAPACITY`（100000）、`GAME_PLAYING_TTL_SECONDS`（3600）、`GAME_FINISHED_TTL_SECONDS`（900）、`MAX_GAMES_PER_IP`（10）和 `MAX_GAMES`（5000）。

默认不信任转发请求头；若确认请求只会经过受信反向代理，可用 `TRUSTED_PROXY_IPS` 设置逗号分隔的代理 IP 地址。横向扩容前需将棋局、限流计数和锁迁移到 Redis。

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
