import { test, expect, type Page } from "@playwright/test";

async function openGame(page: Page, path = "/tea-party") {
  await page.goto(path);
  const close = page.getByRole("button", { name: "关闭规则说明", exact: true });
  if (await close.isVisible()) await close.click();
  await expect(page.getByRole("region", { name: "月亮棋棋盘" })).toBeVisible();
}

test("play, AI reply, atomic undo and confirmed restart", async ({ page }) => {
  await openGame(page);
  await page.getByRole("button", { name: "位置 5; 可落", exact: true }).click();
  await expect(page.getByText("已落 2 / 14 手", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "悔棋", exact: true }).click();
  await expect(page.getByText("已落 0 / 14 手", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "位置 5; 可落", exact: true }).click();
  await expect(page.getByText("已落 2 / 14 手", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "重新开始", exact: true }).click();
  await expect(page.getByRole("dialog", { name: "开始新的棋局？" })).toBeVisible();
  await page.getByRole("button", { name: "开始新局", exact: true }).click();
  await expect(page.getByText("已落 0 / 14 手", { exact: true })).toBeVisible();
});

test("offline reconciliation leaves an enabled synchronize button", async ({ page }) => {
  await openGame(page, "/lunar-orbit");
  await page.route("**/api/games/**", route => route.abort());
  await page.getByRole("button", { name: "位置 5; 可落", exact: true }).click();
  const sync = page.getByRole("button", { name: "重新同步", exact: true });
  await expect(sync).toBeEnabled();
  await expect(page.locator(".game-cell").nth(1)).toBeDisabled();
  await page.unroute("**/api/games/**");
  await sync.click();
  await expect(page.locator(".game-cell").nth(1)).toBeEnabled();
});

test("AI delay can be undone, submitted AI blocks actions", async ({ page }) => {
  await openGame(page);
  await page.getByRole("button", { name: "位置 5; 可落", exact: true }).click();
  await page.getByRole("button", { name: "悔棋", exact: true }).click();
  await expect(page.getByText("已落 0 / 14 手", { exact: true })).toBeVisible();
  let release!: () => void;
  const barrier = new Promise<void>(done => { release = done; });
  await page.route("**/ai-move", async route => {
    await barrier;
    await route.continue();
  });
  await page.getByRole("button", { name: "位置 5; 可落", exact: true }).click();
  await expect(page.getByRole("button", { name: "悔棋", exact: true })).toBeDisabled();
  await expect(page.getByRole("button", { name: "重新开始", exact: true })).toBeDisabled();
  release();
  await expect(page.getByText("已落 2 / 14 手", { exact: true })).toBeVisible();
});

test("canceling side change preserves side, confirming changes only after reset", async ({ page }) => {
  await openGame(page);
  await page.getByRole("button", { name: "位置 5; 可落", exact: true }).click();
  await expect(page.getByText("已落 2 / 14 手", { exact: true })).toBeVisible();
  await page.getByRole("radio", { name: "旅行者后手", exact: true }).click();
  await page.getByRole("button", { name: "保留棋局", exact: true }).click();
  await expect(page.getByRole("radio", { name: "旅行者先手", exact: true })).toBeChecked();
  await page.getByRole("radio", { name: "旅行者后手", exact: true }).click();
  await page.getByRole("button", { name: "开始新局", exact: true }).click();
  await expect(page.getByRole("radio", { name: "旅行者后手", exact: true })).toBeChecked();
  await expect(page.getByText("已落 1 / 14 手", { exact: true })).toBeVisible();
});

test("mobile draw opens result and home modes remain navigable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openGame(page, "/lunar-orbit");
  for (const cell of [1, 2, 3, 4, 5, 7, 1, 9, 8, 2, 3, 4, 1, 5]) {
    await page.locator(".game-cell").nth(cell - 1).click();
  }
  await expect(page.getByRole("region", { name: "对局结果" })).toContainText("平局");
  await page.screenshot({ path: "../artifacts/ui/orbit-390-draw.png", fullPage: true, animations: "disabled" });
  await page.getByRole("link", { name: "← 返回银月之庭" }).click();
  await expect(page.getByRole("link", { name: "进入银月茶会 AI 对战" })).toBeVisible();
  await page.screenshot({ path: "../artifacts/ui/home-390.png", fullPage: true });
});

test("failed creation and busy AI have recovery controls", async ({ page }) => {
  await page.route("**/api/games", route => route.fulfill({
    status: 503, contentType: "application/json",
    body: JSON.stringify({ detail: { code: "game_capacity_reached", params: {} } }),
  }));
  await page.goto("/tea-party");
  const close = page.getByRole("button", { name: "关闭规则说明", exact: true });
  if (await close.isVisible()) await close.click();
  await expect(page.getByRole("alert")).toBeVisible();
  await page.unroute("**/api/games");
  await page.getByRole("button", { name: "开始新对局 / 重试创建" }).click();
  await page.route("**/ai-move", route => route.fulfill({
    status: 503, contentType: "application/json", headers: { "Retry-After": "1" },
    body: JSON.stringify({ detail: { code: "ai_busy", params: {} } }),
  }));
  await page.getByRole("button", { name: "位置 5; 可落", exact: true }).click();
  const retry = page.getByRole("button", { name: /继续 AI 回合/ });
  await expect(retry).toBeVisible();
  await page.unroute("**/ai-move");
  await expect(retry).toBeEnabled();
  await retry.click();
  await expect(page.getByText("已落 2 / 14 手", { exact: true })).toBeVisible();
});

test("lost response synchronizes without replaying a move", async ({ page }) => {
  await openGame(page, "/lunar-orbit");
  let requests = 0;
  await page.route("**/moves", async route => {
    requests++;
    await route.fetch();
    await route.abort();
  });
  await page.getByRole("button", { name: "位置 5; 可落", exact: true }).click();
  await expect(page.getByText("已落 1 / 14 手", { exact: true })).toBeVisible();
  expect(requests).toBe(1);
  await expect(page.getByRole("button", { name: "位置 2; 可落", exact: true })).toBeEnabled();
});

test("win, result and history", async ({ page }) => {
  await openGame(page, "/lunar-orbit");
  for (const cell of [1, 4, 2, 5, 3]) {
    await page.locator(".game-cell").nth(cell - 1).click();
  }
  await expect(page.getByRole("region", { name: "对局结果" })).toContainText("旅行者 胜利");
  await expect(page.getByRole("link", { name: "查看棋谱" })).toBeVisible();
});

for (const size of [{ width: 390, height: 844 }, { width: 768, height: 1024 }, { width: 1366, height: 768 }]) {
  test(`layout ${size.width}, themes, languages and keyboard`, async ({ page }) => {
    await page.setViewportSize(size);
    await page.emulateMedia({ reducedMotion: "reduce" });
    await openGame(page);
    for (const theme of ["dark", "light"]) {
      if (theme === "light") await page.getByRole("button", { name: "切换到浅色模式" }).click();
      for (const language of ["zh", "en"]) {
        if (language === "en") await page.getByRole("button", { name: "切换到英语" }).click();
        expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
        const bounds = await page.locator(".game-actions").boundingBox();
        expect(bounds!.y + bounds!.height).toBeLessThanOrEqual(size.height);
        await page.screenshot({ path: `../artifacts/ui/tea-${size.width}-${theme}-${language}.png`, fullPage: true });
        if (language === "en") await page.getByRole("button", { name: "Switch to Chinese" }).click();
      }
    }
    await page.getByRole("button", { name: "查看规则说明" }).click();
    const quick = page.getByRole("tab", { name: "快速上手" });
    await quick.focus();
    await page.keyboard.press("ArrowRight");
    await expect(page.getByRole("tab", { name: "完整规则" })).toBeFocused();
    await page.keyboard.press("Escape");
    await expect(page.getByRole("button", { name: "查看规则说明" })).toBeFocused();
  });
}
