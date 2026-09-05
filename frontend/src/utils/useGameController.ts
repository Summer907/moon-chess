import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { createGame, makeAiMove, makeMove, undo } from "../api/client";
import type { AiLevel, Piece } from "../types/game";
import type { TravelerSide } from "../types/display";
import { errorText } from "../i18n/errorMap";
import { createPlayerDisplay, formatPieceFull, formatPieceShort, formatPlayer, isRoleTurn, pieceDisplayClass } from "./playerDisplay";
import { loadGamePreferences, saveGamePreferences } from "./useGamePreferences";
import { useGameSession } from "./useGameSession";
import { useElementHeightCssVar } from "./useElementHeightCssVar";

export function useGameController(mode: "teaParty" | "lunarOrbit") {
  const session = useGameSession();
  const { gameState, phase, failure, blocked, run } = session;
  const { t } = useI18n();
  const saved = loadGamePreferences();
  const travelerSide = ref<TravelerSide>(saved[mode].travelerSide);
  const aiLevel = ref<AiLevel>(saved.teaParty.aiLevel);
  const displayMap = computed(() => createPlayerDisplay(travelerSide.value, t));
  const showCellNumbers = ref(saved[mode].display.numbers);
  const showLegalMoves = ref(saved[mode].display.legal);
  const showWinningMoves = ref(saved[mode].display.wins);
  const showThreatMoves = ref(saved[mode].display.threats);
  const showRemovalPreview = ref(saved[mode].display.removal);
  const aiTurn = computed(() => mode === "teaParty" && gameState.value?.status === "playing" &&
    isRoleTurn(gameState.value.current_player, displayMap.value, "columbina"));
  const aiThinking = computed(() => phase.value === "thinking" || aiTurn.value && phase.value === "submitting");
  const loading = blocked;
  const canPlace = computed(() => !!gameState.value && gameState.value.status === "playing" && !blocked.value && !aiTurn.value);
  const undoSteps = computed(() => {
    const state = gameState.value;
    if (!state?.history.length) return 0;
    if (mode === "lunarOrbit") return 1;
    const last = state.history[state.history.length - 1]!;
    return displayMap.value[last.player].role === "traveler" ? 1 : state.history.length >= 2 ? 2 : 0;
  });
  const canUndo = computed(() => !blocked.value && undoSteps.value > 0);
  const errorMessage = computed(() => failure.value ? errorText(failure.value, t) : "");
  const statusPillText = computed(() => {
    const state = gameState.value;
    if (session.needsSync.value || phase.value === "syncing") return t("recovery.syncing");
    if (!state) return t("common.loading");
    if (state.status === "won") return t("game.winner", { player: formatPlayer(state.winner, displayMap.value) });
    if (state.status === "draw") return t("game.draw");
    if (aiThinking.value) return t("teaParty.thinking");
    return t("game.yourTurn", { player: formatPlayer(state.current_player, displayMap.value) });
  });
  let timer: ReturnType<typeof setTimeout> | undefined;
  function cancelDelay() { clearTimeout(timer); timer = undefined; }
  async function runAi() {
    const state = gameState.value;
    if (!state || !aiTurn.value || blocked.value) return;
    cancelDelay();
    await run(async signal => (await makeAiMove(state.game_id, {
      level: aiLevel.value, auto_apply: true, expected_revision: state.revision,
    }, signal)).state);
  }
  function schedule() {
    if (!aiTurn.value || blocked.value) return;
    cancelDelay();
    phase.value = "thinking";
    timer = setTimeout(() => { void runAi(); }, 600);
  }
  async function startNewGame() {
    if (blocked.value && phase.value !== "loading") return;
    cancelDelay();
    const state = await run(signal => createGame({ first_player: "X" }, signal), true);
    if (state) schedule();
  }
  async function placeAt(position: number) {
    const state = gameState.value;
    if (!state || !canPlace.value) return;
    const next = await run(signal => makeMove(state.game_id, position, state.revision, signal));
    if (next) schedule();
  }
  async function undoMove() {
    const state = gameState.value;
    if (!state || !canUndo.value) return;
    cancelDelay();
    await run(signal => undo(state.game_id, state.revision, undoSteps.value, signal));
  }
  const pendingSide = ref<TravelerSide | null>(null);
  const confirmOpen = ref(false);
  function requestRestart() {
    if (blocked.value) return;
    if (gameState.value?.history.length) confirmOpen.value = true;
    else void startNewGame();
  }
  function confirmRestart() {
    confirmOpen.value = false;
    if (pendingSide.value) travelerSide.value = pendingSide.value;
    pendingSide.value = null;
    void startNewGame();
  }
  function cancelRestart() { confirmOpen.value = false; pendingSide.value = null; }
  function updateTravelerSide(value: TravelerSide) {
    if (blocked.value || value === travelerSide.value) return;
    if (gameState.value?.history.length) { pendingSide.value = value; confirmOpen.value = true; return; }
    travelerSide.value = value;
    void startNewGame();
  }
  function updateAiLevel(value: AiLevel) { if (!blocked.value) aiLevel.value = value; }
  async function recover() {
    if (session.retryAfter.value > 0) return;
    if (!gameState.value) await startNewGame();
    else if (session.needsSync.value) await session.synchronize();
    else if (aiTurn.value) await runAi();
    else await session.synchronize();
  }
  const recoveryLabel = computed(() => !gameState.value ? t("recovery.create") :
    session.needsSync.value || !aiTurn.value ? t("recovery.sync") : t("recovery.ai"));
  watch([travelerSide, aiLevel, showCellNumbers, showLegalMoves, showWinningMoves, showThreatMoves, showRemovalPreview], () => {
    const prefs = loadGamePreferences();
    prefs[mode].travelerSide = travelerSide.value;
    prefs[mode].display = { numbers: showCellNumbers.value, legal: showLegalMoves.value, wins: showWinningMoves.value, threats: showThreatMoves.value, removal: showRemovalPreview.value };
    if (mode === "teaParty") prefs.teaParty.aiLevel = aiLevel.value;
    saveGamePreferences(prefs);
  });
  onMounted(() => { void startNewGame(); });
  onBeforeUnmount(cancelDelay);
  const { elementRef: boardPanelRef, heightStyle: boardHeightStyle } = useElementHeightCssVar("--game-board-panel-height");
  return { ...session, confirmOpen, requestRestart, confirmRestart, cancelRestart, t, travelerSide, aiLevel, displayMap, showCellNumbers, showLegalMoves, showWinningMoves,
    showThreatMoves, showRemovalPreview, loading, aiThinking, canPlace, canUndo, errorMessage, statusPillText,
    startNewGame, placeAt, undoMove, updateTravelerSide, updateAiLevel, recover, recoveryLabel, boardPanelRef, boardHeightStyle,
    pieceShortName: (piece: Piece) => formatPieceShort(piece),
    pieceFullName: (piece: Piece) => formatPieceFull(piece, displayMap.value),
    pieceClassName: (piece: Piece) => pieceDisplayClass(piece, displayMap.value),
  };
}
