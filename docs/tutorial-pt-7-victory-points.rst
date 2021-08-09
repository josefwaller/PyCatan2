Now let's show the victory points at the top: ::

    while choice != 4:
        print(game.board)
        print("Current Victory point standings:")
        for i in range(len(game.players)):
            print("Player %d: %d VP" % (i + 1, game.get_victory_points(game.players[i])))

 And now let's end the game at 10 victory points: ::

     if game.get_victory_points(current_player) >= 10:
        print("Congratuations! Player %d wins!" % (current_player_num + 1))
        print("Final board:")
        print(game.board)
        sys.exit(0)

And we're done!
Let's add some more info on where those VPs are coming from: ::

        print("Current Victory point standings:")
        for i in range(len(game.players)):
            print("Player %d: %d VP" % (i + 1, game.get_victory_points(game.players[i])))
        print("Current longest road owner: %s" % ("Player %d" % (game.players.index(game.longest_road_owner) + 1) if game.longest_road_owner else "Nobody"))
        print("Current largest army owner: %s" % ("Player %d" % (game.players.index(game.largest_army_owner) + 1) if game.largest_army_owner else "Nobody"))

And with that, our game is completely finished!
The full text game source code is available on github: https://gist.github.com/josefwaller/a3c3c19b19e46150224e7a4f34bc4dbd
