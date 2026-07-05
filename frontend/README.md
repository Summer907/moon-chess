# 前端

Vue 3 + TypeScript + Vite 实现月亮棋演示界面，包含两套视图：

- **银月茶会**（路由 `/`）——玩家对玩家 / 玩家对 AI 对弈界面。
- **月轨推演**（路由 `/lunar-orbit`）——单步回溯、局面分析的沙盒模式。

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
