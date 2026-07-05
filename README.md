# 月亮棋 B/S 演示程序

用于制作 B 站视频的《原神》月亮棋规则演示：三子连线是表象，第四子触发旧子消失才是本征。

## 目录结构

```text
backend/
  app/
    game.py        # 月亮棋规则引擎与内存棋局管理
    main.py        # FastAPI API
    models.py      # Pydantic 数据模型
  tests/           # pytest 规则测试
frontend/
  src/
    api/           # 后端 API 客户端
    components/    # Vue 单文件组件
    styles/        # 全局样式
    types/         # TypeScript 类型
```

## 后端启动

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

健康检查：

```bash
curl http://localhost:8000/api/health
```

运行测试：

```bash
cd backend
python -m pytest -q
```

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端默认读取：

```text
VITE_API_BASE_URL=http://localhost:8000
```

如需修改后端地址，在 `frontend/.env` 中设置：

```text
VITE_API_BASE_URL=http://localhost:8000
```

生产构建：

```bash
cd frontend
npm run build
```

## 规则边界

- 后端负责所有规则判断、合法落子、消子、胜负、平局和分析说明。
- 前端只展示后端返回的 `GameState`，不自行推导 `pending_removal`、`upcoming_removal`、`legal_moves`、`winner`、`winning_line`、`current_winning_moves` 或 `opponent_real_threats`。
- 第 14 手，也就是后手第 7 手结束后，如果仍未分出胜负，则判平局；胜利判断优先于第 14 手平局。
- `POST /api/games` 的 `max_moves` 保留为兼容字段，但当前规则固定为 14。
- repetition draw 仍使用“当前行动方 + X 有序位置 + O 有序位置”的局面签名，棋子年龄顺序会影响签名。
