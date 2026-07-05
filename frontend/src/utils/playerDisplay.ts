import type { MoveEvent, Piece, Player } from "../types/game";
import type { PlayerDisplayMap, TravelerSide } from "../types/display";
import { toRoman } from "./roman";

export function createPlayerDisplay(travelerSide: TravelerSide): PlayerDisplayMap {
  const travelerPlayer: Player = travelerSide === "first" ? "X" : "O";
  const columbinaPlayer: Player = travelerPlayer === "X" ? "O" : "X";

  return {
    [travelerPlayer]: {
      player: travelerPlayer,
      role: "traveler",
      name: "旅行者",
      pieceClass: "piece-traveler",
    },
    [columbinaPlayer]: {
      player: columbinaPlayer,
      role: "columbina",
      name: "哥伦比娅",
      pieceClass: "piece-columbina",
    },
  } as PlayerDisplayMap;
}

export function formatPlayer(player: Player | null, displayMap: PlayerDisplayMap): string {
  return player ? displayMap[player].name : "无";
}

export function formatPieceShort(piece: Piece | null): string {
  return piece ? toRoman(piece.order) : "无";
}

export function formatPieceFull(piece: Piece | null, displayMap: PlayerDisplayMap): string {
  if (!piece) {
    return "无";
  }
  return `${formatPlayer(piece.player, displayMap)}${formatPieceShort(piece)}`;
}

export function pieceDisplayClass(piece: Piece, displayMap: PlayerDisplayMap): string {
  return displayMap[piece.player].pieceClass;
}

export function isRoleTurn(player: Player, displayMap: PlayerDisplayMap, role: "traveler" | "columbina"): boolean {
  return displayMap[player].role === role;
}

export function formatMoveEvent(event: MoveEvent, displayMap: PlayerDisplayMap): string {
  const beforeRemoval =
    event.removed_piece && event.removed_piece.player === event.player
      ? `${formatPieceFull(event.removed_piece, displayMap)} 先消失，`
      : "";
  const afterRemoval =
    event.removed_piece && event.removed_piece.player !== event.player
      ? `，随后 ${formatPieceFull(event.removed_piece, displayMap)} 消失`
      : "";
  const result = event.winner ? `，${formatPlayer(event.winner, displayMap)} 胜利` : "";

  return `第 ${event.move_number} 手：${beforeRemoval}${formatPieceFull(
    event.placed_piece,
    displayMap,
  )} 落在 ${event.position}${afterRemoval}${result}。`;
}
