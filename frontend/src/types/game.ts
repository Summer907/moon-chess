export type Player = "X" | "O";
export type GameStatus = "playing" | "won" | "draw";

export interface Piece {
  id: string;
  player: Player;
  position: number;
  order: number;
}

export interface MoveEvent {
  move_number: number;
  player: Player;
  removed_piece: Piece | null;
  placed_piece: Piece;
  position: number;
  winner: Player | null;
  line: number[] | null;
  note: string;
}

export interface Analysis {
  current_player: Player;
  pending_removal: Piece | null;
  upcoming_removal: Piece | null;
  retained_pieces_after_removal: Piece[];
  current_winning_moves: number[];
  opponent_real_threats: number[];
  explanation: string[];
}

export interface GameState {
  game_id: string;
  current_player: Player;
  move_number: number;
  pieces: Piece[];
  board: Array<Piece | null>;
  status: GameStatus;
  winner: Player | null;
  winning_line: number[] | null;
  history: MoveEvent[];
  pending_removal: Piece | null;
  upcoming_removal: Piece | null;
  legal_moves: number[];
  analysis: Analysis;
}

export interface CreateGameRequest {
  first_player?: Player;
  max_moves?: number;
}
