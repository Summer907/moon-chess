<template>
  <section class="moon-hall" aria-labelledby="moon-hall-title">
    <div class="moon-hall__aura" aria-hidden="true"></div>
    <header class="moon-hall__hero">
      <p class="moon-hall__eyebrow">Moon Chess</p>
      <h1 id="moon-hall-title">月下对弈，落子成光</h1>
      <p>眼前月是天上月，月上人是心上人。</p>
    </header>

    <div class="mode-card-grid" aria-label="选择游戏模式">
      <RouterLink class="mode-card mode-card--tea" to="/tea-party" aria-label="进入银月茶会 AI 对战">
        <div class="mode-card__illustration mode-card__illustration--tea" aria-hidden="true">
          <div class="piece-columbina"><span class="piece-label"></span></div>
          <div class="piece-traveler"><span class="piece-label"></span></div>
        </div>
        <p class="mode-card__kicker">AI 对战</p>
        <h2>银月茶会</h2>
        <p>与哥伦比娅隔月对弈。选择席位与难度，在月影更替间取得三连。</p>
        <ul aria-label="银月茶会特性">
          <li>三档难度</li>
          <li>自动应手</li>
          <li>完整棋谱</li>
        </ul>
        <span class="mode-card__enter">入席对弈 <span aria-hidden="true">→</span></span>
      </RouterLink>

      <RouterLink class="mode-card mode-card--orbit" to="/lunar-orbit" aria-label="进入月轨推演">
        <div class="mode-card__illustration mode-card__illustration--orbit" aria-hidden="true">
          <span></span><span></span><span></span>
        </div>
        <p class="mode-card__kicker">自由推演</p>
        <h2>月轨推演</h2>
        <p>自由落子，观察旧子消失顺序、当前胜点与对手真实威胁。</p>
        <ul aria-label="月轨推演特性">
          <li>后端判定</li>
          <li>威胁分析</li>
          <li>逐步回退</li>
        </ul>
        <span class="mode-card__enter">推演月轨 <span aria-hidden="true">→</span></span>
      </RouterLink>
    </div>
    <!-- <p class="moon-hall__note">选择模式后即可开始；开局设置会在对应页面保留。</p> -->
  </section>
</template>
