import pytest

from oh_no_my_queen import detect_queen_blunders


def test_no_blunders():
    pgn_text = """
[Event "Rated bullet game"]
[Site "https://lichess.org/wgE0vCXR"]
[Date "2025.03.10"]
[White "doreality"]
[Black "OnePysy"]
[Result "1-0"]
[GameId "wgE0vCXR"]
[UTCDate "2025.03.10"]
[UTCTime "09:45:26"]
[WhiteElo "3008"]
[BlackElo "3035"]
[WhiteRatingDiff "+6"]
[BlackRatingDiff "-6"]
[Variant "Standard"]
[TimeControl "60+0"]
[ECO "C26"]
[Opening "Vienna Game: Falkbeer Variation"]
[Termination "Normal"]

1. e4 e5 2. Nc3 Nf6 3. d4 exd4 4. Qxd4 Nc6 5. Qd3 Bc5 6. Be3 Nb4 7. Qd2 Bxe3 8. fxe3 d6 9. a3 Nc6 10. O-O-O Be6 11. Nf3 Qe7 12. Nd4 O-O-O 13. Nxc6 bxc6 14. Qd4 c5 15. Ba6+ Kd7 16. Qa4+ c6 17. e5 Nd5 18. Nxd5 Bxd5 19. Rxd5 Rb8 20. Rxd6+ 1-0
    """
    blunders = detect_queen_blunders(pgn_text)
    assert len(blunders) == 0


def test_with_blunders():
    pgn_text = """
[Event "Casual correspondence game"]
[Site "https://lichess.org/ZMUDUiYY"]
[Date "2025.03.10"]
[White "Anonymous"]
[Black "lichess AI level 8"]
[Result "0-1"]
[GameId "ZMUDUiYY"]
[UTCDate "2025.03.10"]
[UTCTime "09:33:35"]
[WhiteElo "?"]
[BlackElo "?"]
[Variant "Standard"]
[TimeControl "-"]
[ECO "B10"]
[Opening "Caro-Kann Defense"]
[Termination "Normal"]
[Annotator "lichess.org"]

1. e4 c6 2. Nc3 d5 { B10 Caro-Kann Defense } 3. d3 d4 4. Qg4 Bxg4 5. f3 Bd7 6. Nge2 dxc3 7. Nxc3 Qb6 8. Nd5 cxd5 9. exd5 Qa5+ 10. Bd2 Qxd5 11. O-O-O Qxa2 12. Re1 Qa1# { Black wins by checkmate. } 0-1
    """
    blunders = detect_queen_blunders(pgn_text)
    assert len(blunders) == 1
