# 前端

Vue 3 + TypeScript + Vite 实现月亮棋演示界面，包含两套视图：

- **月下对弈大厅**（路由 `/`）——选择银月茶会或月轨推演。
- **银月茶会**（路由 `/tea-party`）——单人挑战 AI 的对弈界面，支持三档难度。
- **月轨推演**（路由 `/lunar-orbit`）——单步回溯、局面分析的沙盒模式。

当前仅支持玩家对 AI，暂不规划多人对战模式。

```bash
npm install
npm run dev
```

默认使用同源 `/api`。独立运行 Vite 开发服务器时，`/api` 会代理到 `http://localhost:8000`。

如需改用其他后端地址，通过环境变量配置：

```text
VITE_API_BASE_URL=http://localhost:8000
```

构建后产物输出到 `frontend/dist`，由 FastAPI 直接 serve：

```bash
npm run build
```

路由定义在 `src/router.ts`，组件位于 `src/components/`，页面级视图位于 `src/views/`。
