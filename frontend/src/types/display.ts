import type { Player } from "./game";

export type TravelerSide = "first" | "second";
export type PlayerRole = "traveler" | "columbina";

export interface PlayerDisplay {
  player: Player;
  role: PlayerRole;
  name: string;
  pieceClass: string;
}

export type PlayerDisplayMap = Record<Player, PlayerDisplay>;
