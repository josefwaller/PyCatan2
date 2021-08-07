******************
Text game Tutorial
******************

In this tutorial, we're going to use pycatan to make a version of the game playable in the terminal.

Initializing the Game
---------------------

Our game is just going to use the beginner board, which is already provided. ::

    from pycatan import Game
    from pycatan.board import BeginnerBoard

    game = Game(BeginnerBoard())

Done! Now we have a 4 player game of catan all set up. We can show the board by simply printing it. ::

    print(game.board)

The Building Phase
------------------

First let's set up the turn order: ::

    # Building phase
    player_order = list(range(len(game.players)))
    for i in player_order + list(reversed(player_order)):
        current_player = game.players[i]
        print("Player %d, it is your turn!" % (i + 1))
        coords = choose_intersection(game.board.get_valid_settlement_coords(current_player, ensure_connected = False))


Now we need the player to choose where they want to place their first settlement.
Usually the player could just click on it, but since we're in the console it's a big harder.
Luckily BoardRenderer lets us label the different intersections, and Board has methods to filter out the valid ones: ::

    # We're going to do some more complicated rendering, so import the BoardRenderer utility class
    from pycatan.board import BoardRenderer
    import string

    renderer = BoardRenderer(game.board)

    def choose_intersection(intersection_coords, renderer):
        # Long list of all letters and numbers to use as labels over the points
        label_letters = string.ascii_lowercase + string.ascii_uppercase + "123456789"
        # Now we make a map of letter to intersection, and give that to board renderer
        intersection_list = [game.board.intersections[i] for i in intersection_coords]
        intersection_labels = {intersection_list[i]: label_letters[i] for i in range(len(intersection_list))}
        renderer.render_board(intersection_labels = intersection_labels)

Run it and we get: ::

             3:1         2:1
              u--g--P--b--f--R--Z
              | 10  |  2  |  9  | 2:1
           t--e--c--d--X--G--E--m--F
       2:1 | 12  |  6  |  4  | 10  |
        a--Q--W--C--Y--l--B--j--O--r--2
        |  9  | 11  |   R |  3  |  8  | 3:1
        z--D--k--x--y--L--s--1--N--T--A
       2:1 |  8  |  3  |  4  |  5  |
           i--I--p--q--M--V--w--K--n
              |  5  |  6  | 11  | 2:1
              J--U--S--H--o--v--h
             3:1         3:1

Each intersection is now labelled with a letter!
Now we just ask the player where they want to build a settlement: ::

    def choose_intersection(intersection_coords, prompt):
        ...
        # Prompt the user
        letter = input(prompt)
        letter_to_intersection = {v: k for k, v in intersection_labels.items()}
        intersection = letter_to_intersection[letter]
        return intersection.coords

And then finally, build a settlement there! ::

    game.build_settlement(player = current_player, coords = coords, cost_resources = False, ensure_connected = False)

The entire file at this point should look like this: ::

    from pycatan import Game
    from pycatan.board import BeginnerBoard, BoardRenderer
    import string

    game = Game(BeginnerBoard())
    renderer = BoardRenderer(game.board)


    label_letters = string.ascii_lowercase + string.ascii_uppercase + "123456789"
    def choose_intersection(intersection_coords, prompt):
        # Label all the letters on the board
        intersection_list = [game.board.intersections[i] for i in intersection_coords]
        intersection_labels = {intersection_list[i]: label_letters[i] for i in range(len(intersection_list))}
        renderer.render_board(intersection_labels = intersection_labels)
        # Prompt the user
        letter = input(prompt)
        letter_to_intersection = {v: k for k, v in intersection_labels.items()}
        intersection = letter_to_intersection[letter]
        return intersection.coords

    player_order = list(range(len(game.players)))
    for i in player_order + list(reversed(player_order)):
        current_player = game.players[i]
        print("Player %d, it is your turn!" % (i + 1))
        coords = choose_intersection(game.board.get_valid_settlement_coords(current_player, ensure_connected = False), "Where do you want to build your settlement? ")
        game.build_settlement(player = current_player, coords = coords, cost_resources = False, ensure_connected = False)

Now run the code, and try building a settlement on the intersection labelled M.
It should look like this: ::

    Player 1, it is your turn!




                     3:1         2:1
                      u--g--P--b--f--R--Z
                      | 10  |  2  |  9  | 2:1
                   t--e--c--d--X--G--E--m--F
               2:1 | 12  |  6  |  4  | 10  |
                a--Q--W--C--Y--l--B--j--O--r--2
                |  9  | 11  |   R |  3  |  8  | 3:1
                z--D--k--x--y--L--s--1--N--T--A
               2:1 |  8  |  3  |  4  |  5  |
                   i--I--p--q--M--V--w--K--n
                      |  5  |  6  | 11  | 2:1
                      J--U--S--H--o--v--h
                     3:1         3:1



    Where do you want to build your first settlement?  M
    Player 2, it is your turn!




                     3:1         2:1
                      t--g--M--b--f--O--V
                      | 10  |  2  |  9  | 2:1
                   s--e--c--d--T--F--D--m--E
               2:1 | 12  |  6  |  4  | 10  |
                a--N--S--B--U--l--A--j--L--q--X
                |  9  | 11  |   R |  3  |  8  | 3:1
                y--C--k--w--x--.--r--W--K--Q--z
               2:1 |  8  |  3  |  4  |  5  |
                   i--H--p--.--s--.--v--J--n
                      |  5  |  6  | 11  | 2:1
                      I--R--P--G--o--u--h
                     3:1         3:1



    Where do you want to build your first settlement?

There's now a settlement on the board!
And notice that the next player doesn't have the intersections directly beisde it as an option to select - because they aren't valid intersections for their settlement.
Now let's allow the player to build a road.
First we'll add another function that allows the player to choose a road from the board: ::

    def choose_path(path_coords, prompt):
        # Label all the paths with a letter
        path_list = [game.board.paths[i] for i in path_coords]
        path_labels = {path_list[i]: label_letters[i] for i in range(len(path_coords))}
        renderer.render_board(path_labels = path_labels)
        # Ask the user for a letter
        letter = input(prompt)[0]
        # Get the path from the letter entered by the user
        letter_to_path = {v: k for k, v in path_labels.items()}
        return letter_to_path[letter].path_coords

And now use it in the building phase: ::

    # Get the valid locations for the player to build a road
    road_options = game.board.get_valid_road_coords(current_player, connected_intersection = coords)
    # Ask the user to choose one
    road_coords = choose_path(road_options, "Where do you want to build your road to? ")
    # Build a road
    game.build_road(player = current_player, path_coords = road_coords, cost_resources = False)

Now the player is able to build a road!
The last thing to add to the building phase is the player getting the resources around a settlement when they build it.
So let's add that: ::

    game.build_settlement(player = current_player, coords = coords, cost_resources = False, ensure_connected = False)
    # Add the resources around the intersection to the player's hand
    current_player.add_resources(game.board.get_hex_resources_for_intersection(coords))

The entire file should look like this now: ::

    from pycatan import Game
    from pycatan.board import BeginnerBoard, BoardRenderer
    import string

    game = Game(BeginnerBoard())
    renderer = BoardRenderer(game.board)


    label_letters = string.ascii_lowercase + string.ascii_uppercase + "123456789"
    def choose_intersection(intersection_coords, prompt):
        # Label all the letters on the board
        intersection_list = [game.board.intersections[i] for i in intersection_coords]
        intersection_labels = {intersection_list[i]: label_letters[i] for i in range(len(intersection_list))}
        renderer.render_board(intersection_labels = intersection_labels)
        # Prompt the user
        letter = input(prompt)
        letter_to_intersection = {v: k for k, v in intersection_labels.items()}
        intersection = letter_to_intersection[letter]
        return intersection.coords

    def choose_path(path_coords, prompt):
        # Label all the paths with a letter
        path_list = [game.board.paths[i] for i in path_coords]
        path_labels = {path_list[i]: label_letters[i] for i in range(len(path_coords))}
        renderer.render_board(path_labels = path_labels)
        # Ask the user for a letter
        letter = input(prompt)[0]
        # Get the path from the letter entered by the user
        letter_to_path = {v: k for k, v in path_labels.items()}
        return letter_to_path[letter].path_coords

    player_order = list(range(len(game.players)))
    for i in player_order + list(reversed(player_order)):
        current_player = game.players[i]
        print("Player %d, it is your turn!" % (i + 1))
        coords = choose_intersection(game.board.get_valid_settlement_coords(current_player, ensure_connected = False), "Where do you want to build your settlement? ")
        game.build_settlement(player = current_player, coords = coords, cost_resources = False, ensure_connected = False)
        current_player.add_resources(game.board.get_hex_resources_for_intersection(coords))
        # Print the road options
        road_options = game.board.get_valid_road_coords(current_player, connected_intersection = coords)
        road_coords = choose_path(road_options, "Where do you want to build your road to? ")
        game.build_road(player = current_player, path_coords = road_coords, cost_resources = False)
