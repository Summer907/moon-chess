<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue";

const emit = defineEmits<{
  close: [];
}>();

type GuideTab = "quick" | "rules" | "modes" | "markers";

const activeTab = ref<GuideTab>("quick");
const dialogRef = ref<HTMLElement | null>(null);

const tabs: Array<{ id: GuideTab; label: string }> = [
  { id: "quick", label: "快速上手" },
  { id: "rules", label: "完整规则" },
  { id: "modes", label: "模式说明" },
  { id: "markers", label: "界面标记" },
];

function closeDialog() {
  emit("close");
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === "Escape") {
    closeDialog();
  }
}

onMounted(() => {
  document.addEventListener("keydown", handleKeydown);
  void nextTick(() => {
    dialogRef.value?.focus();
  });
});

onBeforeUnmount(() => {
  document.removeEventListener("keydown", handleKeydown);
});
</script>

<template>
  <Teleport to="body">
    <div class="guide-backdrop" role="presentation" @click.self="closeDialog">
      <section
        ref="dialogRef"
        class="guide-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="guide-title"
        tabindex="-1"
      >
        <header class="guide-header">
          <div>
            <p class="guide-kicker">规则说明</p>
            <h2 id="guide-title">月亮棋指南</h2>
          </div>
          <button type="button" class="guide-icon-button" title="关闭" aria-label="关闭规则说明" @click="closeDialog">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M18 6 6 18" />
              <path d="m6 6 12 12" />
            </svg>
          </button>
        </header>

        <div class="guide-tabs" role="tablist" aria-label="指南内容">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            type="button"
            class="guide-tab"
            :class="{ active: activeTab === tab.id }"
            role="tab"
            :aria-selected="activeTab === tab.id"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>

        <div class="guide-content">
          <section v-if="activeTab === 'quick'" class="guide-panel" role="tabpanel">
            <div class="guide-callout">
              <strong>一句话规则</strong>
              <p>在九宫格里轮流落子，三子连线获胜；但从第 4 枚同方棋子开始，最早落下的旧子会先消失。</p>
            </div>
            <ol class="guide-steps">
              <li>看高亮的合法落点，选择一个空格落子。</li>
              <li>留意粉色消失预告：轮到一方时，自己的最旧棋子可能会先离场。</li>
              <li>绿色是当前方直接胜点，橙色是对手下一回合的真实威胁。</li>
              <li>落子后如果形成横、竖、斜任意三连，立即获胜。</li>
            </ol>
          </section>

          <section v-else-if="activeTab === 'rules'" class="guide-panel" role="tabpanel">
            <dl class="guide-rule-list">
              <div>
                <dt>棋盘</dt>
                <dd>棋盘是 1 到 9 的九宫格，胜线包括 3 横、3 竖、2 条斜线。</dd>
              </div>
              <div>
                <dt>落子</dt>
                <dd>双方轮流在合法位置落一枚棋子。被占用的位置不可落子，除非占用它的棋子会在本回合先消失。</dd>
              </div>
              <div>
                <dt>消子</dt>
                <dd>每方场上最多稳定保留 3 枚棋子。轮到某方行动且该方已有 3 枚棋子时，最早落下的一枚先消失，然后再落新子。</dd>
              </div>
              <div>
                <dt>胜负</dt>
                <dd>落子后先判断三连胜利。若第 14 手结束后仍未分胜负，棋局判为平局。</dd>
              </div>
            </dl>
          </section>

          <section v-else-if="activeTab === 'modes'" class="guide-panel" role="tabpanel">
            <div class="guide-mode-grid">
              <article>
                <h3>银月茶会</h3>
                <p>首页对弈模式。你可以选择旅行者先手或后手，设置哥伦比娅的 AI 难度，然后直接开始一局。</p>
              </article>
              <article>
                <h3>月轨推演</h3>
                <p>分析沙盒模式。双方都由你手动落子，适合回退、试招、观察消子后的胜点和威胁。</p>
              </article>
            </div>
          </section>

          <section v-else class="guide-panel" role="tabpanel">
            <ul class="guide-marker-list">
              <li><strong>格号</strong><span>棋盘上的 1-9 编号，方便描述落点。</span></li>
              <li><strong>合法落点</strong><span>当前回合可以落子的格子。</span></li>
              <li><strong>直接胜点</strong><span>当前方落下即可形成三连的位置。</span></li>
              <li><strong>真实威胁</strong><span>对手下一回合在消子规则生效后仍然能取胜的位置。</span></li>
              <li><strong>消失预告</strong><span>本回合或下一回合会先离场的最旧棋子。</span></li>
            </ul>
          </section>
        </div>
      </section>
    </div>
  </Teleport>
</template>
