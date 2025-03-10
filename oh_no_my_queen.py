import io
import os

import berserk
import chess.engine
import chess.pgn
from tqdm import tqdm

API_TOKEN = os.getenv("LICHES_API_TOKEN")
PLAYER = os.getenv("LICHESS_PLAYER")


def detect_queen_blunders(
    pgn_text, stockfish_path="stockfish", depth=15, eval_threshold=5
):
    """
    Analyzes a chess game to detect potential queen blunders.

    Args:
        pgn_text (str): The PGN text of the chess game
        stockfish_path (str): Path to the Stockfish executable
        depth (int): Analysis depth for Stockfish
        eval_threshold (int): Evaluation threshold for a blunder

    Returns:
        list: Information about detected queen blunders
    """
    # Check if Stockfish exists at the specified path
    if not os.path.exists(stockfish_path) and stockfish_path != "stockfish":
        raise FileNotFoundError(f"Stockfish not found at {stockfish_path}")

    # Initialize Stockfish engine
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)

    # Parse the PGN
    pgn = io.StringIO(pgn_text)
    game = chess.pgn.read_game(pgn)

    # Prepare for analysis
    board = game.board()
    moves = list(game.mainline_moves())
    blunders = []

    # Track piece positions
    prev_eval = None

    # Analyze each move in the game
    for move_number, move in tqdm(
        enumerate(moves), total=len(moves), desc="Analyzing", unit="move", ncols=100
    ):
        # Get board state before the move
        pre_move_board = board.copy()
        pre_move_queens = {
            square: piece
            for square, piece in pre_move_board.piece_map().items()
            if piece.piece_type == chess.QUEEN
        }

        # Get evaluation before the move
        if prev_eval is None:
            info = engine.analyse(pre_move_board, chess.engine.Limit(depth=depth))
            prev_eval = info["score"].white().score(mate_score=10000)
            if prev_eval is None:  # Handle mate scores
                prev_eval = 10000 if info["score"].white().is_mate() else -10000

        # Make the move
        board.push(move)

        # Get board state after the move
        post_move_queens = {
            square: piece
            for square, piece in board.piece_map().items()
            if piece.piece_type == chess.QUEEN
        }

        # Get evaluation after the move
        info = engine.analyse(board, chess.engine.Limit(depth=depth))
        current_eval = info["score"].white().score(mate_score=10000)
        if current_eval is None:  # Handle mate scores
            current_eval = 10000 if info["score"].white().is_mate() else -10000

        # Calculate evaluation change from the perspective of the player who just moved
        perspective_multiplier = (
            -1 if move_number % 2 == 0 else 1
        )  # Adjust for white/black
        eval_change = perspective_multiplier * (current_eval - prev_eval)

        # Check if a queen disappeared and there was a significant eval drop
        queen_count_before = len(pre_move_queens)
        queen_count_after = len(post_move_queens)

        # Check if a queen was lost
        if queen_count_after < queen_count_before:
            if eval_change < -eval_threshold:
                player = (
                    game.headers["White"]
                    if move_number % 2 == 0
                    else game.headers["Black"]
                )
                blunders.append(
                    {
                        "move_number": move_number + 1,
                        "player": player,
                        "move": pre_move_board.san(move),
                        "position_before": pre_move_board.fen(),
                        "position_after": board.fen(),
                        "eval_before": prev_eval,
                        "eval_after": current_eval,
                        "eval_change": eval_change,
                    }
                )

        # Update previous evaluation for next iteration
        prev_eval = current_eval

    # Clean up
    engine.quit()

    return blunders


def main():
    session = berserk.TokenSession(API_TOKEN)
    client = berserk.Client(session=session)
    games = client.games.export_by_player(PLAYER, as_pgn=True)

    QueenBlunders = 0
    Streak = 0
    LongestStreak = 0
    Total = 0

    all_games = []

    for game in tqdm(games, desc="Fetching game", unit="", ncols=100):
        all_games.append(game)

    for game in tqdm(all_games, desc="Processing games", unit="game", ncols=100):
        Total += 1
        blunders = detect_queen_blunders(game, "stockfish")
        for blunder in blunders:
            if blunder["player"] == PLAYER:
                tqdm.write("Oh no! My queen!")
                QueenBlunders += 1
                tqdm.write(f"Blundered the queen in {QueenBlunders} / {Total} games.")
                Streak = 0
            else:
                Streak += 1
                if Streak > LongestStreak:
                    LongestStreak = Streak
                tqdm.write(f"No queen blunders for {Streak} games")


if __name__ == "__main__":
    main()
