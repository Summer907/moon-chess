<script setup lang="ts">
defineProps<{
  loading: boolean;
  canUndo: boolean;
  showCellNumbers: boolean;
  showLegalMoves: boolean;
  showWinningMoves: boolean;
  showThreatMoves: boolean;
  showRemovalPreview: boolean;
}>();

defineEmits<{
  newGame: [];
  undo: [];
  "update:showCellNumbers": [value: boolean];
  "update:showLegalMoves": [value: boolean];
  "update:showWinningMoves": [value: boolean];
  "update:showThreatMoves": [value: boolean];
  "update:showRemovalPreview": [value: boolean];
}>();
</script>

<template>
  <section class="control-panel" aria-label="操作区">
    <div class="button-row">
      <button type="button" :disabled="loading" @click="$emit('newGame')">新开一局</button>
      <button type="button" :disabled="loading || !canUndo" @click="$emit('undo')">悔棋</button>
    </div>

    <label class="toggle-row">
      <input
        type="checkbox"
        :checked="showCellNumbers"
        @change="$emit('update:showCellNumbers', ($event.target as HTMLInputElement).checked)"
      />
      <span>显示编号</span>
    </label>

    <label class="toggle-row">
      <input
        type="checkbox"
        :checked="showLegalMoves"
        @change="$emit('update:showLegalMoves', ($event.target as HTMLInputElement).checked)"
      />
      <span>合法落子</span>
    </label>

    <label class="toggle-row">
      <input
        type="checkbox"
        :checked="showWinningMoves"
        @change="$emit('update:showWinningMoves', ($event.target as HTMLInputElement).checked)"
      />
      <span>直接胜点</span>
    </label>

    <label class="toggle-row">
      <input
        type="checkbox"
        :checked="showThreatMoves"
        @change="$emit('update:showThreatMoves', ($event.target as HTMLInputElement).checked)"
      />
      <span>真实威胁</span>
    </label>

    <label class="toggle-row">
      <input
        type="checkbox"
        :checked="showRemovalPreview"
        @change="$emit('update:showRemovalPreview', ($event.target as HTMLInputElement).checked)"
      />
      <span>消失预告</span>
    </label>

  </section>
</template>
