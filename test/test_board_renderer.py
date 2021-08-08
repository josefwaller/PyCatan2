from pycatan.board import BoardRenderer, BeginnerBoard, Coords


def test_renders_beginner_board(capsys, snapshot):
    BoardRenderer(BeginnerBoard()).render_board()
    captured = capsys.readouterr()
    snapshot.assert_match(captured.out, "board.txt")


def test_can_get_as_string(snapshot):
    snapshot.assert_match(
        BoardRenderer(BeginnerBoard()).get_board_as_string(), "board.txt"
    )


def test_can_render_using_hex_labels(snapshot):
    b = BeginnerBoard()
    snapshot.assert_match(
        BoardRenderer(b).get_board_as_string(
            hex_labels={h: "%d" % (h.coords.q + h.coords.r) for h in b.hexes.values()}
        ),
        "label_hexes.txt",
    )


def test_can_render_using_labels(snapshot):
    b = BeginnerBoard()
    snapshot.assert_match(
        BoardRenderer(b).get_board_as_string(
            intersection_labels={b.intersections[Coords(1, 0)]: "a"}
        ),
        "label_intersections.txt",
    )


def test_can_render_using_path_labels(snapshot):
    b = BeginnerBoard()
    snapshot.assert_match(
        BoardRenderer(b).get_board_as_string(
            path_labels={
                b.paths[frozenset({Coords(1, 0), Coords(0, 1)})]: "A",
                b.paths[frozenset({Coords(1, 0), Coords(2, 0)})]: "B",
            }
        ),
        "label_paths.txt",
    )
