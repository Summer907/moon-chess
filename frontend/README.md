# 前端

Vue 3 + TypeScript + Vite 实现月亮棋演示界面。

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
