<script setup lang="ts">
import { RouterLink } from "vue-router";
import GameBoard from "../components/GameBoard.vue";
import ResponsiveDisclosure from "../components/ResponsiveDisclosure.vue";
import GameHistoryList from "../components/game/GameHistoryList.vue";
import GameSettingsCard from "../components/game/GameSettingsCard.vue";
import GameStatusCard from "../components/game/GameStatusCard.vue";
import ConfirmDialog from "../components/ConfirmDialog.vue";
import { useGameController } from "../utils/useGameController";
const { confirmOpen, requestRestart, confirmRestart, cancelRestart, gameState, loading, aiThinking, errorMessage, t, travelerSide, aiLevel, displayMap, showCellNumbers, showLegalMoves, showWinningMoves, showThreatMoves, showRemovalPreview, canPlace, canUndo, statusPillText, startNewGame, undoMove, placeAt, updateTravelerSide, updateAiLevel, recover, recoveryLabel, retryAfter, boardPanelRef, boardHeightStyle, pieceShortName, pieceFullName, pieceClassName } = useGameController("teaParty");
</script>

<template>
  <ConfirmDialog v-if="confirmOpen" @confirm="confirmRestart" @cancel="cancelRestart" />
  <header class="app-header">
    <div class="title-block">
      <RouterLink class="return-home-link" to="/">{{ t('common.backHome') }}</RouterLink>
      <h1 class="app-title">{{ t('teaParty.title') }}</h1><p class="subtitle">{{ t('teaParty.subtitle') }}</p>
    </div>
  </header>

  <section v-if="errorMessage" class="error-message" role="alert"><p>{{ errorMessage }}</p><button :disabled="loading || retryAfter > 0" @click="recover">{{ recoveryLabel }} <span v-if="retryAfter">{{ t("recovery.countdown", { count: retryAfter }) }}</span></button></section>

  <section v-if="gameState" class="game-main-layout" :style="boardHeightStyle">
    <div class="play-column">
    <div class="turn-banner" role="status" aria-live="polite"><strong>{{ statusPillText }}</strong><span v-if="gameState.status === 'playing'">{{ t(loading || aiThinking ? "ux.wait" : "ux.choose") }}</span></div>
    <div ref="boardPanelRef" class="game-board-slot">
      <div class="piece-legend"><span v-for="player in displayMap" :key="player.player"><i :class="player.pieceClass"></i>{{ player.name }}</span></div>
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

    <div class="game-actions button-row" :aria-label="t('teaParty.actions')">
      <button type="button" :disabled="loading" :title="t('teaParty.restartTitle')" @click="requestRestart">
        {{ t(gameState.status === 'playing' ? 'ux.restart' : 'ux.again') }}
      </button>
      <button type="button" :disabled="loading || !canUndo" :title="t('teaParty.undoTitle')" @click="undoMove">
        {{ t('ux.undo') }}
      </button>
      <a v-if="gameState.status !== 'playing'" href="#game-history">{{ t("ux.viewHistory") }}</a>
    </div>

    </div>
    <div class="game-side-stack game-side-stack--duo">
      <ResponsiveDisclosure
        class="disclosure-status"
        :title="t('game.status')"
        :status-text="statusPillText"
        :force-open="gameState.status !== 'playing'"
      >
        <GameStatusCard
          :state="gameState"
          :display-map="displayMap"
          :ai-thinking="aiThinking"
          :thinking-text="statusPillText"
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
        @new-game="requestRestart"
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

  <section v-if="gameState" id="game-history" class="game-history-row">
    <GameHistoryList :history="gameState.history" :display-map="displayMap" />
  </section>

  <section v-else-if="!errorMessage" class="loading-panel">{{ t('common.loading') }}</section>
</template>
