# 前端

Vue 3 + TypeScript + Vite 实现月亮棋演示界面，包含两套视图：

- **银月之庭**（路由 `/`）——选择银月茶会或月轨推演。
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

## 国际化

国际化配置位于 `src/i18n/`：

- `index.ts` 创建 `vue-i18n` Composition API 实例（`legacy: false`），回退语言为 `zh-CN`。
- `locales/zh-CN.ts` 与 `locales/en-US.ts` 按业务域维护消息；英语语言包使用 `satisfies typeof zhCN` 保证键一致。
- `locale.ts` 负责选择、持久化与切换语言，并同步 `document.documentElement.lang`。
- `errorMap.ts` 将 API 错误码映射为本地化消息。

语言选择优先读取 `localStorage` 的 `moon-chess-locale-v1`，其次使用浏览器语言；以 `zh` 开头选择 `zh-CN`，其他语言选择 `en-US`，无法读取时回退到 `zh-CN`。不要在组件中拼接用户可见字符串；使用 `t("domain.key", params)` 进行插值。

路由 `meta.titleKey` 定义标题翻译键。路由切换和语言切换都会立即更新 `document.title`；favicon 仍由 `router.ts` 按路由维护。
