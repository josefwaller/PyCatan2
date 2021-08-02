from colored import stylize, fg, bg

from ..game import Game
from .board import Board
from .coords import Coords
from ..player import Player
from .beginner_board import BeginnerBoard
from .hex_type import HexType
from .building_type import BuildingType
from .hex import Hex
from ..resource import Resource


class BoardRenderer:
    DEFAULT_PLAYER_COLORS = ["#00c40d", "#ff00d9", "#0000FF", "#00FFFF"]

    DEFAULT_HEX_COLORS = {
        HexType.FIELDS: "#ffea29",
        HexType.FOREST: "#005e09",
        HexType.PASTURE: "#52ff62",
        HexType.HILLS: "#cc1f0c",
        HexType.MOUNTAINS: "#7a7a7a",
        HexType.DESERT: "#ffe5a3",
    }

    DEFAULT_RESOURCE_COLORS = {
        Resource.GRAIN: "#ffea29",
        Resource.LUMBER: "#005e09",
        Resource.WOOL: "#52ff62",
        Resource.BRICK: "#cc1f0c",
        Resource.ORE: "#7a7a7a",
    }

    WATER_COLOR = "#2387de"

    def __init__(
        self,
        player_color_map={},
        hex_color_map=DEFAULT_HEX_COLORS,
        resource_color_map=DEFAULT_RESOURCE_COLORS,
    ):
        self._unused_player_colors = BoardRenderer.DEFAULT_PLAYER_COLORS
        self.player_color_map = player_color_map
        self.hex_color_map = hex_color_map
        self.resource_color_map = resource_color_map

    def _get_player_color(self, player: Player):
        if player not in self.player_color_map:
            self.player_color_map[player] = self._unused_player_colors.pop(0)
        return self.player_color_map[player]

    def _get_path(self, chars, path, board):
        fore = "#9c7500"
        back = self.hex_color_map[HexType.DESERT]
        if path.building is not None:
            fore = self._get_player_color(path.building.owner)
        elif frozenset(path.path_coords) in board.harbors:
            fore = "#000000"
        return list(map(lambda x: stylize(x, fg(fore) + bg(back)), chars))

    def _get_intersection(self, char, intersection):
        fore = "#9c7500"
        back = self.hex_color_map[HexType.DESERT]
        if intersection.building is not None:
            fore = self._get_player_color(intersection.building.owner)
            char = (
                "s"
                if intersection.building.building_type is BuildingType.SETTLEMENT
                else "c"
            )
        return [stylize(char, fg(fore) + bg(back))]

    def _get_hex_center(self, h):
        space = stylize(" ", bg(self.hex_color_map[h.hex_type]))
        if h.token_number is None:
            return [space] * 5
        token_color = (
            "#FF0000" if h.token_number == 6 or h.token_number == 8 else "#000000"
        )
        token_chars = [space if h.token_number < 10 else ""] + [
            stylize(h.token_number, fg(token_color) + bg("#FFFFFF"))
        ]
        return [space] + [t for t in token_chars] + [space, space]

    def _get_hex(self, board, coords):
        intersection_coords = [
            c + coords
            for c in (
                Coords(1, -1),
                Coords(1, 0),
                Coords(0, 1),
                Coords(-1, 1),
                Coords(-1, 0),
                Coords(0, -1),
            )
        ]
        intersections = [board.intersections[c] for c in intersection_coords]
        paths = [
            board.paths[
                frozenset(
                    {
                        intersection_coords[i],
                        intersection_coords[(i + 1) % len(intersection_coords)],
                    }
                )
            ]
            for i in range(len(intersection_coords))
        ]
        return [
            self._get_intersection(".", intersections[0])
            + self._get_path(["-", "-"], paths[0], board)
            + self._get_intersection("'", intersections[1])
            + self._get_path(["-", "-"], paths[1], board)
            + self._get_intersection(".", intersections[2]),
            self._get_path(["|"], paths[5], board)
            + self._get_hex_center(board.hexes[coords])
            + self._get_path(["|"], paths[2], board),
            self._get_intersection("'", intersections[5])
            + self._get_path(["-", "-"], paths[4], board)
            + self._get_intersection(".", intersections[4])
            + self._get_path(["-", "-"], paths[3], board)
            + self._get_intersection("'", intersections[3]),
        ]

    def _stylize_arr(self, arr, styles):
        return [stylize(s, styles) for s in arr]

    def _get_harbor(self, harbor):
        fore = (
            "#FFFFFF"
            if harbor.resource is None
            else self.resource_color_map[harbor.resource]
        )
        return [
            self._stylize_arr(
                ["3" if harbor.resource is None else "2", ":", "1"],
                fg(fore) + bg(BoardRenderer.WATER_COLOR),
            )
        ]

    def _get_harbor_coords(self, harbor, board):
        connected_coords = [
            [c + coord for c in Hex.CONNECTED_CORNER_OFFSETS]
            for coord in harbor.path_coords
        ]
        overlap = [
            c
            for c in connected_coords[0]
            if c in connected_coords[1] and c not in board.hexes
        ]
        hex_coords = self.get_hex_center_coords(overlap[0])
        return (hex_coords[0] + 2, hex_coords[1] + 1)

    def copy_into_array(self, buf, to_copy, x, y):
        for i in range(len(to_copy)):
            for j in range(len(to_copy[i])):
                buf[y + i][x + j] = to_copy[i][j]

    def get_hex_center_coords(self, coords):
        return ((int)(3 * coords.r), -(int)(1.34 * coords.q + 0.67 * coords.r))

    def render_board(self, board: Board):
        size = 20, 55
        buf = [
            [stylize(" ", bg(BoardRenderer.WATER_COLOR)) for j in range(size[1])]
            for i in range(size[0])
        ]

        center = int(size[1] / 2) - 3, int(size[0] / 2) - 1
        print(center)

        for hex_coords in board.hexes:
            x, y = self.get_hex_center_coords(hex_coords)
            self.copy_into_array(
                buf, self._get_hex(board, hex_coords), center[0] + x, center[1] + y
            )
        for harbor in board.harbors.values():
            x, y = self._get_harbor_coords(harbor, board)
            self.copy_into_array(
                buf, self._get_harbor(harbor), center[0] + x, center[1] + y
            )

        x, y = self.get_hex_center_coords(board.robber)
        self.copy_into_array(
            buf,
            [[stylize("R", fg("#FFFFFF") + bg("#000000"))]],
            center[0] + x + 4,
            center[1] + y + 1,
        )

        for row in buf:
            print("".join(row))


if __name__ == "__main__":
    g = Game(BeginnerBoard())
    g.build_settlement(
        g.players[0], Coords(1, 0), ensure_connected=False, cost_resources=False
    )
    g.build_road(g.players[0], {Coords(1, 0), Coords(2, 0)}, cost_resources=False)
    g.build_settlement(
        g.players[1], Coords(-3, 1), ensure_connected=False, cost_resources=False
    )
    g.build_road(g.players[1], {Coords(-3, 1), Coords(-3, 2)}, cost_resources=False)
    BoardRenderer().render_board(g.board)
