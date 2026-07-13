import type { Piece, Player } from "../types/game";
import type { PlayerDisplayMap, TravelerSide } from "../types/display";
import { toRoman } from "./roman";

export function createPlayerDisplay(travelerSide: TravelerSide, translate: (key: string) => string): PlayerDisplayMap {
  const travelerPlayer: Player = travelerSide === "first" ? "X" : "O";
  const columbinaPlayer: Player = travelerPlayer === "X" ? "O" : "X";

  return {
    [travelerPlayer]: {
      player: travelerPlayer,
      role: "traveler",
      name: translate("player.traveler"),
      pieceClass: "piece-traveler",
    },
    [columbinaPlayer]: {
      player: columbinaPlayer,
      role: "columbina",
      name: translate("player.columbina"),
      pieceClass: "piece-columbina",
    },
  } as PlayerDisplayMap;
}

export function formatPlayer(player: Player | null, displayMap: PlayerDisplayMap, none = ""): string {
  return player ? displayMap[player].name : none;
}

export function formatPieceShort(piece: Piece | null, none = ""): string {
  return piece ? toRoman(piece.order) : none;
}

export function formatPieceFull(piece: Piece | null, displayMap: PlayerDisplayMap, none = ""): string {
  if (!piece) {
    return none;
  }
  return `${formatPlayer(piece.player, displayMap)}${formatPieceShort(piece)}`;
}

export function pieceDisplayClass(piece: Piece, displayMap: PlayerDisplayMap): string {
  return displayMap[piece.player].pieceClass;
}

export function isRoleTurn(player: Player, displayMap: PlayerDisplayMap, role: "traveler" | "columbina"): boolean {
  return displayMap[player].role === role;
}

