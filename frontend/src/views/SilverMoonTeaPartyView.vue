<script setup lang="ts">
import { RouterLink } from "vue-router";
import GameBoard from "../components/GameBoard.vue";
import ResponsiveDisclosure from "../components/ResponsiveDisclosure.vue";
import GameHistoryList from "../components/game/GameHistoryList.vue";
import GameSettingsCard from "../components/game/GameSettingsCard.vue";
import GameStatusCard from "../components/game/GameStatusCard.vue";
import { useGameController } from "../utils/useGameController";
const { gameState, loading, aiThinking, errorMessage, t, travelerSide, aiLevel, displayMap, showCellNumbers, showLegalMoves, showWinningMoves, showThreatMoves, showRemovalPreview, canPlace, canUndo, statusPillText, startNewGame, undoMove, placeAt, updateTravelerSide, updateAiLevel, recover, recoveryLabel, retryAfter, boardPanelRef, boardHeightStyle, pieceShortName, pieceFullName, pieceClassName } = useGameController("teaParty");
</script>

<template>
  <header class="app-header">
    <div class="title-block">
      <RouterLink class="return-home-link" to="/">{{ t('common.backHome') }}</RouterLink>
      <h1 class="app-title">{{ t('teaParty.title') }}</h1><p class="subtitle">{{ t('teaParty.subtitle') }}</p>
    </div>
    <div v-if="gameState" class="status-pill" :class="`status-${gameState.status}`">
      <span>{{ statusPillText }}</span>
    </div>
  </header>

  <section v-if="errorMessage" class="error-message" role="alert"><p>{{ errorMessage }}</p><button :disabled="loading || retryAfter > 0" @click="recover">{{ recoveryLabel }} <span v-if="retryAfter">{{ t("recovery.countdown", { count: retryAfter }) }}</span></button></section>

  <section v-if="gameState" class="game-main-layout" :style="boardHeightStyle">
    <div ref="boardPanelRef" class="game-board-slot">
      <GameBoard
        :state="gameState"
        :show-cell-numbers="showCellNumbers"
        :show-legal-moves="showLegalMoves"
        :show-winning-moves="showWinningMoves"
        :show-threat-moves="showThreatMoves"
        :show-removal-preview="showRemovalPreview"
        :disabled="!canPlace"
        :format-piece-label="pieceShortName"
        :format-piece-description="pieceFullName"
        :piece-class="pieceClassName"
        @place="placeAt"
      />
    </div>

    <div class="mobile-game-actions button-row" :aria-label="t('teaParty.actions')">
      <button type="button" :disabled="loading" :title="t('teaParty.restartTitle')" @click="startNewGame">
        {{ t('teaParty.restart') }}
      </button>
      <button type="button" :disabled="loading || !canUndo" :title="t('teaParty.undoTitle')" @click="undoMove">
        {{ t('teaParty.undo') }}
      </button>
    </div>

    <div class="game-side-stack game-side-stack--duo">
      <ResponsiveDisclosure
        class="disclosure-status"
        :title="t('game.status')"
        :status-text="statusPillText"
        :force-open="gameState.status === 'won'"
      >
        <GameStatusCard
          :state="gameState"
          :display-map="displayMap"
          :ai-thinking="aiThinking"
          :show-removal-preview="showRemovalPreview"
        />
      </ResponsiveDisclosure>
      <ResponsiveDisclosure class="disclosure-settings" :title="t('settings.configuration')">
        <GameSettingsCard
        :traveler-side="travelerSide"
        :ai-level="aiLevel"
        :show-ai-level="true"
        :loading="loading"
        :can-undo="canUndo"
        :show-cell-numbers="showCellNumbers"
        :show-legal-moves="showLegalMoves"
        :show-winning-moves="showWinningMoves"
        :show-threat-moves="showThreatMoves"
        :show-removal-preview="showRemovalPreview"
        @new-game="startNewGame"
        @undo="undoMove"
        @update:traveler-side="updateTravelerSide"
        @update:ai-level="updateAiLevel"
        @update:show-cell-numbers="showCellNumbers = $event"
        @update:show-legal-moves="showLegalMoves = $event"
        @update:show-winning-moves="showWinningMoves = $event"
        @update:show-threat-moves="showThreatMoves = $event"
        @update:show-removal-preview="showRemovalPreview = $event"
        />
      </ResponsiveDisclosure>
    </div>
  </section>

  <section v-if="gameState" class="game-history-row">
    <GameHistoryList :history="gameState.history" :display-map="displayMap" />
  </section>

  <section v-else-if="!errorMessage" class="loading-panel">{{ t('common.loading') }}</section>
</template>
