from pycatan.board import BoardRenderer, BeginnerBoard


def test_renders_beginner_board(capsys, snapshot):
    BoardRenderer().render_board(BeginnerBoard())
    captured = capsys.readouterr()
    snapshot.assert_match(captured.out, "board.txt")
